import streamlit as st
import pdfplumber
import docx
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import re
import tempfile
import os

# ---------------- 1. PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="CareerCraft AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a professional look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; }
    .metric-card { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); text-align: center; }
    h1, h2, h3 { color: #2c3e50; }
    </style>
    """, unsafe_allow_html=True)

# ---------------- 2. KNOWLEDGE BASE (DATABASE) ----------------
# Comprehensive skill mapping for detection
SKILL_DB = {
    "Programming": ["python", "java", "c++", "c", "javascript", "typescript", "ruby", "swift", "go", "php"],
    "Web Frameworks": ["react", "angular", "vue", "django", "flask", "spring boot", "node.js", "express", "fastapi"],
    "Data Science": ["pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "matplotlib", "seaborn", "tableau", "power bi"],
    "Database": ["sql", "mysql", "postgresql", "mongodb", "oracle", "redis", "firebase"],
    "DevOps/Cloud": ["aws", "azure", "google cloud", "docker", "kubernetes", "jenkins", "git", "github", "gitlab", "ci/cd"],
    "Tools": ["jira", "trello", "slack", "excel", "linux", "bash"],
    "Soft Skills": ["communication", "leadership", "problem solving", "teamwork", "time management", "critical thinking"]
}

# Role definitions for "Preset" mode and "Role Fit" analysis
ROLES_DB = {
    "Software Engineer": ["python", "java", "c++", "git", "sql", "problem solving", "data structures", "algorithms"],
    "Data Scientist": ["python", "machine learning", "statistics", "sql", "pandas", "numpy", "tensorflow", "data visualization"],
    "Frontend Developer": ["javascript", "react", "html", "css", "figma", "git", "responsive design"],
    "Backend Developer": ["python", "java", "node.js", "sql", "api", "database", "server", "django"],
    "DevOps Engineer": ["linux", "aws", "docker", "kubernetes", "jenkins", "scripting", "network"],
    "Product Manager": ["communication", "jira", "roadmap", "agile", "scrum", "analytics", "user research"]
}

# Learning Resources Map
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
    """Extracts text from PDF or DOCX."""
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
    """Cleans text for NLP processing."""
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text

def extract_skills_from_text(text):
    """Matches text against the SKILL_DB."""
    found_skills = set()
    for category, skills in SKILL_DB.items():
        for skill in skills:
            # Regex to find exact word matches (avoids matching 'java' in 'javascript')
            if re.search(r'\b' + re.escape(skill) + r'\b', text):
                found_skills.add(skill)
    return found_skills

def calculate_ai_match(resume_text, jd_text):
    """Uses TF-IDF and Cosine Similarity for a 'Smart' match score."""
    documents = [resume_text, jd_text]
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(documents)
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return round(similarity[0][0] * 100, 2)

def generate_pdf_report(title, content_dict, filename):
    """Generates a professional PDF using ReportLab."""
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tfile.name, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 12))

    # Content Loop
    for section, text in content_dict.items():
        elements.append(Paragraph(f"<b>{section}</b>", styles['Heading2']))
        elements.append(Spacer(1, 6))
        # Handle list or string
        if isinstance(text, list):
            for item in text:
                elements.append(Paragraph(f"• {item}", styles['Normal']))
        else:
            elements.append(Paragraph(text, styles['Normal']))
        elements.append(Spacer(1, 12))

    doc.build(elements)
    return tfile.name

# ---------------- 4. MAIN APP LAYOUT ----------------

def main():
    # Sidebar: Inputs
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
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
            target_role = st.text_input("Enter Role Name (e.g., Python Dev)")
            jd_text = st.text_area("Paste Job Description Here")

        user_name = st.text_input("Your Name", "Candidate")
        
        analyze_btn = st.button("🚀 Analyze Career Path")

    # Main Dashboard
    if analyze_btn and uploaded_file and jd_text:
        # --- PROCESSING ---
        with st.spinner("Analyzing profile against industry standards..."):
            resume_text = extract_text_from_file(uploaded_file)
            resume_skills = extract_skills_from_text(resume_text)
            jd_skills = extract_skills_from_text(jd_text.lower())
            
            # Match Logic
            matched_skills = resume_skills.intersection(jd_skills)
            missing_skills = jd_skills.difference(resume_skills)
            
            # Scores
            keyword_score = round((len(matched_skills) / len(jd_skills)) * 100) if jd_skills else 0
            ai_score = calculate_ai_match(resume_text, jd_text)
            
            # Weighted Final Score (60% Keyword, 40% AI Context)
            final_score = int((keyword_score * 0.6) + (ai_score * 0.4))

        # --- HEADER ---
        st.title(f"👋 Hello, {user_name}!")
        st.subheader(f"Targeting: {target_role}")
        st.markdown("---")

        # --- 3️⃣ ATS READINESS & SCORING ---
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### 🎯 ATS Readiness Score")
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = final_score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Match %"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#2ecc71" if final_score > 70 else "#f1c40f" if final_score > 40 else "#e74c3c"},
                    'steps': [
                        {'range': [0, 40], 'color': "lightgray"},
                        {'range': [40, 70], 'color': "gray"}],
                }
            ))
            fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig, use_container_width=True)
            
            if final_score >= 80:
                st.success("✅ **Ready to Apply!** Your profile is strong.")
            elif final_score >= 50:
                st.warning("⚠️ **Needs Improvement.** Focus on the missing skills below.")
            else:
                st.error("❌ **Not a Match.** Consider learning basics or pivoting roles.")

        with col2:
            st.markdown("### 🧠 Recruiter's Verdict (Simulated)")
            st.info(f"""
            **Assessment:** Based on the analysis, you cover **{len(matched_skills)} out of {len(jd_skills)}** critical skills required for this role. 
            The AI context match is **{ai_score}%**, indicating your resume vocabulary { "aligns well" if ai_score > 50 else "needs more industry-specific keywords"}.
            
            **Recommendation:**
            {"You are a top-tier candidate." if final_score > 75 else "You are a potential fit but need to highlight specific projects." if final_score > 50 else "Significantly upgrade your technical stack before applying."}
            """)
            
            # 5️⃣ JOB ROLE FIT (Radar Chart)
            st.markdown("### 🏆 Role Fit Analysis")
            # Calculate match for ALL preset roles to show alternatives
            role_scores = {}
            for role, skills in ROLES_DB.items():
                r_skills = set(skills)
                match = len(resume_skills.intersection(r_skills))
                total = len(r_skills)
                role_scores[role] = (match / total) * 100

            df_radar = pd.DataFrame(dict(
                r=list(role_scores.values()),
                theta=list(role_scores.keys())
            ))
            fig_radar = px.line_polar(df_radar, r='r', theta='theta', line_close=True, range_r=[0,100])
            fig_radar.update_traces(fill='toself')
            st.plotly_chart(fig_radar, use_container_width=True)

        st.markdown("---")

        # --- 4️⃣ SKILL GAP ANALYSIS ---
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("💚 Matched Skills (Keep These)")
            if matched_skills:
                st.write(", ".join([f"`{s}`" for s in matched_skills]))
            else:
                st.write("No direct matches found.")
        
        with c2:
            st.subheader("🌱 Missing Skills (Focus Here)")
            if missing_skills:
                for s in missing_skills:
                    st.error(f"❌ {s}")
            else:
                st.write("No critical skills missing!")

        # --- 6️⃣ LEARNING ROADMAP ---
        st.subheader("📚 Personalized Learning Roadmap")
        with st.expander("View Learning Resources for Missing Skills", expanded=True):
            found_resource = False
            for s in missing_skills:
                if s in LEARNING_LINKS:
                    st.write(f"📘 **{s.title()}**: [Start Learning]({LEARNING_LINKS[s]})")
                    found_resource = True
            if not found_resource:
                st.write("Use generic platforms like Udemy, Coursera, or YouTube for these specific niche skills.")

        st.markdown("---")

        # --- 7️⃣ INTERVIEW & LINKEDIN ---
        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("🎤 Interview Talking Points")
            st.caption("Use these to answer: 'Tell me about your strengths'")
            for s in list(matched_skills)[:5]:
                st.write(f"✅ *'I have applied {s} in various projects to solve real-world problems.'*")
            st.write(f"🚀 *'I am currently upskilling in {', '.join(list(missing_skills)[:3])} to minimize the gap.'*")

        with col4:
            st.subheader("💼 LinkedIn About Section")
            st.caption("Copy-paste this to your profile")
            linkedin_bio = (
                f"🚀 Aspiring {target_role} | Tech Enthusiast\n\n"
                f"Passionate about leveraging technology to solve problems. "
                f"Skilled in {', '.join(list(matched_skills)[:5])}. "
                f"Currently expanding my expertise in {', '.join(list(missing_skills)[:3])} to drive impact in the {target_role} domain.\n\n"
                f"Open to opportunities where I can apply my skills in {list(matched_skills)[0] if matched_skills else 'tech'} and grow as a developer."
            )
            st.code(linkedin_bio, language='text')

        # --- 10 & 11 GENERATORS ---
        st.markdown("---")
        st.subheader("📄 Export Career Assets")
        
        c5, c6 = st.columns(2)
        
        with c5:
            # Resume Generation
            resume_content = {
                "Profile Summary": f"Motivated {target_role} with a strong foundation in {', '.join(list(matched_skills)[:4])}. Eager to contribute to innovative projects.",
                "Technical Skills": ", ".join(resume_skills),
                "Project Focus": f"Ready to work on {target_role} projects utilizing {list(matched_skills)[0] if matched_skills else 'modern tech'}.",
                "Declaration": "I hereby declare that the above information is true to the best of my knowledge."
            }
            if st.button("Generate Optimized Resume"):
                pdf_path = generate_pdf_report(f"{user_name} - Resume", resume_content, "resume.pdf")
                with open(pdf_path, "rb") as f:
                    st.download_button("⬇ Download Resume PDF", f, file_name=f"{user_name}_Resume.pdf")

        with c6:
            # Cover Letter Generation
            cl_content = {
                "Salutation": "Dear Hiring Manager,",
                "Opening": f"I am writing to express my enthusiastic interest in the {target_role} position.",
                "Body": f"With a solid grounding in {', '.join(list(matched_skills)[:3])}, I am confident in my ability to contribute effectively. My analysis shows a {final_score}% match with your requirements, and I am actively closing gaps in {', '.join(list(missing_skills)[:2])}.",
                "Closing": "Thank you for considering my application. I look forward to discussing how my skills align with your team's needs.",
                "Sign-off": f"Sincerely,\n{user_name}"
            }
            if st.button("Generate Cover Letter"):
                pdf_path = generate_pdf_report("Cover Letter", cl_content, "cover_letter.pdf")
                with open(pdf_path, "rb") as f:
                    st.download_button("⬇ Download Cover Letter PDF", f, file_name=f"{user_name}_Cover_Letter.pdf")

    elif analyze_btn:
        st.warning("⚠️ Please upload a resume and provide a job description.")

if __name__ == "__main__":
    main()
