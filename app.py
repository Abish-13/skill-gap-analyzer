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

# --- UPGRADED: ADVANCED INTERVIEW QUESTIONS ---
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
        # Direct geometric angle (0-100%). No baseline. Pure accuracy.
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

# --- FIXED: CONTEXTUAL MAGIC REWRITE (Reads the actual resume) ---
def generate_contextual_rewrite(resume_text, skill):
    """Finds the actual sentence in the resume containing the skill and rewrites IT, not a template."""
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

# --- UPGRADED: SMARTER ANSWER ANALYZER ---
def analyze_answer(answer, target_skill):
    """Deep analysis of interview answers looking for technical depth and the STAR method."""
    impact_words = ["optimized", "architected", "integrated", "solved", "built", "reduced", "improved", "implemented", "debugged", "refactored"]
    words = answer.split()
    
    # 1. Check Length
    if len(words) < 12:
        return "⚠️ Incomplete Answer", "Engineers use data. Expand your answer using the STAR method (Situation, Task, Action, Result) with specific metrics.", "weak"
    
    impact_score = sum(1 for word in impact_words if word in answer.lower())
    skill_mentioned = target_skill.lower() in answer.lower()
    
    # 2. Check for Skill + Action
    if impact_score >= 2 and skill_mentioned:
        return "✅ Hireable Answer", "Excellent. You used high-impact verbs and addressed the core tech. This is exactly what Senior Engineers sound like.", "strong"
    elif skill_mentioned and impact_score < 2:
        return "⚠️ Needs Impact", f"You mentioned {target_skill}, but it sounds passive. Use action verbs like 'Architected' or 'Optimized' to show ownership.", "weak"
    elif impact_score >= 1 and not skill_mentioned:
        return "⚠️ Missed the Core Tech", f"Good action verbs, but you forgot to mention how you specifically used {target_skill}. Connect the tech to the result.", "weak"
    else:
        return "🛑 Generic Answer", f"This is too vague. You must mention {target_skill} and the specific actions you took to solve the problem.", "weak"

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
        st.session_state['readiness_score'] = 0 
        
    # --- START PAGE (Main UI Input) ---
    if not st.session_state['analyzed']:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=60)
            st.title("CareerCraft AI")
            st.caption("Recruiter Edition v15.0 (Diamond Ultimate)")
            st.markdown("---")
            
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

            if st.button("🚀 Analyze My Fit", use_container_width=True):
                if resume_text_content and jd_text:
                    progress_text = "Initializing AI Agent..."
                    my_bar = st.progress(0, text=progress_text)
                    time.sleep(0.3)
                    my_bar.progress(30, text="📄 Parsing Resume & TF-IDF Vectorization...")
                    time.sleep(0.3)
                    my_bar.progress(70, text="🔍 Calculating Pure Cosine Similarity...")
                    
                    r_skills = extract_skills(resume_text_content)
                    j_skills = extract_skills(jd_text.lower())
                    final_score, k_s, c_s = calculate_metrics(resume_text_content, jd_text, r_skills, j_skills)

                    st.session_state['analyzed'] = True
                    st.session_state['resume_text'] = resume_text_content
                    st.session_state['jd_text'] = jd_text
                    st.session_state['role_title'] = role_title
                    st.session_state['readiness_score'] = final_score 
                    st.session_state['completed_projects'] = set()
                    
                    my_bar.progress(100, text="✅ Analysis Complete!")
                    time.sleep(0.5)
                    my_bar.empty()
                    st.rerun()
                else:
                    st.toast("⚠️ Please provide Resume text and Job Description!", icon="🚨")

    # --- MAIN DASHBOARD (Analysis Page) ---
    else:
        if st.button("⬅️ Analyze Another Resume"):
            st.session_state['analyzed'] = False
            st.session_state['completed_projects'] = set()
            st.session_state['readiness_score'] = 0 
            st.rerun()

        r_text = st.session_state['resume_text']
        j_text = st.session_state['jd_text']
        r_skills = extract_skills(r_text)
        j_skills = extract_skills(j_text.lower())
        matched = r_skills.intersection(j_skills)
        missing = j_skills.difference(r_skills)
        final, k_score, c_score = calculate_metrics(r_text, j_text, r_skills, j_skills)
        
        archetype = get_candidate_archetype(r_skills)
        comm_style = analyze_communication_style(r_text)

        # HERO
        st.title(f"🔍 Analysis: {st.session_state['role_title']}")
        
        col_bar, col_export = st.columns([3, 1])
        with col_bar:
            st.caption("🎓 Interview Readiness Level (Pure TF-IDF Cosine Match)")
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
            
            with st.expander("✨ Peek at Magic Rewrites (Reads Your Resume)"):
                st.caption("AI found these lines in your resume and upgraded them with the 'XYZ' impact formula.")
                matched_list = list(matched)
                if len(matched_list) > 0:
                    for i in range(min(3, len(matched_list))): 
                        skill = matched_list[i]
                        original_line, better_line = generate_contextual_rewrite(r_text, skill)
                        st.markdown(f"**Instead of:** *'{original_line}'*")
                        st.success(f"**Write this:** '{better_line}'")
                        st.write("---")
                else:
                    st.info("No technical matches found. Try adding Core IT skills like Python or React.")

        # --- SOFT SKILLS & DYNAMIC LINKEDIN ---
        st.markdown("---")
        col_chart, col_linkedin = st.columns([1, 1])
        with col_chart:
            chart = create_soft_skills_chart(r_text)
            st.plotly_chart(chart, use_container_width=True)
        with col_linkedin:
            st.subheader("🔗 LinkedIn Makeover")
            st.caption("Tailored to your specific candidate archetype & writing style.")
            
            top_skills = list(matched)[:3] if matched else ["Tech"]
            if "Backend" in archetype:
                headline = f"🚀 {archetype} | Scaling APIs & Systems with {', '.join([s.title() for s in top_skills])} | Cloud Enthusiast"
            elif "Frontend" in archetype:
                headline = f"✨ {archetype} | Crafting Pixel-Perfect UIs with {', '.join([s.title() for s in top_skills])} | UX Focused"
            elif "Data" in archetype:
                headline = f"📊 {archetype} | Turning Raw Data into Insights via {', '.join([s.title() for s in top_skills])} | ML Enthusiast"
            else:
                headline = f"🚀 Aspiring Software Engineer | Proficient in {', '.join([s.title() for s in top_skills])} | Solving complex problems with Code"
            
            st.code(headline, language="text")
            
            if "Passive" in comm_style:
                st.info("💡 **Pro Tip:** Your resume uses passive verbs (e.g., 'helped'). Recruiters search for 'Led' and 'Architected'. Update your 'About' section with stronger verbs!")
            elif "High Impact" in comm_style:
                st.success("💡 **Pro Tip:** Your communication style is excellent! Pin your GitHub profile to your LinkedIn 'Featured' section to prove your code matches your strong claims.")
            else:
                st.info("💡 **Pro Tip:** Adding a 'Project Portfolio' link with a live demo increases recruiter clicks by 40%.")

        st.markdown("---")

        # BLUEPRINTS
        col_L, col_R = st.columns([1, 1.2])

        with col_L:
            st.subheader("✅ Skills You Have")
            if matched:
                st.success(", ".join([s.title() for s in matched]))

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
                        btn_label = "✅ I Built It!" if skill not in st.session_state['completed_projects'] else "🎉 Completed!"
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
        st.subheader("🚀 Career Assets")
        tab1, tab2, tab3, tab4 = st.tabs(["🔥 Hot Seat", "📄 Cover Letter", "⚖️ Recruiter View", "📝 Full Resume Draft"])

        # TAB 1: INTERVIEW SIMULATOR
        with tab1:
            st.caption("Questions appear here as you unlock skills.")
            active_question = None
            active_skill = None 
            
            # Show Questions for Current Skills
            if matched:
                st.markdown("### 🎯 Questions based on your CURRENT skills:")
                for s in list(matched)[:5]:
                     q = INTERVIEW_Q.get(s, f"Recruiter: Explain a complex architectural challenge you solved using {s.title()}.")
                     st.info(f"**{s.title()}:** {q}")
                     active_question = q
                     active_skill = s
                     
            # Show Questions for Unlocked Skills
            if st.session_state['completed_projects']:
                st.markdown("### 🔓 UNLOCKED Questions (New Skills):")
                for s in st.session_state['completed_projects']:
                    q = INTERVIEW_Q.get(s, f"Recruiter: How did you implement {s.title()} and ensure the code was scalable?")
                    st.success(f"**{s.title()} (Unlocked):** {q}")
                    active_question = q 
                    active_skill = s
                    
            if active_question and active_skill:
                st.markdown("---")
                st.markdown("🎙️ **Practice Your Answer:**")
                st.caption("Use the STAR Method. Mention metrics, action verbs, and the specific technology.")
                user_ans = st.text_area("Type your answer here to get AI feedback...", height=100)
                if st.button("Analyze My Answer"):
                    if user_ans:
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
            
            if final >= 80:
                st.markdown(f"<div class='ats-badge-green'>✅ VERDICT: SHORTLIST (Top 10%)</div>", unsafe_allow_html=True)
            elif final >= 50:
                 st.markdown(f"<div class='ats-badge-yellow'>⚠️ VERDICT: ON HOLD (Potential Fit)</div>", unsafe_allow_html=True)
            else:
                 st.markdown(f"<div class='ats-badge-red'>🛑 VERDICT: REJECT (Critical Gaps)</div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                st.info(f"**Candidate Archetype:** {archetype}")
                st.caption("Based on skill cluster analysis.")
            with c_p2:
                st.info(f"**Communication Style:** {comm_style}")
                st.caption("Based on 'Power Word' frequency.")

            st.markdown("#### 🎯 Hiring Decision Matrix")
            c_green, c_red = st.columns(2)
            with c_green:
                st.markdown("**✅ STRENGTHS (Green Flags)**")
                for s in list(matched): st.success(f"**{s.title()}**: Validated")
            with c_red:
                st.markdown("**🚩 RISKS (Red Flags)**")
                for s in list(missing)[:5]: 
                    st.error(f"**{s.title()}**: Missing")
            
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

## PROFESSIONAL EXPERIENCE
**[Job Title]** | [Company Name] | [Dates]
* Leveraged **{list(matched)[0] if matched else 'Java'}** to improve application performance, resulting in a 15% reduction in latency.
* Collaborated with cross-functional teams to design and deploy features using **{list(matched)[1] if len(matched)>1 else 'SQL'}**.

## PROJECT PORTFOLIO
"""
            if st.session_state['completed_projects']:
                for s in st.session_state['completed_projects']:
                    bullet = RESUME_BULLETS.get(s, f"Implemented {s} project.")
                    resume_draft += f"**{PROJECT_BLUEPRINTS[s]['title']}** | *Stack: {s.title()}*\n* {bullet}\n\n"
            
            for s in list(matched)[:2]:
                resume_draft += f"**{s.title()} Implementation** | *Stack: {s.title()}*\n* Designed and developed a solution using **{s.title()}** to solve key business challenges.\n\n"

            st.text_area("Full Resume Text", resume_draft, height=600)

if __name__ == "__main__":
    main()
