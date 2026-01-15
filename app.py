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
    page_title="CareerCraft AI - Ultimate",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Market Leader" UI
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 5rem; }
    h1, h2, h3 { font-family: 'Inter', sans-serif; color: #1e293b; }
    .stButton>button { 
        border-radius: 8px; font-weight: 600; border: none; 
        padding: 0.6rem 1.2rem; transition: all 0.2s ease;
        background-color: #2563eb; color: white;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2); }
    .project-card { 
        background-color: #f8fafc; padding: 20px; border-radius: 12px; 
        margin-bottom: 15px; border-left: 5px solid #2563eb; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .missing-tag {
        background-color: #fee2e2; color: #991b1b; padding: 4px 8px; 
        border-radius: 6px; font-size: 0.9em; font-weight: 600; margin-right: 5px;
    }
    .unlocked-badge {
        background-color: #dcfce7; color: #166534; padding: 4px 8px;
        border-radius: 6px; font-size: 0.8em; font-weight: bold; border: 1px solid #166534;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------- 2. INTELLIGENT DATABASES ----------------

SKILL_DB = {
    "Frontend": ["javascript", "react", "angular", "vue", "html", "css", "tailwind", "redux", "typescript", "figma", "jest", "next.js"],
    "Backend": ["python", "django", "flask", "node.js", "express", "java", "spring boot", "go", "c#", ".net"],
    "Database": ["sql", "mysql", "postgresql", "mongodb", "redis", "firebase", "elasticsearch"],
    "DevOps": ["aws", "docker", "kubernetes", "jenkins", "git", "ci/cd", "linux", "terraform", "azure"],
    "Data": ["pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "tableau", "power bi", "excel", "spark"]
}

# MICRO-PROJECT BLUEPRINTS (The "Benefit" Fix)
PROJECT_BLUEPRINTS = {
    "react": {"title": "Trello Clone (Kanban)", "task": "Build a Drag-and-Drop Task Board using **React DnD** and **Redux Toolkit**."},
    "typescript": {"title": "Strictly Typed Calculator", "task": "Convert a JS Calculator to **TypeScript**, enforcing strict types on all event handlers."},
    "figma": {"title": "Dark Mode Dashboard UI", "task": "Design a 'Login & Dashboard' UI kit (Dark Mode) demonstrating **Component Variants** and **Auto-Layout**."},
    "python": {"title": "Crypto Price Tracker", "task": "Build a script using **Requests & Pandas** to fetch live BTC prices and calculate moving averages."},
    "sql": {"title": "E-Commerce Schema (3NF)", "task": "Design a normalized DB for an Amazon clone. Write a query to find 'Top 3 Spenders' using **JOINs**."},
    "aws": {"title": "Serverless API", "task": "Deploy a 'Hello World' function on **AWS Lambda** triggered by API Gateway."},
    "docker": {"title": "Microservice Dockerfile", "task": "Write a multi-stage **Dockerfile** for a Python app to reduce image size by 40%."},
    "git": {"title": "Simulate Merge Conflict", "task": "Create two branches, edit the same line in both, and resolve the conflict using **Git CLI**."},
    "redux": {"title": "Shopping Cart State", "task": "Implement a global Shopping Cart using **Redux**, handling add/remove actions."}
}

# DYNAMIC INTERVIEW QUESTIONS (The "Killer Feature")
INTERVIEW_Q = {
    "react": "Recruiter: I see you built a Trello Clone. How did you optimize rendering to prevent lag when dragging items?",
    "typescript": "Recruiter: You migrated to TypeScript. What specific bugs did strict typing catch that you missed in JS?",
    "figma": "Recruiter: Walk me through your Dark Mode system. How did you handle color tokens for accessibility?",
    "python": "Recruiter: In your Crypto Tracker, how would you handle a sudden API rate limit error?",
    "sql": "Recruiter: Why did you choose 3rd Normal Form? When would you intentionally denormalize this data?",
    "git": "Recruiter: Explain a situation where you chose 'Git Rebase' over 'Git Merge' and why."
}

# RESUME BULLETS (The "Reward")
RESUME_BULLETS = {
    "react": "• Architected a Trello-style Kanban board using **React**, utilizing **Redux** for state management of 50+ tasks.",
    "typescript": "• Refactored a legacy codebase to **TypeScript**, reducing runtime type errors by 90% through strict typing.",
    "figma": "• Designed a scalable Dark Mode UI System in **Figma**, utilizing Auto-Layout and Variants to speed up dev handoff.",
    "python": "• Developed a financial data pipeline using **Python (Pandas)**, automating real-time crypto analysis."
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
    k_score = int((len(r_skills.intersection(j_skills)) / len(j_skills)) * 100)
    
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
    # --- SESSION STATE (Persistence is Key) ---
    if 'analyzed' not in st.session_state:
        st.session_state['analyzed'] = False
        st.session_state['completed_projects'] = set() # Track unlocked skills
        st.session_state['readiness_score'] = 20 # Start at 20%
        
    # --- SIDEBAR ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=50)
        st.title("CareerCraft AI")
        st.caption("Ultimate Edition v4.0")
        
        uploaded_file = st.file_uploader("1. Upload Resume", type=["pdf", "docx"])
        
        target_mode = st.radio("2. Target Job", ["Paste JD (Recommended)", "Preset Role"])
        jd_text = ""
        role_title = "General"

        if target_mode == "Paste JD (Recommended)":
            role_title = st.text_input("Job Title", "Senior Frontend Engineer")
            jd_text = st.text_area("Paste JD Here")
        else:
            role_title = st.selectbox("Select Role", ["Frontend Developer", "Backend Developer", "Data Scientist"])
            presets = {
                "Frontend Developer": "react javascript html css git figma redux typescript jest next.js",
                "Backend Developer": "python java django spring boot sql api docker aws",
                "Data Scientist": "python pandas sql machine learning statistics tensorflow"
            }
            jd_text = presets.get(role_title, "")

        if st.button("🚀 Analyze My Fit"):
            if uploaded_file and jd_text:
                st.session_state['analyzed'] = True
                st.session_state['resume_text'] = extract_text(uploaded_file)
                st.session_state['jd_text'] = jd_text
                st.session_state['role_title'] = role_title
                st.session_state['readiness_score'] = 20 # Reset on new analysis
                st.session_state['completed_projects'] = set()
            else:
                st.toast("⚠️ Upload Resume & Set Job Target!", icon="🚨")

    # --- MAIN DASHBOARD ---
    if st.session_state['analyzed']:
        # Load Data
        r_text = st.session_state['resume_text']
        j_text = st.session_state['jd_text']
        
        r_skills = extract_skills(r_text)
        j_skills = extract_skills(j_text.lower())
        
        matched = r_skills.intersection(j_skills)
        missing = j_skills.difference(r_skills)
        
        final, k_score, c_score = calculate_metrics(r_text, j_text, r_skills, j_skills)

        # 1. HERO & GAMIFICATION (Attraction)
        st.title(f"🔍 Analysis: {st.session_state['role_title']}")
        
        # The Gamified Progress Bar
        st.caption("🎓 Interview Readiness Level")
        st.progress(st.session_state['readiness_score'] / 100)
        st.markdown(f"**Level: {st.session_state['readiness_score']}%** (Build projects to level up!)")

        # 2. X-RAY METRICS (Accuracy)
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Overall Match", f"{final}%", f"{final-60}% vs Market")
        with c2:
            st.metric("Keyword Match", f"{k_score}%")
            # THE X-RAY LIST
            if missing:
                st.caption("❌ **CRITICAL MISSING:**")
                # Fancy HTML display for missing tags
                tags_html = "".join([f"<span class='missing-tag'>{s}</span>" for s in list(missing)[:6]])
                st.markdown(tags_html, unsafe_allow_html=True)
            else:
                st.success("✅ No Keywords Missing!")
        with c3:
            st.metric("Context Score", f"{c_score}%")
            # THE PEEK-A-BOO REWRITE (UX Fix)
            with st.expander("✨ Peek at Magic Rewrite"):
                st.info(f"**Instead of:** 'Used {list(matched)[0] if matched else 'Java'}'")
                st.success(f"**Write this:** 'Leveraged **{list(matched)[0] if matched else 'Java'}** to architect scalable solutions, improving latency by 30%.'")

        st.markdown("---")

        # 3. MICRO-PROJECT BLUEPRINTS (Benefit + Killer Feature)
        col_L, col_R = st.columns([1, 1.2])

        with col_L:
            st.subheader("✅ Skills You Have")
            if matched:
                st.success(", ".join([s.title() for s in matched]))
            else:
                st.warning("No matches found.")

        with col_R:
            st.subheader("🛠️ Build to Level Up")
            st.caption("Complete these blueprints to unlock Resume Bullets & Interview Questions.")
            
            if missing:
                for skill in list(missing)[:3]:
                    # Get Specific Blueprint
                    bp = PROJECT_BLUEPRINTS.get(skill, {"title": f"{skill.title()} Project", "task": f"Build a practical application using {skill}."})
                    
                    with st.container():
                        st.markdown(f"""
                        <div class="project-card">
                            <h4 style="margin:0;">{bp['title']}</h4>
                            <p style="font-size:14px; color:#555;">{bp['task']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # THE "I BUILT IT" LOOP
                        btn_label = "✅ I Built It! (Unlock Rewards)"
                        if skill in st.session_state['completed_projects']:
                            btn_label = "🎉 Completed!"
                        
                        if st.button(btn_label, key=f"btn_{skill}", disabled=(skill in st.session_state['completed_projects'])):
                            # Update State
                            st.session_state['completed_projects'].add(skill)
                            st.session_state['readiness_score'] += 15 # Level Up!
                            st.rerun() # Refresh to show progress

                        # Show Rewards if Completed
                        if skill in st.session_state['completed_projects']:
                            bullet = RESUME_BULLETS.get(skill, f"• Implemented **{skill.title()}** to optimize workflows.")
                            st.markdown(f"**Resume Bullet:**")
                            st.code(bullet, language="markdown")
                            st.toast(f"Level Up! {skill.title()} Interview Question Unlocked!", icon="🔓")
            else:
                st.success("You have the perfect stack! Go to the Grill.")

        st.markdown("---")

        # 4. THE DYNAMIC INTERVIEW GRILL (Killer Feature Integration)
        st.subheader("🔥 The Interview Grill")
        
        tab1, tab2 = st.tabs(["🔥 Hot Seat (Dynamic)", "📄 Cover Letter"])

        with tab1:
            st.caption("Questions appear here as you unlock skills.")
            
            # 1. Always show questions for matched skills
            if matched:
                st.markdown("**Based on your current resume:**")
                for s in list(matched)[:2]:
                     q = INTERVIEW_Q.get(s, f"Tell me about your experience with {s}.")
                     st.info(f"**{s.title()}:** {q}")

            # 2. Show UNLOCKED questions from "I Built It"
            if st.session_state['completed_projects']:
                st.markdown("---")
                st.markdown("**🔓 UNLOCKED QUESTIONS (New Skills):**")
                for s in st.session_state['completed_projects']:
                    q = INTERVIEW_Q.get(s, f"How did you implement {s} in your recent project?")
                    st.success(f"**{s.title()} (Unlocked):** {q}")
            
            if not matched and not st.session_state['completed_projects']:
                st.warning("Upload a matching resume or Build a project to see questions.")

        with tab2:
            tone = "I am a rapid learner actively closing technical gaps." if final < 70 else "I am ready to deliver value immediately."
            cl_text = f"Dear Hiring Manager,\n\nI am applying for the {st.session_state['role_title']} role. {tone}\n\nMy analysis shows strong foundations in {', '.join(list(matched)[:3])}. I am currently building projects in {', '.join(list(missing)[:2])} to ensure I am day-one ready.\n\nSincerely,\nCandidate"
            st.text_area("Cover Letter Draft", cl_text, height=200)

    elif not st.session_state['analyzed']:
        st.info("👈 Upload your resume to start the CareerCraft experience.")

if __name__ == "__main__":
    main()
