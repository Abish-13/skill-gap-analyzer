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
    "spring boot": {"title": "Bookstore REST API", "task": "Build a comprehensive API with CRUD operations, connecting to a local **H2 Database**.", "salary": "₹6 LPA"},
    "python": {"title": "Crypto Price Tracker", "task": "Build a script using **Requests & Pandas** to fetch live BTC prices.", "salary": "₹4 LPA"},
    "sql": {"title": "E-Commerce Schema (3NF)", "task": "Design a normalized DB for an Amazon clone. Write queries using **JOINs**.", "salary": "₹3 LPA"},
    "aws": {"title": "Serverless API", "task": "Deploy a 'Hello World' function on **AWS Lambda** triggered by API Gateway.", "salary": "₹7 LPA"},
    "docker": {"title": "Microservice Dockerfile", "task": "Write a multi-stage **Dockerfile** for a Python app to reduce image size by 40%.", "salary": "₹5 LPA"}
}

# --- FIXED: REALISTIC SENIOR-LEVEL INTERVIEW QUESTIONS ---
INTERVIEW_Q = {
    "javascript": "Recruiter: Explain the **Event Loop** in JavaScript. How does it handle the Execution Stack and Task Queue differently during asynchronous operations?",
    "html": "Recruiter: What is **Semantic HTML**, and why is it critical for both SEO performance and Web Accessibility (A11y) standards?",
    "css": "Recruiter: How do you manage **CSS Specificity** in a large project? Explain the difference between Flexbox and CSS Grid for complex layouts.",
    "react": "Recruiter: Explain the **Virtual DOM** reconciliation process. How do 'keys' help React optimize re-rendering performance?",
    "next.js": "Recruiter: What are the primary trade-offs between **Server-Side Rendering (SSR)** and **Static Site Generation (SSG)**? When would you use ISR?",
    "python": "Recruiter: In Python, what is the difference between a **list** and a **tuple** in terms of memory management? Explain the Global Interpreter Lock (GIL).",
    "sql": "Recruiter: Explain the difference between an **Inner Join** and a **Left Join**. How would you use a Non-Clustered Index to optimize a slow query?",
    "aws": "Recruiter: Since you mentioned AWS, how do you handle **Cold Starts** in Lambda? Why might you choose DynamoDB over an RDS instance for a serverless app?",
    "docker": "Recruiter: What is a **multi-stage Docker build**, and how does it contribute to both security and production performance?",
    "java": "Recruiter: Explain the concept of **Dependency Injection** in Spring Boot. Why is Constructor Injection preferred over Field Injection?",
    "git": "Recruiter: Walk me through your process for resolving a **Merge Conflict**. When would you prefer 'Rebase' over 'Merge'?"
}

RESUME_BULLETS = {
    "react": "Architected a Trello-style Kanban board using React, utilizing Redux for state management of 50+ tasks.",
    "python": "Developed a financial data pipeline using Python (Pandas), automating real-time crypto analysis.",
    "aws": "Deployed a serverless architecture on AWS Lambda, optimizing API Gateway triggers for <100ms latency.",
    "docker": "Optimized container orchestration using multi-stage Dockerfiles, reducing production image size by 40%."
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
        # PURE MATHEMATICAL MATCH (0-100%)
        c_score = int(cosine_similarity(matrix[0:1], matrix[1:2])[0][0] * 100)
    except: 
        c_score = 0
        
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

# --- FIXED: CONTEXTUAL MAGIC REWRITE (Harvard XYZ Formula) ---
def generate_contextual_rewrite(resume_text, skill):
    """Finds the actual bullet in the resume and rewrites it using the Metric-Driven approach."""
    sentences = re.split(r'[.!?\n]', resume_text)
    original_context = ""
    
    for s in sentences:
        if skill.lower() in s.lower() and len(s.split()) > 3:
            original_context = s.strip()
            original_context = re.sub(r'^[^\w]+', '', original_context) 
            break
            
    if not original_context:
        original_context = f"Developed features using {skill.title()}."

    # Dynamic Senior-Level Transformations
    if skill.lower() in ["react", "html", "css", "figma", "next.js", "javascript"]:
        verb = random.choice(["Architected", "Engineered", "Optimized"])
        metric = random.choice(["improving PageSpeed insights by 30%", "reducing Lighthouse performance bottlenecks by 40%", "enhancing user-engagement retention by 15%"])
    elif skill.lower() in ["python", "sql", "pandas", "mongodb", "mysql"]:
        verb = random.choice(["Automated", "Streamlined", "Optimized"])
        metric = random.choice(["processing 50k+ daily records with <200ms latency", "reducing query execution time by 50%", "eliminating 20 hours of manual data entry weekly"])
    else:
        verb = random.choice(["Orchestrated", "Implemented", "Scaled"])
        metric = random.choice(["achieving 99.9% deployment uptime", "reducing cloud infrastructure costs by 20%", "supporting 1,000+ concurrent API requests"])

    rewrite = f"{verb} production-grade modules using {skill.title()}, {metric}."
    return original_context, rewrite

def analyze_answer(answer, target_skill):
    impact_words = ["optimized", "architected", "integrated", "solved", "built", "reduced", "improved"]
    if len(answer.split()) < 20:
        return "⚠️ Weak Answer", "Too short! A professional answer should detail the Situation, Task, Action, and Result (STAR method).", "weak"
    
    impact_score = sum(1 for word in impact_words if word in answer.lower())
    skill_mentioned = target_skill.lower() in answer.lower()
    
    if impact_score >= 1 and skill_mentioned:
        return "✅ Strong Answer", "Excellent. You quantified your impact and used professional terminology.", "strong"
    else:
        return "⚠️ Needs Improvement", f"Make sure to explain *how* you used {target_skill} to solve a specific business problem.", "weak"

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
        st.session_state['readiness_score'] = 0 
        
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=50)
        st.title("CareerCraft AI")
        st.caption("Diamond Tier v15.0 - Final Build")
        
        st.markdown("### 1. Resume Input")
        upload_mode = st.radio("Input Method", ["Upload File", "Paste Text"], horizontal=True, label_visibility="collapsed")
        
        resume_text_content = ""
        if upload_mode == "Upload File":
            uploaded_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
            if uploaded_file: resume_text_content = extract_text(uploaded_file)
        else:
            resume_text_content = st.text_area("Paste Resume Text Here", height=200)

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
                "Frontend Developer": "react javascript html css git figma next.js",
                "Backend Developer": "python java spring boot sql api docker aws",
                "Data Scientist": "python pandas sql scikit-learn tensorflow"
            }
            jd_text = presets.get(role_title, "")

        if st.button("🚀 Run Deep Analysis"):
            if resume_text_content and jd_text:
                my_bar = st.progress(0, text="Initializing Neural Engine...")
                time.sleep(0.3)
                my_bar.progress(50, text="🔍 Calculating Geometric Match...")
                r_skills = extract_skills(resume_text_content)
                j_skills = extract_skills(jd_text.lower())
                final_score, k_s, c_s = calculate_metrics(resume_text_content, jd_text, r_skills, j_skills)
                st.session_state['analyzed'] = True
                st.session_state['resume_text'] = resume_text_content
                st.session_state['jd_text'] = jd_text
                st.session_state['role_title'] = role_title
                st.session_state['readiness_score'] = final_score 
                st.session_state['completed_projects'] = set()
                my_bar.progress(100, text="✅ Done!")
                time.sleep(0.5)
                my_bar.empty()
                st.rerun()

    if st.session_state['analyzed']:
        r_text = st.session_state['resume_text']
        j_text = st.session_state['jd_text']
        r_skills = extract_skills(r_text)
        j_skills = extract_skills(j_text.lower())
        matched = r_skills.intersection(j_skills)
        missing = j_skills.difference(r_skills)
        final, k_score, c_score = calculate_metrics(r_text, j_text, r_skills, j_skills)
        archetype = get_candidate_archetype(r_skills)
        comm_style = analyze_communication_style(r_text)

        st.title(f"🔍 Dashboard: {st.session_state['role_title']}")
        
        st.caption("🎓 Interview Readiness Level (Pure Geometric Math)")
        st.progress(st.session_state['readiness_score'] / 100)
        st.markdown(f"**Level: {st.session_state['readiness_score']}%**")

        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Overall Match", f"{final}%")
        with c2: 
            st.metric("Keyword Match", f"{k_score}%")
            if missing:
                tags = " ".join([f"<span class='missing-tag'>{s}</span>" for s in list(missing)[:5]])
                st.markdown(tags, unsafe_allow_html=True)
        with c3:
            st.metric("Context Score", f"{c_score}%")
            with st.expander("✨ Magic Rewrites (Reads Resume)"):
                matched_list = list(matched)
                if matched_list:
                    for i in range(min(3, len(matched_list))):
                        old, better = generate_contextual_rewrite(r_text, matched_list[i])
                        st.markdown(f"**Original:** *'{old}'*")
                        st.success(f"**Upgrade:** '{better}'")
                        st.write("---")

        st.markdown("---")
        col_chart, col_linkedin = st.columns([1, 1])
        with col_chart: st.plotly_chart(create_soft_skills_chart(r_text))
        with col_linkedin:
            st.subheader("🔗 LinkedIn Makeover")
            top_skills = list(matched)[:3] if matched else ["Tech"]
            headline = f"🚀 {archetype} | Specialized in {', '.join([s.title() for s in top_skills])} | ROI-Focused Engineer"
            st.code(headline, language="text")
            if "Passive" in comm_style: st.info("💡 **Pro Tip:** Switch to active verbs to increase visibility.")
            else: st.success("💡 **Pro Tip:** Strong communication detected. Focus on showcasing live projects.")

        st.markdown("---")
        st.subheader("🚀 Career Assets")
        tab1, tab2, tab3, tab4 = st.tabs(["🔥 Hot Seat", "📄 Cover Letter", "⚖️ Recruiter View", "📝 Full Resume Draft"])

        with tab1:
            st.subheader("🎤 Senior-Level Interview Prep")
            active_skill = list(matched)[0] if matched else "coding"
            # FIXED: Real professional question
            q = INTERVIEW_Q.get(active_skill, f"Explain a complex problem you solved using {active_skill.title()} and how you optimized the final solution.")
            st.info(f"**Q:** {q}")
            user_ans = st.text_area("Type your STAR answer here:", height=100)
            if st.button("Analyze Answer"):
                if user_ans:
                    verdict, text, style = analyze_answer(user_ans, active_skill)
                    st.markdown(f"<div class='feedback-box-{style}'><b>{verdict}</b><br>{text}</div>", unsafe_allow_html=True)

        with tab2:
            cl_text = f"Dear Hiring Manager,\n\nI am writing to apply for the {st.session_state['role_title']} position. My technical foundation in {', '.join(list(matched)[:3])} makes me an immediate asset to your team. I am highly focused on production-grade excellence.\n\nSincerely,\nCandidate"
            st.text_area("Cover Letter Draft", cl_text, height=300)

        with tab3:
            st.markdown("### 👔 Hiring Manager View")
            if final >= 75: st.markdown(f"<div class='ats-badge-green'>✅ VERDICT: SHORTLIST</div>", unsafe_allow_html=True)
            else: st.markdown(f"<div class='ats-badge-yellow'>⚠️ VERDICT: ON HOLD</div>", unsafe_allow_html=True)
            st.info(f"**Archetype:** {archetype}")
            st.info(f"**Comm Style:** {comm_style}")
            st.markdown("#### 🕵️‍♂️ Trap Questions")
            if matched: st.write(f"- 'Walk me through a system bottleneck you solved with {list(matched)[0].title()}.'")
            if missing: st.write(f"- 'I see you lack {list(missing)[0].title()}. How will you close this gap in the first 30 days?'")

        with tab4:
            draft = f"# YOUR NAME\n\n## SUMMARY\nProfessional {st.session_state['role_title']} expert in {', '.join(list(matched)[:3])}."
            st.text_area("Full Resume Draft", draft, height=600)

if __name__ == "__main__":
    main()
