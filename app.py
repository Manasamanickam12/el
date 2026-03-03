import streamlit as st
import google.generativeai as genai
from rag_utils import load_documents, create_faiss_index, search
from PIL import Image

# Sidebar for Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    user_api_key = st.text_input("Enter Gemini API Key", type="password", help="Get your key from https://aistudio.google.com/")
    st.info("💡 If you are on Streamlit Cloud, you can also set this in the 'Secrets' dashboard to save it permanently.")

# Determine which API key to use
API_KEY = user_api_key if user_api_key else st.secrets.get("GEMINI_API_KEY")

if not API_KEY:
    st.warning("⚠️ Please enter your Gemini API Key in the sidebar to start.")
    st.stop()

# Basic validation (length check)
if len(API_KEY) < 30:
    st.error("❌ The API Key appears too short. Please double-check it.")
    st.stop()

genai.configure(api_key=API_KEY)

# Use Gemini Pro (Better compatibility for older library versions)
try:
    model = genai.GenerativeModel("gemini-pro")
except Exception as e:
    st.error(f"Failed to initialize gemini-pro: {e}")
    st.stop()

# Helper to debug model names if needed
if "DEBUG_MODELS" in st.query_params:
    try:
        available_models = [m.name for m in genai.list_models()]
        st.info(f"Available models: {available_models}")
    except Exception as e:
        st.error(f"Could not list models: {e}")

docs = load_documents("data/election_knowledge.txt")
index, embeddings = create_faiss_index(docs)

st.set_page_config(page_title="Election Voice Chatbot", layout="centered")

# Custom CSS for Premium Mobile Look
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
    
    .stMarkdown, .stImage {
        display: flex;
        justify-content: center;
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

st.title("🗳️ Election Assistant")

main_container = st.container()
with main_container:
    response_area = st.empty()
    symbol_area = st.empty()

def generate_response(user_input):
    """Handles both text and audio input."""
    system_prompt = """
You are an Election Information Assistant.
STRICT RULES:
- Answer ONLY election related topics (parties, leaders, symbols, process, dates).
- No opinions, comparisons, or bias.
- If the question is NOT election-related, reply exactly: I answer only election related questions.
"""
    
    # RAG Context (using a placeholder string for search query if audio is used)
    # Note: For pure audio, we can optionally transcribe or just use general context
    search_query = user_input if isinstance(user_input, str) else "election information"
    context = search(search_query, docs, index)

    prompt_parts = [
        system_prompt,
        f"Context:\n{context}",
        "User Question:"
    ]
    
    if isinstance(user_input, str):
        prompt_parts.append(user_input)
    else:
        # User input is audio bytes/file
        prompt_parts.append({
            "mime_type": "audio/wav",
            "data": user_input.getvalue()
        })

    try:
        response = model.generate_content(prompt_parts)
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg:
            return """
**❌ API Key Invalid**
The API key being used is not recognized by Google. 

**If you are on Streamlit Cloud:**
1. Go to your **Streamlit Dashboard**.
2. Click on **Manage App** (bottom right).
3. Go to **Settings > Secrets**.
4. Ensure `GEMINI_API_KEY` is set correctly there.
5. Save and reboot the app.

**If you are local:**
Check your `.streamlit/secrets.toml` file for typos.
"""
        return f"Error generating response: {error_msg}"

def show_party_symbol(text):
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
            try:
                img = Image.open(f"symbols/{img_file}")
                symbol_area.image(img, caption=caption, width=150)
                return
            except:
                continue
    symbol_area.empty()

# Multi-Mode Input: Audio and Text Chat
audio_value = st.audio_input("🎤 Record your question")
text_value = st.chat_input("⌨️ Or type your question here...")

# Process either input
user_input = audio_value or text_value

if user_input:
    # Use a status message while thinking
    with st.status("🧠 Thinking...", expanded=False):
        ai_response = generate_response(user_input)
    
    response_area.markdown(f"### 🤖 AI Response:\n{ai_response}")
    show_party_symbol(ai_response)


