import streamlit as st
import requests
import time

# ---------------- CONFIG ----------------
API_URL = "http://localhost:8000/chat"

st.set_page_config(
    page_title="E-Commerce Support AI",
    page_icon="🛒",
    layout="centered"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>

body {
    background: radial-gradient(circle at top, #0f2027, #000000);
}

.main {
    background: transparent;
}

/* Glass container */
.chat-container {
    background: rgba(255, 255, 255, 0.06);
    border-radius: 22px;
    padding: 20px;
    box-shadow: 0 25px 60px rgba(0,0,0,0.6);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.08);
}

/* Header */
.chat-header {
    font-size: 26px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 10px;
    background: linear-gradient(90deg, #00dbde, #fc00ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Subtext */
.chat-sub {
    text-align: center;
    color: #aaa;
    margin-bottom: 15px;
}

/* Thinking animation */
.thinking {
    font-style: italic;
    color: #bbb;
    animation: blink 1.5s infinite;
}

@keyframes blink {
    0% { opacity: 0.3; }
    50% { opacity: 1; }
    100% { opacity: 0.3; }
}

/* Chat bubble shadow */
.stChatMessage {
    border-radius: 16px !important;
    padding: 12px !important;
    box-shadow: 0 8px 25px rgba(0,0,0,0.35) !important;
}

/* Input box */
textarea {
    border-radius: 14px !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
st.markdown("<div class='chat-header'>🛒 E-Commerce Support AI</div>", unsafe_allow_html=True)
st.markdown("<div class='chat-sub'>Ask about products, delivery, returns, payments & more</div>", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- DISPLAY CHAT ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- USER INPUT ----------------
user_input = st.chat_input("Type your message here...")

if user_input:

    # ---- USER MESSAGE ----
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # ---- THINKING ANIMATION ----
    with st.chat_message("assistant"):
        thinking_box = st.empty()
        thinking_box.markdown(
            "<span class='thinking'>🤖 Thinking...</span>",
            unsafe_allow_html=True
        )

    # ---- API CALL ----
    try:
        time.sleep(0.4)  # smooth UX
        res = requests.post(API_URL, json={"message": user_input}, timeout=60)
        data = res.json()
        bot_reply = data.get("reply", "No response from server.")
    except Exception as e:
        bot_reply = f"⚠️ Error connecting to server: {e}"

    # ---- SHOW FINAL RESPONSE ----
    thinking_box.markdown(bot_reply)

    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_reply
    })

st.markdown("</div>", unsafe_allow_html=True)
