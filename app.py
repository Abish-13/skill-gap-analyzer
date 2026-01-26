import streamlit as st
import numpy as np
import pdfplumber
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# ==========================================
# PAGE CONFIG & CSS STYLING
# ==========================================
st.set_page_config(page_title="CareerCraft AI", layout="wide", page_icon="🚀")

st.markdown("""
<style>
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #4CAF50, #8BC34A); }
    .project-card { border: 1px solid #ddd; padding: 15px; border-radius: 10px; margin-bottom: 10px; background-color: #f9f9f9;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# BACKEND LOGIC (The ML Engine)
# ==========================================
def extract_pdf_text(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def calculate_match(resume_text, jd_text):
    if not resume_text or not jd_text: return 0, []
    tfidf = TfidfVectorizer(stop_words='english')
    matrix = tfidf.fit_transform([resume_text, jd_text])
    score = int(cosine_similarity(matrix[0:1], matrix[1:2])[0][0] * 100)
    jd_words = set(re.findall(r'\b\w+\b', jd_text.lower()))
    res_words = set(re.findall(r'\b\w+\b', resume_text.lower()))
    return score, list(jd_words - res_words)[:5]

def generate_cover_letter(role, gaps):
    gap_text = f"specifically in areas like {', '.join(gaps[:2])}," if gaps else ""
    return f"""Dear Hiring Manager,
    
I am writing to express my strong interest in the {role} position. As a proactive engineer, I have a passion for building scalable solutions.

Recognizing the evolving needs of the industry, {gap_text} I have independently developed high-impact projects, such as a full-stack dashboard, to ensure my skills align perfectly with your production needs. 

I am eager to bring my problem-solving mindset and technical adaptability to your team. Thank you for your time.

Sincerely, 
[Your Name]"""

def analyze_student_answer(answer, target_skill):
    impact_words = ["optimized", "architected", "integrated", "solved", "built"]
    if len(answer.split()) < 15: return "❌ Too short! Mention a specific challenge.", "low"
    if any(word in answer.lower() for word in impact_words) and target_skill.lower() in answer.lower():
        return "✅ Great! High-impact action verbs detected. You sound like a real engineer.", "high"
    return f"⚠️ You mentioned {target_skill}, but use verbs like 'Optimized' to show impact.", "mid"

# ==========================================
# PRESET JOB DATA
# ==========================================
PRESET_ROLES = {
    "Software Engineer (SDE I)": "Looking for a software engineer with strong data structures, algorithms, Java, Python, SQL, and Git experience. Must know REST APIs.",
    "Data Scientist": "Seeking a data scientist proficient in Python, Pandas, Scikit-Learn, SQL, and Data Visualization. Experience with ML models preferred.",
    "Frontend Developer": "Frontend role requiring React.js, Next.js, Tailwind CSS, JavaScript, HTML5, and responsive UI design skills.",
    "Backend Architect": "Backend role requiring Node.js, Express, MongoDB, Docker, AWS, and Microservices architecture experience."
}

# ==========================================
# UI FRONTEND
# ==========================================
st.title("🚀 CareerCraft AI: Diamond Tier")
st.write("The Build-to-Hire Loop for the Modern Engineer")

# --- SIDEBAR: TARGET JOB INPUT ---
st.sidebar.header("🎯 Step 1: Set Target Job")
job_input_method = st.sidebar.radio("How do you want to set the job?", ["Select Preset Role", "Paste Job Description"])

if job_input_method == "Select Preset Role":
    selected_role = st.sidebar.selectbox("Choose a Role:", list(PRESET_ROLES.keys()))
    jd_text = PRESET_ROLES[selected_role]
    role_title = selected_role
else:
    jd_text = st.sidebar.text_area("Paste JD Here:", height=200)
    role_title = "Custom Job Role"

# --- MAIN AREA: RESUME INPUT ---
st.subheader("📄 Step 2: Input Your Resume")
resume_input_method = st.radio("Choose Input Method (Paste handles slow networks):", ["Upload PDF", "Paste Text"])

resume_text = ""
if resume_input_method == "Upload PDF":
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
    if uploaded_file: resume_text = extract_pdf_text(uploaded_file)
else:
    resume_text = st.text_area("Paste Resume Text Here:", height=150)

# RUN ANALYSIS
if st.button("🔍 Run AI Gap Analysis") and resume_text and jd_text:
    score, gaps = calculate_match(resume_text, jd_text)
    st.session_state['score'] = score
    st.session_state['gaps'] = gaps
    st.session_state['role'] = role_title
    st.session_state['resume'] = resume_text

st.markdown("---")

# --- TABS: THE FULL ECOSYSTEM ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Analysis & Blueprints", "✍️ Docs & Cover Letter", "🎤 Interview Grill", "👔 Recruiter View"])

if 'score' in st.session_state:
    score = st.session_state['score']
    gaps = st.session_state['gaps']
    target_skill = gaps[0] if gaps else "React"

    # --- TAB 1: ANALYSIS & PROJECTS ---
    with tab1:
        st.subheader(f"✅ Match Score: {score}%")
        st.progress(score / 100.0)
        
        st.markdown("### 🛠️ Recommended Micro-Project")
        st.markdown(f"""
        <div class='project-card'>
            <h4>Missing Skill: {target_skill.capitalize()}</h4>
            <p><b>Blueprint:</b> Build an industry-standard project to prove your competency in {target_skill}.</p>
            <p style='color: #4CAF50; font-weight: bold;'>💰 Est. Salary Boost: +₹5 LPA</p>
        </div>
        """, unsafe_allow_html=True)

    # --- TAB 2: RESUME DRAFT & COVER LETTER (RESTORED) ---
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("✉️ Auto-Generated Cover Letter")
            cover_letter = generate_cover_letter(st.session_state['role'], gaps)
            st.text_area("Copy your Cover Letter:", value=cover_letter, height=300)
        
        with col2:
            st.subheader("✨ Magic Resume Rewrite")
            st.write(f"Based on your gap ({target_skill}), add this bullet point to your resume after building the project:")
            st.code(f"Architected a scalable solution using {target_skill.capitalize()}, improving system efficiency by 15%.", language="markdown")

    # --- TAB 3: INTERVIEW GRILL ---
    with tab3:
        st.subheader("🎤 Technical Defense")
        st.info(f"**Q:** How did you implement {target_skill} in your recent project?")
        user_ans = st.text_area("Type your answer:")
        if st.button("Verify Answer"):
            feedback, status = analyze_student_answer(user_ans, target_skill)
            if status == "high": st.success(feedback)
            else: st.warning(feedback)

    # --- TAB 4: RECRUITER VIEW ---
    with tab4:
        st.subheader("👔 Hiring Manager Dashboard")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.metric("Technical Match", f"{score}%")
            st.metric("Candidate Persona", "Growth-Oriented Builder")
        with col_r2:
            st.markdown("### 🎣 Trap Questions")
            st.write(f"1. Ask them to whiteboard the data flow using {target_skill}.")
            st.write("2. 'What was the hardest bug you faced and how did you debug it?'")
