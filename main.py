import streamlit as st
from pdfminer.high_level import extract_text as pdf_extract
from docx import Document
import spacy

# Load spaCy model once and cache it for performance
@st.cache_resource
def load_nlp():
    return spacy.load('en_core_web_sm')
nlp = load_nlp()

# Sample skill list - extend as needed
SKILLS = [
    'python', 'java', 'c++', 'data analysis', 'machine learning', 'deep learning', 'nlp', 'sql',
    'aws', 'azure', 'docker', 'flask', 'django', 'linux', 'git', 'tensorflow', 'keras'
]

def extract_text_from_pdf(file):
    return pdf_extract(file)

def extract_text_from_docx(file):
    doc = Document(file)
    return '\n'.join([para.text for para in doc.paragraphs])

def extract_skills(text, skills_list):
    doc = nlp(text.lower())
    found = set()
    for token in doc:
        for skill in skills_list:
            if skill in token.text:
                found.add(skill)
    return list(found)

def check_sections(text):
    # Checking for presence of essential sections in a resume
    sections = ["experience", "education", "skills"]
    return [section.capitalize() for section in sections if section not in text.lower()]

# Streamlit page config
st.set_page_config(page_title="Resume Analyzer", page_icon=":memo:", layout="wide")

# Page header with custom style
st.markdown("<h1 style='color: #02457A;'>Resume Analyzer & Optimizer</h1>", unsafe_allow_html=True)

# Sidebar with logo and instructions
with st.sidebar:
    st.image("https://static.streamlit.io/examples/dice.jpg", width=100)  # You can replace with your logo
    st.write("Upload your resume below.\n\nSupports PDF and DOCX formats.")

# File uploader widget
uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX):", type=["pdf", "docx"])

if uploaded_file:
    # Extract text based on file extension
    if uploaded_file.name.endswith('.pdf'):
        resume_text = extract_text_from_pdf(uploaded_file)
    else:
        resume_text = extract_text_from_docx(uploaded_file)

    # Display extracted text with a proper label
    st.subheader("Extracted Resume Text")
    st.text_area("Extracted Resume Text", resume_text, height=250, label_visibility="visible")

    st.markdown("---")

    # Optional: job description input
    st.subheader("Check against a Job Description (Optional)")
    job_desc = st.text_area("Paste Target Job Description:")

    # Extract skills from resume text
    resume_skills = extract_skills(resume_text, SKILLS)

    if job_desc and job_desc.strip():
        # Extract skills from job description
        job_skills = extract_skills(job_desc, SKILLS)
        match = set(resume_skills) & set(job_skills)
        missing = set(job_skills) - set(resume_skills)
        match_pct = len(match) / len(job_skills) * 100 if job_skills else 0

        # Skill match info and progress bar
        st.info(f"**Skill Match:** {match_pct:.2f}%")
        st.write("✅ **Matched Skills:**", ', '.join(match) if match else "None found")
        st.write("🔍 **Missing Skills:**", ', '.join(missing) if missing else "None missing")
        st.progress(match_pct / 100 if job_skills else 0)

        # ATS section check
        st.markdown("---")
        st.subheader("ATS Section Check")
        missing_sections = check_sections(resume_text)
        if missing_sections:
            for section in missing_sections:
                st.warning(f"⚠️ {section} section missing!")
        else:
            st.success("✅ All key sections (Experience, Education, Skills) found.")

        st.markdown("---")

        # Feedback & suggestions for missing skills
        st.markdown("**Feedback & Suggestions:**")
        if missing:
            for skill in missing:
                st.write(f"• Suggest adding evidence of **{skill}** experience.")
        else:
            st.write("Great! Your resume matches the job requirements well.")

        # Prepare feedback text for download
        feedback_txt = (
            f"Skill Match: {match_pct:.2f}%\n"
            f"Matched Skills: {', '.join(match)}\n"
            f"Missing Skills: {', '.join(missing)}\n"
            f"Missing Resume Sections: {', '.join(missing_sections)}\n"
        )

        # Download button for feedback
        st.download_button(
            label="Download Feedback",
            data=feedback_txt,
            file_name="resume_feedback.txt",
            mime="text/plain"
        )
    else:
        st.info("Paste a job description above to get skill match and tailored suggestions.")

else:
    st.info("Please upload a PDF or DOCX resume to begin.")

# Footer note
st.markdown(
    "<small style='color:gray;'>Powered by Streamlit · Built for MCA Project Guidance</small>",
    unsafe_allow_html=True
)
