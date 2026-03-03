import streamlit as st
import google.generativeai as genai
from rag_utils import load_documents, create_faiss_index, search
from PIL import Image
import os

# 1. PAGE CONFIG (MUST BE FIRST)
st.set_page_config(page_title="Election Voice Chatbot", layout="centered", page_icon="🗳️")

# 2. CUSTOM CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #0f172a;
        color: #f8fafc;
    }
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 60px;
        font-size: 1.2rem;
        font-weight: 600;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        transition: all 0.3s ease;
    }
    h1 {
        text-align: center;
        font-weight: 700;
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# 3. SIDEBAR CONFIGURATION
with st.sidebar:
    st.header("⚙️ Configuration")
    user_api_key = st.text_input("Enter Gemini API Key", type="password")
    
    API_KEY = user_api_key if user_api_key else st.secrets.get("GEMINI_API_KEY")
    
    if not API_KEY:
        st.warning("⚠️ Please enter your Gemini API Key to start.")
        st.stop()
    
    genai.configure(api_key=API_KEY)

    # Model Discovery
    @st.cache_data(show_spinner=False)
    def get_available_models():
        try:
            return [m.name.replace("models/", "") for m in genai.list_models() 
                    if "generateContent" in m.supported_generation_methods]
        except:
            return ["gemini-1.5-flash", "gemini-1.5-pro"]

    available_models = get_available_models()
    selected_model_name = st.selectbox("Select Model", available_models, index=0)
    model = genai.GenerativeModel(selected_model_name)

# 4. RAG INITIALIZATION (CACHED)
@st.cache_resource
def init_rag():
    try:
        docs = load_documents("data/election_knowledge.txt")
        index, _ = create_faiss_index(docs)
        return docs, index
    except Exception as e:
        st.error(f"Error loading RAG data: {e}")
        return [], None

docs, index = init_rag()

# 5. CORE FUNCTIONS
def show_party_symbol(text, container):
    party_map = {
        "BJP": ("bjp.png", "BJP Symbol - Lotus"),
        "Congress": ("congress.png", "Congress Symbol - Hand"),
        "DMK": ("dmk.png", "DMK Symbol - Rising Sun"),
        "ADMK": ("admk.png", "ADMK Symbol - Two Leaves"),
        "TVK": ("tvk.png", "TVK Symbol - Two Elephants"),
        "NTK": ("ntk.png", "NTK Symbol - Microphone")
    }
    
    for keyword, (img_file, caption) in party_map.items():
        if keyword.lower() in text.lower():
            path = f"symbols/{img_file}"
            if os.path.exists(path):
                img = Image.open(path)
                container.image(img, caption=caption, width=150)
                return
    container.empty()

def generate_response(user_input):
    system_prompt = """You are an Election Information Assistant. 
STRICT RULES:
- Answer ONLY election related topics (parties, leaders, symbols, process, dates).
- No opinions, comparisons, or bias.
- If the question is NOT election-related, reply exactly: "I answer only election related questions." """
    
    # Handle Audio transcription for better RAG context
    search_query = ""
    if isinstance(user_input, str):
        search_query = user_input
    else:
        # Quick transcription using Gemini to get search terms
        try:
            trans_resp = model.generate_content([
                "Extract the core election-related search query from this audio briefly:",
                {"mime_type": "audio/wav", "data": user_input.getvalue()}
            ])
            search_query = trans_resp.text
        except:
            search_query = "election"

    # Search RAG
    context = ""
    if index:
        # Show what we're searching for in the status
        st.write(f"🔍 Searching context for: `{search_query}`")
        context = search(search_query, docs, index)

    prompt_parts = [
        system_prompt,
        f"Context:\n{context}",
        "User Question:"
    ]

    if isinstance(user_input, str):
        prompt_parts.append(user_input)
    else:
        prompt_parts.append({
            "mime_type": "audio/wav",
            "data": user_input.getvalue()
        })

    try:
        response = model.generate_content(prompt_parts)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# 6. UI LAYOUT
st.title("🗳️ Election Assistant")

# Use columns or containers for better response positioning
response_container = st.container()
symbol_container = st.container()

# 7. INPUT HANDLING
audio_value = st.audio_input("🎤 Record your question")
text_value = st.chat_input("⌨️ Or type your question here...")

user_input = audio_value or text_value

if user_input:
    with st.status("🧠 Processing...", expanded=False) as status:
        ai_response = generate_response(user_input)
        status.update(label="✅ Ready!", state="complete", expanded=False)
    
    with response_container:
        st.chat_message("assistant").markdown(ai_response)
    
    with symbol_container:
        show_party_symbol(ai_response, st)