import streamlit as st
import pdfplumber
import docx
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import re
import io  # Critical for the download fix

# ---------------- 1. PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="CareerCraft AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for the "Pro" look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; }
    .metric-card { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    h1, h2, h3 { color: #2c3e50; }
    </style>
    """, unsafe_allow_html=True)

# ---------------- 2. KNOWLEDGE BASE ----------------
SKILL_DB = {
    "Programming": ["python", "java", "c++", "c", "javascript", "typescript", "ruby", "swift", "go", "php"],
    "Web Frameworks": ["react", "angular", "vue", "django", "flask", "spring boot", "node.js", "express", "fastapi"],
    "Data Science": ["pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "matplotlib", "seaborn", "tableau", "power bi"],
    "Database": ["sql", "mysql", "postgresql", "mongodb", "oracle", "redis", "firebase"],
    "DevOps/Cloud": ["aws", "azure", "google cloud", "docker", "kubernetes", "jenkins", "git", "github", "gitlab", "ci/cd"],
    "Tools": ["jira", "trello", "slack", "excel", "linux", "bash"],
    "Soft Skills": ["communication", "leadership", "problem solving", "teamwork", "time management", "critical thinking"]
}

ROLES_DB = {
    "Software Engineer": ["python", "java", "c++", "git", "sql", "problem solving", "data structures", "algorithms"],
    "Data Scientist": ["python", "machine learning", "statistics", "sql", "pandas", "numpy", "tensorflow", "data visualization"],
    "Frontend Developer": ["javascript", "react", "html", "css", "figma", "git", "responsive design"],
    "Backend Developer": ["python", "java", "node.js", "sql", "api", "database", "server", "django"],
    "DevOps Engineer": ["linux", "aws", "docker", "kubernetes", "jenkins", "scripting", "network"],
    "Product Manager": ["communication", "jira", "roadmap", "agile", "scrum", "analytics", "user research"]
}

LEARNING_LINKS = {
    "python": "https://www.coursera.org/specializations/python",
    "java": "https://www.udemy.com/topic/java/",
    "react": "https://react.dev/learn",
    "sql": "https://www.khanacademy.org/computing/computer-programming/sql",
    "machine learning": "https://www.coursera.org/learn/machine-learning",
    "aws": "https://aws.amazon.com/training/",
    "git": "https://git-scm.com/doc",
    "docker": "https://docs.docker.com/get-started/",
    "communication": "https://www.linkedin.com/learning/topics/communication"
}

# ---------------- 3. HELPER FUNCTIONS ----------------

def extract_text_from_file(uploaded_file):
    text = ""
    try:
        if uploaded_file.name.endswith('.pdf'):
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        elif uploaded_file.name.endswith('.docx'):
            doc = docx.Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"
    except Exception as e:
        st.error(f"Error reading file: {e}")
    return text.lower()

def extract_skills_from_text(text):
    found_skills = set()
    for category, skills in SKILL_DB.items():
        for skill in skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text):
                found_skills.add(skill)
    return found_skills

def calculate_ai_match(resume_text, jd_text):
    documents = [resume_text, jd_text]
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(documents)
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return round(similarity[0][0] * 100, 2)

def create_pdf_bytes(title, content_dict):
    """Generates PDF in memory (Fixes blank page issue)"""
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph(title, styles['Title']))
        elements.append(Spacer(1, 12))

        for section, text in content_dict.items():
            elements.append(Paragraph(f"<b>{section}</b>", styles['Heading2']))
            elements.append(Spacer(1, 6))
            if isinstance(text, list):
                for item in text:
                    elements.append(Paragraph(f"• {item}", styles['Normal']))
            else:
                elements.append(Paragraph(str(text), styles['Normal']))
            elements.append(Spacer(1, 12))

        doc.build(elements)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"Error generating PDF: {e}")
        return None

# ---------------- 4. MAIN APPLICATION ----------------

def main():
    # --- SIDEBAR ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=60)
        st.title("CareerCraft AI")
        st.markdown("### 1️⃣ Inputs")
        uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])
        
        input_mode = st.radio("Target:", ["Preset Role", "Custom JD"])
        
        target_role = "General"
        jd_text = ""
        
        if input_mode == "Preset Role":
            target_role = st.selectbox("Role", list(ROLES_DB.keys()))
            jd_text = " ".join(ROLES_DB[target_role])
        else:
            target_role = st.text_input("Role Name")
            jd_text = st.text_area("Paste JD")

        user_name = st.text_input("Name", "Candidate")
        analyze_btn = st.button("🚀 Analyze Profile")

    # --- MAIN CONTENT ---
    if analyze_btn and uploaded_file and jd_text:
        
        # --- 1. CALCULATIONS ---
        with st.spinner("Analyzing your profile..."):
            resume_text = extract_text_from_file(uploaded_file)
            resume_skills = extract_skills_from_text(resume_text)
            jd_skills = extract_skills_from_text(jd_text.lower())
            
            matched_skills = resume_skills.intersection(jd_skills)
            missing_skills = jd_skills.difference(resume_skills)
            
            keyword_score = round((len(matched_skills) / len(jd_skills)) * 100) if jd_skills else 0
            ai_score = calculate_ai_match(resume_text, jd_text)
            final_score = int((keyword_score * 0.6) + (ai_score * 0.4))

            # Role Fit Radar Logic
            role_scores = {}
            for role, skills in ROLES_DB.items():
                r_skills = set(skills)
                match = len(resume_skills.intersection(r_skills))
                role_scores[role] = (match / len(r_skills)) * 100

        # --- 2. HEADER ---
        st.title(f"👋 Hello, {user_name}!")
        st.subheader(f"Analysis for Role: **{target_role}**")
        st.markdown("---")

        # --- 3. ATS & RECRUITER VERDICT ---
        col1, col2 = st.columns([1, 1.5])
        
        with col1:
            st.markdown("### 🎯 ATS Readiness")
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = final_score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#2ecc71" if final_score > 70 else "#f1c40f" if final_score > 40 else "#e74c3c"}
                }
            ))
            fig.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### 🧠 Recruiter's Verdict")
            if final_score > 75:
                st.success(f"**Strong Candidate!** You have {len(matched_skills)} matching skills. Your vocabulary aligns well with industry standards. Ready for interviews.")
            elif final_score > 50:
                st.warning(f"**Potential Fit.** You have the basics ({len(matched_skills)} matches), but you are missing key tech stacks like {', '.join(list(missing_skills)[:2])}. Upskill now.")
            else:
                st.error(f"**Needs Work.** High skill gap detected. Focus on the 'Missing Skills' section below before applying.")
            
            st.markdown("**Role Fit Analysis:**")
            df_radar = pd.DataFrame(dict(r=list(role_scores.values()), theta=list(role_scores.keys())))
            fig_radar = px.line_polar(df_radar, r='r', theta='theta', line_close=True, range_r=[0,100])
            fig_radar.update_traces(fill='toself')
            fig_radar.update_layout(height=200, margin=dict(t=20, b=20, l=40, r=40))
            st.plotly_chart(fig_radar, use_container_width=True)

        st.markdown("---")

        # --- 4. SKILLS GAP ---
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("💚 Matched Skills")
            if matched_skills:
                for s in matched_skills:
                    st.success(f"✔ {s.title()}")
            else:
                st.info("No direct matches.")
        
        with c2:
            st.subheader("🌱 Missing Skills")
            if missing_skills:
                for s in missing_skills:
                    st.error(f"❌ {s.title()}")
            else:
                st.success("All skills matched!")

        st.markdown("---")

        # --- 5. LEARNING ROADMAP ---
        st.subheader("📚 Personalized Learning Plan")
        with st.expander("Show Recommended Resources", expanded=True):
            if missing_skills:
                for s in list(missing_skills)[:5]:
                    link = LEARNING_LINKS.get(s, f"https://www.google.com/search?q={s}+course")
                    st.write(f"**{s.title()}** → [Start Learning]({link})")
            else:
                st.write("You are good to go! Focus on building projects now.")

        st.markdown("---")

        # --- 6. INTERVIEW & LINKEDIN ---
        i1, i2 = st.columns(2)
        with i1:
            st.subheader("🎤 Interview Talking Points")
            if matched_skills:
                st.write(f"• \"I have hands-on experience with **{list(matched_skills)[0].title()}** in building scalable applications.\"")
                if len(matched_skills) > 1:
                    st.write(f"• \"I use **{list(matched_skills)[1].title()}** to solve data/logic problems efficiently.\"")
            st.write(f"• \"I am actively learning **{list(missing_skills)[0].title() if missing_skills else 'advanced concepts'}** to stay industry-ready.\"")

        with i2:
            st.subheader("💼 LinkedIn 'About' Generator")
            linkedin_bio = (
                f"🚀 Aspiring {target_role} | Tech Enthusiast\n\n"
                f"Passionate about leveraging technology to solve real-world problems. "
                f"Skilled in {', '.join([s.title() for s in list(matched_skills)[:5]])}. "
                f"Currently expanding my expertise in {', '.join([s.title() for s in list(missing_skills)[:3]])} to drive impact in the {target_role} domain.\n\n"
                f"Open to opportunities where I can apply my skills in {list(matched_skills)[0].title() if matched_skills else 'tech'} and grow as a developer."
            )
            st.text_area("Copy for LinkedIn:", linkedin_bio, height=150)

        st.markdown("---")

        # --- 7. EXPORT DOCUMENTS (FIXED) ---
        st.subheader("📄 Download Optimized Assets")
        
        # Prepare Data
        resume_content = {
            "Summary": f"Motivated {target_role} with expertise in {', '.join(list(matched_skills)[:3])}.",
            "Skills": ", ".join(resume_skills),
            "Gap Analysis": f"Addressing gaps in: {', '.join(list(missing_skills)[:3])}"
        }
        cl_content = {
            "Subject": f"Application for {target_role}",
            "Body": f"I am writing to express my interest in the {target_role} position. With my background in {', '.join(list(matched_skills)[:3])}, I am confident in my ability to contribute.",
        }

        # Generate PDFs in Memory (Fast & Bug-Free)
        resume_bytes = create_pdf_bytes(f"{user_name}_Resume", resume_content)
        cl_bytes = create_pdf_bytes(f"{user_name}_Cover_Letter", cl_content)

        d1, d2 = st.columns(2)
        with d1:
            if resume_bytes:
                st.download_button("⬇ Download Resume PDF", data=resume_bytes, file_name="Resume.pdf", mime="application/pdf")
        with d2:
            if cl_bytes:
                st.download_button("⬇ Download Cover Letter PDF", data=cl_bytes, file_name="Cover_Letter.pdf", mime="application/pdf")

    elif analyze_btn:
        st.warning("⚠️ Please upload a resume and provide a job description to proceed.")

if __name__ == "__main__":
    main()
