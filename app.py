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
import io  # FIXED: Added io for in-memory file handling

# ---------------- 1. PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="CareerCraft AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; }
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

def clean_text(text):
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text

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
    """FIXED: Generates PDF in memory (BytesIO) instead of temp file."""
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        elements.append(Paragraph(title, styles['Title']))
        elements.append(Spacer(1, 12))

        # Content
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

# ---------------- 4. MAIN APP LAYOUT ----------------

def main():
    # Sidebar
    with st.sidebar:
        st.title("CareerCraft AI")
        st.markdown("### 1️⃣ Resume Understanding")
        uploaded_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
        
        st.markdown("### 2️⃣ Job Target Definition")
        input_mode = st.radio("Select Target:", ["Preset Role", "Custom JD"])
        
        target_role = "General"
        jd_text = ""
        
        if input_mode == "Preset Role":
            target_role = st.selectbox("Choose Role", list(ROLES_DB.keys()))
            jd_text = " ".join(ROLES_DB[target_role])
        else:
            target_role = st.text_input("Enter Role Name")
            jd_text = st.text_area("Paste Job Description")

        user_name = st.text_input("Your Name", "Candidate")
        
        # We only need one main button for analysis
        analyze_btn = st.button("🚀 Analyze Career Path")

    # Main Logic
    if analyze_btn and uploaded_file and jd_text:
        # ANALYSIS
        with st.spinner("Analyzing..."):
            resume_text = extract_text_from_file(uploaded_file)
            resume_skills = extract_skills_from_text(resume_text)
            jd_skills = extract_skills_from_text(jd_text.lower())
            
            matched_skills = resume_skills.intersection(jd_skills)
            missing_skills = jd_skills.difference(resume_skills)
            
            keyword_score = round((len(matched_skills) / len(jd_skills)) * 100) if jd_skills else 0
            ai_score = calculate_ai_match(resume_text, jd_text)
            final_score = int((keyword_score * 0.6) + (ai_score * 0.4))

        # --- DISPLAY RESULTS ---
        st.title(f"👋 Hello, {user_name}!")
        st.subheader(f"Targeting: {target_role}")
        st.markdown("---")

        # 1. Gauge Chart
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("### 🎯 ATS Score")
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = final_score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#2ecc71" if final_score > 70 else "#f1c40f"}}
            ))
            fig.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### 🧠 Feedback")
            st.info(f"You matched **{len(matched_skills)}** key skills. Your AI relevance score is **{ai_score}%**.")
            st.write(f"**Missing Critical Skills:** {', '.join(list(missing_skills)[:5]) if missing_skills else 'None!'}")

        st.markdown("---")

        # 2. Skill Gap
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("✅ Matched Skills")
            st.success(", ".join(matched_skills) if matched_skills else "No matches found.")
        with c2:
            st.subheader("⚠️ Skills to Learn")
            st.warning(", ".join(missing_skills) if missing_skills else "All clear!")

        # 3. Learning Roadmap
        if missing_skills:
            st.markdown("### 📚 Recommended Learning")
            for s in list(missing_skills)[:5]:
                if s in LEARNING_LINKS:
                    st.write(f"- 🔗 **Learn {s.title()}:** [Click Here]({LEARNING_LINKS[s]})")

        st.markdown("---")

        # 4. EXPORT SECTION (FIXED)
        st.subheader("📄 Export Career Assets")
        c3, c4 = st.columns(2)
        
        # Resume Data
        resume_data = {
            "Name": user_name,
            "Role": target_role,
            "Summary": f"Aspiring {target_role} with skills in {', '.join(list(matched_skills)[:5])}.",
            "Skills": ", ".join(resume_skills),
            "Missing Skills (To Add Later)": ", ".join(missing_skills)
        }
        
        # Cover Letter Data
        cl_data = {
            "Subject": f"Application for {target_role}",
            "Salutation": "Dear Hiring Manager,",
            "Body": f"I am excited to apply for the {target_role} position. With experience in {', '.join(list(matched_skills)[:3])}, I believe I am a strong fit.",
            "Closing": "Sincerely,",
            "Signature": user_name
        }

        with c3:
            # FIXED: Direct generation inside the download button
            resume_pdf = create_pdf_bytes(f"{user_name} - Resume", resume_data)
            if resume_pdf:
                st.download_button(
                    label="⬇ Download Optimized Resume",
                    data=resume_pdf,
                    file_name="Optimized_Resume.pdf",
                    mime="application/pdf"
                )

        with c4:
            # FIXED: Direct generation inside the download button
            cl_pdf = create_pdf_bytes("Cover Letter", cl_data)
            if cl_pdf:
                st.download_button(
                    label="⬇ Download Cover Letter",
                    data=cl_pdf,
                    file_name="Cover_Letter.pdf",
                    mime="application/pdf"
                )

    elif analyze_btn:
        st.error("Please upload a resume and select a job role first!")

if __name__ == "__main__":
    main()
