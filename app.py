import os
import streamlit as st
from pypdf import PdfReader

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")

# Read API key from Streamlit Cloud secrets or local environment.
try:
    API_KEY = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    API_KEY = ""
API_KEY = API_KEY or os.getenv("GEMINI_API_KEY", "")

def ask_gemini(prompt, resume_text=""):
    if not API_KEY:
        return None, "Gemini API key is not configured."
    try:
        from google import genai
        client = genai.Client(api_key=API_KEY)
        response = client.models.generate_content(
            model="model=MODEL_NAME,",
            contents=prompt + (("\n\nRESUME TEXT:\n" + resume_text[:25000]) if resume_text else "")
        )
        return response.text, None
    except Exception as exc:
        return None, f"AI request failed: {exc}"

def simple_review(text):
    lower = text.lower()
    checks = {
        "Contact details": any(x in lower for x in ["@", "phone", "mobile"]),
        "Skills section": "skill" in lower or "technical" in lower,
        "Education section": any(x in lower for x in ["education", "degree", "university", "college"]),
        "Projects or experience": any(x in lower for x in ["project", "experience", "internship", "work history"]),
        "Achievements or measurable results": any(x in lower for x in ["%", "achieved", "improved", "increased", "reduced"]),
    }
    return checks

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("📄 AI Resume Analyzer")
st.caption("Upload your resume, receive practical feedback, and ask the resume assistant questions.")
st.info("Privacy tip: Upload only a resume you are comfortable processing. AI feedback can be imperfect; review suggestions before using them.")

with st.sidebar:
    st.header("About")
    st.write("This tool reviews resume content and gives suggestions to improve clarity, skills presentation, and impact.")
    st.write("**Features:** PDF upload • AI review • Resume chatbot")
    if API_KEY:
        st.success("Gemini API key detected")
    else:
        st.warning("Gemini API key not set. PDF reading and a basic checklist still work; AI answers require a key.")

tab_review, tab_chat = st.tabs(["🔍 Resume Analysis", "💬 AI Chatbot"])

with tab_review:
    uploaded = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
    if uploaded:
        try:
            reader = PdfReader(uploaded)
            extracted = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
            if not extracted:
                st.error("No selectable text found. This may be a scanned PDF. Try a text-based PDF.")
            else:
                st.session_state.resume_text = extracted
                st.success(f"Resume loaded successfully ({len(extracted.split())} words detected).")
        except Exception as exc:
            st.error(f"Could not read this PDF: {exc}")

    if st.session_state.resume_text:
        st.subheader("Resume text preview")
        with st.expander("Show extracted text"):
            st.text(st.session_state.resume_text[:6000])

        if st.button("Analyze My Resume", type="primary", use_container_width=True):
            with st.spinner("Reviewing your resume..."):
                prompt = """You are a careful resume reviewer. Analyze this resume in simple, constructive language.
Return these sections with clear headings:
1. Short Resume Summary
2. Strengths (3-5 bullet points)
3. Areas to Improve (3-5 specific bullet points)
4. Skills and Keywords Found
5. Missing or unclear information (do not assume facts)
6. Example improvements for up to 2 resume bullet points, without inventing achievements.
Do not claim an exact ATS score. Be respectful and concise."""
                answer, error = ask_gemini(prompt, st.session_state.resume_text)
            if answer:
                st.session_state.analysis = answer
            else:
                checks = simple_review(st.session_state.resume_text)
                st.session_state.analysis = None
                st.warning(error + " Showing a basic checklist instead.")
                st.write("### Basic Resume Checklist")
                for item, passed in checks.items():
                    st.write(("✅ " if passed else "⚠️ ") + item + (": detected" if passed else ": consider adding or checking"))
                st.write("Set GEMINI_API_KEY to enable the full AI review.")
        if st.session_state.get("analysis"):
            st.markdown(st.session_state.analysis)
    else:
        st.write("Upload a PDF to begin. Your resume text will appear here after extraction.")

with tab_chat:
    st.subheader("Ask questions about your resume")
    if not st.session_state.resume_text:
        st.caption("Upload a resume in the Resume Analysis tab first. You can also ask general resume questions.")
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("Example: How can I improve my project descriptions?")
    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                history = "\n".join(
                    f'{m["role"].upper()}: {m["content"]}'
                    for m in st.session_state.chat_history[-8:]
                )
                prompt = """You are a helpful resume assistant. Answer in clear, simple language.
Focus on resume writing, job applications, interview preparation, and explaining the uploaded resume.
Do not invent qualifications, work experience, or achievements. If the user asks about their resume,
base your response only on the supplied text. Keep the answer practical.

Recent chat:
""" + history
                answer, error = ask_gemini(prompt, st.session_state.resume_text)
                if not answer:
                    answer = ("I can't access the AI service right now. Please check that a valid "
                              "GEMINI_API_KEY is configured in Streamlit secrets. You can still use "
                              "the resume checklist. Error: " + str(error))
                st.markdown(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

st.divider()
st.caption("AI-generated feedback is a guide, not a hiring decision. Always verify all suggestions.")
