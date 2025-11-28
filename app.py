import os
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"
import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# ------------------------
# Page Configuration
# ------------------------
st.set_page_config(
    page_title="Qanoon Buddy – AI Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        color: white;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: white !important;
        color: #667eea !important;
    }
    div[data-testid="stExpander"] {
        background-color: white;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .case-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------
# Helper: Configure Gemini
# ------------------------
def get_gemini_model():
    api_key = os.getenv("GEMINI_API_KEY") or st.session_state.get("gemini_api_key")
    if not api_key:
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        return model
    except Exception as e:
        st.error(f"Error configuring Gemini: {e}")
        return None


def ask_gemini(prompt, system_prompt=""):
    model = get_gemini_model()
    if model is None:
        return None

    try:
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt
        
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        st.error(f"Error from Gemini API: {e}")
        return None


# ------------------------
# PDF Helper
# ------------------------
def extract_text_from_pdf(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Could not read PDF: {e}")
        return ""


# ------------------------
# Demo Case Law Database
# ------------------------
DEMO_CASES = [
    {
        "title": "Ali vs State – Cyber Harassment Case",
        "year": 2021,
        "citation": "2021 SCMR 123",
        "tags": ["cybercrime", "harassment", "PECA"],
        "summary": (
            "The case concerns online harassment under PECA. The court clarified how "
            "electronic communication and social media messages can fall under cyber harassment "
            "and emphasized the importance of digital evidence."
        ),
    },
    {
        "title": "Fatima vs Ahmed – Family Maintenance Dispute",
        "year": 2019,
        "citation": "PLD 2019 Karachi 456",
        "tags": ["family", "maintenance", "marriage"],
        "summary": (
            "A family law dispute regarding maintenance after separation. The court interpreted "
            "maintenance obligations, the standard of living, and the financial capacity of the husband."
        ),
    },
    {
        "title": "FBR vs XYZ Pvt Ltd – Tax Assessment",
        "year": 2022,
        "citation": "2022 PTD 789",
        "tags": ["tax", "income tax", "business"],
        "summary": (
            "The case deals with a dispute over income tax assessment for a private company. "
            "The court discussed documentation, burden of proof, and interpretation of tax provisions."
        ),
    },
    {
        "title": "Maryam vs Hassan – Khula Case",
        "year": 2020,
        "citation": "PLD 2020 Lahore 234",
        "tags": ["family", "khula", "divorce"],
        "summary": (
            "Landmark case on khula (wife-initiated divorce) rights in Pakistan. The court ruled on "
            "the circumstances under which a woman can obtain khula and return of haq mehr."
        ),
    },
]


def search_cases(keyword: str):
    keyword = keyword.lower()
    results = []
    for case in DEMO_CASES:
        haystack = " ".join([
            case["title"],
            case["citation"],
            " ".join(case["tags"]),
            case["summary"],
        ]).lower()
        if keyword in haystack:
            results.append(case)
    return results


# ------------------------
# Header
# ------------------------
st.markdown("""
    <div style='text-align: center; padding: 2rem 0; color: white;'>
        <h1>⚖️ Qanoon Buddy</h1>
        <p style='font-size: 1.2rem;'>AI-Powered Legal Assistant for Pakistan</p>
        <p style='font-size: 0.9rem; opacity: 0.9;'>FYP Demo | Group 024 | SSUET 2022F-CS</p>
    </div>
""", unsafe_allow_html=True)

# ------------------------
# Sidebar: API Key + Info
# ------------------------
with st.sidebar:
    st.header("🔑 Configuration")
    
    api_input = st.text_input("Gemini API Key", type="password", 
                               help="Get from https://aistudio.google.com/app/apikey")
    if api_input:
        st.session_state["gemini_api_key"] = api_input
        st.success("✅ API key saved!")
    
    if not get_gemini_model():
        st.warning("⚠️ Please enter your API key to use all features")
    
    st.divider()
    
    st.header("👥 Team Members")
    st.markdown("""
    - **Reyan Umar Khan Lodhi** (2022F-CS-314)
    - **Umer Ali Khan Lodhi** (2022F-CS-080)
    - **Rao Muhammad Mairaj** (2022F-CS-082)
    - **Abubakar Siddiq** (2022F-CS-086)
    """)
    
    st.divider()
    
    st.header("📚 Scope of Work")
    st.markdown("""
    - Family Law
    - Tax Law
    - Cyber Crime Law (PECA)
    """)
    
    st.divider()
    
    st.header("⚠️ Disclaimer")
    st.warning(
        "This is a **demo academic project** for FYP. "
        "It does **not** provide official legal advice. "
        "Always consult a qualified lawyer for real cases."
    )
    
    st.divider()
    st.caption("Supervised by: Ms. Razia Nisar Noorani")

# ------------------------
# Main Tabs
# ------------------------
tab_chat, tab_pdf, tab_translate, tab_cases = st.tabs(
    ["💬 Legal Chatbot", "📄 PDF Summarizer", "🌐 Translation", "📚 Case Law Search"]
)

# ------------------------
# TAB 1: Chatbot
# ------------------------
with tab_chat:
    st.markdown("### 💬 Ask Your Legal Questions")
    st.caption("Get instant answers about Pakistani Family Law, Tax Law, and Cyber Crime Law")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = [
            {
                "role": "assistant",
                "content": "السلام علیکم! I'm Qanoon Buddy, your AI legal assistant. Ask me anything about Family Law, Tax Law, or Cyber Crime Law in Pakistan. How can I help you today?"
            }
        ]

    system_prompt = (
        "You are Qanoon Buddy, an AI legal assistant for Pakistani users specializing in "
        "Family Law, Tax Law, and Cyber Crime (PECA Act). Provide clear, simple explanations "
        "in a friendly tone. Use both English and Urdu phrases where appropriate. "
        "ALWAYS include a disclaimer that you are not a lawyer and users should consult "
        "qualified legal professionals for specific advice. Keep responses concise (3-5 paragraphs)."
    )

    # Display chat history
    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("Type your legal question here...")
    if user_input:
        # Add user message
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Researching..."):
                resp = ask_gemini(prompt=user_input, system_prompt=system_prompt)
                if resp is None:
                    resp = "⚠️ Sorry, I couldn't generate a response. Please check your API key."
                st.markdown(resp)
        
        st.session_state["chat_history"].append({"role": "assistant", "content": resp})
        st.rerun()

    # Example questions
    st.divider()
    st.markdown("#### 💡 Example Questions:")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("What is khula?"):
            st.session_state["chat_history"].append({"role": "user", "content": "What is khula in Pakistani law?"})
            st.rerun()
    
    with col2:
        if st.button("Tax on salary?"):
            st.session_state["chat_history"].append({"role": "user", "content": "What is the tax on salary in Pakistan?"})
            st.rerun()
    
    with col3:
        if st.button("Cyber harassment?"):
            st.session_state["chat_history"].append({"role": "user", "content": "What is cyber harassment under PECA?"})
            st.rerun()

# ------------------------
# TAB 2: PDF Summarizer
# ------------------------
with tab_pdf:
    st.markdown("### 📄 Legal Document Summarizer")
    st.caption("Upload a PDF document (judgment, legal notice, etc.) for AI-powered summary")

    uploaded_pdf = st.file_uploader("Choose a PDF file", type=["pdf"], key="pdf_uploader")

    if uploaded_pdf is not None:
        with st.spinner("📖 Extracting text from PDF..."):
            text = extract_text_from_pdf(uploaded_pdf)
        
        if text:
            st.success(f"✅ Extracted {len(text)} characters from PDF")
            
            with st.expander("📝 View Extracted Text (Preview)"):
                st.text_area("", text[:2000] + "..." if len(text) > 2000 else text, height=200)

            st.divider()
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📋 Summarize in English", use_container_width=True):
                    with st.spinner("✨ Generating summary..."):
                        prompt = (
                            "Summarize the following Pakistani legal document in clear, simple English. "
                            "Include: main parties, key issues, legal provisions cited, and outcome/decision:\n\n" 
                            + text[:4000]  # Limit to avoid token limits
                        )
                        summary = ask_gemini(prompt)
                        if summary:
                            st.markdown("#### 📄 Summary (English)")
                            st.info(summary)

            with col2:
                if st.button("📋 خلاصہ اردو میں", use_container_width=True):
                    with st.spinner("✨ خلاصہ تیار ہو رہا ہے..."):
                        prompt = (
                            "Summarize the following Pakistani legal document in simple Urdu "
                            "that a common person can understand:\n\n" + text[:4000]
                        )
                        summary_ur = ask_gemini(prompt)
                        if summary_ur:
                            st.markdown("#### 📄 خلاصہ (اردو)")
                            st.info(summary_ur)

# ------------------------
# TAB 3: Translation
# ------------------------
with tab_translate:
    st.markdown("### 🌐 Legal Text Translation")
    st.caption("Translate legal documents between Urdu and English")

    direction = st.radio(
        "Translation Direction:",
        ["English → Urdu", "Urdu → English"],
        horizontal=True,
    )

    src_text = st.text_area(
        "Enter text to translate:",
        height=200,
        placeholder="Paste your legal text here..."
    )

    if st.button("🔄 Translate", type="primary", use_container_width=True):
        if not src_text.strip():
            st.warning("⚠️ Please enter some text first.")
        else:
            with st.spinner("🔄 Translating..."):
                if direction == "English → Urdu":
                    prompt = (
                        "Translate the following legal or formal English text into clear, natural Urdu "
                        "that maintains legal accuracy:\n\n" + src_text
                    )
                else:
                    prompt = (
                        "Translate the following Urdu legal text into formal, accurate English "
                        "while preserving legal terminology:\n\n" + src_text
                    )

                translated = ask_gemini(prompt)
                if translated:
                    st.success("✅ Translation complete!")
                    st.markdown("#### Translated Text:")
                    st.info(translated)

# ------------------------
# TAB 4: Case Law Search
# ------------------------
with tab_cases:
    st.markdown("### 📚 Case Law Database (Demo)")
    st.caption("Search through sample Pakistani case laws")

    st.info("💡 This is a demo with sample cases. In the final FYP, this will connect to a real legal database with vector search (FAISS).")

    keyword = st.text_input(
        "🔍 Search by keyword:",
        placeholder="e.g., maintenance, tax, harassment, khula, PECA"
    )

    if st.button("🔍 Search Cases", type="primary", use_container_width=True):
        if not keyword.strip():
            st.warning("⚠️ Please enter a keyword.")
        else:
            results = search_cases(keyword)
            
            if not results:
                st.info("No matching cases found. Try another keyword like 'family', 'tax', or 'cyber'.")
            else:
                st.success(f"✅ Found {len(results)} matching case(s)")
                
                for i, case in enumerate(results, start=1):
                    with st.expander(f"📁 {case['title']} ({case['year']})"):
                        st.markdown(f"**Citation:** {case['citation']}")
                        st.markdown(f"**Tags:** {', '.join(['`' + tag + '`' for tag in case['tags']])}")
                        st.markdown(f"**Summary:**\n{case['summary']}")
                        
                        if st.button(f"🤖 Explain in Simple Terms", key=f"explain_{i}"):
                            with st.spinner("🤔 Generating explanation..."):
                                prompt = (
                                    "Explain the following Pakistani case in simple language for a non-lawyer. "
                                    "Also explain why this case is important:\n\n"
                                    f"Case: {case['title']}\n"
                                    f"Year: {case['year']}\n"
                                    f"Summary: {case['summary']}"
                                )
                                explanation = ask_gemini(prompt)
                                if explanation:
                                    st.markdown("**🎓 Simple Explanation:**")