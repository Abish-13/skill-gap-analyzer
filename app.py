import streamlit as st
import pdfplumber
import docx
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# ---------------- 1. PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="CareerCraft AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 5rem; }
    h1, h2, h3 { font-family: 'Inter', sans-serif; color: #0f172a; }
    
    /* Buttons */
    .stButton>button { 
        border-radius: 8px; font-weight: 600; border: none; 
        padding: 0.6rem 1.2rem; background-color: #2563eb; color: white;
        transition: all 0.2s ease;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2); }
    
    /* Recruiter Tables */
    .dataframe { font-size: 14px; }
    
    /* Badges */
    .winner-badge {
        background-color: #dcfce7; color: #166534; padding: 5px 10px; 
        border-radius: 6px; font-weight: bold; border: 1px solid #166534;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------- 2. DATABASES & CONSTANTS ----------------

SKILL_DB = {
    "Frontend": ["javascript", "react", "angular", "vue", "html", "css", "tailwind", "redux", "typescript", "figma", "jest", "next.js"],
    "Backend": ["python", "django", "flask", "node.js", "express", "java", "spring boot", "go", "c#", ".net"],
    "Database": ["sql", "mysql", "postgresql", "mongodb", "redis", "firebase"],
    "DevOps": ["aws", "docker", "kubernetes", "jenkins", "git", "ci/cd", "linux", "terraform"],
    "Data": ["pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "tableau", "power bi", "excel"]
}

# ---------------- 3. LOGIC ENGINES ----------------

def extract_text(file):
    text = ""
    try:
        if file.name.endswith('.pdf'):
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages: text += page.extract_text() or ""
        elif file.name.endswith('.docx'):
            doc = docx.Document(file)
            for p in doc.paragraphs: text += p.text + "\n"
    except: return ""
    return text

def extract_skills(text):
    text = text.lower()
    found = set()
    for cat, skills in SKILL_DB.items():
        for skill in skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text):
                found.add(skill)
    return found

def calculate_metrics(resume_text, jd_text, r_skills, j_skills):
    if not j_skills: return 0, 0, 0
    
    # 1. Keyword Match
    k_score = int((len(r_skills.intersection(j_skills)) / len(j_skills)) * 100)
    
    # 2. Context Match
    tfidf = TfidfVectorizer(stop_words='english')
    try:
        matrix = tfidf.fit_transform([resume_text, jd_text])
        raw_c_score = int(cosine_similarity(matrix[0:1], matrix[1:2])[0][0] * 100)
    except: raw_c_score = 0
    c_score = max(raw_c_score, 10) # Floor at 10%
    
    # Final Weighted Score
    final = int((k_score * 0.6) + (c_score * 0.4))
    return final, k_score, c_score

# ---------------- 4. MAIN APP LOGIC ----------------

def main():
    
    # --- SIDEBAR: MODE SWITCHER ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=50)
        st.title("CareerCraft AI")
        
        # THE SWITCH
        app_mode = st.selectbox("Select Mode:", ["Student / Candidate", "Recruiter / Hiring Manager"])
        st.markdown("---")

    # =========================================================
    # MODE 1: RECRUITER (COMPARISON)
    # =========================================================
    if app_mode == "Recruiter / Hiring Manager":
        st.title("👥 Resume Comparison Tool")
        st.markdown("Upload multiple resumes to see who fits the job best.")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # 1. JOB DEFINITION
            st.subheader("1. Define the Job")
            target_mode = st.radio("Input Method:", ["Paste JD", "Preset Role"])
            jd_text = ""
            
            if target_mode == "Paste JD":
                jd_text = st.text_area("Paste Job Description", height=200)
            else:
                role = st.selectbox("Select Role", ["Frontend Dev", "Backend Dev", "Data Scientist"])
                presets = {
                    "Frontend Dev": "react javascript html css git figma redux typescript jest",
                    "Backend Dev": "python java django spring boot sql api docker aws",
                    "Data Scientist": "python pandas sql machine learning statistics tensorflow"
                }
                jd_text = presets.get(role, "")

        with col2:
            # 2. BULK UPLOAD
            st.subheader("2. Upload Candidates")
            # accept_multiple_files=True is the key here
            uploaded_files = st.file_uploader("Upload Resumes (PDF/DOCX)", type=["pdf", "docx"], accept_multiple_files=True)

        if st.button("⚖️ Compare Candidates") and uploaded_files and jd_text:
            
            results = []
            jd_skills = extract_skills(jd_text.lower())
            
            progress_bar = st.progress(0)
            
            for i, file in enumerate(uploaded_files):
                # Process each file
                r_text = extract_text(file)
                r_skills = extract_skills(r_text)
                
                final, k_score, c_score = calculate_metrics(r_text, jd_text, r_skills, jd_skills)
                
                results.append({
                    "Candidate File": file.name,
                    "Overall Match": final,
                    "Keyword Score": k_score,
                    "Context Score": c_score,
                    "Skills Found": len(r_skills.intersection(jd_skills)),
                    "Missing Critical": len(jd_skills.difference(r_skills))
                })
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            # Convert to DataFrame
            df = pd.DataFrame(results)
            df = df.sort_values(by="Overall Match", ascending=False).reset_index(drop=True)
            
            st.success("Analysis Complete!")
            st.markdown("---")
            
            # --- LEADERBOARD ---
            st.subheader("🏆 Candidate Leaderboard")
            
            # Highlight Winner
            winner = df.iloc[0]
            st.markdown(f"""
            <div style="background-color: #f0fdf4; padding: 20px; border-radius: 10px; border: 1px solid #166534; margin-bottom: 20px;">
                <h3 style="color: #166534; margin:0;">🥇 Top Candidate: {winner['Candidate File']}</h3>
                <p style="margin:0;">Score: <b>{winner['Overall Match']}%</b> | Skills Matched: {winner['Skills Found']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Visual Comparison Bar Chart
            fig = px.bar(
                df, 
                x='Candidate File', 
                y='Overall Match', 
                color='Overall Match',
                title="Match Score Comparison",
                color_continuous_scale='Bluered_r',
                text_auto=True
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Detailed Table
            st.subheader("📊 Detailed Breakdown")
            st.dataframe(
                df.style.background_gradient(subset=['Overall Match'], cmap='Greens'),
                use_container_width=True
            )

    # =========================================================
    # MODE 2: STUDENT (EXISTING FEATURES)
    # =========================================================
    else:
        # This is the "Student" mode logic (Summary of previous code)
        if 'analyzed' not in st.session_state: st.session_state['analyzed'] = False
        
        with st.sidebar:
            st.markdown("### Student Inputs")
            uploaded_file = st.file_uploader("Upload Your Resume", type=["pdf", "docx"])
            target_mode = st.radio("Target Job", ["Paste JD", "Preset Role"])
            jd_text = ""
            role_title = "General"
            
            if target_mode == "Paste JD":
                role_title = st.text_input("Job Title")
                jd_text = st.text_area("Paste JD")
            else:
                role_title = st.selectbox("Role", ["Frontend Developer", "Backend Developer"])
                presets = {"Frontend Developer": "react javascript", "Backend Developer": "python sql"}
                jd_text = presets.get(role_title, "")
            
            if st.button("🚀 Analyze My Resume"):
                if uploaded_file and jd_text:
                    st.session_state['analyzed'] = True
                    st.session_state['resume_text'] = extract_text(uploaded_file)
                    st.session_state['jd_text'] = jd_text
                    st.session_state['role_title'] = role_title
                else:
                    st.warning("Upload Resume & JD")

        if st.session_state['analyzed']:
            # Simplified Student View for this demo (Full features are in v9 code)
            r_text = st.session_state['resume_text']
            j_text = st.session_state['jd_text']
            r_skills = extract_skills(r_text)
            j_skills = extract_skills(j_text.lower())
            final, k, c = calculate_metrics(r_text, j_text, r_skills, j_skills)
            
            st.title(f"Student Analysis: {st.session_state['role_title']}")
            c1, c2 = st.columns(2)
            with c1: st.metric("Your Match Score", f"{final}%")
            with c2: st.metric("Missing Skills", f"{len(j_skills - r_skills)}")
            st.info("Switch to 'Recruiter Mode' in the sidebar to compare multiple resumes!")

if __name__ == "__main__":
    main()
