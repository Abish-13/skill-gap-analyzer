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
    page_title="CareerCraft AI - Platinum",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Market Leader" UI & Text Wrapping Fixes
st.markdown("""
    <style>
    /* Global Spacing */
    .block-container { padding-top: 2rem; padding-bottom: 5rem; }
    h1, h2, h3 { font-family: 'Inter', sans-serif; color: #1e293b; }
    
    /* Buttons */
    .stButton>button { 
        border-radius: 8px; font-weight: 600; border: none; 
        padding: 0.6rem 1.2rem; transition: all 0.2s ease;
        background-color: #2563eb; color: white;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2); }
    
    /* Project Cards */
    .project-card { 
        background-color: #f8fafc; padding: 20px; border-radius: 12px; 
        margin-bottom: 15px; border-left: 5px solid #2563eb; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Badges */
    .missing-tag {
        background-color: #fee2e2; color: #991b1b; padding: 4px 8px; 
        border-radius: 6px; font-size: 0.9em; font-weight: 600; margin-right: 5px; display: inline-block; margin-bottom: 5px;
    }
    
    /* Fix Text Wrapping in Expanders/Info Boxes */
    .streamlit-expanderContent div {
        word-wrap: break-word;
        white-space: normal;
    }
    .stAlert {
        word-wrap: break-word;
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

# MICRO-PROJECT BLUEPRINTS (Fixed: No Lazy AI)
PROJECT_BLUEPRINTS = {
    "react": {"title": "Trello Clone (Kanban)", "task": "Build a Drag-and-Drop Task Board using **React DnD** and **Redux Toolkit**."},
    "spring boot": {"title": "Bookstore REST API", "task": "Build a comprehensive API with CRUD operations, connecting to a local **H2 Database** and handling exceptions."},
    "typescript": {"title": "Strictly Typed Calculator", "task": "Convert a JS Calculator to **TypeScript**, enforcing strict types on all event handlers."},
    "figma": {"title": "Dark Mode Dashboard UI", "task": "Design a 'Login & Dashboard' UI kit (Dark Mode) demonstrating **Component Variants** and **Auto-Layout**."},
    "python": {"title": "Crypto Price Tracker", "task": "Build a script using **Requests & Pandas** to fetch live BTC prices and calculate moving averages."},
    "sql": {"title": "E-Commerce Schema (3NF)", "task": "Design a normalized DB for an Amazon clone. Write a query to find 'Top 3 Spenders' using **JOINs**."},
    "aws": {"title": "Serverless API", "task": "Deploy a 'Hello World' function on **AWS Lambda** triggered by API Gateway."},
    "docker": {"title": "Microservice Dockerfile", "task": "Write a multi-stage **Dockerfile** for a Python app to reduce image size by 40%."},
    "git": {"title": "Simulate Merge Conflict", "task": "Create two branches, edit the same line in both, and resolve the conflict using **Git CLI**."},
    "redux": {"title": "Shopping Cart State", "task": "Implement a global Shopping Cart using **Redux**, handling add/remove actions."},
    "java": {"title": "Library Management System", "task": "Build a console-based app using **OOP Principles** (Inheritance, Polymorphism) to manage book inventory."}
}

# DYNAMIC INTERVIEW QUESTIONS (Fixed: Deep Technical Dives)
INTERVIEW_Q = {
    "react": "Recruiter: I see you built a Trello Clone. How did you optimize rendering to prevent lag when dragging items? Did you use `React.memo`?",
    "spring boot": "Recruiter: You mentioned using Spring Boot. How did you handle **Dependency Injection** for your Service and Repository layers? Why use Constructor Injection over Field Injection?",
    "typescript": "Recruiter: You migrated to TypeScript. What specific bugs did strict typing catch that you missed in JS? How did you handle `any` types?",
    "figma": "Recruiter: Walk me through your Dark Mode system. How did you handle color tokens for accessibility to ensure sufficient contrast?",
    "python": "Recruiter: In your Crypto Tracker, how would you handle a sudden API rate limit error without crashing the script?",
    "sql": "Recruiter: Why did you choose 3rd Normal Form? When would you intentionally denormalize this data for read performance?",
    "aws": "Recruiter: Since you used **AWS Lambda**, how did you manage **Cold Starts**, and why did you choose API Gateway over a Load Balancer?",
    "docker": "Recruiter: You reduced image size by 40%. Did you use **Alpine Linux** images? What were the security trade-offs of that decision?",
    "git": "Recruiter: Explain a situation where you chose 'Git Rebase' over 'Git Merge'. How did you handle the history rewrite safety?",
    "java": "Recruiter: In your Library System, how did you handle concurrent borrowing? Did you use the `synchronized` keyword or `ConcurrentHashMap`?"
}

# RESUME BULLETS (The "Reward")
RESUME_BULLETS = {
    "react": "• Architected a Trello-style Kanban board using **React**, utilizing **Redux** for state management of 50+ tasks.",
    "spring boot": "• Developed a scalable **RESTful API** for a Bookstore using **Spring Boot**, implementing **H2** persistence and custom error handling.",
    "typescript": "• Refactored a legacy codebase to **TypeScript**, reducing runtime type errors by 90% through strict typing.",
    "figma": "• Designed a scalable Dark Mode UI System in **Figma**, utilizing Auto-Layout and Variants to speed up dev handoff.",
    "python": "• Developed a financial data pipeline using **Python (Pandas)**, automating real-time crypto analysis.",
    "aws": "• Deployed a serverless architecture on **AWS Lambda**, optimizing API Gateway triggers for <100ms latency.",
    "docker": "• Optimized container orchestration using multi-stage **Dockerfiles**, reducing production image size by 40%."
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
    if not j_skills: return 0, 0, 15 # Floor context score at 15
    
    # Keyword Score
    k_score = int((len(r_skills.intersection(j_skills)) / len(j_skills)) * 100)
    
    # Context Score
    tfidf = TfidfVectorizer(stop_words='english')
    try:
        matrix = tfidf.fit_transform([resume_text, jd_text])
        raw_c_score = int(cosine_similarity(matrix[0:1], matrix[1:2])[0][0] * 100)
    except:
        raw_c_score = 0
        
    # LOGIC FIX: Floor the Context Score at 15% (Psychological Safety)
    c_score = max(raw_c_score, 15)
        
    final = int((k_score * 0.6) + (c_score * 0.4))
    return final, k_score, c_score

# ---------------- 4. MAIN APP ----------------

def main():
    # --- SESSION STATE ---
    if 'analyzed' not in st.session_state:
        st.session_state['analyzed'] = False
        st.session_state['completed_projects'] = set()
        st.session_state['readiness_score'] = 25 # Start with some hope
        
    # --- SIDEBAR ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=50)
        st.title("CareerCraft AI")
        st.caption("Platinum Edition v5.0")
        
        uploaded_file = st.file_uploader("1. Upload Resume", type=["pdf", "docx"])
        
        target_mode = st.radio("2. Target Job", ["Paste JD (Recommended)", "Preset Role"])
        jd_text = ""
        role_title = "General"

        if target_mode == "Paste JD (Recommended)":
            role_title = st.text_input("Job Title", "Senior Software Engineer")
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
                st.session_state['readiness_score'] = 25
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

        # 1. HERO & GAMIFICATION
        st.title(f"🔍 Analysis: {st.session_state['role_title']}")
        
        # Gamified Progress Bar
        st.caption("🎓 Interview Readiness Level")
        st.progress(st.session_state['readiness_score'] / 100)
        st.markdown(f"**Level: {st.session_state['readiness_score']}%** (Build projects to level up!)")

        # 2. X-RAY METRICS
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Overall Match", f"{final}%", f"{final-60}% vs Market")
        with c2:
            st.metric("Keyword Match", f"{k_score}%")
            if missing:
                st.caption("❌ **CRITICAL MISSING:**")
                tags_html = "".join([f"<span class='missing-tag'>{s}</span>" for s in list(missing)[:6]])
                st.markdown(tags_html, unsafe_allow_html=True)
            else:
                st.success("✅ No Keywords Missing!")
        with c3:
            st.metric("Context Score", f"{c_score}%")
            # PEEK-A-BOO REWRITE (With CSS Text Wrap Fix)
            with st.expander("✨ Peek at Magic Rewrite"):
                st.info(f"**Instead of:** 'Used {list(matched)[0] if matched else 'Java'}'")
                st.success(f"**Write this:** 'Leveraged **{list(matched)[0] if matched else 'Java'}** to architect scalable solutions, improving system latency by 30%.'")

        st.markdown("---")

        # 3. MICRO-PROJECT BLUEPRINTS (Fixed: No Lazy AI)
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
                    # Specific Blueprints only
                    bp = PROJECT_BLUEPRINTS.get(skill, {"title": f"{skill.title()} Project", "task": f"Build a practical application demonstrating {skill}."})
                    
                    with st.container():
                        st.markdown(f"""
                        <div class="project-card">
                            <h4 style="margin:0;">{bp['title']}</h4>
                            <p style="font-size:14px; color:#555;">{bp['task']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # "I BUILT IT" LOOP
                        btn_label = "✅ I Built It! (Unlock Rewards)"
                        if skill in st.session_state['completed_projects']:
                            btn_label = "🎉 Completed!"
                        
                        if st.button(btn_label, key=f"btn_{skill}", disabled=(skill in st.session_state['completed_projects'])):
                            st.session_state['completed_projects'].add(skill)
                            st.session_state['readiness_score'] += 15
                            st.rerun()

                        if skill in st.session_state['completed_projects']:
                            bullet = RESUME_BULLETS.get(skill, f"• Implemented **{skill.title()}** to optimize workflows.")
                            st.markdown(f"**Resume Bullet:**")
                            st.code(bullet, language="markdown")
                            st.toast(f"Level Up! {skill.title()} Interview Question Unlocked!", icon="🔓")
            else:
                st.success("You have the perfect stack! Go to the Grill.")

        st.markdown("---")

        # 4. THE DYNAMIC INTERVIEW GRILL (Fixed: Specific Questions)
        st.subheader("🔥 The Interview Grill")
        
        tab1, tab2 = st.tabs(["🔥 Hot Seat (Dynamic)", "📄 Cover Letter"])

        with tab1:
            st.caption("Questions appear here as you unlock skills.")
            
            if matched:
                st.markdown("**Based on your current resume:**")
                for s in list(matched)[:2]:
                     q = INTERVIEW_Q.get(s, f"Tell me about your experience with {s}.")
                     st.info(f"**{s.title()}:** {q}")

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
