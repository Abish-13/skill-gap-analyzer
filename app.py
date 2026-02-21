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
    page_title="CareerCraft AI | Premium Recruiter Pro",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Premium CSS with Glassmorphism and Modern Typography
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="View"] {
        font-family: 'Inter', sans-serif;
        background-color: #020617;
        color: #f8fafc;
    }

    .stApp {
        background: radial-gradient(circle at top right, #1e1b4b, #020617);
    }

    /* Glassmorphism Containers */
    .glass-card {
        background: rgba(30, 41, 59, 0.5);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 2.5rem;
        border-radius: 24px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        margin-bottom: 2rem;
    }

    h1 { font-weight: 800 !important; letter-spacing: -0.05em !important; color: #f8fafc !important; }
    h2, h3 { color: #e2e8f0 !important; font-weight: 600 !important; }

    /* Premium Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        border: none;
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px -5px rgba(59, 130, 246, 0.5);
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
    }

    /* Badges & Tags */
    .salary-badge {
        background: rgba(34, 197, 94, 0.2);
        color: #4ade80;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        border: 1px solid rgba(74, 222, 128, 0.3);
    }

    .missing-tag {
        background: rgba(239, 68, 68, 0.1);
        color: #f87171;
        padding: 6px 14px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid rgba(248, 113, 113, 0.2);
        margin: 4px;
        display: inline-block;
    }

    /* ATS Metrics */
    .metric-container {
        text-align: center;
        padding: 1.5rem;
        background: rgba(15, 23, 42, 0.4);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Feedback Boxes */
    .feedback-box-weak { border-left: 4px solid #ef4444; background: rgba(239, 68, 68, 0.05); padding: 1.5rem; border-radius: 12px; }
    .feedback-box-strong { border-left: 4px solid #10b981; background: rgba(16, 185, 129, 0.05); padding: 1.5rem; border-radius: 12px; }

    /* Smooth Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        height: 8px;
        border-radius: 10px;
    }
    
    /* Hide specific streamlit elements for cleaner UI */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ---------------- 2. INTELLIGENT DATABASES ----------------
# (Database kept identical to maintain core logic)
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
    "spring boot": {"title": "Bookstore REST API", "task": "Build a comprehensive API with CRUD operations, connecting to a local **H2 Database**.", "salary": "₹6 LPA"},
    "typescript": {"title": "Strictly Typed Calculator", "task": "Convert a JS Calculator to **TypeScript**, enforcing strict types on all event handlers.", "salary": "₹3 LPA"},
    "figma": {"title": "Dark Mode Dashboard UI", "task": "Design a 'Login & Dashboard' UI kit (Dark Mode) demonstrating **Component Variants**.", "salary": "₹2 LPA"},
    "python": {"title": "Crypto Price Tracker", "task": "Build a script using **Requests & Pandas** to fetch live BTC prices.", "salary": "₹4 LPA"},
    "sql": {"title": "E-Commerce Schema (3NF)", "task": "Design a normalized DB for an Amazon clone. Write queries using **JOINs**.", "salary": "₹3 LPA"},
    "aws": {"title": "Serverless API", "task": "Deploy a 'Hello World' function on **AWS Lambda** triggered by API Gateway.", "salary": "₹7 LPA"},
    "docker": {"title": "Microservice Dockerfile", "task": "Write a multi-stage **Dockerfile** for a Python app to reduce image size by 40%.", "salary": "₹5 LPA"},
    "git": {"title": "Simulate Merge Conflict", "task": "Create two branches and resolve the conflict using **Git CLI**.", "salary": "₹2 LPA"},
    "java": {"title": "Multithreaded Chat Server", "task": "Build a basic real-time chat room using Java Sockets and Multithreading.", "salary": "₹5 LPA"}
}

INTERVIEW_Q = {
    "javascript": "Recruiter: Explain a scenario where you had to fix a memory leak in a Single Page Application using JavaScript. How did you use the DevTools heap snapshot?",
    "css": "Recruiter: CSS Grid vs Flexbox. Walk me through a complex layout problem you solved where one was superior to the other. Did you consider browser reflow?",
    "html": "Recruiter: In a recent project, how did you ensure your HTML was fully accessible (WCAG compliant)? Which ARIA attributes did you implement and why?",
    "jest": "Recruiter: Testing async code can be tricky. How did you mock an API response in Jest to test a failure state (like a 500 Server Error)?",
    "react": "Recruiter: Tell me about a time you optimized a React app's performance. Did you use useMemo/useCallback, and how did you measure the render time reduction?",
    "python": "Recruiter: How did you handle Global Interpreter Lock (GIL) limitations when building multithreaded Python applications?",
    "sql": "Recruiter: Describe a situation where a complex SQL JOIN caused a bottleneck. How did you refactor the query or use indexing to optimize the execution plan?",
    "aws": "Recruiter: What was the hardest infrastructure bug you faced on AWS? How did you use CloudWatch to debug the latency issue?",
    "docker": "Recruiter: Tell me about a time your Docker container failed in production but worked locally. How did you debug the environment discrepancy?",
    "java": "Recruiter: Explain how you managed JVM memory tuning in your last large-scale Java application."
}

RESUME_BULLETS = {
    "react": "Architected a Trello-style Kanban board using React, utilizing Redux for state management of 50+ tasks.",
    "python": "Developed a financial data pipeline using Python (Pandas), automating real-time crypto analysis.",
    "aws": "Deployed a serverless architecture on AWS Lambda, optimizing API Gateway triggers for <100ms latency.",
    "docker": "Optimized container orchestration using multi-stage Dockerfiles, reducing production image size by 40%.",
    "sql": "Designed a scalable 3NF database schema, optimizing complex JOIN queries for <50ms execution time."
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
    except: c_score = 0
    final = int((k_score * 0.6) + (c_score * 0.4))
    return final, k_score, c_score

def analyze_communication_style(resume_text):
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
    fe_count = len(r_skills.intersection(set(SKILL_DB["Frontend"])))
    be_count = len(r_skills.intersection(set(SKILL_DB["Backend"])))
    ds_count = len(r_skills.intersection(set(SKILL_DB["Data"])))
    if fe_count > be_count and fe_count > ds_count: return "🎨 Frontend Specialist"
    elif be_count > fe_count and be_count > ds_count: return "⚙️ Backend Architect"
    elif ds_count > fe_count: return "📊 Data Scientist"
    elif fe_count > 0 and be_count > 0: return "🦄 Full Stack Developer"
    else: return "🌱 Generalist / Fresher"

def generate_contextual_rewrite(resume_text, skill):
    sentences = re.split(r'[.!?\n]', resume_text)
    original_context = ""
    for s in sentences:
        if skill.lower() in s.lower() and len(s.split()) > 3:
            original_context = s.strip()
            original_context = re.sub(r'^[^\w]+', '', original_context) 
            break
    if not original_context:
        original_context = f"Used {skill.title()} in my projects."

    if skill.lower() in ["react", "html", "css", "figma", "next.js", "vue"]:
        verb = random.choice(["Architected", "Redesigned", "Developed"])
        metric = random.choice(["improving user retention by 20%", "reducing page load time by 1.5s", "increasing conversion rates by 15%"])
    elif skill.lower() in ["python", "sql", "pandas", "mongodb", "mysql"]:
        verb = random.choice(["Optimized", "Engineered", "Automated"])
        metric = random.choice(["processing 100k+ rows of data daily", "reducing query execution time by 40%", "saving 15 hours of manual work weekly"])
    else: 
        verb = random.choice(["Deployed", "Orchestrated", "Implemented"])
        metric = random.choice(["ensuring 99.9% system uptime", "reducing server costs by 25%", "handling 500+ concurrent API requests"])

    rewrite = f"{verb} robust solutions using {skill.title()}, {metric}."
    return original_context, rewrite

def analyze_answer(answer, target_skill):
    impact_words = ["optimized", "architected", "integrated", "solved", "built", "reduced", "improved", "implemented", "debugged", "refactored"]
    words = answer.split()
    if len(words) < 12:
        return "⚠️ Incomplete Answer", "Engineers use data. Expand your answer using the STAR method with specific metrics.", "weak"
    impact_score = sum(1 for word in impact_words if word in answer.lower())
    skill_mentioned = target_skill.lower() in answer.lower()
    if impact_score >= 2 and skill_mentioned:
        return "✅ Hireable Answer", "Excellent. You used high-impact verbs and addressed the core tech.", "strong"
    else:
        return "🛑 Needs Impact", "This is too vague. Mention the specific tech and actions you took.", "weak"

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
    y -= 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "2. Project Stories (STAR Method)")
    y -= 25
    c.setFont("Helvetica", 10)
    for skill, bullet in list(bullets.items())[:5]:
        text = bullet.replace("**", "")
        c.drawString(50, y, f"[{skill.upper()}] - {text[:80]}...") 
        y -= 20
    c.save()
    buffer.seek(0)
    return buffer

def create_soft_skills_chart(resume_text):
    soft_skills = ["communication", "teamwork", "leadership", "problem solving", "adaptability", "creativity"]
    scores = []
    resume_text_lower = resume_text.lower()
    for skill in soft_skills:
        count = resume_text_lower.count(skill)
        scores.append(min(count + 2, 5) if count > 0 else 1)
    fig = go.Figure(data=go.Scatterpolar(
        r=scores, theta=[s.title() for s in soft_skills],
        fill='toself', name='Soft Skills', line_color='#3b82f6'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=False, range=[0, 5]), bgcolor="rgba(0,0,0,0)"),
        showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f8fafc"), height=300, margin=dict(t=40, b=20, l=40, r=40)
    )
    return fig

# ---------------- 4. MAIN APP ----------------

def main():
    if 'analyzed' not in st.session_state:
        st.session_state.update({'analyzed': False, 'completed_projects': set(), 'readiness_score': 0})
        
    # --- LANDING PAGE (Pure Wow Factor) ---
    if not st.session_state['analyzed']:
        # Header Centered
        st.markdown("<br><br>", unsafe_allow_html=True)
        col_title1, col_title2, col_title3 = st.columns([1, 4, 1])
        with col_title2:
            st.markdown("<h1 style='text-align: center; font-size: 4rem; margin-bottom: 0;'>CareerCraft <span style='color:#3b82f6'>AI</span></h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 1.2rem;'>The world's most powerful Resume-JD Alignment Engine.</p>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Main Input Glass Card
        col_main1, col_main2, col_main3 = st.columns([1, 6, 1])
        with col_main2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            
            # Step 1: Resume
            st.markdown("### 💎 Step 1: Your Talent Profile")
            upload_mode = st.segmented_control("Input Method", ["Upload File", "Paste Text"], default="Upload File")
            
            resume_text_content = ""
            if upload_mode == "Upload File":
                uploaded_file = st.file_uploader("Drop your resume (PDF/DOCX)", type=["pdf", "docx"], label_visibility="collapsed")
                if uploaded_file: resume_text_content = extract_text(uploaded_file)
            else:
                resume_text_content = st.text_area("Paste text here...", height=150)

            st.markdown("<br>", unsafe_allow_html=True)

            # Step 2: Target
            st.markdown("### 🎯 Step 2: The Target Opportunity")
            target_mode = st.segmented_control("Selection Method", ["Paste JD", "Preset Role"], default="Paste JD")
            jd_text = ""
            role_title = "Candidate"

            if target_mode == "Paste JD":
                role_title = st.text_input("Target Job Title", "Software Engineer", placeholder="e.g. Senior Backend Dev")
                jd_text = st.text_area("Paste Job Description", height=150)
            else:
                role_title = st.selectbox("Select Role", ["Frontend Developer", "Backend Developer", "Data Scientist"])
                presets = {
                    "Frontend Developer": "react javascript html css git figma redux typescript jest next.js",
                    "Backend Developer": "python java django spring boot sql api docker aws",
                    "Data Scientist": "python pandas sql machine learning statistics tensorflow"
                }
                jd_text = presets.get(role_title, "")

            st.markdown("<br>", unsafe_allow_html=True)

            # Analyze Button
            if st.button("RUN DEEP ANALYSIS", use_container_width=True):
                if resume_text_content and jd_text:
                    with st.spinner("Decoding Professional DNA..."):
                        time.sleep(1.5)
                        r_skills = extract_skills(resume_text_content)
                        j_skills = extract_skills(jd_text.lower())
                        final_score, _, _ = calculate_metrics(resume_text_content, jd_text, r_skills, j_skills)
                        
                        st.session_state.update({
                            'analyzed': True,
                            'resume_text': resume_text_content,
                            'jd_text': jd_text,
                            'role_title': role_title,
                            'readiness_score': final_score,
                            'completed_projects': set()
                        })
                        st.rerun()
                else:
                    st.error("Missing Data: Please provide both Resume and Job Description.")
            
            st.markdown('</div>', unsafe_allow_html=True)

    # --- ANALYSIS DASHBOARD (The "Wow" Result) ---
    else:
        # Top Bar
        col_back, col_spacer, col_btn = st.columns([1, 2, 1])
        with col_back:
            if st.button("⬅ START OVER", use_container_width=False):
                st.session_state['analyzed'] = False
                st.rerun()
        with col_btn:
            r_skills = extract_skills(st.session_state['resume_text'])
            j_skills = extract_skills(st.session_state['jd_text'].lower())
            matched = r_skills.intersection(j_skills)
            pdf_bytes = generate_cheat_sheet("Candidate", st.session_state['role_title'], matched, RESUME_BULLETS)
            st.download_button("📥 EXPORT CHEAT SHEET", data=pdf_bytes, file_name="Interview_Prep.pdf")

        # Hero Metrics Section
        final, k_score, c_score = calculate_metrics(st.session_state['resume_text'], st.session_state['jd_text'], r_skills, j_skills)
        missing = j_skills.difference(r_skills)
        
        st.markdown(f"<h1 style='text-align: center;'>Fit Analysis: <span style='color:#3b82f6'>{st.session_state['role_title']}</span></h1>", unsafe_allow_html=True)
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.markdown(f"<h3>{final}%</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color:#94a3b8; font-size:0.8rem;'>ATS COMPATIBILITY</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with m2:
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.markdown(f"<h3>{k_score}%</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color:#94a3b8; font-size:0.8rem;'>KEYWORD SYNERGY</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with m3:
            st.markdown('<div class="metric-container">', unsafe_allow_html=True)
            st.markdown(f"<h3>{c_score}%</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color:#94a3b8; font-size:0.8rem;'>CONTEXTUAL RELEVANCE</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Content Grid
        left_col, right_col = st.columns([1, 1])

        with left_col:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("🛠 Technical Gap Analysis")
            if missing:
                st.markdown("<p style='color:#ef4444; font-weight:600;'>CRITICAL GAPS DETECTED:</p>", unsafe_allow_html=True)
                tags = "".join([f'<span class="missing-tag">{s.upper()}</span>' for s in list(missing)[:8]])
                st.markdown(tags, unsafe_allow_html=True)
            else:
                st.success("Perfect Match! No gaps found.")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("🧠 Professional DNA")
            st.plotly_chart(create_soft_skills_chart(st.session_state['resume_text']), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with right_col:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("⚡ Project Blueprints")
            st.caption("Complete these tasks to close your gaps instantly.")
            if missing:
                for skill in list(missing)[:2]:
                    bp = PROJECT_BLUEPRINTS.get(skill, {"title": f"{skill.title()} Lab", "task": f"Build a system using {skill}.", "salary": "₹3 LPA"})
                    st.markdown(f"""
                        <div style="background: rgba(15,23,42,0.4); padding: 1.2rem; border-radius: 12px; margin-bottom: 1rem; border: 1px solid rgba(255,255,255,0.05);">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <b style="color:#f8fafc;">{bp['title']}</b>
                                <span class="salary-badge">+{bp['salary']}</span>
                            </div>
                            <p style="font-size:0.9rem; color:#94a3b8; margin-top:8px;">{bp['task']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"VERIFY COMPLETION ({skill.upper()})", key=f"v_{skill}"):
                        st.session_state['completed_projects'].add(skill)
                        st.session_state['readiness_score'] += 10
                        st.toast("Profile Strength Increasing!")
            else:
                st.info("Your technical profile is already at maximum capacity for this role.")
            st.markdown('</div>', unsafe_allow_html=True)

        # Tabs for Assets
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        t1, t2, t3 = st.tabs(["🔥 INTERVIEW PREP", "📄 RECRUITER VIEW", "✍️ RESUME DRAFT"])
        
        with t1:
            st.markdown("### The Hot Seat")
            if matched:
                skill = list(matched)[0]
                q = INTERVIEW_Q.get(skill, f"Explain a challenging problem you solved with {skill}.")
                st.markdown(f"<div class='feedback-box-strong'><b>TARGET SKILL: {skill.upper()}</b><br>{q}</div>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                ans = st.text_area("Your Response...", placeholder="Use the STAR method...")
                if st.button("ANALYZE RESPONSE"):
                    v, t, s = analyze_answer(ans, skill)
                    st.markdown(f"<div class='feedback-box-{s}'><b>{v}</b><br>{t}</div>", unsafe_allow_html=True)

        with t2:
            st.markdown("### Recruiter Strategy")
            st.caption("What the hiring manager is thinking.")
            st.write(f"**Archetype:** {get_candidate_archetype(r_skills)}")
            st.write(f"**Communication:** {analyze_communication_style(st.session_state['resume_text'])}")
            st.markdown("---")
            st.markdown("**TRAP QUESTION FOR INTERVIEWER:**")
            st.code(f"Explain why you decided NOT to use {list(missing)[0] if missing else 'a database'} in your most recent project?")

        with t3:
            st.markdown("### Optimized Resume Content")
            st.caption("AI-Powered 'Magic Rewrites' based on your profile.")
            if matched:
                orig, better = generate_contextual_rewrite(st.session_state['resume_text'], list(matched)[0])
                st.markdown(f"**Original:** *{orig}*")
                st.success(f"**Better:** {better}")
            
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
