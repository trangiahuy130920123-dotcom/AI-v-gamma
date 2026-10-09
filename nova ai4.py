import os
import re
import html
import json
import streamlit as st

import requests
import io
from urllib.parse import quote
from datetime import datetime

# Tùy chọn: cài thêm python-pptx và python-docx để xuất tệp
try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
except ImportError:
    Presentation = None

try:
    from docx import Document
except ImportError:
    Document = None

# ============================================================
# NOVA AI — GROQ AI + PRESENTATION
# One-file Streamlit app
#
# Cài:
#   pip install streamlit requests python-pptx python-docx
#
# Chạy:
#   streamlit run nova_ai.py
#
# API key:
#   Cách 1: nhập ở thanh bên
#   Cách 2: đặt biến môi trường GROQ_API_KEY (hoặc st.secrets)
# ============================================================

st.set_page_config(
    page_title="Nova AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# STYLE
# ============================================================

st.markdown("""
<style>
/* Không ẩn <header>: nó chứa nút mở thanh bên (nhập API key). */
#MainMenu, footer {visibility:hidden;}
header[data-testid="stHeader"] {background:transparent;}

.stApp {
    background:#f7f7f8;
}

.block-container {
    max-width:1100px;
    padding:28px 24px 110px;
}

.topbar {
    display:flex;
    align-items:center;
    margin-bottom:38px;
}

.brand {
    display:flex;
    align-items:center;
    gap:12px;
}

.logo {
    width:42px;
    height:42px;
    border-radius:13px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:#111;
    color:white;
    font-size:21px;
    font-weight:700;
}

.brand-name {
    font-size:20px;
    font-weight:700;
    color:#111;
}

.badge {
    font-size:12px;
    padding:5px 9px;
    border-radius:999px;
    background:#ececf0;
    color:#666;
}

.hero {
    text-align:center;
    margin:70px auto 35px;
}

.hero h1 {
    font-size:46px;
    line-height:1.05;
    letter-spacing:-1.8px;
    color:#111;
    margin-bottom:13px;
}

.hero p {
    color:#777;
    font-size:17px;
}

.feature {
    border:1px solid #e5e5e8;
    border-radius:18px;
    padding:18px;
    background:white;
    min-height:120px;
}

.card-title {
    font-weight:700;
    color:#222;
    font-size:15px;
    margin-bottom:8px;
}

.card-desc {
    color:#777;
    font-size:13px;
    line-height:1.5;
}

/* Tin nhắn chat (st.chat_message) */
[data-testid="stChatMessage"] {
    background:white;
    border:1px solid #e5e5e8;
    border-radius:18px;
    padding:14px 18px;
    max-width:780px;
    margin:10px auto;
    overflow-wrap:anywhere;
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span {
    color:#222;
}

.slide-card {
    background:white;
    border:1px solid #e2e2e6;
    border-radius:20px;
    padding:28px;
    margin:16px auto;
    max-width:800px;
    box-shadow:0 8px 28px rgba(0,0,0,.04);
}

.slide-number {
    color:#888;
    font-size:12px;
    font-weight:700;
    text-transform:uppercase;
    letter-spacing:1px;
    margin-bottom:8px;
}

.slide-title {
    color:#111;
    font-size:25px;
    font-weight:750;
    margin-bottom:12px;
}

.slide-body {
    color:#444;
    font-size:15px;
    line-height:1.65;
}

@media (max-width:700px) {
    .block-container {
        padding:18px 14px 100px;
    }

    .hero {
        margin-top:45px;
    }

    .hero h1 {
        font-size:34px;
    }

    .hero p {
        font-size:15px;
    }

    .slide-card {
        padding:20px;
    }
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "started" not in st.session_state:
    st.session_state.started = False

if "presentation" not in st.session_state:
    st.session_state.presentation = None

# ============================================================
# OPENAI
# ============================================================

with st.sidebar:
    st.markdown("## ✦ Nova AI")
    st.caption("Kết nối AI bằng Groq API (miễn phí)")

    # Thứ tự ưu tiên: biến môi trường -> st.secrets (Streamlit Cloud) -> nhập tay
    env_key = os.getenv("GROQ_API_KEY", "")
    if not env_key:
        try:
            env_key = st.secrets.get("GROQ_API_KEY", "")
        except Exception:
            env_key = ""

    api_key = st.text_input(
        "Groq API Key",
        value=env_key,
        type="password",
        placeholder="gsk_...",
        help="Key chỉ được dùng trong phiên Streamlit hiện tại.",
    )

    @st.cache_data(ttl=300, show_spinner=False)
    def fetch_models(key):
        """Hỏi Groq xem key này dùng được model nào."""
        r = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {key}"},
            timeout=20,
        )
        if r.status_code != 200:
            try:
                detail = r.json().get("error", {}).get("message", r.text)
            except Exception:
                detail = r.text
            raise RuntimeError(f"HTTP {r.status_code}: {detail[:200]}")
        skip = ("whisper", "tts", "guard", "playai", "distil-whisper")
        ids = sorted(
            m["id"] for m in r.json().get("data", [])
            if m.get("active", True) and not any(x in m["id"].lower() for x in skip)
        )
        return ids

    model_options = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    if api_key and api_key.strip():
        try:
            fetched = fetch_models(api_key.strip())
            if fetched:
                model_options = fetched
                st.caption(f"✅ Key hợp lệ — có {len(fetched)} model dùng được.")
            else:
                st.warning("Key hợp lệ nhưng không có model nào dùng được. Kiểm tra Model permissions trên console.groq.com.")
        except Exception as exc:
            st.warning(f"Không lấy được danh sách model: {exc}")

    model = st.selectbox("Model", model_options, index=0)

    custom_model = st.text_input(
        "Hoặc nhập tên model khác",
        placeholder="vd: llama-3.3-70b-versatile",
        help="Nếu điền, sẽ dùng model này thay cho danh sách trên.",
    )
    if custom_model.strip():
        model = custom_model.strip()

    st.divider()
    st.caption("Ví dụ:")
    st.caption("• Logistics là gì?")
    st.caption("• Giải thích AI cho học sinh lớp 10")
    st.caption("• Tạo bài thuyết trình 8 slide về Logistics")

    st.divider()
    st.markdown("### 🎨 Tạo hình ảnh (miễn phí)")
    image_prompt = st.text_area(
        "Mô tả hình ảnh muốn tạo",
        placeholder="Ví dụ: tranh minh họa hệ mặt trời phong cách 3D...",
        key="image_prompt",
    )
    image_size = st.selectbox("Kích thước ảnh", ["1024x1024", "1280x720", "720x1280"])
    gen_clicked = st.button("Tạo ảnh", use_container_width=True)


def get_client():
    """Trả về API key (hoặc None nếu chưa nhập)."""
    if not api_key or not api_key.strip():
        return None
    return api_key.strip()

def call_openai(key, messages):
    """Gọi Groq (API tương thích OpenAI) bằng requests."""
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        json={"model": model, "messages": messages},
        timeout=120,
    )
    if r.status_code != 200:
        try:
            detail = r.json().get("error", {}).get("message", r.text)
        except Exception:
            detail = r.text
        raise RuntimeError(f"HTTP {r.status_code}: {detail[:400]}")

    data = r.json()
    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError("API không trả về nội dung.")
    return (choices[0].get("message", {}).get("content") or "").strip()

def is_presentation_request(text):
    """
    Chỉ bật chế độ presentation khi người dùng thực sự yêu cầu.
    Các câu hỏi thông thường sẽ đi vào chat bình thường.
    """
    t = text.lower().strip()

    explicit_phrases = [
        "tạo bài thuyết trình",
        "tạo bài trình bày",
        "làm bài thuyết trình",
        "làm bài trình bày",
        "tạo slide",
        "tạo slides",
        "làm slide",
        "làm slides",
        "tạo powerpoint",
        "tạo powerpoint",
        "làm powerpoint",
        "presentation",
        "presentation về",
        "slides về",
        "slide về",
        "bài thuyết trình",
    ]

    return any(p in t for p in explicit_phrases)

def ask_ai(user_prompt):
    client = get_client()

    if client is None:
        return (
            "⚠️ Chưa có Groq API Key.\n\n"
            "Mở thanh bên trái → nhập API Key → gửi lại câu hỏi."
        )

    history = []
    for role, content in st.session_state.messages[-12:]:
        if content.startswith(("❌", "⚠️")):
            continue
        if role == "user":
            history.append({"role": "user", "content": content})
        elif role == "assistant":
            history.append({"role": "assistant", "content": content})

    # Tránh gửi lại câu user hiện tại 2 lần.
    if history and history[-1]["role"] == "user" and history[-1]["content"] == user_prompt:
        history = history[:-1]

    system = """
Bạn là Nova AI, một trợ lý AI thân thiện, thông minh và hữu ích.

Quy tắc quan trọng:
1. Nếu người dùng chỉ hỏi một câu hỏi bình thường, hãy TRẢ LỜI CÂU HỎI.
2. Không tự biến câu trả lời thành bài thuyết trình.
3. Chỉ khi người dùng rõ ràng yêu cầu tạo bài thuyết trình/slide/PowerPoint,
   ứng dụng mới chuyển sang chế độ presentation.
4. Trả lời bằng tiếng Việt nếu người dùng dùng tiếng Việt.
5. Không nói rằng bạn là Gamma. Bạn chỉ cung cấp tính năng tạo nội dung
   trình bày theo phong cách hiện đại, tương tự một công cụ presentation AI.
6. Nếu câu hỏi không cần dài, trả lời ngắn gọn và dễ hiểu.
7. Viết công thức toán bằng LaTeX với dấu $...$ (trong dòng) hoặc $$...$$ (riêng dòng).
   Không dùng \\( \\) hay \\[ \\].
"""

    messages = [{"role": "system", "content": system}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_prompt})

    try:
        return call_openai(client, messages)
    except Exception as e:
        return (
            "❌ Không gọi được AI.\n\n"
            f"Chi tiết lỗi: `{type(e).__name__}: {e}`"
        )

def create_presentation(user_prompt):
    client = get_client()

    if client is None:
        return None, (
            "⚠️ Chưa có Groq API Key.\n\n"
            "Mở thanh bên trái → nhập API Key → gửi lại yêu cầu."
        )

    presentation_instruction = f"""
Người dùng yêu cầu tạo một bài thuyết trình.

Yêu cầu gốc:
{user_prompt}

Hãy tạo nội dung bài thuyết trình hiện đại, rõ ràng, dễ trình bày.
Nếu người dùng không ghi số slide thì tự chọn khoảng 7-10 slide.

Chỉ trả về JSON hợp lệ, không markdown, theo đúng cấu trúc:
{{
  "title": "Tên bài",
  "subtitle": "Mô tả ngắn",
  "slides": [
    {{
      "title": "Tiêu đề slide",
      "bullets": ["Ý 1", "Ý 2", "Ý 3"]
    }}
  ]
}}

Không thêm text ngoài JSON.
"""

    try:
        raw = call_openai(
            client,
            [
                {
                    "role": "system",
                    "content": (
                        "Bạn là công cụ tạo presentation AI. "
                        "JSON phải hợp lệ và nội dung phải bằng tiếng Việt."
                    ),
                },
                {"role": "user", "content": presentation_instruction},
            ],
        )

        # Loại bỏ markdown fence nếu model vô tình thêm vào.
        raw = re.sub(r"^```json\s*", "", raw, flags=re.I)
        raw = re.sub(r"^```\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        data = json.loads(raw)

        if not isinstance(data, dict) or not isinstance(data.get("slides"), list):
            raise ValueError("AI trả về cấu trúc slide không hợp lệ.")

        return data, None

    except Exception as e:
        return None, (
            "❌ Không tạo được bài thuyết trình.\n\n"
            f"Chi tiết lỗi: `{type(e).__name__}: {e}`"
        )


def build_pptx(data):
    if Presentation is None:
        raise RuntimeError("Thiếu thư viện python-pptx. Cài bằng: pip install python-pptx")
    prs = Presentation()
    title_slide = prs.slides.add_slide(prs.slide_layouts[0])
    title_slide.shapes.title.text = str(data.get("title", "Bài thuyết trình"))
    subtitle = data.get("subtitle", "")
    if len(title_slide.placeholders) > 1:
        title_slide.placeholders[1].text = str(subtitle)
    for item in data.get("slides", []):
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = str(item.get("title", ""))
        body = slide.placeholders[1].text_frame
        body.clear()
        for i, bullet in enumerate(item.get("bullets", [])):
            paragraph = body.paragraphs[0] if i == 0 else body.add_paragraph()
            paragraph.text = str(bullet)
            paragraph.level = 0
            paragraph.font.size = Pt(22)
    buffer = io.BytesIO()
    prs.save(buffer)
    return buffer.getvalue()

def build_docx(title, content):
    if Document is None:
        raise RuntimeError("Thiếu thư viện python-docx. Cài bằng: pip install python-docx")
    doc = Document()
    doc.add_heading(title, 0)
    for line in content.splitlines():
        if line.strip():
            doc.add_paragraph(line)
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

def fix_math(text):
    """Đổi \\( \\) và \\[ \\] của LaTeX sang $ $ / $$ $$ để Streamlit hiển thị công thức."""
    text = re.sub(r"\\\[(.+?)\\\]", lambda m: "\n$$" + m.group(1).strip() + "$$\n", text, flags=re.S)
    text = re.sub(r"\\\((.+?)\\\)", lambda m: "$" + m.group(1).strip() + "$", text, flags=re.S)
    # Trường hợp model chỉ viết [ ... ] (mất dấu gạch chéo) quanh một công thức
    text = re.sub(
        r"^[ \t]*\[\s*(.*\\[a-zA-Z]+.*?)\s*\][ \t]*$",
        lambda m: "\n$$" + m.group(1) + "$$\n",
        text,
        flags=re.M,
    )
    return text

def generate_image(prompt, size="1024x1024"):
    """Tạo ảnh miễn phí qua Pollinations.ai (không cần API key)."""
    width, height = size.split("x")
    url = (
        "https://image.pollinations.ai/prompt/" + quote(prompt)
        + f"?width={width}&height={height}&nologo=true&model=flux"
    )
    r = requests.get(url, timeout=180)
    if r.status_code != 200 or "image" not in r.headers.get("content-type", ""):
        raise RuntimeError(f"HTTP {r.status_code}: dịch vụ tạo ảnh không trả về ảnh.")
    return r.content

def to_english_prompt(text):
    """Nhờ Groq dịch mô tả sang tiếng Anh để ảnh đẹp hơn; lỗi thì dùng nguyên văn."""
    key = get_client()
    if key is None:
        return text
    try:
        out = call_openai(key, [
            {"role": "system", "content": "Translate the user's image description into a detailed English prompt for an image generator. Reply with the prompt only."},
            {"role": "user", "content": text},
        ])
        return out or text
    except Exception:
        return text

if gen_clicked:
    if not image_prompt.strip():
        st.sidebar.warning("Nhập mô tả hình ảnh trước.")
    else:
        try:
            with st.spinner("Đang tạo ảnh..."):
                st.session_state.generated_image = generate_image(
                    to_english_prompt(image_prompt.strip()), image_size
                )
        except Exception as exc:
            st.sidebar.error(f"Không tạo được ảnh: {exc}")

def render_ai_message(message):
    # Markdown renderer của Streamlit đẹp hơn HTML thủ công và an toàn hơn.
    st.markdown(fix_math(message))

# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="topbar">
    <div class="brand">
        <div class="logo">✦</div>
        <div class="brand-name">Nova AI</div>
        <div class="badge">AI + Presentation</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# HOME
# ============================================================

if not st.session_state.started:
    st.markdown("""
    <div class="hero">
        <h1>What can I help you create?</h1>
        <p>
            Hỏi AI bất cứ điều gì — hoặc yêu cầu tạo bài trình bày khi bạn cần.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# CHAT HISTORY
# ============================================================

for role, message in st.session_state.messages:
    with st.chat_message(role):
        st.markdown(fix_math(message))  # không bật unsafe_allow_html nên an toàn

# ============================================================
# PRESENTATION RESULT
# ============================================================

if st.session_state.presentation:
    data = st.session_state.presentation

    st.markdown(
        f"""
        <div class="slide-card">
            <div class="slide-number">Presentation</div>
            <div class="slide-title">{html.escape(str(data.get("title", "Bài thuyết trình")))}</div>
            <div class="slide-body">{html.escape(str(data.get("subtitle", "")))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for i, slide in enumerate(data.get("slides", []), start=1):
        title = html.escape(str(slide.get("title", f"Slide {i}")))
        bullets = slide.get("bullets", [])

        bullet_html = "".join(
            f"<li>{html.escape(str(item))}</li>"
            for item in bullets
        )

        st.markdown(
            f"""
            <div class="slide-card">
                <div class="slide-number">Slide {i}</div>
                <div class="slide-title">{title}</div>
                <div class="slide-body">
                    <ul>{bullet_html}</ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ============================================================
# EXPORT TỆP
# ============================================================

if st.session_state.presentation:
    try:
        pptx_bytes = build_pptx(st.session_state.presentation)
        st.download_button(
            "⬇️ Tải PowerPoint (.pptx)",
            data=pptx_bytes,
            file_name="nova_ai_presentation.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            use_container_width=True,
        )
    except Exception as exc:
        st.info(f"Muốn xuất PowerPoint, hãy cài thư viện: pip install python-pptx ({exc})")

if st.session_state.messages:
    transcript = "\n\n".join(
        ("Bạn: " if role == "user" else "Nova AI: ") + message
        for role, message in st.session_state.messages
    )
    st.download_button(
        "⬇️ Tải cuộc trò chuyện (.txt)",
        data=transcript.encode("utf-8"),
        file_name="nova_ai_chat.txt",
        mime="text/plain; charset=utf-8",
        use_container_width=True,
    )
    if Document is not None:
        try:
            docx_bytes = build_docx("Cuộc trò chuyện Nova AI", transcript)
            st.download_button(
                "⬇️ Tải cuộc trò chuyện (.docx)",
                data=docx_bytes,
                file_name="nova_ai_chat.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        except Exception:
            pass

if st.session_state.get("generated_image"):
    st.image(st.session_state.generated_image, caption="Ảnh do Nova AI tạo", use_container_width=True)
    st.download_button(
        "⬇️ Tải hình ảnh (.png)",
        data=st.session_state.generated_image,
        file_name="nova_ai_image.png",
        mime="image/png",
        use_container_width=True,
    )

# ============================================================
# INPUT
# ============================================================

prompt = st.chat_input(
    "Hỏi một câu hỏi hoặc yêu cầu tạo bài trình bày..."
)

if prompt:
    st.session_state.started = True
    st.session_state.messages.append(("user", prompt))

    with st.chat_message("user"):
        st.markdown(prompt)

    # Chỉ kích hoạt presentation khi người dùng yêu cầu rõ ràng.
    if is_presentation_request(prompt):
        with st.spinner("✦ Nova AI đang tạo bài thuyết trình..."):
            presentation, error = create_presentation(prompt)

        if error:
            st.session_state.messages.append(("assistant", error))
        else:
            st.session_state.presentation = presentation
            st.session_state.messages.append(
                (
                    "assistant",
                    "Đã tạo xong bài thuyết trình. Mình hiển thị các slide bên dưới."
                )
            )
    else:
        with st.spinner("✦ Nova AI đang suy nghĩ..."):
            answer = ask_ai(prompt)

        st.session_state.messages.append(("assistant", answer))

    st.rerun()

# ============================================================
# FEATURES
# ============================================================

if not st.session_state.messages:
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature">
            <div class="card-title">💬 Hỏi đáp</div>
            <div class="card-desc">
                Hỏi câu hỏi bình thường và nhận câu trả lời từ AI thật.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature">
            <div class="card-title">📊 Tạo trình bày</div>
            <div class="card-desc">
                Chỉ tạo slide khi bạn thực sự yêu cầu bài thuyết trình.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature">
            <div class="card-title">✨ Một AI duy nhất</div>
            <div class="card-desc">
                Một giao diện cho hỏi đáp và tạo nội dung trình bày.
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# RESET
# ============================================================

if st.session_state.messages:
    if st.button("🗑️ Xóa cuộc trò chuyện"):
        st.session_state.messages = []
        st.session_state.started = False
        st.session_state.presentation = None
        st.rerun()
