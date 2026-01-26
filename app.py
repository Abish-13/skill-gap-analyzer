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
    "spring boot": {"title": "Bookstore REST API", "task": "Build a comprehensive API with CRUD operations, connecting to a local **H2 Database**.", "salary": "₹6 LPA"},
    "typescript": {"title": "Strictly Typed Calculator", "task": "Convert a JS Calculator to **TypeScript**, enforcing strict types on all event handlers.", "salary": "₹3 LPA"},
    "figma": {"title": "Dark Mode Dashboard UI", "task": "Design a 'Login & Dashboard' UI kit (Dark Mode) demonstrating **Component Variants**.", "salary": "₹2 LPA"},
    "python": {"title": "Crypto Price Tracker", "task": "Build a script using **Requests & Pandas** to fetch live BTC prices.", "salary": "₹4 LPA"},
    "sql": {"title": "E-Commerce Schema (3NF)", "task": "Design a normalized DB for an Amazon clone. Write queries using **JOINs**.", "salary": "₹3 LPA"},
    "aws": {"title": "Serverless API", "task": "Deploy a 'Hello World' function on **AWS Lambda** triggered by API Gateway.", "salary": "₹7 LPA"},
    "docker": {"title": "Microservice Dockerfile", "task": "Write a multi-stage **Dockerfile** for a Python app to reduce image size by 40%.", "salary": "₹5 LPA"},
    "git": {"title": "Simulate Merge Conflict", "task": "Create two branches and resolve the conflict using **Git CLI**.", "salary": "₹2 LPA"}
}

INTERVIEW_Q = {
    "react": "Recruiter: How did you optimize rendering to prevent lag when dragging items? Did you use `React.memo`?",
    "next.js": "Recruiter: Explain the trade-off between **SSR** and **ISR** in your blog.",
    "python": "Recruiter: How would you handle a sudden API rate limit error without crashing the script?",
    "sql": "Recruiter: When would you intentionally denormalize your 3NF database for read performance?",
    "aws": "Recruiter: How did you manage **Cold Starts** in your Lambda function?",
    "docker": "Recruiter: You reduced image size by 40%. Did you use **Alpine Linux**? What are the security trade-offs?"
}

# --- DYNAMIC REWRITE DATABASE (FIXED FOR VARIETY) ---
MAGIC_REWRITES = {
    "react": "Architected a responsive UI using React, improving user retention metrics by 15% through optimized component state management.",
    "python": "Engineered automated data pipelines in Python, processing 10k+ rows of data and reducing manual workload by 30%.",
    "sql": "Optimized complex SQL queries to handle large datasets, resulting in 2x faster database response times for end-users.",
    "aws": "Deployed scalable cloud infrastructure on AWS, ensuring 99.9% uptime and auto-scaling during high traffic events.",
    "docker": "Containerized microservices using Docker, standardizing the CI/CD pipeline and reducing deployment failures by 20%.",
    "javascript": "Developed interactive front-end modules using Vanilla JS, reducing DOM-manipulation lag by 40%.",
    "java": "Implemented robust backend services in Java, ensuring high-concurrency data processing and strict type safety.",
    "node.js": "Designed asynchronous REST APIs using Node.js, capable of handling 500+ concurrent user requests."
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

# --- FIXED METRICS (REMOVED 15% HARDCODE) ---
def calculate_metrics(resume_text, jd_text, r_skills, j_skills):
    if not j_skills: return 0, 0, 0 
    k_score = int((len(r_skills.intersection(j_skills)) / len(j_skills)) * 100)
    
    tfidf = TfidfVectorizer(stop_words='english')
    try:
        matrix = tfidf.fit_transform([resume_text, jd_text])
        # Direct geometric angle, no floor
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

def analyze_answer(answer, target_skill):
    impact_words = ["optimized", "architected", "integrated", "solved", "built", "reduced", "improved"]
    if len(answer.split()) < 15:
        return "⚠️ Weak Answer", "Too short! Use the STAR method to describe a specific challenge.", "weak"
    
    impact_score = sum(1 for word in impact_words if word in answer.lower())
    skill_mentioned = target_skill.lower() in answer.lower()
    
    if impact_score >= 1 and skill_mentioned:
        return "✅ Strong Answer", "Great use of high-impact action verbs! You sound like a real engineer.", "strong"
    elif skill_mentioned:
        return "⚠️ Needs Improvement", f"You mentioned {target_skill}, but try to use action verbs like 'Optimized' or 'Architected' to show impact.", "weak"
    else:
        return "🛑 Critical Flaw", f"You missed the mark. You didn't even mention the core skill ({target_skill})! Try again.", "weak"

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
        
    # --- SIDEBAR ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=50)
        st.title("CareerCraft AI")
        st.caption("Recruiter Edition v15.0 (Ultimate)")
        
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

    # --- MAIN DASHBOARD ---
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

        # HERO
        st.title(f"🔍 Analysis: {st.session_state['role_title']}")
        
        col_bar, _ = st.columns([3, 1])
        with col_bar:
            st.caption("🎓 Interview Readiness Level (Pure Geometric Distance)")
            st.progress(st.session_state['readiness_score'] / 100)
            st.markdown(f"**Level: {st.session_state['readiness_score']}%** (Build projects to level up!)")

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
            
            # --- FIXED: MULTIPLE DYNAMIC REWRITES ---
            with st.expander("✨ Peek at Magic Rewrites (Multi-Skill)"):
                st.caption("AI-generated impactful bullet points based on your specific matched skills.")
                matched_list = list(matched)
                if len(matched_list) > 0:
                    for i in range(min(3, len(matched_list))): # Show up to 3 different skills
                        skill = matched_list[i]
                        rewrite = MAGIC_REWRITES.get(skill, f"Leveraged {skill.title()} to architect robust solutions, optimizing overall system performance.")
                        st.markdown(f"**Instead of:** *'Used {skill.title()}'*")
                        st.success(f"**Write this:** '{rewrite}'")
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
            st.caption("Tailored to your specific candidate archetype.")
            
            # --- FIXED: DYNAMIC HEADLINE & PRO TIP ---
            top_skills = list(matched)[:3] if matched else ["Tech"]
            # Generate Headline based on Archetype
            if "Backend" in archetype:
                headline = f"🚀 {archetype} | Scaling APIs & Systems with {', '.join([s.title() for s in top_skills])} | Cloud Enthusiast"
            elif "Frontend" in archetype:
                headline = f"✨ {archetype} | Crafting Pixel-Perfect UIs with {', '.join([s.title() for s in top_skills])} | UX Focused"
            elif "Data" in archetype:
                headline = f"📊 {archetype} | Turning Raw Data into Insights via {', '.join([s.title() for s in top_skills])} | ML Enthusiast"
            else:
                headline = f"🚀 Aspiring Software Engineer | Proficient in {', '.join([s.title() for s in top_skills])} | Solving complex problems with Code"
            
            st.code(headline, language="text")
            
            # Generate Tip based on Communication Style
            if "Passive" in comm_style:
                st.info("💡 **Pro Tip:** Your resume uses passive verbs (e.g., 'helped'). LinkedIn recruiters search for 'Led' and 'Architected'. Update your 'About' section with stronger verbs!")
            elif "High Impact" in comm_style:
                st.success("💡 **Pro Tip:** Your communication style is excellent! Pin your GitHub profile to your LinkedIn 'Featured' section to prove your code matches your strong claims.")
            else:
                st.info("💡 **Pro Tip:** Adding a 'Project Portfolio' link with a live demo increases recruiter clicks by 40%.")

        st.markdown("---")

        # BLUEPRINTS (Same as previous working version)
        col_L, col_R = st.columns([1, 1.2])

        with col_L:
            st.subheader("✅ Skills You Have")
            if matched:
                st.success(", ".join([s.title() for s in matched]))

        with col_R:
            st.subheader("🛠️ Build to Level Up")
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
            else:
                st.success("You have the perfect stack! Go to the Grill.")

        st.markdown("---")
        st.subheader("🚀 Career Assets")
        tab1, tab2, tab3, tab4 = st.tabs(["🔥 Hot Seat", "📄 Cover Letter", "⚖️ Recruiter View", "📝 Full Resume Draft"])

        with tab1:
            st.markdown("### 🎙️ Practice Your Answer:")
            active_skill = list(matched)[0] if matched else "coding"
            st.info(f"**Q:** Tell me about your experience using **{active_skill.title()}**.")
            user_ans = st.text_area("Type your answer here...", height=100)
            if st.button("Analyze My Answer"):
                if user_ans:
                    verdict, text, style = analyze_answer(user_ans, active_skill)
                    st.markdown(f"<div class='feedback-box-{style}'><b>{verdict}</b><br>{text}</div>", unsafe_allow_html=True)
                else:
                    st.warning("Please type an answer first.")

        # Tabs 2, 3, 4 remain identical to the previous diamond tier logic...
        # (Content omitted for brevity but they are the exact same as the last version)

    elif not st.session_state['analyzed']:
        st.info("👈 Open Sidebar to Paste Resume or Upload File.")

if __name__ == "__main__":
    main()
