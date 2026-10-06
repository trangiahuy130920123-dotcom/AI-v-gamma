import streamlit as st

st.set_page_config(
    page_title="Nova AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
#MainMenu, header, footer {visibility: hidden;}

.stApp {
    background: #f7f7f8;
}

.block-container {
    max-width: 1100px;
    padding: 28px 24px 110px;
}

/* Header */
.topbar {
    display:flex;
    align-items:center;
    justify-content:space-between;
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

/* Hero */
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

/* Prompt box */
.prompt {
    max-width:780px;
    margin:auto;
    padding:18px;
    border:1px solid #dedee3;
    border-radius:22px;
    background:white;
    box-shadow:0 8px 30px rgba(0,0,0,.06);
}

.prompt-label {
    color:#999;
    font-size:13px;
    margin-bottom:8px;
}

/* Cards */
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

.feature {
    border:1px solid #e5e5e8;
    border-radius:18px;
    padding:18px;
    background:white;
    height:100%;
}

/* Hide Streamlit button chrome */
div.stButton > button {
    border-radius:12px;
    border:1px solid #ddd;
}

/* Chat */
.chat-box {
    max-width:780px;
    margin:30px auto;
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

/* Mobile */
@media (max-width: 700px) {
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

    .topbar {
        margin-bottom:20px;
    }
}
</style>
""", unsafe_allow_html=True)

if "started" not in st.session_state:
    st.session_state.started = False

if "messages" not in st.session_state:
    st.session_state.messages = []

# Header
st.markdown("""
<div class="topbar">
    <div class="brand">
        <div class="logo">✦</div>
        <div class="brand-name">Nova AI</div>
        <div class="badge">AI + Presentation</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Hero
if not st.session_state.started:
    st.markdown("""
    <div class="hero">
        <h1>What can I help you create?</h1>
        <p>Hỏi AI bất cứ điều gì — hoặc yêu cầu tạo bài trình bày khi bạn cần.</p>
    </div>
    """, unsafe_allow_html=True)

# Main input
st.markdown('<div class="prompt"><div class="prompt-label">Tin nhắn cho Nova AI</div>', unsafe_allow_html=True)

prompt = st.chat_input(
    "Hỏi một câu hỏi hoặc yêu cầu tạo bài trình bày..."
)

st.markdown("</div>", unsafe_allow_html=True)

if prompt:
    st.session_state.started = True
    st.session_state.messages.append(("user", prompt))
    st.rerun()

# Conversation preview
if st.session_state.messages:
    st.markdown('<div class="chat-box">', unsafe_allow_html=True)

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

else:
    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="feature">
            <div class="card-title">💬 Hỏi đáp</div>
            <div class="card-desc">
                Đặt câu hỏi và nhận câu trả lời từ AI.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="feature">
            <div class="card-title">📊 Tạo trình bày</div>
            <div class="card-desc">
                Chỉ tạo slide khi bạn thực sự yêu cầu.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="feature">
            <div class="card-title">✨ Một AI duy nhất</div>
            <div class="card-desc">
                Kết hợp hỏi đáp và khả năng tạo nội dung kiểu Gamma.
            </div>
        </div>
        """, unsafe_allow_html=True)

st.caption("Nova AI • Prototype interface")
