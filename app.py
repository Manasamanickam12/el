import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
import os
import base64
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
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 50px;
        font-weight: 600;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
    }
    
    .status-box {
        padding: 10px;
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🗳️ Election Assistant")

# UI Placeholders
response_placeholder = st.empty()
symbol_placeholder = st.empty()
audio_placeholder = st.empty()

def recognize_speech():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.toast("🎙️ Listening...")
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            return text
    except Exception as e:
        st.error("Microphone failed or not detected. Please type your question.")
        return None

def speak_text(text):
    filename = "response.mp3"
    try:
        tts = gTTS(text=text, lang='en')
        tts.save(filename)
        
        with open(filename, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            
            # Autoplay HTML + Visible Player
            audio_html = f"""
                <div style="margin-top: 20px; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px;">
                    <p style="margin-bottom: 5px;">🔊 Click play if it doesn't start automatically:</p>
                    <audio autoplay="true" controls style="width: 100%;">
                        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                    </audio>
                </div>
            """
            audio_placeholder.markdown(audio_html, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Voice error: {e}")

def generate_ai_response(user_query):
    system_prompt = "You are an Election Information Assistant. Answer ONLY election related topics factualy. If not related, say: I answer only election related questions."
    context = search(user_query, docs, index)
    final_prompt = f"{system_prompt}\n\nContext: {context}\n\nUser Question: {user_query}"
    response = model.generate_content(final_prompt)
    return response.text

def show_party_symbol(text):
    party_map = {
        "BJP": "bjp.png", "Congress": "congress.png","ADMK": "admk.png", "DMK": "dmk.png" , "TVK": "tvk.png", "NTK": "ntk.png"
    }
    for party, img_file in party_map.items():
        if party in text:
            try:
                img = Image.open(f"symbols/{img_file}")
                symbol_placeholder.image(img, width=100)
                break
            except: continue

# --- MAIN APP LOGIC ---

# 1. Text Input (Reliable for Web)
user_query = st.chat_input("Type your question here...")

# 2. Voice Button
if st.button("🎤 Tap to Speak"):
    voice_input = recognize_speech()
    if voice_input:
        user_query = voice_input

# 3. Process Input
if user_query:
    with st.spinner("AI is thinking..."):
        ans = generate_ai_response(user_query)
        response_placeholder.markdown(f"### 🤖 AI Response:\n{ans}")
        speak_text(ans)
        show_party_symbol(ans)
