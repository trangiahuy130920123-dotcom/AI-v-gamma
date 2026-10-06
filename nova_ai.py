import streamlit as st

# ==============================
# NOVA AI — UI PROTOTYPE
# One-file Streamlit app
# ==============================

st.set_page_config(
    page_title="Nova AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
#MainMenu, header, footer {visibility:hidden;}

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

.chat-wrap {
    max-width:780px;
    margin:35px auto;
}

.user-msg {
    background:#111;
    color:white;
    padding:13px 17px;
    border-radius:18px 18px 5px 18px;
    margin:12px 0 12px auto;
    max-width:80%;
}

.ai-msg {
    background:white;
    border:1px solid #e5e5e8;
    color:#222;
    padding:15px 18px;
    border-radius:18px 18px 18px 5px;
    max-width:80%;
}

.presentation {
    background:white;
    border:1px solid #e2e2e6;
    border-radius:20px;
    padding:28px;
    margin:18px auto;
    max-width:800px;
}

.presentation h2 {
    margin-bottom:15px;
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
}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# SESSION STATE
# ------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "started" not in st.session_state:
    st.session_state.started = False

# ------------------------------
# HEADER
# ------------------------------

st.markdown("""
<div class="topbar">
    <div class="brand">
        <div class="logo">✦</div>
        <div class="brand-name">Nova AI</div>
        <div class="badge">AI + Presentation</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------
# HOME
# ------------------------------

if not st.session_state.started:
    st.markdown("""
    <div class="hero">
        <h1>What can I help you create?</h1>
        <p>
            Hỏi AI bất cứ điều gì — hoặc yêu cầu tạo bài trình bày khi bạn cần.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------
# CHAT HISTORY
# ------------------------------

if st.session_state.messages:
    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)

    for role, message in st.session_state.messages:
        if role == "user":
            st.markdown(
                f'<div class="user-msg">{message}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="ai-msg">{message}</div>',
                unsafe_allow_html=True
            )

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------
# INPUT
# ------------------------------

prompt = st.chat_input(
    "Hỏi một câu hỏi hoặc yêu cầu tạo bài trình bày..."
)

if prompt:
    st.session_state.started = True
    st.session_state.messages.append(("user", prompt))

    # Prototype response.
    # AI thật sẽ được kết nối ở bước tiếp theo.
    st.session_state.messages.append((
        "assistant",
        "Mình đã nhận yêu cầu của bạn. Phần AI thật sẽ được kết nối ở bước tiếp theo."
    ))

    st.rerun()

# ------------------------------
# FEATURES
# ------------------------------

if not st.session_state.messages:
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature">
            <div class="card-title">💬 Hỏi đáp</div>
            <div class="card-desc">
                Đặt câu hỏi và nhận câu trả lời từ AI.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature">
            <div class="card-title">📊 Tạo trình bày</div>
            <div class="card-desc">
                Chỉ tạo nội dung trình bày khi người dùng yêu cầu.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature">
            <div class="card-title">✨ Một AI duy nhất</div>
            <div class="card-desc">
                Kết hợp hỏi đáp và khả năng tạo nội dung kiểu Gamma.
            </div>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------
# RESET
# ------------------------------

if st.session_state.messages:
    if st.button("🗑️ Xóa cuộc trò chuyện"):
        st.session_state.messages = []
        st.session_state.started = False
        st.rerun()
