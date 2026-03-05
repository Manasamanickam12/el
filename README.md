# 🗳️ Election Information Chatbot

A premium, mobile-responsive Streamlit application that provides election-related information using RAG (Retrieval-Augmented Generation) and Google's Gemini Multimodal AI.

## 🚀 Features
- **Dual-Mode Input**: Supports both **Voice Recording** (browser-based) and **Text Chat**.
- **Gemini Multimodal**: Processes audio directly for high accuracy in Tamil and English.
- **RAG System**: Accurate factual answers based on local election knowledge data.
- **Mobile UI**: Premium dark-theme design optimized for mobile web views.
- **Multi-Cloud Ready**: Pre-configured for local, NIMBUS, and Render.com hosting.

---

## 🛠️ Local Setup & Execution

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Key**:
   Create a file at `.streamlit/secrets.toml`:
   ```toml
   GEMINI_API_KEY = "YOUR_API_KEY_HERE"
   ```

3. **Run the App**:
   ```bash
   streamlit run app.py
   ```

---

## ☁️ Deployment Guides

### 1. Render.com (Full Manual Setup)
If you don't want to use the Blueprint, you can create a **New Web Service**:

1.  **Connect GitHub**: In the Render Dashboard, click **New +** > **Web Service** and select your repository.
2.  **Environment**: Select **Python 3**.
3.  **Build Command**: 
    ```bash
    pip install -r requirements.txt
    ```
4.  **Start Command**: 
    ```bash
    streamlit run app.py --server.port $PORT --server.address 0.0.0.0
    ```
5.  **Environment Variables**:
    - Click **Advanced** > **Add Environment Variable**.
    - Key: `GEMINI_API_KEY`
    - Value: [Your Actual Google API Key]
6.  **Deploy**: Click **Create Web Service**.

### 2. NIMBUS BYTE XL
- **Steps**:
  1. Upload all project files.
  2. Open the terminal and run:
     ```bash
     pip install -r requirements.txt
     streamlit run app.py
     ```
- **Tip**: If the microphone doesn't work on `http`, enable the Chrome flag: `chrome://flags/#unsafely-treat-insecure-origin-as-secure` and add your ByteXL URL.

---

## 📂 Project Structure
- `app.py`: Main Streamlit application.
- `rag_utils.py`: Logic for document loading and vector search.
- `requirements.txt`: Python dependencies.
- `render.yaml`: Deployment blueprint for Render.com.
- `.streamlit/`:
  - `config.toml`: Server & theme settings.
  - `secrets.toml`: Local API key storage.
- `data/`: Knowledge base text files.
- `symbols/`: Images for political party symbols.
