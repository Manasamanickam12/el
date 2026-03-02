import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
from rag_utils import load_documents, create_faiss_index, search
from PIL import Image

API_KEY = "AIzaSyAzGYdqYrl7TQbsrEjiMilyafG-ETnlxyk"
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-flash-latest")

docs = load_documents("data/election_knowledge.txt")
index, embeddings = create_faiss_index(docs)

st.set_page_config(page_title="Election Voice Chatbot", layout="centered")

# Custom CSS for Premium Mobile Look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #0f172a; /* Sleek dark blue background */
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
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.4);
    }
    
    /* Center text and symbols */
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
        margin-bottom: 30px;
    }
    
    .status-box {
        padding: 15px;
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🗳️ Election Assistant")

# UI Areas with grouping for mobile
main_container = st.container()
with main_container:
    response_area = st.empty()
    symbol_area = st.empty()
    info_area = st.empty()

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        info_area.markdown('<div class="status-box">🎙️ Listening... Speak now</div>', unsafe_allow_html=True)
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        info_area.empty()
        return text
    except:
        info_area.markdown('<div class="status-box">❌ Could not hear anything.</div>', unsafe_allow_html=True)
        return None

def speak_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def generate_response(user_query):

    system_prompt = """
You are an Election Information Assistant.

STRICT RULES:
- Answer ONLY election related topics.
- Allowed topics:
  political parties, leaders, symbols, voting process,
  election dates, candidates, constituencies, election results (factual only).
- No opinions.
- No comparisons.
- No political bias.
- If the question is NOT election-related,
  reply exactly: I answer only election related questions.
"""

    context = search(user_query, docs, index)

    final_prompt = f"""
{system_prompt}

Context:
{context}

User Question:
{user_query}
"""

    response = model.generate_content(final_prompt)
    return response.text

def show_party_symbol(text):
    # Mapping party names/keywords to their symbol image and caption
    party_map = {
        "Bharatiya Janata Party": ("bjp.png", "BJP Symbol - Lotus"),
        "BJP": ("bjp.png", "BJP Symbol - Lotus"),
        "Indian National Congress": ("congress.png", "Congress Symbol - Hand"),
        "Congress": ("congress.png", "Congress Symbol - Hand"),
        "DMK": ("dmk.png", "DMK Symbol - Rising Sun"),
        "Dravida Munnetra Kazhagam": ("dmk.png", "DMK Symbol - Rising Sun"),
        "ADMK": ("admk.png", "ADMK Symbol - Two Leaves"),
        "AIADMK": ("admk.png", "ADMK Symbol - Two Leaves"),
        "TVK": ("tvk.png", "TVK Symbol - Two Elephants & Vaagai Flower"),
        "Tamilaga Vettri Kazhagam": ("tvk.png", "TVK Symbol - Two Elephants & Vaagai Flower"),
        "NTK": ("ntk.png", "NTK Symbol - Microphone"),
        "Naam Tamilar Katchi": ("ntk.png", "NTK Symbol - Microphone")
    }

    found = False
    for keyword, (img_file, caption) in party_map.items():
        if keyword in text:
            try:
                img = Image.open(f"symbols/{img_file}")
                symbol_area.image(img, caption=caption, width=150)
                found = True
                break
            except Exception:
                # If image is missing, we just skip it or show a placeholder
                continue
    
    if not found:
        symbol_area.empty()

if st.button("🎤 Tap to Speak"):

    user_text = recognize_speech()

    if user_text:
        st.write("**You said:**", user_text)
        ai_response = generate_response(user_text)
        response_area.markdown(f"### 🤖 AI Response:\n{ai_response}")
        speak_text(ai_response)
        show_party_symbol(ai_response)
    else:
        st.error("Could not recognize speech. Try again.")
