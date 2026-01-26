import streamlit as st
import time
import pdfplumber
import docx
import pandas as pd
import plotly.graph_objects as go
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import random
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# ---------------- 1. PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="CareerCraft AI - Recruiter Pro",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 5rem; }
    h1, h2, h3 { font-family: 'Inter', sans-serif; color: #0f172a; }
    .stButton>button { 
        border-radius: 8px; font-weight: 600; border: none; 
        padding: 0.6rem 1.2rem; transition: all 0.2s ease;
        background-color: #3b82f6; color: white;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3); }
    .project-card { 
        background-color: #f8fafc; padding: 20px; border-radius: 12px; 
        margin-bottom: 15px; border-left: 5px solid #3b82f6; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .salary-badge {
        background-color: #dcfce7; color: #166534; padding: 2px 6px; 
        border-radius: 4px; font-size: 0.8em; font-weight: bold; border: 1px solid #166534; margin-left: 5px;
    }
    .missing-tag {
        background-color: #fee2e2; color: #991b1b; padding: 4px 10px; 
        border-radius: 6px; font-size: 0.9em; font-weight: 600; 
        margin-right: 8px; display: inline-block; margin-bottom: 8px;
        border: 1px solid #fecaca;
    }
    .ats-badge-green { background-color: #dcfce7; color: #15803d; padding: 5px 10px; border-radius: 5px; font-weight: bold; border: 1px solid #15803d; }
    .ats-badge-red { background-color: #fee2e2; color: #b91c1c; padding: 5px 10px; border-radius: 5px; font-weight: bold; border: 1px solid #b91c1c; }
    .ats-badge-yellow { background-color: #fef9c3; color: #a16207; padding: 5px 10px; border-radius: 5px; font-weight: bold; border: 1px solid #a16207; }
    
    .feedback-box-weak { border-left: 5px solid #ef4444; background: #fef2f2; padding: 15px; border-radius: 5px; }
    .feedback-box-strong { border-left: 5px solid #22c55e; background: #f0fdf4; padding: 15px; border-radius: 5px; }
    .streamlit-expanderContent div { word-wrap: break-word; white-space: normal; line-height: 1.6; }
    /* Dynamic Progress Bar CSS */
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #4CAF50, #8BC34A); }
    </style>
    """, unsafe_allow_html=True)

# ---------------- 2. INTELLIGENT DATABASES ----------------

SKILL_DB = {
    "Frontend": ["javascript", "react", "angular", "vue", "html", "css", "tailwind", "redux", "typescript", "figma", "jest", "next.js"],
    "Backend": ["python", "django", "flask", "node.js", "express", "java", "spring boot", "go", "c#", ".net"],
    "Database": ["sql", "mysql", "postgresql", "mongodb", "redis", "firebase", "elasticsearch"],
    "DevOps": ["aws", "docker", "kubernetes", "jenkins", "git", "ci/cd", "linux", "terraform", "azure"],
    "Data": ["pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "tableau", "power bi", "excel", "spark"],
    "Soft Skills": ["communication", "teamwork", "leadership", "problem solving", "adaptability", "time management", "creativity", "collaboration", "mentoring", "agile"]
}

PROJECT_BLUEPRINTS = {
    "react": {"title": "Trello Clone (Kanban)", "task": "Build a Drag-and-Drop Task Board using **React DnD** and **Redux Toolkit**.", "salary": "₹4 LPA"},
    "next.js": {"title": "SSR Blog Platform", "task": "Build a Server-Side Rendered (SSR) Blog using **getStaticProps** to optimize SEO performance.", "salary": "₹5 LPA"},
    "jest": {"title": "Login Unit Tests", "task": "Write a Unit Test Suite for a Login Form that validates email formats and mocks the API response.", "salary": "₹3 LPA"},
    "spring boot": {"title": "Bookstore REST API", "task": "Build a comprehensive API with CRUD operations, connecting to a local **H2 Database** and handling exceptions.", "salary": "₹6 LPA"},
    "typescript": {"title": "Strictly Typed Calculator", "task": "Convert a JS Calculator to **TypeScript**, enforcing strict types on all event handlers.", "salary": "₹3 LPA"},
    "figma": {"title": "Dark Mode Dashboard UI", "task": "Design a 'Login & Dashboard' UI kit (Dark Mode) demonstrating **Component Variants** and **Auto-Layout**.", "salary": "₹2 LPA"},
    "python": {"title": "Crypto Price Tracker", "task": "Build a script using **Requests & Pandas** to fetch live BTC prices and calculate moving averages.", "salary": "₹4 LPA"},
    "sql": {"title": "E-Commerce Schema (3NF)", "task": "Design a normalized DB for an Amazon clone. Write a query to find 'Top 3 Spenders' using **JOINs**.", "salary": "₹3 LPA"},
    "aws": {"title": "Serverless API", "task": "Deploy a 'Hello World' function on **AWS Lambda** triggered by API Gateway.", "salary": "₹7 LPA"},
    "docker": {"title": "Microservice Dockerfile", "task": "Write a multi-stage **Dockerfile** for a Python app to reduce image size by 40%.", "salary": "₹5 LPA"},
    "git": {"title": "Simulate Merge Conflict", "task": "Create two branches, edit the same line in both, and resolve the conflict using **Git CLI**.", "salary": "₹2 LPA"},
    "redux": {"title": "Shopping Cart State", "task": "Implement a global Shopping Cart using **Redux**, handling add/remove actions.", "salary": "₹4 LPA"},
    "html": {"title": "Accessible Landing Page", "task": "Refactor a `div`-heavy page into **Semantic HTML** (<nav>, <article>, <main>) to score 100 on Lighthouse.", "salary": "₹1 LPA"}
}

INTERVIEW_Q = {
    "react": "Recruiter: I see you built a Trello Clone. How did you optimize rendering to prevent lag when dragging items? Did you use `React.memo`?",
    "next.js": "Recruiter: Explain the trade-off between **SSR (Server-Side Rendering)** and **ISR (Incremental Static Regeneration)** in your blog.",
    "jest": "Recruiter: How did you calculate **Code Coverage**? Did you focus on statement coverage or branch coverage?",
    "spring boot": "Recruiter: How did you handle **Dependency Injection** for your Service and Repository layers? Why use Constructor Injection?",
    "typescript": "Recruiter: What specific bugs did strict typing catch that you missed in JS? How did you handle `any` types?",
    "figma": "Recruiter: Walk me through your Dark Mode system. How did you handle color tokens for accessibility?",
    "python": "Recruiter: In your Crypto Tracker, how would you handle a sudden API rate limit error without crashing the script?",
    "sql": "Recruiter: Why did you choose 3rd Normal Form? When would you intentionally denormalize this data for read performance?",
    "aws": "Recruiter: Since you used **AWS Lambda**, how did you manage **Cold Starts**, and why did you choose API Gateway over a Load Balancer?",
    "docker": "Recruiter: You reduced image size by 40%. Did you use **Alpine Linux** images? What were the security trade-offs of that decision?",
    "git": "Recruiter: Explain a situation where you chose 'Git Rebase' over 'Git Merge'. How did you handle the history rewrite safety?",
    "html": "Recruiter: Explain the importance of **Semantic HTML** (like `<article>` vs `<div>`) for accessibility."
}

RESUME_BULLETS = {
    "react": "Architected a Trello-style Kanban board using React, utilizing Redux for state management of 50+ tasks.",
    "next.js": "Engineered a Server-Side Rendered (SSR) blog using Next.js, improving SEO indexing and FCP by 40%.",
    "jest": "Implemented Unit Testing suites using Jest, achieving 100% code coverage for critical authentication modules.",
    "spring boot": "Developed a scalable RESTful API for a Bookstore using Spring Boot, implementing H2 persistence and custom error handling.",
    "typescript": "Refactored a legacy codebase to TypeScript, reducing runtime type errors by 90% through strict typing.",
    "figma": "Designed a scalable Dark Mode UI System in Figma, utilizing Auto-Layout and Variants to speed up dev handoff.",
    "python": "Developed a financial data pipeline using Python (Pandas), automating real-time crypto analysis.",
    "aws": "Deployed a serverless architecture on AWS Lambda, optimizing API Gateway triggers for <100ms latency.",
    "docker": "Optimized container orchestration using multi-stage Dockerfiles, reducing production image size by 40%."
}

# --- DYNAMIC REWRITE DATABASE (FIX 3) ---
MAGIC_REWRITES = {
    "react": "Architected a responsive UI using React, improving user retention metrics by 15% through optimized load times.",
    "python": "Engineered automated data pipelines in Python, reducing manual processing time by 30%.",
    "sql": "Optimized complex SQL queries to handle 1M+ rows, resulting in 2x faster database response times.",
    "aws": "Deployed scalable cloud infrastructure on AWS, ensuring 99.9% uptime for high-traffic applications.",
    "docker": "Containerized microservices using Docker, standardizing the CI/CD pipeline and reducing deployment failures."
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
    if not j_skills: return 0, 0, 15 
    k_score = int((len(r_skills.intersection(j_skills)) / len(j_skills)) * 100)
    tfidf = TfidfVectorizer(stop_words='english')
    try:
        matrix = tfidf.fit_transform([resume_text, jd_text])
        raw_c_score = int(cosine_similarity(matrix[0:1], matrix[1:2])[0][0] * 100)
    except: raw_c_score = 0
    c_score = max(raw_c_score, 15)
    final = int((k_score * 0.6) + (c_score * 0.4))
    return final, k_score, c_score

def analyze_communication_style(resume_text):
    # Detects passive vs active voice indicators
    power_words = ["architected", "developed", "led", "optimized", "engineered", "designed", "implemented", "reduced", "increased"]
    weak_words = ["worked on", "helped", "used", "responsible for", "participated"]
    
    score = 50
    text_lower = resume_text.lower()
    
    found_power = [w for w in power_words if w in text_lower]
    found_weak = [w for w in weak_words if w in text_lower]
    
    score += (len(found_power) * 5)
    score -= (len(found_weak) * 5)
    
    if score >= 80: return "🔥 High Impact (Leader)"
    elif score >= 50: return "✅ Professional (Doer)"
    else: return "⚠️ Passive (Task-based)"

def get_candidate_archetype(r_skills):
    # Determines the 'Persona' based on skill clusters
    fe_count = len(r_skills.intersection(set(SKILL_DB["Frontend"])))
    be_count = len(r_skills.intersection(set(SKILL_DB["Backend"])))
    ds_count = len(r_skills.intersection(set(SKILL_DB["Data"])))
    
    if fe_count > be_count and fe_count > ds_count: return "🎨 Frontend Specialist"
    elif be_count > fe_count and be_count > ds_count: return "⚙️ Backend Architect"
    elif ds_count > fe_count: return "📊 Data Scientist"
    elif fe_count > 0 and be_count > 0: return "🦄 Full Stack Developer"
    else: return "🌱 Generalist / Fresher"

# --- FIXED DYNAMIC ANALYZER (FIX 2) ---
def analyze_answer(answer, target_skill):
    impact_words = ["optimized", "architected", "integrated", "solved", "built", "reduced", "improved"]
    word_count = len(answer.split())
    
    if word_count < 15:
        return "⚠️ Weak Answer", "Too short! Use the STAR method to describe a specific challenge.", "weak"
    
    impact_score = sum(1 for word in impact_words if word in answer.lower())
    skill_mentioned = target_skill.lower() in answer.lower()
    
    if impact_score >= 1 and skill_mentioned:
        return "✅ Strong Answer", "Great use of high-impact action verbs! You sound like a real engineer.", "strong"
    elif skill_mentioned:
        return "⚠️ Needs Improvement", f"You mentioned {target_skill}, but try to use action verbs like 'Optimized' or 'Architected' to show impact.", "weak"
    else:
        return "🛑 Critical Flaw", f"You missed the mark. You didn't even mention the core skill ({target_skill})! Try again.", "weak"

def generate_cheat_sheet(name, role, skills, bullets):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, f"Interview Cheat Sheet: {name}")
    c.setFont("Helvetica", 12)
    c.drawString(50, 730, f"Target Role: {role}")
    c.line(50, 720, 550, 720)
    y = 690
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "1. My Power Hooks")
    y -= 20
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"• \"I specialize in {', '.join(list(skills)[:2])} to build scalable apps.\"")
    y -= 20
    c.drawString(50, y, "• \"I focus on performance optimization and clean architecture.\"")
    y -= 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "2. Project Stories (STAR Method)")
    y -= 25
    c.setFont("Helvetica", 10)
    for skill, bullet in list(bullets.items())[:5]:
        text = bullet.replace("**", "")
        c.drawString(50, y, f"[{skill.upper()}]")
        y -= 15
        c.drawString(60, y, text[:90] + "...") 
        y -= 20
    y -= 20
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "3. Tech Keywords to Drop")
    y -= 25
    c.setFont("Helvetica-Oblique", 12)
    keywords = ["Scalability", "CI/CD Pipeline", "Latency Reduction", "State Management", "Unit Testing"]
    c.drawString(50, y, ", ".join(keywords))
    c.save()
    buffer.seek(0)
    return buffer

def create_soft_skills_chart(resume_text):
    soft_skills = ["communication", "teamwork", "leadership", "problem solving", "adaptability", "creativity"]
    scores = []
    resume_text_lower = resume_text.lower()
    for skill in soft_skills:
        count = resume_text_lower.count(skill)
        if count > 0: scores.append(min(count + 2, 5))
        else: scores.append(1)
            
    fig = go.Figure(data=go.Scatterpolar(
        r=scores, theta=[s.title() for s in soft_skills],
        fill='toself', name='Soft Skills', line_color='#2563eb'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=False, title="🧠 Soft Skills Profile",
        height=300, margin=dict(t=40, b=20, l=40, r=40)
    )
    return fig

# ---------------- 4. MAIN APP ----------------

def main():
    if 'analyzed' not in st.session_state:
        st.session_state['analyzed'] = False
        st.session_state['completed_projects'] = set()
        st.session_state['readiness_score'] = 0 # Fixed: No longer starts at 25
        
    # --- SIDEBAR (MOBILE FRIENDLY) ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=50)
        st.title("CareerCraft AI")
        st.caption("Recruiter Edition v14.0 (Diamond)")
        
        st.markdown("### 1. Resume Input")
        upload_mode = st.radio("Input Method", ["Upload File", "Paste Text"], horizontal=True, label_visibility="collapsed")
        
        resume_text_content = ""
        uploaded_file = None

        if upload_mode == "Upload File":
            uploaded_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
            if uploaded_file: resume_text_content = extract_text(uploaded_file)
        else:
            resume_text_content = st.text_area("Paste Resume Text Here", height=200, placeholder="Copy-paste your full resume text here...")

        st.markdown("### 2. Target Job")
        target_mode = st.radio("Target Method", ["Paste JD (Recommended)", "Preset Role"], horizontal=True, label_visibility="collapsed")
        jd_text = ""
        role_title = "General"

        if target_mode == "Paste JD (Recommended)":
            role_title = st.text_input("Job Title", "Full Stack Engineer")
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
            if resume_text_content and jd_text:
                # --- AI THEATRICS ---
                progress_text = "Initializing AI Agent..."
                my_bar = st.progress(0, text=progress_text)
                
                time.sleep(0.3)
                my_bar.progress(25, text="📄 Parsing Resume Text Layers...")
                time.sleep(0.3)
                my_bar.progress(50, text="🧮 Vectorizing Text (TF-IDF)...")
                time.sleep(0.3)
                my_bar.progress(75, text="🔍 Calculating Cosine Similarity...")
                time.sleep(0.3)
                my_bar.progress(90, text="📊 Generating Gap Analysis...")

                # Recalculate everything upfront to FIX Progress Bar
                r_skills = extract_skills(resume_text_content)
                j_skills = extract_skills(jd_text.lower())
                final_score, k_s, c_s = calculate_metrics(resume_text_content, jd_text, r_skills, j_skills)

                st.session_state['analyzed'] = True
                st.session_state['resume_text'] = resume_text_content
                st.session_state['jd_text'] = jd_text
                st.session_state['role_title'] = role_title
                st.session_state['readiness_score'] = final_score # FIX: Set to REAL final score
                st.session_state['completed_projects'] = set()
                
                my_bar.progress(100, text="✅ Analysis Complete!")
                time.sleep(0.5)
                my_bar.empty()
                st.rerun()
            else:
                st.toast("⚠️ Please provide Resume text and Job Description!", icon="🚨")

    # --- MAIN DASHBOARD ---
    if st.session_state['analyzed']:
        r_text = st.session_state['resume_text']
        j_text = st.session_state['jd_text']
        r_skills = extract_skills(r_text)
        j_skills = extract_skills(j_text.lower())
        matched = r_skills.intersection(j_skills)
        missing = j_skills.difference(r_skills)
        final, k_score, c_score = calculate_metrics(r_text, j_text, r_skills, j_skills)
        
        # New Analysis Functions
        archetype = get_candidate_archetype(r_skills)
        comm_style = analyze_communication_style(r_text)

        # HERO
        st.title(f"🔍 Analysis: {st.session_state['role_title']}")
        
        col_bar, col_export = st.columns([3, 1])
        with col_bar:
            st.caption("🎓 Interview Readiness Level (Based on Match Score)")
            # FIX 1: Dynamic Progress Bar based on actual score
            st.progress(st.session_state['readiness_score'] / 100)
            st.markdown(f"**Level: {st.session_state['readiness_score']}%** (Build projects to level up!)")
        with col_export:
            pdf_bytes = generate_cheat_sheet("Candidate", st.session_state['role_title'], matched, RESUME_BULLETS)
            st.download_button("📄 Interview Cheat Sheet", data=pdf_bytes, file_name="Interview_Cheat_Sheet.pdf", mime="application/pdf")

        # METRICS
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Overall Match", f"{final}%", f"{final-60}% vs Market")
        with c2:
            st.metric("Keyword Match", f"{k_score}%")
            if missing:
                st.caption("❌ **CRITICAL MISSING:**")
                tags_html = " ".join([f"<span class='missing-tag'>{s}</span>" for s in list(missing)[:6]])
                st.markdown(tags_html, unsafe_allow_html=True)
            else:
                st.success("✅ No Keywords Missing!")
        with c3:
            st.metric("Context Score", f"{c_score}%")
            with st.expander("✨ Peek at Magic Rewrite"):
                # FIX 3: Dynamic Rewrite logic
                target_skill = list(matched)[0] if matched else "python"
                custom_rewrite = MAGIC_REWRITES.get(target_skill, f"Leveraged {target_skill.title()} to architect scalable solutions, improving system latency by 30%.")
                st.info(f"**Instead of:** 'Used {target_skill.title()}'")
                st.success(f"**Write this:** '{custom_rewrite}'")

        # --- SOFT SKILLS & LINKEDIN ---
        st.markdown("---")
        col_chart, col_linkedin = st.columns([1, 1])
        with col_chart:
            chart = create_soft_skills_chart(r_text)
            st.plotly_chart(chart, use_container_width=True)
        with col_linkedin:
            st.subheader("🔗 LinkedIn Makeover")
            st.caption("Copy this to your LinkedIn Headline for better visibility.")
            top_skills = list(matched)[:3] if matched else ["Tech"]
            headline = f"🚀 Aspiring {st.session_state['role_title']} | Proficient in {', '.join([s.title() for s in top_skills])} | Solving complex problems with Code"
            st.code(headline, language="text")
            st.info("💡 **Pro Tip:** Adding a 'Project Portfolio' link to your bio increases recruiter clicks by 40%.")

        st.markdown("---")

        # BLUEPRINTS
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
                    bp = PROJECT_BLUEPRINTS.get(skill, {"title": f"{skill.title()} Project", "task": f"Build a practical application demonstrating {skill}.", "salary": "₹2 LPA"})
                    
                    with st.container():
                        st.markdown(f"""
                        <div class="project-card">
                            <h4 style="margin:0;">{bp['title']} <span class="salary-badge">+{bp.get('salary')}</span></h4>
                            <p style="font-size:14px; color:#555;">{bp['task']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
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

        # TABBED SECTIONS (Diamond Tier Tabs Maintained)
        st.subheader("🚀 Career Assets")
        tab1, tab2, tab3, tab4 = st.tabs(["🔥 Hot Seat", "📄 Cover Letter", "⚖️ Recruiter View", "📝 Full Resume Draft"])

        # TAB 1: INTERVIEW SIMULATOR
        with tab1:
            st.caption("Questions appear here as you unlock skills.")
            active_question = None
            active_skill = None # Track skill for Answer Analyzer
            
            if matched:
                st.markdown("### 🎯 Questions based on your CURRENT skills:")
                for s in list(matched)[:5]: # Show top 5 matched skill questions
                     q = INTERVIEW_Q.get(s, f"Tell me about your experience with {s}.")
                     st.info(f"**{s.title()}:** {q}")
                     active_question = q
                     active_skill = s
                     
            if st.session_state['completed_projects']:
                st.markdown("### 🔓 UNLOCKED Questions (New Skills):")
                for s in st.session_state['completed_projects']:
                    q = INTERVIEW_Q.get(s, f"How did you implement {s}?")
                    st.success(f"**{s.title()} (Unlocked):** {q}")
                    active_question = q 
                    active_skill = s
                    
            if active_question and active_skill:
                st.markdown("---")
                st.markdown("🎙️ **Practice Your Answer:**")
                user_ans = st.text_area("Type your answer here to get AI feedback...", height=100)
                if st.button("Analyze My Answer"):
                    if user_ans:
                        # FIX 2: Pass the specific skill to the analyzer
                        verdict, text, style = analyze_answer(user_ans, active_skill)
                        st.markdown(f"<div class='feedback-box-{style}'><b>{verdict}</b><br>{text}</div>", unsafe_allow_html=True)
                    else:
                        st.warning("Please type an answer first.")

        # TAB 2: COVER LETTER
        with tab2:
            tone = "I am a rapid learner actively closing technical gaps." if final < 70 else "I am ready to deliver value immediately."
            cl_text = f"Dear Hiring Manager,\n\nI am applying for the {st.session_state['role_title']} role. {tone}\n\nMy analysis shows strong foundations in {', '.join(list(matched)[:3])}. I am currently building projects in {', '.join(list(missing)[:2])} to ensure I am day-one ready.\n\nSincerely,\nCandidate"
            st.text_area("Cover Letter Draft", cl_text, height=300)

        # TAB 3: RECRUITER VIEW (ADVANCED DASHBOARD)
        with tab3:
            st.markdown("### 👓 Recruiter Risk Assessment Dashboard")
            st.caption("This is the 'Secret View' hiring managers see.")
            
            # 1. ATS STATUS BANNER
            if final >= 80:
                st.markdown(f"<div class='ats-badge-green'>✅ VERDICT: SHORTLIST (Top 10%)</div>", unsafe_allow_html=True)
            elif final >= 50:
                 st.markdown(f"<div class='ats-badge-yellow'>⚠️ VERDICT: ON HOLD (Potential Fit)</div>", unsafe_allow_html=True)
            else:
                 st.markdown(f"<div class='ats-badge-red'>🛑 VERDICT: REJECT (Critical Gaps)</div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 2. CANDIDATE PERSONA & STYLE
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                st.info(f"**Candidate Archetype:** {archetype}")
                st.caption("Based on skill cluster analysis (Frontend vs Backend vs Data).")
            with c_p2:
                st.info(f"**Communication Style:** {comm_style}")
                st.caption("Based on 'Power Word' frequency in resume text.")

            # 3. DETAILED RISK GRID
            st.markdown("#### 🎯 Hiring Decision Matrix")
            c_green, c_red = st.columns(2)
            
            with c_green:
                st.markdown("**✅ STRENGTHS (Green Flags)**")
                if matched:
                    for s in list(matched):
                        st.success(f"**{s.title()}**: Validated")
                else:
                    st.warning("No core strengths identified.")
            
            with c_red:
                st.markdown("**🚩 RISKS (Red Flags)**")
                if missing:
                    for s in list(missing)[:5]:
                        risk_level = "HIGH" if s in ["react", "node.js", "python", "sql"] else "MED"
                        st.error(f"**{s.title()}**: Missing ({risk_level} Risk)")
                else:
                    st.success("No critical red flags found.")
            
            # 4. TRAP QUESTIONS FOR RECRUITER
            st.markdown("---")
            st.markdown("#### 🕵️‍♂️ Recommended 'Trap' Questions for Interviewer")
            st.caption("Ask these to verify the candidate isn't bluffing.")
            if missing:
                trap_skill = list(missing)[0]
                st.markdown(f"- *'I see you don't have **{trap_skill.title()}** on your resume. How would you handle a task that requires it?'*")
            if matched:
                verify_skill = list(matched)[0]
                st.markdown(f"- *'Walk me through a specific bug you fixed using **{verify_skill.title()}**.'*")

        # TAB 4: FULL PROFESSIONAL RESUME GENERATOR
        with tab4:
            st.markdown("### 📝 Professional Resume Draft")
            st.caption("Formatted for Applicant Tracking Systems (ATS). Copy-paste into your editor.")
            
            resume_draft = f"""
# YOUR NAME
[City, State] | [Phone Number] | [Email Address] | [LinkedIn Profile URL]

## PROFESSIONAL SUMMARY
Results-oriented **{st.session_state['role_title']}** with a strong technical foundation in **{', '.join([s.title() for s in list(matched)[:3]])}**. Proven ability to architect scalable applications and optimize system performance. Dedicated to continuous learning, currently expanding expertise in **{', '.join([s.title() for s in list(missing)[:2]])}** through practical project implementation.

## TECHNICAL SKILLS
* **Core Competencies:** {', '.join([s.title() for s in matched])}
* **Emerging Tech:** {', '.join([s.title() for s in list(missing)[:3]])}
* **Tools & Platforms:** Git, VS Code, JIRA, Postman

## PROFESSIONAL EXPERIENCE
**[Job Title]** | [Company Name] | [Dates]
* Leveraged **{list(matched)[0] if matched else 'Java'}** to improve application performance, resulting in a 15% reduction in latency.
* Collaborated with cross-functional teams to design and deploy features using **{list(matched)[1] if len(matched)>1 else 'SQL'}**.
* (Placeholder: Add your specific work achievements here, quantifying results where possible).

## PROJECT PORTFOLIO
"""
            if st.session_state['completed_projects']:
                for s in st.session_state['completed_projects']:
                    bullet = RESUME_BULLETS.get(s, f"Implemented {s} project.")
                    resume_draft += f"**{PROJECT_BLUEPRINTS[s]['title']}** | *Stack: {s.title()}*\n"
                    resume_draft += f"* {bullet}\n\n"
            
            for s in list(matched)[:2]:
                resume_draft += f"**{s.title()} Implementation** | *Stack: {s.title()}*\n"
                resume_draft += f"* Designed and developed a solution using **{s.title()}** to solve key business challenges.\n\n"

            resume_draft += """
## EDUCATION
**Bachelor of Technology in Computer Science**
[University Name], [Graduation Year]
* Relevant Coursework: Data Structures, Algorithms, Database Management Systems.

## CERTIFICATIONS
* Full Stack Web Development Bootcamp
* [Add other certifications here]
"""
            st.text_area("Full Resume Text", resume_draft, height=600)

    elif not st.session_state['analyzed']:
        st.info("👈 Open Sidebar to Paste Resume or Upload File.")

if __name__ == "__main__":
    main()
