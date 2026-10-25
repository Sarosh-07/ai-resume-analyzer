# AI Resume Analyzer + Chatbot

A small Streamlit website that extracts text from PDF resumes, provides a resume checklist, and uses Google Gemini for AI resume feedback and chat.

## Run locally
1. Install Python and open a terminal in this folder.
2. Install dependencies:
   `python -m pip install -r requirements.txt`
3. Set your Gemini API key as an environment variable:
   - Windows PowerShell: `$env:GEMINI_API_KEY="YOUR_API_KEY"`
   - macOS/Linux: `export GEMINI_API_KEY="YOUR_API_KEY"`
4. Start the website:
   `python -m streamlit run app.py`

Get a Gemini API key from Google AI Studio. Do not commit the key to GitHub.

## Deploy to Streamlit Community Cloud
1. Create a GitHub repository and upload `app.py`, `requirements.txt`, and `README.md`.
2. In Streamlit Community Cloud, create an app from that repository and select `app.py`.
3. In the app's Settings / Secrets, add:
   `GEMINI_API_KEY = "your_actual_key"`
4. Save and wait for the app to restart.

The app can show a basic resume checklist without an API key, but full AI analysis and chatbot responses require a valid Gemini API key.
