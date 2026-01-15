import streamlit as st
import pdfplumber
import docx
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import random

# ---------------- 1. PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="CareerCraft AI - Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Market Leader" polish
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1, h2, h3 { color: #2c3e50; font-family: 'Helvetica Neue', sans-serif; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; border: none; padding: 0.5rem 1rem; }
    .stButton>button:hover { transform: scale(1.02); transition: 0.2s; }
    .stTextArea textarea { font-family: 'Courier New', monospace; font-size: 14px; background-color: #f8f9fa; }
    .metric-box { border: 1px solid #e0e0e0; padding: 15px; border-radius: 10px; background: white; text-align: center; }
    .success-text { color: #27ae60; font-weight: bold; }
    .warning-text { color: #d35400; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ---------------- 2. INTELLIGENT DATABASES ----------------

SKILL_DB = {
    # Expanded with related terms for smarter matching
    "Frontend": ["javascript", "react", "angular", "vue", "html", "css", "tailwind", "bootstrap", "redux", "typescript", "figma", "responsive"],
    "Backend": ["python", "django", "flask", "fastapi", "node.js", "express", "java", "spring boot", "c#", ".net", "go", "ruby", "php"],
    "Database": ["sql", "mysql", "postgresql", "mongodb", "firebase", "redis", "oracle", "dynamodb"],
    "DevOps": ["aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "github actions", "terraform", "linux", "bash", "ci/cd"],
    "Data": ["pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "sql", "power bi", "tableau", "excel", "spark", "hadoop"],
    "Core": ["git", "github", "agile", "scrum", "jira", "unit testing", "rest api", "graphql"]
}

# Project-Based Learning Map (The "Fix")
PROJECT_IDEAS = {
    "react": "Build a **Trello Clone** (Drag & Drop) to master State & Props.",
    "python": "Create a **Web Scraper** for stock prices using BeautifulSoup.",
    "sql": "Design a **Library Management System** schema and write complex JOIN queries.",
    "javascript": "Build a **Weather Dashboard** fetching real data from an API.",
    "aws": "Deploy a static website using **S3 & CloudFront**.",
    "docker": "Containerize a simple Python/Node app and run it locally.",
    "git": "Contribute to an **Open Source** repo or simulate a Merge Conflict resolution."
}

# Interview "Grill" Questions (The "Differentiation")
INTERVIEW_QUESTIONS = {
    "react": "I see you don't list React. How would you handle state management in a large application if you had to learn it today?",
    "sql": "We use SQL heavily. Since it's missing, how would you approach optimizing a slow database query?",
    "python": "Our stack is Python-based. Explain how you would manage memory in a resource-heavy script.",
    "git": "Version control is critical. Describe a situation where you'd need to use 'git rebase' vs 'git merge'."
}

# ---------------- 3. SMART FUNCTIONS ----------------

def extract_text(uploaded_file):
    text = ""
    try:
        if uploaded_file.name.endswith('.pdf'):
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages: text += page.extract_text() or ""
        elif uploaded_file.name.endswith('.docx'):
            doc = docx.Document(uploaded_file)
            for para in doc.paragraphs: text += para.text + "\n"
    except Exception: return ""
    return text

def extract_skills(text):
    text = text.lower()
    found = set()
    for category, skills in SKILL_DB.items():
        for skill in skills:
            # Smart regex: looks for word boundaries to avoid finding "Java" in "Javascript"
            if re.search(r'\b' + re.escape(skill) + r'\b', text):
                found.add(skill)
    return found

def get_name_from_file(filename, text):
    """Tries to be smart about extracting the name."""
    # 1. Try filename cleaning (e.g., "John_Doe_Resume.pdf")
    clean_name = filename.split('.')[0].replace('_', ' ').replace('-', ' ')
    clean_name = re.sub(r'\bresume\b', '', clean_name, flags=re.IGNORECASE).strip()
    if len(clean_name.split()) >= 2:
        return clean_name.title()
    # 2. Fallback: First line of resume
    first_line = text.split('\n')[0].strip()
    if len(first_line.split()) <= 3:
        return first_line.title()
    return "Candidate"

def calculate_match(resume_text, jd_text, resume_skills, jd_skills):
    # 1. Keyword Score (Hard Skills)
    if not jd_skills:
        k_score = 0
    else:
        k_score = int((len(resume_skills.intersection(jd_skills)) / len(jd_skills)) * 100)
    
    # 2. Context Score (Soft/Semantic Match)
    tfidf = TfidfVectorizer(stop_words='english')
    try:
        matrix = tfidf.fit_transform([resume_text, jd_text])
        c_score = int(cosine_similarity(matrix[0:1], matrix[1:2])[0][0] * 100)
    except:
        c_score = 0
        
    # Weighted Average: 60% Keywords (ATS reality), 40% Context (Human reality)
    final_score = int((k_score * 0.6) + (c_score * 0.4))
    return final_score, k_score, c_score

# ---------------- 4. APP LAYOUT ----------------

def main():
    # --- SIDEBAR: ONBOARDING ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=50)
        st.title("CareerCraft AI")
        st.markdown("Optimize your resume for the **Top 1%**.")
        
        uploaded_file = st.file_uploader("📄 Upload Resume", type=["pdf", "docx"])
        
        jd_input = st.radio("🎯 Target Job:", ["Paste JD (Recommended)", "Preset Role"])
        jd_text = ""
        role_title = "General Role"

        if jd_input == "Paste JD (Recommended)":
            role_title = st.text_input("Job Title (e.g. Senior React Dev)")
            jd_text = st.text_area("Paste the Job Description here...")
        else:
            role_title = st.selectbox("Select Role", ["Frontend Developer", "Backend Developer", "Data Scientist", "DevOps Engineer"])
            # Simple preset generation
            presets = {"Frontend Developer": "react javascript html css git figma redux", "Backend Developer": "python django sql api docker aws", "Data Scientist": "python pandas sql machine learning statistics", "DevOps Engineer": "aws docker kubernetes linux ci/cd"}
            jd_text = presets.get(role_title, "")

        # Auto-Extract Name (Fixing Friction)
        if uploaded_file:
            raw_text = extract_text(uploaded_file)
            auto_name = get_name_from_file(uploaded_file.name, raw_text)
            user_name = st.text_input("Your Name", value=auto_name)
        else:
            user_name = st.text_input("Your Name", value="Candidate")
            raw_text = ""

        analyze_btn = st.button("🚀 Analyze My Fit")

    # --- MAIN CONTENT ---
    if analyze_btn and uploaded_file and jd_text:
        
        # PROCESSING
        resume_skills = extract_skills(raw_text)
        jd_skills = extract_skills(jd_text)
        
        matched = resume_skills.intersection(jd_skills)
        missing = jd_skills.difference(resume_skills)
        
        final_score, k_score, c_score = calculate_match(raw_text, jd_text, resume_skills, jd_skills)

        # --- 1. HERO SECTION ---
        st.title(f"👋 Hello, {user_name}.")
        st.caption(f"Targeting: **{role_title}**")
        
        # --- 2. SCORECARD (Fixed: Detailed Breakdown) ---
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Overall Match", f"{final_score}%", delta=f"{final_score-50}% vs Avg", delta_color="normal")
        with c2:
            st.metric("Keyword Match (ATS)", f"{k_score}%", "Hard Skills")
        with c3:
            st.metric("Context Match (AI)", f"{c_score}%", "Relevance")

        # --- 3. GAMIFICATION: "WHAT IF" SIMULATOR (The Killer Feature) ---
        if missing:
            st.markdown("---")
            st.subheader("🧪 The 'What If' Simulator")
            st.caption("Select skills you plan to learn this week to see how it affects your score.")
            
            simulated_learning = st.multiselect("Add skills to simulate:", list(missing))
            
            if simulated_learning:
                # Recalculate Logic
                sim_matched = matched.union(set(simulated_learning))
                sim_k_score = int((len(sim_matched) / len(jd_skills)) * 100)
                sim_final = int((sim_k_score * 0.6) + (c_score * 0.4))
                
                st.success(f"🚀 **Potential Score:** {sim_final}% (+{sim_final - final_score}%)")
                st.progress(sim_final)
            else:
                st.info("👈 Try adding skills above to see your potential growth!")

        st.markdown("---")

        # --- 4. DEEP DIVE ANALYSIS ---
        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.subheader("✅ You Have")
            if matched:
                st.write(", ".join([f"**{s.title()}**" for s in matched]))
            else:
                st.warning("No exact keyword matches found. Check your spelling.")

        with col_right:
            st.subheader("⚠️ You Need (Project-Based Fix)")
            if missing:
                for skill in list(missing)[:5]: # Show top 5
                    idea = PROJECT_IDEAS.get(skill, f"Build a small project using **{skill.title()}**.")
                    st.markdown(f"**{skill.title()}**: {idea}")
            else:
                st.success("You have all the required skills! Focus on Interview Prep.")

        st.markdown("---")

        # --- 5. GENERATORS (Fixed Logic) ---
        st.subheader("📝 Intelligent Generators")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Cover Letter", "LinkedIn About", "Interview Prep", "ATS Text"])

        # TAB 1: SMART COVER LETTER
        with tab1:
            st.caption("This draft adjusts based on your match score. It NEVER mentions low percentages.")
            
            # Logic: If Score > 70 (Confidence), If Score < 70 (Growth Mindset)
            if final_score > 70:
                opening_line = f"My proven track record in {', '.join(list(matched)[:3])} aligns perfectly with the requirements for the {role_title} role."
                focus_area = "I am eager to bring my expertise to your team immediately."
            else:
                opening_line = f"I am excited to apply for the {role_title} position. While I am proficient in {', '.join(list(matched)[:2])}, I am a rapid learner actively upskilling in {', '.join(list(missing)[:2])}."
                focus_area = "My ability to adapt quickly to new tech stacks makes me a strong long-term asset."

            cl_text = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {role_title} position at your company. {opening_line}

Throughout my academic and project experience, I have developed a disciplined approach to software development. For example, my work with {list(matched)[0].title() if matched else 'technology'} demonstrated my ability to solve complex problems efficiently.

{focus_area}

Thank you for your time and consideration.

Sincerely,
{user_name}"""
            st.text_area("Copy this Draft:", value=cl_text, height=300)

        # TAB 2: STAR METHOD LINKEDIN
        with tab2:
            st.caption("Narrative-style bio for your profile.")
            linkedin_text = f"""🚀 Aspiring {role_title} | Problem Solver

I am a developer passionate about building scalable solutions. With a strong foundation in {', '.join(list(matched)[:3])}, I focus on writing clean, efficient code.

Currently, I am expanding my technical toolkit by building projects in {', '.join(list(missing)[:3]) if missing else 'advanced system design'}. My goal is to leverage technology to drive real-world impact.

Open to connecting with fellow engineers and recruiters!"""
            st.text_area("LinkedIn Bio:", value=linkedin_text, height=200)

        # TAB 3: INTERVIEW GRILL (New Feature)
        with tab3:
            st.caption("🔥 Tough Questions based on your MISSING skills.")
            if missing:
                for skill in list(missing)[:3]:
                    q = INTERVIEW_QUESTIONS.get(skill, f"Tell me about a time you had to learn **{skill.title()}** quickly. How did you do it?")
                    st.info(f"**Q:** {q}")
            else:
                st.success("You are well-prepared technically! Prepare for behavioral questions now.")

        # TAB 4: ATS FRIENDLY VERSION
        with tab4:
            st.caption("Plain text version of your resume (Robots love this).")
            ats_text = f"""NAME: {user_name}
ROLE: {role_title}

SKILLS:
{', '.join([s.title() for s in matched])}

SUMMARY:
Motivated professional with exposure to {', '.join(list(matched)[:3])}. Dedicated to writing clean code and continuous learning.
"""
            st.text_area("ATS-Friendly Text:", value=ats_text, height=200)
            st.download_button("Download .txt", ats_text, "resume_ats.txt")

    elif analyze_btn:
        st.warning("⚠️ Please upload a resume and ensure the Job Description is filled.")

if __name__ == "__main__":
    main()
