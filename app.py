import os
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"
import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Qanoon Buddy – AI Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# CHATGPT UI + DARK MODE CSS
# ---------------------------------------------------------
st.markdown("""
<style>

body {
    background-color: #f8f9fa;
}

/* CHAT AREA */
.chat-container {
    max-width: 780px;
    margin: auto;
    padding-bottom: 130px;
}

/* CHAT BUBBLES */
.user-msg, .bot-msg {
    border-radius: 12px;
    padding: 14px 18px;
    margin: 10px 0;
    font-size: 15.5px;
    line-height: 1.6;
    width: fit-content;
    max-width: 92%;
}

.user-msg {
    background-color: #d6ebff;
    border: 1px solid #b1d7ff;
    margin-left: auto;
}

.bot-msg {
    background: white;
    border: 1px solid #e6e6e6;
    margin-right: auto;
}

/* DARK MODE CHAT */
[data-theme="dark"] .user-msg {
    background-color: #005f73 !important;
    border-color: #0a9396 !important;
    color: white !important;
}
[data-theme="dark"] .bot-msg {
    background-color: #1b1b1d !important;
    border-color: #333 !important;
    color: white !important;
}

/* INPUT BAR */
.chat-input-box {
    position: fixed;
    bottom: 0; left: 0; right: 0;
    padding: 14px 20px;
    background: white;
    border-top: 1px solid #e5e7eb;
}
[data-theme="dark"] .chat-input-box {
    background: #0f0f0f !important;
    border-color: #333 !important;
}

/* TYPING ANIMATION */
.typing-dot {
    height: 10px;
    width: 10px;
    margin: 0 3px;
    background-color: #bbb;
    border-radius: 50%;
    display: inline-block;
    animation: blink 1.4s infinite both;
}
@keyframes blink {
    0% { opacity: .2; }
    20% { opacity: 1; }
    100% { opacity: .2; }
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# VOICE INPUT JAVASCRIPT
# ---------------------------------------------------------
st.markdown("""
<script>
function recordVoice() {
  const recognition = new(window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = "en-US";
  recognition.start();
  recognition.onresult = function(event) {
      const text = event.results[0][0].transcript;
      window.parent.postMessage({type:"voice_input", text:text}, "*");
  };
}
</script>
""", unsafe_allow_html=True)

voice_text = st.experimental_get_query_params().get("voice_input", [""])[0]

# ---------------------------------------------------------
# GEMINI CONFIG
# ---------------------------------------------------------
def get_gemini_model():
    api_key = os.getenv("GEMINI_API_KEY") or st.session_state.get("gemini_api_key")
    if not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel("gemini-1.5-flash")
    except:
        return None

def ask_gemini(prompt, system_prompt=""):
    model = get_gemini_model()
    if not model:
        return None
    try:
        combined = system_prompt + "\n\n" + prompt
        resp = model.generate_content(combined)
        return resp.text
    except:
        return None

# ---------------------------------------------------------
# PDF HELPER
# ---------------------------------------------------------
def extract_text_from_pdf(uploaded):
    try:
        reader = PdfReader(uploaded)
        text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
        return text.strip()
    except:
        return ""

# ---------------------------------------------------------
# DEMO CASES
# ---------------------------------------------------------
DEMO_CASES = [
    {
        "title": "Ali vs State – Cyber Harassment Case",
        "year": 2021,
        "citation": "2021 SCMR 123",
        "tags": ["cybercrime", "harassment", "PECA"],
        "summary": "Case involves cyber harassment under PECA and digital evidence rules."
    },
    {
        "title": "Fatima vs Ahmed – Family Maintenance Dispute",
        "year": 2019,
        "citation": "PLD 2019 Karachi 456",
        "tags": ["family", "maintenance"],
        "summary": "Court reviewed maintenance rights and financial responsibility."
    }
]

def search_cases(keyword):
    keyword = keyword.lower()
    results = []
    for c in DEMO_CASES:
        if keyword in c["title"].lower() or keyword in c["summary"].lower():
            results.append(c)
    return results

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown("""
    <div style='text-align: center; padding: 1.5rem 0;'>
        <h1>⚖️ Qanoon Buddy</h1>
        <p>AI-Powered Legal Assistant for Pakistan</p>
        <p style='font-size: 0.85rem;'>FYP Demo | SSUET</p>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.header("🔑 API Configuration")
    key = st.text_input("Gemini API Key", type="password")
    if key:
        st.session_state["gemini_api_key"] = key

    st.divider()
    st.header("Team Members")
    st.markdown("""
    - Reyan Umar Khan Lodhi  
    - Umer Ali Khan Lodhi  
    - Rao Muhammad Mairaj  
    - Abubakar Siddiq  
    """)

    st.divider()
    st.header("Disclaimer")
    st.warning("This is a demo FYP project. Not official legal advice.")

# ---------------------------------------------------------
# TABS
# ---------------------------------------------------------
tab_chat, tab_pdf, tab_translate, tab_cases = st.tabs(
    ["💬 Legal Chatbot", "📄 PDF Summarizer", "🌐 Translation", "📚 Case Law Search"]
)

# =========================================================
# TAB 1 — CHATGPT STYLE CHATBOT
# =========================================================
with tab_chat:
    st.markdown("<h3 style='text-align:center;'>💬 Ask Any Legal Question</h3>", unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "👋 Assalam-o-Alaikum! I'm Qanoon Buddy — your Pakistani legal assistant. How can I help you today?"}
        ]

    # SHOW CHAT BUBBLES
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        bubble = "user-msg" if msg["role"] == "user" else "bot-msg"
        st.markdown(f"<div class='{bubble}'>{msg['content']}</div>", unsafe_allow_html=True)

    # Typing animation
    if st.session_state.get("typing", False):
        st.markdown("""
            <div class='bot-msg'>
                <span class='typing-dot'></span>
                <span class='typing-dot'></span>
                <span class='typing-dot'></span>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # INPUT BAR
    st.markdown("<div class='chat-input-box'>", unsafe_allow_html=True)
    colA, colB, colC = st.columns([8,1,1])

    with colA:
        user_text = st.text_input("Ask", placeholder="Ask any Pakistani legal question...", label_visibility="collapsed")

    with colB:
        send = st.button("Send")

    with colC:
        if st.button("🎤"):
            st.markdown("<script>recordVoice()</script>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # PROCESS SEND
    if send and user_text.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_text})
        st.session_state["typing"] = True
        st.rerun()

    if voice_text:
        st.session_state.chat_history.append({"role": "user", "content": voice_text})
        st.session_state["typing"] = True
        st.rerun()

    if st.session_state.get("typing", False):
        with st.spinner("Thinking..."):
            reply = ask_gemini(
                prompt=st.session_state.chat_history[-1]["content"],
                system_prompt="You are Qanoon Buddy, Pakistani legal AI assistant."
            )
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.session_state["typing"] = False
        st.rerun()

# =========================================================
# TAB 2 — PDF SUMMARIZER
# (UNCHANGED)
# =========================================================
with tab_pdf:
    st.markdown("### 📄 Legal Document Summarizer")
    uploaded = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded:
        text = extract_text_from_pdf(uploaded)
        if text:
            st.success("PDF extracted!")
            if st.button("Summarize"):
                summary = ask_gemini("Summarize:\n\n" + text[:3500])
                st.info(summary)

# =========================================================
# TAB 3 — TRANSLATION
# (UNCHANGED)
# =========================================================
with tab_translate:
    st.markdown("### 🌐 Legal Text Translation")
    direction = st.radio("Translate:", ["English → Urdu", "Urdu → English"])
    data = st.text_area("Enter text:")
    if st.button("Translate Now"):
        if direction == "English → Urdu":
            msg = ask_gemini("Translate to Urdu:\n" + data)
        else:
            msg = ask_gemini("Translate to English:\n" + data)
        st.success(msg)

# =========================================================
# TAB 4 — CASE LAW SEARCH
# (UNCHANGED)
# =========================================================
with tab_cases:
    st.markdown("### 📚 Case Law Search (Demo)")
    q = st.text_input("Search case:")
    if st.button("Search"):
        res = search_cases(q)
        for c in res:
            with st.expander(c["title"]):
                st.write(c["summary"])
