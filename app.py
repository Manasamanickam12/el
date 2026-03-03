import streamlit as st
import google.generativeai as genai
from rag_utils import load_documents, create_faiss_index, search
from PIL import Image

# Fetch API Key from Streamlit Secrets or Environment Variables
API_KEY = st.secrets.get("GEMINI_API_KEY")

if not API_KEY:
    st.error("Missing GEMINI_API_KEY. Please add it to .streamlit/secrets.toml or Streamlit Cloud Secrets.")
    st.stop()
# Basic validation (length check)
if len(API_KEY) < 30:
    st.error("The API Key appears too short. Please double-check it in Google AI Studio.")
    st.stop()

genai.configure(api_key=API_KEY)

# Use Gemini 1.5 Flash
model = genai.GenerativeModel("gemini-1.5-flash")

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
        return f"Error generating response: {str(e)}"

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


