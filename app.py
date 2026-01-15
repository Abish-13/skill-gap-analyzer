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
import io

# ---------------- 1. PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="CareerCraft AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; }
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

# ---------------- 4. MAIN APP ----------------

def main():
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

    if analyze_btn and uploaded_file and jd_text:
        with st.spinner("Analyzing..."):
            resume_text = extract_text_from_file(uploaded_file)
            resume_skills = extract_skills_from_text(resume_text)
            jd_skills = extract_skills_from_text(jd_text.lower())
            
            matched_skills = resume_skills.intersection(jd_skills)
            missing_skills = jd_skills.difference(resume_skills)
            
            keyword_score = round((len(matched_skills) / len(jd_skills)) * 100) if jd_skills else 0
            ai_score = calculate_ai_match(resume_text, jd_text)
            final_score = int((keyword_score * 0.6) + (ai_score * 0.4))

            # Role Analysis
            role_scores = {}
            for role, skills in ROLES_DB.items():
                r_skills = set(skills)
                match = len(resume_skills.intersection(r_skills))
                role_scores[role] = int((match / len(r_skills)) * 100)
            
            # Sort roles by score
            sorted_roles = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)

        # --- DISPLAY ---
        st.title(f"👋 Hello, {user_name}!")
        st.subheader(f"Targeting: **{target_role}**")
        st.markdown("---")

        col1, col2 = st.columns([1, 1.5])
        
        with col1:
            st.markdown("### 🎯 ATS Score")
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = final_score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#2ecc71" if final_score > 70 else "#f1c40f"}}
            ))
            fig.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### 🧠 Recruiter's Verdict")
            if final_score > 75:
                st.success("Strong Match! You are ready for interviews.")
            elif final_score > 50:
                st.warning("Good potential, but key skills are missing.")
            else:
                st.error("Low match. Significant upskilling needed.")
            
            # --- NEW ADDITION: GRAPH + TEXT LIST ---
            st.markdown("**🏆 Role Fit Analysis**")
            
            # 1. The Graph
            df_radar = pd.DataFrame(dict(r=list(role_scores.values()), theta=list(role_scores.keys())))
            fig_radar = px.line_polar(df_radar, r='r', theta='theta', line_close=True, range_r=[0,100])
            fig_radar.update_traces(fill='toself')
            fig_radar.update_layout(height=200, margin=dict(t=20, b=20, l=40, r=40))
            st.plotly_chart(fig_radar, use_container_width=True)
            
            # 2. The Bullet List (What you asked for!)
            with st.expander("📋 View Role Match Details (Click to Expand)", expanded=True):
                for role, score in sorted_roles:
                    if score >= 80:
                        st.write(f"✅ **{role}**: {score}% (Excellent)")
                    elif score >= 50:
                        st.write(f"⚠️ **{role}**: {score}% (Moderate)")
                    else:
                        st.write(f"❌ **{role}**: {score}% (Low)")

        st.markdown("---")

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("✅ Matched Skills")
            if matched_skills:
                for s in matched_skills:
                    st.success(f"{s.title()}")
            else:
                st.info("No matches found.")
        
        with c2:
            st.subheader("⚠️ Missing Skills")
            if missing_skills:
                for s in missing_skills:
                    st.error(f"{s.title()}")
            else:
                st.success("No missing skills!")

        st.markdown("---")
        
        # Learning
        st.subheader("📚 Learning Roadmap")
        if missing_skills:
            for s in list(missing_skills)[:5]:
                link = LEARNING_LINKS.get(s, f"https://www.google.com/search?q={s}+tutorial")
                st.write(f"🔹 **{s.title()}** → [Start Learning]({link})")
        else:
            st.write("Keep building projects!")

        st.markdown("---")
        
        # Export
        st.subheader("📄 Download Report")
        resume_bytes = create_pdf_bytes(f"{user_name}_Resume", {"Summary": f"Targeting {target_role}.", "Skills": ", ".join(resume_skills)})
        cl_bytes = create_pdf_bytes(f"{user_name}_Cover_Letter", {"Body": f"Applying for {target_role}."})
        
        d1, d2 = st.columns(2)
        with d1:
            if resume_bytes:
                st.download_button("⬇ Resume PDF", resume_bytes, "Resume.pdf", "application/pdf")
        with d2:
            if cl_bytes:
                st.download_button("⬇ Cover Letter PDF", cl_bytes, "Cover_Letter.pdf", "application/pdf")

    elif analyze_btn:
        st.warning("Please upload a resume first.")

if __name__ == "__main__":
    main()
