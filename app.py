import streamlit as st
import pdfplumber
import docx
import pandas as pd
import plotly.graph_objects as go
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# ---------------- 1. PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="CareerCraft AI - Coach Edition",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Pro SaaS" Look
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1, h2, h3 { color: #2c3e50; font-family: 'Inter', sans-serif; }
    .stButton>button { 
        border-radius: 8px; font-weight: 600; border: none; 
        padding: 0.6rem 1.2rem; transition: all 0.2s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.15); }
    .metric-card { 
        background: white; padding: 20px; border-radius: 12px; 
        box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid #f0f2f6; 
        text-align: center;
    }
    .project-card { 
        background-color: #ffffff; padding: 20px; border-radius: 10px; 
        margin-bottom: 15px; border-left: 5px solid #3498db; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .success-badge { color: #27ae60; font-weight: bold; background: #e8f8f5; padding: 4px 8px; border-radius: 4px; }
    .warning-badge { color: #d35400; font-weight: bold; background: #fef5e7; padding: 4px 8px; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

# ---------------- 2. INTELLIGENT DATABASES ----------------

SKILL_DB = {
    "Frontend": ["javascript", "react", "angular", "vue", "html", "css", "tailwind", "redux", "typescript", "figma"],
    "Backend": ["python", "django", "flask", "node.js", "express", "java", "spring boot", "go", "c#"],
    "Database": ["sql", "mysql", "postgresql", "mongodb", "redis", "firebase"],
    "DevOps": ["aws", "docker", "kubernetes", "jenkins", "git", "ci/cd", "linux"],
    "Data": ["pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "tableau", "power bi", "excel"]
}

# FIXED: Specificity is Back!
PROJECT_IDEAS = {
    "react": {"title": "Trello Clone (Kanban)", "desc": "Build a Drag-and-Drop Task Manager to master **State, Props & Redux**."},
    "python": {"title": "Stock Portfolio Tracker", "desc": "Create a Finance Dashboard using **Pandas & Flask** to visualize real-time stock data."},
    "java": {"title": "Library Management System", "desc": "Build a CRUD application to master **OOP Principles (Inheritance/Polymorphism)** and File I/O."},
    "sql": {"title": "E-Commerce Database Schema", "desc": "Design a normalized database for an Amazon clone using **Complex Joins & Stored Procedures**."},
    "javascript": {"title": "Real-Time Chat App", "desc": "Build a Chatroom using **WebSockets (Socket.io)** to understand asynchronous events."},
    "aws": {"title": "Serverless Image Resizer", "desc": "Use **AWS Lambda & S3** to automatically resize images upon upload."},
    "docker": {"title": "Microservices Containerization", "desc": "Dockerize a Python Flask app and a Redis DB, connecting them via **Docker Compose**."},
    "git": {"title": "Open Source Contribution", "desc": "Simulate a 'Merge Conflict' scenario and resolve it using **Git Rebase**."}
}

# The "I Did It" Resume Bullet Generator
PROJECT_BULLETS = {
    "react": "• Architected a Trello-style Kanban board using **React.js**, implementing **Redux** for global state management of 50+ active tasks.",
    "python": "• Developed a high-performance **Python** financial dashboard, processing 10k+ daily stock records using **Pandas** and **Flask**.",
    "java": "• engineered a robust Library Management System in **Java**, applying **OOP principles** to handle 500+ book records efficiently.",
    "sql": "• Designed a 3NF normalized **SQL** database schema for an e-commerce platform, optimizing query execution time by 35% using indexes.",
    "javascript": "• Built a real-time chat application using **JavaScript** and **WebSockets**, enabling sub-100ms message delivery latency.",
    "aws": "• Deployed a serverless image processing pipeline using **AWS Lambda**, reducing infrastructure costs by 40% compared to EC2.",
    "docker": "• Containerized a microservices architecture using **Docker**, ensuring 100% environment consistency across dev and prod."
}

# FIXED: Dynamic Interview Questions
INTERVIEW_Q = {
    "react": "What is the Virtual DOM, and how does it differ from the Real DOM? Explain Reconciliation.",
    "java": "Explain the difference between an Interface and an Abstract Class. When would you use one over the other?",
    "python": "How does Python handle memory management? Explain the concept of Garbage Collection.",
    "sql": "What is the difference between INNER JOIN, LEFT JOIN, and RIGHT JOIN? Give a scenario for each.",
    "docker": "Explain the difference between a Docker Image and a Docker Container.",
    "aws": "What is the difference between S3 and EBS? When would you choose one over the other?"
}

# ---------------- 3. LOGIC FUNCTIONS ----------------

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

def get_impact_label(score):
    if score < 40: return "Basic", "red"
    if score < 70: return "Intermediate", "orange"
    return "High Impact", "green"

def calculate_metrics(resume_text, jd_text, r_skills, j_skills):
    if not j_skills: return 0, 0, 0
    
    # Hard Skills (Keywords)
    k_score = int((len(r_skills.intersection(j_skills)) / len(j_skills)) * 100)
    
    # Soft Skills (Context) - Simple Simulation for Demo
    tfidf = TfidfVectorizer(stop_words='english')
    try:
        matrix = tfidf.fit_transform([resume_text, jd_text])
        c_score = int(cosine_similarity(matrix[0:1], matrix[1:2])[0][0] * 100)
    except:
        c_score = 10 
        
    final = int((k_score * 0.6) + (c_score * 0.4))
    return final, k_score, c_score

# ---------------- 4. MAIN APP ----------------

def main():
    # Session State
    if 'analyzed' not in st.session_state: st.session_state['analyzed'] = False
    
    # --- SIDEBAR ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=50)
        st.title("CareerCraft AI")
        st.caption("Coach Edition v3.0")
        st.markdown("---")
        
        uploaded_file = st.file_uploader("1. Upload Resume", type=["pdf", "docx"])
        
        target_mode = st.radio("2. Target Job", ["Paste Job Description", "Select Preset Role"])
        jd_text = ""
        role_title = "General"

        if target_mode == "Paste Job Description":
            role_title = st.text_input("Job Title")
            jd_text = st.text_area("Paste JD Here")
        else:
            role_title = st.selectbox("Select Role", ["Frontend Developer", "Backend Developer", "Data Scientist"])
            presets = {
                "Frontend Developer": "react javascript html css git figma redux typescript",
                "Backend Developer": "python java django spring boot sql api docker aws",
                "Data Scientist": "python pandas sql machine learning statistics tensorflow"
            }
            jd_text = presets.get(role_title, "")

        if st.button("🚀 Analyze & Coach Me"):
            if uploaded_file and jd_text:
                st.session_state['analyzed'] = True
                st.session_state['resume_text'] = extract_text(uploaded_file)
                st.session_state['jd_text'] = jd_text
                st.session_state['role_title'] = role_title
            else:
                st.toast("⚠️ Upload Resume & Set Job Target!", icon="🚨")

    # --- MAIN CONTENT ---
    if st.session_state['analyzed']:
        # Load Data
        r_text = st.session_state['resume_text']
        j_text = st.session_state['jd_text']
        
        r_skills = extract_skills(r_text)
        j_skills = extract_skills(j_text.lower())
        
        matched = r_skills.intersection(j_skills)
        missing = j_skills.difference(r_skills)
        
        final, k_score, c_score = calculate_metrics(r_text, j_text, r_skills, j_skills)
        impact_label, impact_color = get_impact_label(c_score)

        # 1. HEADER
        st.title(f"🔍 Coaching Report: {st.session_state['role_title']}")
        st.markdown("---")

        # 2. METRICS ROW
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Overall Match", f"{final}%", f"{final-60}% vs Market Avg")
        with c2:
            st.metric("Keyword Match (ATS)", f"{k_score}%", "Hard Skills")
        with c3:
            # FIXED: Friendly Label instead of scary number
            st.markdown(f"<div style='text-align:center;'><p style='margin:0; font-size:14px;'>Impact Score</p><h2 style='margin:0; color:{impact_color};'>{impact_label}</h2></div>", unsafe_allow_html=True)
            
            # FIXED: "Magic Rewrite" Hidden behind Expander
            with st.expander("✨ See Magic Rewrite Example"):
                st.markdown(f"""
                **Bad:** "Used {list(matched)[0] if matched else 'Java'}."
                
                **Good (Recruiter Ready):** "Leveraged **{list(matched)[0] if matched else 'Java'}** to architect scalable solutions, improving system efficiency by **30%**."
                """)

        st.markdown("---")

        # 3. WHAT IF SIMULATOR
        st.subheader("🧪 The 'What If' Simulator")
        st.caption("Select missing skills to see your potential growth.")
        
        sim_options = [f"{s} (+12%)" for s in missing]
        selected_sim = st.multiselect("Simulate Learning:", sim_options)
        
        if selected_sim:
            # Calculate Boost
            base_boost = len(selected_sim) * 12
            new_score = min(final + base_boost, 98)
            st.success(f"🚀 **Projected Score:** {new_score}%")
            st.progress(new_score)

        st.markdown("---")

        # 4. PROJECT LEARNING (The "I Did It" Feature)
        col_L, col_R = st.columns([1, 1.2])

        with col_L:
            st.subheader("✅ Skills You Have")
            if matched:
                st.success(", ".join([s.title() for s in matched]))
            else:
                st.warning("No matches found. Check spelling.")

        with col_R:
            st.subheader("🛠️ Build to Learn (Gap Closer)")
            if missing:
                for skill in list(missing)[:3]:
                    # FIXED: Specific Project Ideas
                    proj = PROJECT_IDEAS.get(skill, {"title": f"{skill.title()} Project", "desc": f"Build a project using {skill}."})
                    bullet = PROJECT_BULLETS.get(skill, f"• Implemented **{skill.title()}** in a production environment.")
                    
                    with st.container():
                        st.markdown(f"""
                        <div class="project-card">
                            <h4 style="margin:0;">{proj['title']}</h4>
                            <p style="font-size:14px; color:#555;">{proj['desc']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # The Addictive "I Built It" Button
                        if st.button(f"✅ I Built It! (Add to Resume)", key=f"btn_{skill}"):
                            st.code(bullet, language="markdown")
                            st.toast(f"Boom! Added {skill.title()} bullet to clipboard.", icon="🎉")
            else:
                st.success("You have all required skills! Go to Interview Prep.")

        st.markdown("---")

        # 5. GENERATORS & INTERVIEW GRILL
        st.subheader("📝 Career Assets")
        tab1, tab2, tab3 = st.tabs(["Smart Cover Letter", "Interview Grill", "ATS Resume"])

        with tab1:
            tone = "I am a rapid learner actively closing technical gaps." if final < 70 else "I am ready to deliver value immediately."
            cl_text = f"Dear Hiring Manager,\n\nI am applying for the {st.session_state['role_title']} role. {tone}\n\nMy analysis shows strong foundations in {', '.join(list(matched)[:3])}. I am currently building projects in {', '.join(list(missing)[:2])} to ensure I am day-one ready.\n\nSincerely,\nCandidate"
            st.text_area("Cover Letter Draft", cl_text, height=150)

        with tab2:
            st.caption("🔥 Questions based on your MISSING skills.")
            if missing:
                for skill in list(missing)[:3]:
                    q = INTERVIEW_Q.get(skill, f"How would you explain **{skill.title()}** to a non-technical stakeholder?")
                    st.info(f"**{skill.title()}:** {q}")
            else:
                st.success("Your stack is solid. Prepare for behavioral questions!")

        with tab3:
            st.caption("Plain text for Resume Parsers")
            ats_text = f"NAME: Candidate\nROLE: {st.session_state['role_title']}\nSKILLS: {', '.join(list(matched))}"
            st.text_area("ATS Text", ats_text)

    elif not st.session_state['analyzed']:
        st.info("👈 Please upload your resume to begin.")

if __name__ == "__main__":
    main()
