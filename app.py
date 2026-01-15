import streamlit as st
import pdfplumber
import docx
import pandas as pd
import plotly.graph_objects as go
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import random

# ---------------- 1. PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="CareerCraft AI - Coach Edition",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for the "Coach" Vibe
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1, h2, h3 { color: #2c3e50; font-family: 'Helvetica Neue', sans-serif; }
    .stButton>button { border-radius: 8px; font-weight: bold; border: none; padding: 0.5rem 1rem; transition: 0.3s; }
    .stButton>button:hover { transform: scale(1.02); background-color: #f0f2f6; }
    .metric-box { border: 1px solid #e0e0e0; padding: 15px; border-radius: 10px; background: white; text-align: center; }
    .project-card { background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid #3498db; }
    </style>
    """, unsafe_allow_html=True)

# ---------------- 2. INTELLIGENT DATABASES ----------------

SKILL_DB = {
    "Frontend": ["javascript", "react", "angular", "vue", "html", "css", "tailwind", "bootstrap", "redux", "typescript", "figma", "responsive"],
    "Backend": ["python", "django", "flask", "fastapi", "node.js", "express", "java", "spring boot", "c#", ".net", "go", "ruby", "php"],
    "Database": ["sql", "mysql", "postgresql", "mongodb", "firebase", "redis", "oracle", "dynamodb"],
    "DevOps": ["aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "github actions", "terraform", "linux", "bash", "ci/cd"],
    "Data": ["pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "sql", "power bi", "tableau", "excel", "spark", "hadoop"],
    "Core": ["git", "github", "agile", "scrum", "jira", "unit testing", "rest api", "graphql"]
}

PROJECT_IDEAS = {
    "react": {"title": "Trello Clone", "desc": "Build a Drag & Drop Task Manager to master State & Props."},
    "python": {"title": "Stock Scraper", "desc": "Create a script to scrape and analyze stock prices."},
    "sql": {"title": "Library DB", "desc": "Design a complex schema for a library system with JOINs."},
    "javascript": {"title": "Weather App", "desc": "Fetch real-time weather data using Fetch API."},
    "aws": {"title": "Static Resume Site", "desc": "Host your resume on S3 with CloudFront."},
    "docker": {"title": "Containerized App", "desc": "Dockerize a simple Node.js app."},
    "git": {"title": "Open Source Fix", "desc": "Find a repo, fork it, fix a bug, and submit a PR."}
}

# The "I Did It" Bullet Generator
PROJECT_BULLETS = {
    "react": "• Architected a Trello-style Kanban board using **React.js**, implementing **Redux** for state management of 50+ active tasks.",
    "python": "• Developed a high-performance **Python** web scraper using **BeautifulSoup**, automating data collection for financial analysis.",
    "sql": "• Designed a normalized **SQL** database schema for a library system, optimizing query performance by 40% using complex JOINs.",
    "javascript": "• Built a dynamic Weather Dashboard using **JavaScript (ES6+)** and RESTful APIs, handling asynchronous data fetching efficiently.",
    "aws": "• Deployed a highly available static website on **AWS S3** and **CloudFront**, reducing latency by 60% for global users.",
    "docker": "• Containerized a Node.js application using **Docker**, ensuring consistent development and production environments.",
    "git": "• Collaborated on open-source projects using **Git**, managing branching strategies and resolving merge conflicts in a team environment."
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
            if re.search(r'\b' + re.escape(skill) + r'\b', text):
                found.add(skill)
    return found

def calculate_match(resume_text, jd_text, resume_skills, jd_skills):
    if not jd_skills: return 0, 0, 0
    
    # Keyword Score
    k_score = int((len(resume_skills.intersection(jd_skills)) / len(jd_skills)) * 100)
    
    # Context Score (Simulated Logic for Demo)
    # Real logic would check if skills appear in bullet points vs just list
    tfidf = TfidfVectorizer(stop_words='english')
    try:
        matrix = tfidf.fit_transform([resume_text, jd_text])
        c_score = int(cosine_similarity(matrix[0:1], matrix[1:2])[0][0] * 100)
    except:
        c_score = 10 # Default low score to trigger "Booster"
        
    final_score = int((k_score * 0.6) + (c_score * 0.4))
    return final_score, k_score, c_score

def enhance_description(role):
    # The "Context Booster" Logic
    return f"""
    **BEFORE:** "Used {role}."
    **AFTER:** "Leveraged **{role}** to architect scalable solutions, improving system efficiency by 30% and reducing latency in high-traffic environments."
    """

# ---------------- 4. APP LAYOUT ----------------

def main():
    # --- SESSION STATE INITIALIZATION (Fixes Blank Page Bug) ---
    if 'analyzed' not in st.session_state:
        st.session_state['analyzed'] = False
    if 'simulated_skills' not in st.session_state:
        st.session_state['simulated_skills'] = []

    # --- SIDEBAR ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=50)
        st.title("CareerCraft AI")
        st.markdown("### 1️⃣ Inputs")
        
        uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])
        
        jd_input = st.radio("Target:", ["Paste JD", "Preset Role"])
        jd_text = ""
        role_title = "General"

        if jd_input == "Paste JD":
            role_title = st.text_input("Job Title")
            jd_text = st.text_area("Paste JD Here")
        else:
            role_title = st.selectbox("Select Role", ["Frontend Developer", "Backend Developer", "Data Scientist"])
            presets = {"Frontend Developer": "react javascript html css git figma redux", "Backend Developer": "python django sql api docker aws", "Data Scientist": "python pandas sql machine learning statistics"}
            jd_text = presets.get(role_title, "")

        if st.button("🚀 Analyze My Fit"):
            if uploaded_file and jd_text:
                st.session_state['analyzed'] = True
                st.session_state['resume_text'] = extract_text(uploaded_file)
                st.session_state['jd_text'] = jd_text
                st.session_state['role_title'] = role_title
                st.session_state['user_name'] = "Candidate" # Simplified for demo
            else:
                st.warning("Please upload a resume and JD.")

    # --- MAIN DASHBOARD ---
    if st.session_state['analyzed']:
        # Retrieve Data from Session State
        r_text = st.session_state['resume_text']
        jd_text_lower = st.session_state['jd_text'].lower()
        
        resume_skills = extract_skills(r_text)
        jd_skills = extract_skills(jd_text_lower)
        
        matched = resume_skills.intersection(jd_skills)
        missing = jd_skills.difference(resume_skills)
        
        final, k_score, c_score = calculate_match(r_text, jd_text_lower, resume_skills, jd_skills)

        # --- 1. HERO ---
        st.title(f"👋 Coaching Report: {st.session_state['role_title']}")
        
        # --- 2. SCORES (With Context Booster) ---
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Overall Match", f"{final}%", f"{final-50}% vs Avg")
        with c2:
            st.metric("Hard Skills (ATS)", f"{k_score}%", "Keywords")
        with c3:
            st.metric("Context Match (AI)", f"{c_score}%", "Depth")
            if c_score < 50:
                with st.expander("⚡ Boost Context Score"):
                    st.info("Your resume lists skills but doesn't *prove* them. Use this enhancer:")
                    st.markdown(enhance_description(list(matched)[0] if matched else "Tech"))

        st.markdown("---")

        # --- 3. THE "WHAT IF" SIMULATOR (Fixed Logic) ---
        st.subheader("🧪 The 'What If' Simulator")
        st.caption("Select missing skills to see your potential score jump.")
        
        # Create a list of missing skills with potential boost values
        options = [f"{s} (+15%)" for s in missing]
        selected_opts = st.multiselect("Simulate Learning:", options, key="sim_box")
        
        if selected_opts:
            # clean the string to get just the skill name
            clean_selected = [s.split(" (")[0] for s in selected_opts]
            st.session_state['simulated_skills'] = clean_selected
            
            # Recalculate
            sim_matched = matched.union(set(clean_selected))
            sim_k = int((len(sim_matched) / len(jd_skills)) * 100)
            sim_final = int((sim_k * 0.6) + (c_score * 0.4))
            
            st.success(f"🚀 **Projected Score:** {sim_final}% (You gain +{sim_final - final}%)")
            st.progress(sim_final)
            
            if sim_final > 75:
                st.balloons()

        st.markdown("---")

        # --- 4. PROJECT-BASED LEARNING (The "I Did It" Feature) ---
        col_L, col_R = st.columns([1, 1])

        with col_L:
            st.subheader("✅ Skills You Have")
            if matched:
                st.success(", ".join([s.title() for s in matched]))
            else:
                st.warning("No matches found.")

        with col_R:
            st.subheader("🛠️ Build to Learn (Gap Closer)")
            if missing:
                for skill in list(missing)[:3]:
                    proj = PROJECT_IDEAS.get(skill, {"title": f"{skill.title()} Project", "desc": f"Build a project using {skill}."})
                    bullet = PROJECT_BULLETS.get(skill, f"• Implemented **{skill.title()}** in a production environment.")
                    
                    # Project Card
                    with st.container():
                        st.markdown(f"""
                        <div class="project-card">
                            <b>{skill.title()} Challenge:</b> {proj['title']}<br>
                            <small>{proj['desc']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # The "I Did It" Button
                        if st.button(f"✅ I Built the {proj['title']}! (Add to Resume)", key=f"btn_{skill}"):
                            st.code(bullet, language="markdown")
                            st.toast("Bullet point generated! Copy it above.", icon="🎉")
            else:
                st.success("You are technically ready! Focus on behavioral interviews.")

        st.markdown("---")

        # --- 5. SMART CONTENT GENERATION ---
        st.subheader("📄 One-Click Generators")
        tab1, tab2 = st.tabs(["Smart Cover Letter", "Interview Grill"])
        
        with tab1:
            # Context-Aware Logic
            if final > 70:
                tone = "I am ready to hit the ground running."
            else:
                tone = "I am a rapid learner actively closing technical gaps."
                
            cl_text = f"Dear Hiring Manager,\n\nI am applying for the {st.session_state['role_title']} role. {tone}\n\nMy analysis shows I have strong foundations in {', '.join(list(matched)[:3])}. I am currently building projects in {', '.join(list(missing)[:2])} to ensure I am day-one ready.\n\nSincerely,\nCandidate"
            st.text_area("Cover Letter Draft", cl_text, height=200)
            
        with tab2:
            if missing:
                st.warning(f"Prepare for this question: 'I see you don't know {list(missing)[0].title()}. How would you handle a task requiring it?'")
            else:
                st.success("Your technical stack is solid. Prepare for: 'Tell me about a time you failed.'")

    elif not st.session_state['analyzed']:
        st.info("👈 Upload your resume to start the coaching session.")

if __name__ == "__main__":
    main()
