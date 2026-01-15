import streamlit as st
import pdfplumber
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import tempfile

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="CareerCraft AI",
    page_icon="✨",
    layout="wide"
)

# ---------------- SKILL DATABASE ----------------
SKILLS = {
    "Programming": ["python", "java", "c", "c++", "javascript"],
    "Backend": ["api", "sql", "database", "node", "django", "flask"],
    "Data": ["excel", "sql", "statistics", "python", "visualization", "pandas"],
    "AI/ML": ["machine learning", "deep learning", "tensorflow", "numpy"],
    "UI/UX": ["figma", "adobe xd", "wireframe", "prototype", "design principles"],
    "Tools": ["git", "github", "linux", "docker"]
}

ROLES = {
    "Software Engineer": ["python", "java", "git", "data structures", "oop"],
    "Backend Developer": ["python", "java", "sql", "api", "database"],
    "Frontend Developer": ["javascript", "html", "css", "react"],
    "Data Analyst": ["excel", "sql", "python", "statistics", "visualization"],
    "Machine Learning Engineer": ["python", "machine learning", "numpy"],
    "UI/UX Designer": ["figma", "wireframe", "prototype", "design principles"],
    "DevOps Engineer": ["linux", "docker", "git", "ci/cd"],
    "Business Analyst": ["excel", "sql", "communication"],
    "QA Engineer": ["testing", "debugging", "automation"]
}

LEARNING_RESOURCES = {
    "python": "Python – Coursera",
    "java": "Java Basics – Udemy",
    "sql": "SQL – Khan Academy",
    "excel": "Excel for Data Analysis – Coursera",
    "figma": "Figma Learn",
    "data structures": "DSA – GeeksforGeeks",
    "oop": "OOP – Udemy",
    "debugging": "Debugging Best Practices – Google"
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

def extract_skills(text):
    found = set()
    for skill_group in SKILLS.values():
        for skill in skill_group:
            if skill in text:
                found.add(skill)
    return found

def calculate_match(resume_skills, jd_skills):
    if not jd_skills:
        return 0
    return int((len(resume_skills & jd_skills) / len(jd_skills)) * 100)

def generate_pdf(title, content):
    file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(file.name)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"<b>{title}</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    for line in content.split("\n"):
        elements.append(Paragraph(line, styles["Normal"]))
        elements.append(Spacer(1, 8))

    doc.build(elements)
    return file.name

# ---------------- UI ----------------
st.title("✨ CareerCraft AI")
st.caption("Skill gap → learning plan → job-ready")

resume_file = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])

job_mode = st.radio("Job Input Mode", ["Preset Role", "Custom JD"])

preset_role = None
jd_text = ""

if job_mode == "Preset Role":
    preset_role = st.selectbox("Select Target Role", list(ROLES.keys()))
    jd_text = " ".join(ROLES[preset_role])
else:
    jd_text = st.text_area("Paste Job Description")

name = st.text_input("Your Full Name")

# ---------------- PROCESS ----------------
if resume_file and jd_text and name:
    resume_text = extract_text_from_pdf(resume_file)
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text.lower())

    matched = resume_skills & jd_skills
    missing = jd_skills - resume_skills
    ats_score = calculate_match(resume_skills, jd_skills)

    # ---------------- ATS ----------------
    st.subheader("🎯 ATS Readiness")
    st.progress(ats_score)
    st.write(f"**{ats_score}% Match**")

    # ---------------- ROLE FIT ----------------
    st.subheader("🏆 Job Roles That Fit You Best")
    for role, skills in ROLES.items():
        score = calculate_match(resume_skills, set(skills))
        if score > 0:
            st.write(f"**{role} — {score}% match**")

    # ---------------- SKILL GAP ----------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💚 Skills Matched")
        for s in sorted(matched):
            st.success(s)

    with col2:
        st.subheader("🌱 Skills Missing")
        for s in sorted(missing):
            st.warning(s)

    # ---------------- LEARNING ----------------
    st.subheader("📚 Learning Roadmap")
    for s in missing:
        if s in LEARNING_RESOURCES:
            st.write(f"📘 **{s.title()}** → {LEARNING_RESOURCES[s]}")

    # ---------------- INTERVIEW ----------------
    st.subheader("🎤 Interview Talking Points")
    for s in matched:
        st.write(f"• I have hands-on experience with {s} through academic and personal projects.")
    st.write("• I am actively improving missing skills to become industry-ready.")

    # ---------------- LINKEDIN ----------------
    st.subheader("💼 LinkedIn About")
    role_title = preset_role if preset_role else "Professional"
    linkedin_about = (
        f"Aspiring {role_title} with hands-on experience in "
        f"{', '.join(matched)}. Actively building strong foundations and real-world skills."
    )
    st.code(linkedin_about)

    # ---------------- RESUME ----------------
    st.subheader("📄 Generated Resume")
    resume_text_gen = f"""
Name: {name}

Target Role: {role_title}

Key Skills:
{', '.join(matched)}

Profile:
Motivated candidate with hands-on experience and strong learning mindset.
"""
    resume_pdf = generate_pdf("Resume", resume_text_gen)
    st.download_button("⬇ Download Resume (PDF)", open(resume_pdf, "rb"), file_name="resume.pdf")

    # ---------------- COVER LETTER ----------------
    st.subheader("✉ Premium Cover Letter")
    cover_letter = f"""
Dear Hiring Manager,

I am writing to apply for the {role_title} role.
I bring hands-on experience in {', '.join(matched)} and am actively strengthening
skills like {', '.join(missing)}.

I am eager to contribute, learn, and grow with your team.

Sincerely,
{name}
"""
    cover_pdf = generate_pdf("Cover Letter", cover_letter)
    st.download_button("⬇ Download Cover Letter (PDF)", open(cover_pdf, "rb"), file_name="cover_letter.pdf")
