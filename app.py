import streamlit as st
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# ==========================================
# PAGE CONFIG & CSS STYLING
# ==========================================
st.set_page_config(page_title="CareerCraft AI", layout="wide", page_icon="🚀")

# CSS to make progress bar change colors and look professional
st.markdown("""
<style>
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #4CAF50, #8BC34A);
    }
    .high-score { color: #4CAF50; font-weight: bold; }
    .mid-score { color: #FF9800; font-weight: bold; }
    .low-score { color: #F44336; font-weight: bold; }
    .project-card { border: 1px solid #ddd; padding: 15px; border-radius: 10px; margin-bottom: 10px; background-color: #f9f9f9;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# BACKEND LOGIC (The ML Engine)
# ==========================================
def calculate_match(resume_text, jd_text):
    """Deterministic TF-IDF & Cosine Similarity Engine"""
    if not resume_text or not jd_text:
        return 0, []
    
    # Pre-processing & Vectorization
    tfidf = TfidfVectorizer(stop_words='english')
    matrix = tfidf.fit_transform([resume_text, jd_text])
    
    # Calculate geometric angle (Cosine Similarity)
    match_score = int(cosine_similarity(matrix[0:1], matrix[1:2])[0][0] * 100)
    
    # Simple Gap Finder
    jd_words = set(re.findall(r'\b\w+\b', jd_text.lower()))
    res_words = set(re.findall(r'\b\w+\b', resume_text.lower()))
    missing_skills = list(jd_words - res_words)
    
    return match_score, missing_skills[:5] # Return top 5 gaps

def magic_rewrite(skill):
    """Dynamic Action-Result Rewrite logic"""
    rewrites = {
        "react": "Architected a responsive UI using React, improving user retention metrics by 15% through optimized load times.",
        "python": "Engineered automated data pipelines in Python, reducing manual processing time by 30%.",
        "sql": "Optimized complex SQL queries to handle 1M+ rows, resulting in 2x faster database response times.",
        "aws": "Deployed scalable cloud infrastructure on AWS, ensuring 99.9% uptime for high-traffic applications.",
        "docker": "Containerized microservices using Docker, standardizing the CI/CD pipeline and reducing deployment failures."
    }
    return rewrites.get(skill.lower(), f"Leveraged {skill} to solve complex technical challenges and deliver production-grade code.")

def analyze_student_answer(answer, target_skill):
    """Real-time linguistic checking for anti-cheating"""
    impact_words = ["optimized", "architected", "integrated", "solved", "built", "developed", "reduced", "improved"]
    word_count = len(answer.split())
    
    if word_count < 15:
        return "❌ **Too short!** Recruiters want implementation details. Mention a specific challenge you faced.", "low"
    
    impact_score = sum(1 for word in impact_words if word in answer.lower())
    skill_mentioned = target_skill.lower() in answer.lower()
    
    if impact_score >= 2 and skill_mentioned:
        return "✅ **Great!** You used high-impact action verbs. You sound like a real engineer.", "high"
    elif skill_mentioned:
        return f"⚠️ **Okay.** You mentioned {target_skill}, but try to use verbs like 'Optimized' or 'Architected' to show impact.", "mid"
    else:
        return f"❌ **Missed the mark.** You didn't even mention the core skill ({target_skill})! Try again.", "low"


# ==========================================
# UI FRONTEND
# ==========================================
st.title("🚀 CareerCraft AI: From Resume to Job Ready")
st.write("The Build-to-Hire Loop for the Modern Engineer")

# --- SIDEBAR: JOB DESCRIPTION & FALLBACK ---
st.sidebar.header("🎯 Target Role (Input)")
jd_input = st.sidebar.text_area("Paste Job Description here:", height=200, placeholder="E.g., Looking for a React developer with Docker experience...")

# --- MAIN DASHBOARD TABS ---
tab1, tab2, tab3 = st.tabs(["🎓 Student View (Analyze & Build)", "🤖 Interview Grill", "👔 Recruiter View"])

# ------------------------------------------
# TAB 1: STUDENT VIEW (The Fixes are Here)
# ------------------------------------------
with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📄 Your Resume")
        # Fallback Paste Method implemented
        resume_input = st.text_area("Paste Resume Text (Fallback for slow networks):", height=200)
        
        analyze_btn = st.button("🔍 Analyze Skill Gap")

    if analyze_btn and resume_input and jd_input:
        score, gaps = calculate_match(resume_input, jd_input)
        st.session_state['score'] = score
        st.session_state['gaps'] = gaps
    
    with col2:
        if 'score' in st.session_state:
            score = st.session_state['score']
            gaps = st.session_state['gaps']
            
            # 1. FIXED PROGRESS BAR (Now Dynamic)
            st.subheader(f"📊 Match Score: {score}%")
            st.progress(score / 100.0)
            
            # Relatable Feedback based on score
            if score < 40:
                st.error("Ouch! You're speaking 'Student'. Let's help you speak 'Engineer'.")
            elif score < 75:
                st.warning("Good start, but you need more technical depth to beat the ATS.")
            else:
                st.success("Looking sharp! You're almost in the interview room.")

            st.markdown("---")
            st.subheader("🛠️ Micro-Project Blueprints")
            
            # 2. THE LPA HOOK & PROJECT GENERATOR
            target_skill = gaps[0] if gaps else "react" # Default to react if no gaps
            st.session_state['target_skill'] = target_skill # Save for interview tab
            
            st.markdown(f"""
            <div class='project-card'>
                <h4>Missing Skill: {target_skill.capitalize()}</h4>
                <p><b>Blueprint:</b> Build a fully responsive Kanban Board (Trello Clone) with drag-and-drop.</p>
                <p style='color: #4CAF50; font-weight: bold;'>💰 Estimated Market Value Boost: +₹4.5 LPA</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 3. FIXED MAGIC REWRITE
            with st.expander("✨ Peek at Magic Rewrite (For your Resume)"):
                improved_text = magic_rewrite(target_skill)
                st.code(improved_text, language='markdown')

# ------------------------------------------
# TAB 2: INTERVIEW GRILL (Anti-Cheating Fix)
# ------------------------------------------
with tab2:
    st.header("🎤 The Interview Grill")
    current_skill = st.session_state.get('target_skill', 'React').capitalize()
    
    st.info(f"**Verification Question:** Explain how you would optimize the state management in a large-scale {current_skill} application.")
    
    user_answer = st.text_area("Type your technical answer here:", height=150)
    
    if st.button("🧠 Verify My Answer"):
        if user_answer:
            # 4. FIXED ANALYZER (No longer static)
            feedback, status = analyze_student_answer(user_answer, current_skill)
            if status == "high":
                st.success(feedback)
            elif status == "mid":
                st.warning(feedback)
            else:
                st.error(feedback)
        else:
            st.warning("Please type an answer first.")

# ------------------------------------------
# TAB 3: RECRUITER VIEW
# ------------------------------------------
with tab3:
    st.header("👔 Hiring Manager Dashboard")
    
    if 'score' in st.session_state:
        st.subheader("Candidate Risk Assessment")
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.metric("Technical Score", f"{st.session_state['score']}%")
            st.metric("Persona Match", "Backend Developer")
        
        with col_r2:
            st.markdown("### 🎣 Trap Questions for Interview")
            current_skill = st.session_state.get('target_skill', 'React').capitalize()
            st.write(f"1. Ask them to whiteboard the data flow in their {current_skill} project.")
            st.write("2. Ask: 'What was the hardest bug you fixed and how?' (Tests implementation reality).")
    else:
        st.info("Run an analysis in the Student View to generate Recruiter insights.")
