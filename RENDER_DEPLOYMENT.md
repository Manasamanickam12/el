# 🚀 Deploying to Render.com: Full Step-by-Step Guide

Follow these exact steps to host your Election Chatbot on Render.

## Step 1: Push your Code to GitHub
Ensure all your files (including `render.yaml`, `requirements.txt`, and the `.streamlit/` folder) are pushed to a repository on GitHub.

## Step 2: Create a New Blueprint on Render
1.  Log in to [Render.com](https://dashboard.render.com).
2.  Click the **New +** button in the top right.
3.  Select **Blueprint** from the dropdown menu.
4.  Connect your GitHub account and select your **election_chatbot_streamlit_rag** repository.

## Step 3: Configure the Blueprint
1.  Render will read your `render.yaml` file automatically.
2.  Give your Blueprint a Group Name (e.g., `election-bot-group`).
3.  Click **Apply**.

## Step 4: Add your API Key (Crucial!)
1.  Once the Blueprint is created, Render will start building the "election-chatbot" service.
2.  While it's building, click on the **election-chatbot** service in your dashboard.
3.  Go to the **Environment** tab on the left sidebar.
4.  Click **Add Environment Variable**.
5.  Set the Key to `GEMINI_API_KEY`.
6.  Set the Value to your actual Google Gemini API Key.
7.  Click **Save Changes**.

## Step 5: Verify and Launch
1.  Go to the **Events** or **Logs** tab to watch the build process.
2.  Once the build says "Live", click the URL at the top (e.g., `https://election-chatbot-xxxx.onrender.com`).
3.  **Note**: The first load might take a minute as Render "wakes up" the server.

---

### 💡 Troubleshooting
- **Build Fails?**: Check the logs. It usually means a library in `requirements.txt` is missing or the Python version is incompatible.
- **API Error?**: Double-check that `GEMINI_API_KEY` is spelled exactly right in the Environment settings.
- **Audio not working?**: Remember that browsers require `https://` (which Render provides!) for the microphone to work.
