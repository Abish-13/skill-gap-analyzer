import streamlit as st
import pdfplumber
import docx
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# ---------------- 1. PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="CareerCraft AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# FIXED: Added padding-top to preventing text cutoff
st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 { color: #2c3e50; }
    .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; }
    .stCode { border-radius: 10px; }
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

# ---------------- 4. MAIN APPLICATION ----------------

def main():
    # --- SIDEBAR INPUTS ---
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
            target_role = st.text_input("Role Name (e.g., Python Dev)")
            jd_text = st.text_area("Paste Job Description")

        user_name = st.text_input("Candidate Name", "Candidate")
        analyze_btn = st.button("🚀 Analyze Profile")

    # --- MAIN LOGIC ---
    if analyze_btn and uploaded_file and jd_text:
        
        # 1. Processing
        with st.spinner("Analyzing your profile..."):
            resume_text = extract_text_from_file(uploaded_file)
            resume_skills = extract_skills_from_text(resume_text)
            jd_skills = extract_skills_from_text(jd_text.lower())
            
            matched_skills = resume_skills.intersection(jd_skills)
            missing_skills = jd_skills.difference(resume_skills)
            
            keyword_score = round((len(matched_skills) / len(jd_skills)) * 100) if jd_skills else 0
            ai_score = calculate_ai_match(resume_text, jd_text)
            final_score = int((keyword_score * 0.6) + (ai_score * 0.4))

            # Role Fit Calculations
            role_scores = {}
            for role, skills in ROLES_DB.items():
                r_skills = set(skills)
                match = len(resume_skills.intersection(r_skills))
                role_scores[role] = int((match / len(r_skills)) * 100)
            sorted_roles = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)

        # --- RESULTS DASHBOARD ---
        st.title(f"👋 Hello, {user_name}!")
        
        # FIXED: Using markdown with clear formatting to avoid "s for..." cutoff
        st.markdown(f"### 🔎 Analysis for: <span style='color:#2980b9;'>{target_role}</span>", unsafe_allow_html=True)
        st.markdown("---")

        # 2. ATS & Recruiter Verdict
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
                st.success("✅ **Strong Candidate!** Your profile is well-aligned. Ready for interviews.")
            elif final_score > 50:
                st.warning("⚠️ **Potential Fit.** You have the basics, but need to add specific missing skills.")
            else:
                st.error("❌ **Needs Improvement.** Significant skill gap detected. Focus on the roadmap below.")
            
            # Role Fit Graph + List
            st.markdown("**🏆 Role Fit Analysis**")
            df_radar = pd.DataFrame(dict(r=list(role_scores.values()), theta=list(role_scores.keys())))
            fig_radar = px.line_polar(df_radar, r='r', theta='theta', line_close=True, range_r=[0,100])
            fig_radar.update_traces(fill='toself')
            fig_radar.update_layout(height=180, margin=dict(t=20, b=20, l=40, r=40))
            st.plotly_chart(fig_radar, use_container_width=True)
            
            with st.expander("📋 View Role Matches (Click to Expand)", expanded=False):
                for role, score in sorted_roles:
                    if score >= 80: st.write(f"✅ **{role}**: {score}%")
                    elif score >= 50: st.write(f"⚠️ **{role}**: {score}%")
                    else: st.write(f"❌ **{role}**: {score}%")

        st.markdown("---")

        # 3. Skills Analysis
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("💚 Matched Skills")
            if matched_skills:
                for s in matched_skills: st.success(f"✔ {s.title()}")
            else: st.info("No direct matches found.")
        
        with c2:
            st.subheader("🌱 Missing Skills")
            if missing_skills:
                for s in missing_skills: st.error(f"❌ {s.title()}")
            else: st.success("All skills matched!")

        st.markdown("---")

        # 4. Learning & Interview
        st.subheader("📚 Personalized Learning Plan")
        with st.expander("Show Recommended Resources", expanded=True):
            if missing_skills:
                for s in list(missing_skills)[:5]:
                    link = LEARNING_LINKS.get(s, f"https://www.google.com/search?q={s}+tutorial")
                    st.write(f"🔹 **{s.title()}** → [Start Learning]({link})")
            else: st.write("Keep building projects!")

        st.markdown("---")

        # 5. GENERATORS (Text Based)
        st.subheader("📝 Content Generators")
        
        # LinkedIn Generator
        st.markdown("#### 💼 LinkedIn 'About' Section")
        linkedin_bio = (
            f"🚀 Aspiring {target_role} | Tech Enthusiast\n\n"
            f"Passionate about leveraging technology to solve real-world problems. "
            f"Skilled in {', '.join([s.title() for s in list(matched_skills)[:5]])}. "
            f"Currently expanding my expertise in {', '.join([s.title() for s in list(missing_skills)[:3]])} to drive impact in the {target_role} domain.\n\n"
            f"Open to opportunities where I can apply my skills in {list(matched_skills)[0].title() if matched_skills else 'tech'} and grow as a developer."
        )
        st.code(linkedin_bio, language='markdown')

        # Resume Text Generator
        st.markdown("#### 📄 Resume Bullet Points")
        resume_text = (
            f"**PROFILE SUMMARY**\n"
            f"Motivated {target_role} with strong foundation in {', '.join([s.title() for s in list(matched_skills)[:3]])}. "
            f"Eager to contribute to innovative projects and solve complex problems.\n\n"
            f"**TECHNICAL SKILLS**\n"
            f"• Proficient: {', '.join([s.title() for s in matched_skills])}\n"
            f"• Learning: {', '.join([s.title() for s in list(missing_skills)[:3]])}\n\n"
            f"**PROJECT HIGHLIGHTS**\n"
            f"• Developed projects using {list(matched_skills)[0].title() if matched_skills else 'Code'} to optimize workflows.\n"
            f"• Implemented best practices in {list(matched_skills)[1].title() if len(matched_skills)>1 else 'Development'}."
        )
        st.code(resume_text, language='markdown')

        # Cover Letter Text Generator
        st.markdown("#### ✉️ Cover Letter Draft")
        cover_letter_text = (
            f"Dear Hiring Manager,\n\n"
            f"I am writing to express my enthusiastic interest in the {target_role} position. "
            f"With a solid grounding in {', '.join([s.title() for s in list(matched_skills)[:3]])}, "
            f"I am confident in my ability to contribute effectively to your team.\n\n"
            f"My analysis shows a {final_score}% match with your requirements. I am particularly strong in "
            f"{list(matched_skills)[0].title() if matched_skills else 'coding'} and am actively closing gaps in "
            f"{list(missing_skills)[0].title() if missing_skills else 'advanced topics'} to ensure I am industry-ready.\n\n"
            f"Thank you for considering my application. I look forward to the possibility of discussing how my skills align with your needs.\n\n"
            f"Sincerely,\n"
            f"{user_name}"
        )
        st.code(cover_letter_text, language='markdown')

    elif analyze_btn:
        st.warning("⚠️ Please upload a resume and provide a job description.")

if __name__ == "__main__":
    main()
