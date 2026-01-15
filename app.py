import streamlit as st
import pdfplumber
import re
from collections import Counter

# ---------------- CONFIG ----------------
st.set_page_config(page_title="CareerCraft AI", page_icon="✨", layout="wide")

# ---------------- SKILL DICTIONARY ----------------
SKILL_DB = {
    "software": ["python", "java", "git", "oop", "data structures", "debugging"],
    "data": ["excel", "sql", "python", "statistics", "visualization"],
    "uiux": ["figma", "adobe xd", "wireframes", "prototyping", "design principles"]
}

ROLE_SKILLS = {
    "Software Engineer": SKILL_DB["software"],
    "Backend Developer": ["python", "java", "sql", "api", "git"],
    "Data Analyst": SKILL_DB["data"],
    "UI/UX Designer": SKILL_DB["uiux"]
}

LEARNING_RESOURCES = {
    "debugging": "Debugging Best Practices – Google",
    "oop": "Object-Oriented Programming – Udemy",
    "data structures": "DSA – GeeksforGeeks",
    "sql": "SQL Basics – Khan Academy",
    "excel": "Excel for Analysis – Coursera",
    "figma": "Figma UI Design – Figma Learn"
}

STOPWORDS = {
    "the","and","to","of","in","for","with","a","is","are","we","will",
    "should","good","required","candidate","looking","include","includes"
}

# ---------------- FUNCTIONS ----------------
def extract_text_from_pdf(pdf):
    text = ""
    with pdfplumber.open(pdf) as p:
        for page in p.pages:
            text += page.extract_text() or ""
    return text.lower()

def clean_words(text):
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return [w for w in words if w not in STOPWORDS]

def extract_skills(text):
    found = set()
    for group in SKILL_DB.values():
        for skill in group:
            if skill in text:
                found.add(skill)
    return sorted(found)

def match_percentage(resume, jd):
    if not jd:
        return 0
    return int((len(resume & jd) / len(jd)) * 100)

# ---------------- UI ----------------
st.title("✨ CareerCraft AI")
st.caption("Skill gap → learning plan → job-ready")

uploaded_file = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])
jd_text = st.text_area("📌 Paste Job Description")
name = st.text_input("Your Full Name")

if uploaded_file and jd_text:
    resume_text = extract_text_from_pdf(uploaded_file)
    resume_skills = set(extract_skills(resume_text))
    jd_skills = set(extract_skills(jd_text.lower()))

    matched = resume_skills & jd_skills
    missing = jd_skills - resume_skills
    ats = match_percentage(resume_skills, jd_skills)

    # ---------------- ATS ----------------
    st.subheader("🎯 ATS Readiness")
    st.progress(ats)
    st.write(f"**{ats}% Match**")

    # ---------------- ROLE FIT ----------------
    st.subheader("🏆 Job Roles That Fit You Best")
    for role, skills in ROLE_SKILLS.items():
        score = match_percentage(resume_skills, set(skills))
        if score > 0:
            st.write(f"**{role} — {score}% match**")

    # ---------------- SKILL GAP ----------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💚 Skills Matched")
        for s in matched:
            st.success(s)

    with col2:
        st.subheader("🌱 Skills Missing")
        for s in missing:
            st.warning(s)

    # ---------------- LEARNING ----------------
    st.subheader("📚 Learning Roadmap")
    for s in missing:
        if s in LEARNING_RESOURCES:
            st.write(f"📘 **{s.title()}** → {LEARNING_RESOURCES[s]}")

    # ---------------- INTERVIEW ----------------
    st.subheader("🎤 Interview Talking Points")
    for s in matched:
        st.write(f"• I have hands-on experience with **{s}** through academic and personal projects.")
    st.write("• I am actively strengthening missing skills to become industry-ready.")

    # ---------------- LINKEDIN ----------------
    st.subheader("💼 LinkedIn About")
    role_guess = max(ROLE_SKILLS, key=lambda r: match_percentage(resume_skills, set(ROLE_SKILLS[r])))
    st.code(
        f"Aspiring {role_guess} with hands-on experience in "
        f"{', '.join(matched)}. Actively building strong foundations and real-world skills."
    )
