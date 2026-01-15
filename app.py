import streamlit as st
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
    page_title="CareerCraft AI - Ultimate",
    page_icon="🦄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Market Leader" UI
st.markdown("""
    <style>
    /* Global Spacing */
    .block-container { padding-top: 2rem; padding-bottom: 5rem; }
    h1, h2, h3 { font-family: 'Inter', sans-serif; color: #0f172a; }
    
    /* Buttons */
    .stButton>button { 
        border-radius: 8px; font-weight: 600; border: none; 
        padding: 0.6rem 1.2rem; transition: all 0.2s ease;
        background-color: #3b82f6; color: white;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3); }
    
    /* Project Cards */
    .project-card { 
        background-color: #f8fafc; padding: 20px; border-radius: 12px; 
        margin-bottom: 15px; border-left: 5px solid #3b82f6; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Badges */
    .salary-badge {
        background-color: #dcfce7; color: #166534; padding: 2px 6px; 
        border-radius: 4px; font-size: 0.8em; font-weight: bold; border: 1px solid #166534; margin-left: 5px;
    }
    
    /* Missing Keywords Badges */
    .missing-tag {
        background-color: #fee2e2; color: #991b1b; padding: 4px 10px; 
        border-radius: 6px; font-size: 0.9em; font-weight: 600; 
        margin-right: 8px; display: inline-block; margin-bottom: 8px;
        border: 1px solid #fecaca;
    }
    
    /* Answer Analyzer Box */
    .feedback-box-weak { border-left: 5px solid #ef4444; background: #fef2f2; padding: 15px; border-radius: 5px; }
    .feedback-box-strong { border-left: 5px solid #22c55e; background: #f0fdf4; padding: 15px; border-radius: 5px; }
    
    /* Tooltip Fix */
    .streamlit-expanderContent div { word-wrap: break-word; white-space: normal; line-height: 1.6; }
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

# MICRO-PROJECT BLUEPRINTS (Platinum Standard)
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

# DYNAMIC INTERVIEW QUESTIONS
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

# RESUME BULLETS
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

def analyze_answer(answer):
    score = 0
    feedback = []
    weak_words = ["maybe", "think", "probably", "sort of", "just"]
    strong_words = ["architected", "designed", "implemented", "optimized", "reduced", "increased", "led", "built"]
    
    if len(answer) < 20:
        return "⚠️ Weak Answer", "Too short. Use the STAR method (Situation, Task, Action, Result).", "weak"
    
    for w in weak_words:
        if w in answer.lower():
            score -= 10
            feedback.append(f"Avoid uncertain words like '{w}'. Be confident.")
            
    for w in strong_words:
        if w in answer.lower():
            score += 20
    
    if score > 10:
        return "✅ Strong Answer", "Great use of action verbs! Make sure to quantify your results.", "strong"
    else:
        return "⚠️ Needs Improvement", f"Your answer is passive. {feedback[0] if feedback else 'Focus on the impact of your actions.'}", "weak"

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

# ---------------- 4. MAIN APP ----------------

def main():
    if 'analyzed' not in st.session_state:
        st.session_state['analyzed'] = False
        st.session_state['completed_projects'] = set()
        st.session_state['readiness_score'] = 25 
        
    # --- SIDEBAR (UPDATED FOR MOBILE) ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=50)
        st.title("CareerCraft AI")
        st.caption("Ultimate Edition v9.1")
        
        # 1. MOBILE-FRIENDLY RESUME INPUT
        st.markdown("### 1. Resume Input")
        upload_mode = st.radio("Input Method", ["Upload File", "Paste Text"], horizontal=True, label_visibility="collapsed")
        
        resume_text_content = ""
        uploaded_file = None

        if upload_mode == "Upload File":
            uploaded_file = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
            if uploaded_file:
                resume_text_content = extract_text(uploaded_file)
        else:
            resume_text_content = st.text_area("Paste Resume Text Here", height=200, placeholder="Copy-paste your full resume text here...")

        # 2. TARGET JOB
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
                st.session_state['analyzed'] = True
                st.session_state['resume_text'] = resume_text_content
                st.session_state['jd_text'] = jd_text
                st.session_state['role_title'] = role_title
                st.session_state['readiness_score'] = 25
                st.session_state['completed_projects'] = set()
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

        # HERO
        st.title(f"🔍 Analysis: {st.session_state['role_title']}")
        
        col_bar, col_export = st.columns([3, 1])
        with col_bar:
            st.caption("🎓 Interview Readiness Level")
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
                st.info(f"**Instead of:** 'Used {list(matched)[0] if matched else 'Java'}'")
                st.success(f"**Write this:** 'Leveraged **{list(matched)[0] if matched else 'Java'}** to architect scalable solutions, improving system latency by 30%.'")

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

        # TABBED SECTIONS
        st.subheader("🚀 Career Assets")
        tab1, tab2, tab3, tab4 = st.tabs(["🔥 Hot Seat", "📄 Cover Letter", "⚖️ Recruiter View", "📝 Full Resume Draft"])

        # TAB 1: INTERVIEW SIMULATOR
        with tab1:
            st.caption("Questions appear here as you unlock skills.")
            active_question = None
            
            if st.session_state['completed_projects']:
                st.markdown("**🔓 UNLOCKED QUESTIONS (New Skills):**")
                for s in st.session_state['completed_projects']:
                    q = INTERVIEW_Q.get(s, f"How did you implement {s}?")
                    st.success(f"**{s.title()} (Unlocked):** {q}")
                    active_question = q 
            elif matched:
                st.markdown("**Based on your current resume:**")
                for s in list(matched)[:1]:
                     q = INTERVIEW_Q.get(s, f"Tell me about your experience with {s}.")
                     st.info(f"**{s.title()}:** {q}")
                     active_question = q

            if active_question:
                st.markdown("---")
                st.markdown("🎙️ **Practice Your Answer:**")
                user_ans = st.text_area("Type your answer here to get AI feedback...", height=100)
                if st.button("Analyze My Answer"):
                    if user_ans:
                        verdict, text, style = analyze_answer(user_ans)
                        st.markdown(f"<div class='feedback-box-{style}'><b>{verdict}</b><br>{text}</div>", unsafe_allow_html=True)
                    else:
                        st.warning("Please type an answer first.")

        # TAB 2: COVER LETTER
        with tab2:
            tone = "I am a rapid learner actively closing technical gaps." if final < 70 else "I am ready to deliver value immediately."
            cl_text = f"Dear Hiring Manager,\n\nI am applying for the {st.session_state['role_title']} role. {tone}\n\nMy analysis shows strong foundations in {', '.join(list(matched)[:3])}. I am currently building projects in {', '.join(list(missing)[:2])} to ensure I am day-one ready.\n\nSincerely,\nCandidate"
            st.text_area("Cover Letter Draft", cl_text, height=300)

        # TAB 3: RECRUITER VIEW (Comparison Table)
        with tab3:
            st.markdown("### 👓 How a Recruiter Sees You")
            st.caption("Side-by-side comparison of Job Requirements vs. Your Resume")
            
            comp_data = []
            for s in matched:
                comp_data.append({"Skill": s.title(), "Status": "✅ Found", "Recommendation": "Good match. Be ready to explain usage."})
            for s in missing:
                comp_data.append({"Skill": s.title(), "Status": "❌ Missing", "Recommendation": f"Critical gap. Build a {s.title()} project."})
            
            if comp_data:
                df_comp = pd.DataFrame(comp_data)
                st.dataframe(df_comp, use_container_width=True)
            else:
                st.info("No skills found to compare.")

        # TAB 4: FULL RESUME GENERATOR
        with tab4:
            st.markdown("### 📝 Full Resume Draft")
            st.caption("Copy this text into Word or Google Docs.")
            
            resume_draft = f"""# CANDIDATE NAME
[City, State] | [Phone] | [Email] | [LinkedIn URL]

## PROFESSIONAL SUMMARY
Motivated {st.session_state['role_title']} with a strong foundation in {', '.join(list(matched)[:3])}. Proven ability to build scalable web applications and optimize system performance. Eager to contribute technical expertise to [Company Name].

## TECHNICAL SKILLS
**Proficient:** {', '.join([s.title() for s in matched])}
**Learning:** {', '.join([s.title() for s in list(missing)[:3]])}

## PROJECTS
"""
            if st.session_state['completed_projects']:
                for s in st.session_state['completed_projects']:
                    bullet = RESUME_BULLETS.get(s, f"Implemented {s} project.")
                    resume_draft += f"**{PROJECT_BLUEPRINTS[s]['title']}** | *{s.title()}*\n"
                    resume_draft += f"- {bullet}\n\n"
            
            for s in list(matched)[:2]:
                resume_draft += f"**{s.title()} Project** | *{s.title()}*\n"
                resume_draft += f"- Leveraged {s} to build a responsive application, improving user engagement.\n\n"

            resume_draft += """## EDUCATION
**Bachelor of Technology in Computer Science**
[University Name], [Year]

## CERTIFICATIONS
- Full Stack Web Development Bootcamp
- [Specific Skill] Certification
"""
            st.text_area("Full Resume Text", resume_draft, height=600)

    elif not st.session_state['analyzed']:
        # Mobile-friendly start message
        st.info("👈 Open Sidebar to Paste Resume or Upload File.")

if __name__ == "__main__":
    main()
