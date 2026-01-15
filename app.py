import streamlit as st
import pdfplumber
import re
from collections import Counter
from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import tempfile

# ---------------- UI ----------------
st.set_page_config(page_title="CareerCraft AI", layout="wide")

st.markdown("""
<style>
body { background-color: #f8fbff; }
h1 { color:#2563eb; }
.metric { background:#eef2ff; padding:16px; border-radius:12px; text-align:center; }
</style>
""", unsafe_allow_html=True)

st.title("✨ CareerCraft AI")
st.caption("Skill gap → learning plan → job-ready")

# ---------------- SKILL LOGIC ----------------
STOPWORDS = {
    "a","an","the","and","or","to","in","of","for","with","as","on","we",
    "are","is","was","were","be","being","been","such","that","this",
    "it","they","their","you","your","i"
}

VALID_SKILLS = {
    "python","java","sql","git","github","docker",
    "data structures","oop","object oriented programming",
    "debugging","software development","problem solving",
    "api","backend development","databases"
}

ROLE_SKILLS = {
    "Software Engineer": {
        "python","java","data structures","oop","debugging","git"
    },
    "Backend Developer": {
        "python","java","api","databases","sql","docker","git"
    },
    "Data Analyst": {
        "python","sql","problem solving","databases"
    }
}

LEARNING_RESOURCES = {
    "python":"Python for Everybody – Coursera",
    "java":"Java Programming – Coursera",
    "data structures":"DSA – GeeksforGeeks",
    "oop":"Object-Oriented Programming – Udemy",
    "object oriented programming":"OOP Concepts – Udemy",
    "debugging":"Debugging Best Practices – Google",
    "git":"Git & GitHub – freeCodeCamp",
    "sql":"SQL for Data Analysis – Mode",
    "docker":"Docker Essentials – IBM",
    "api":"REST APIs – freeCodeCamp",
    "databases":"Database Fundamentals – Coursera"
}

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z ]"," ",text)
    return text

def extract_skills(text):
    text = clean_text(text)
    found = set()
    for skill in VALID_SKILLS:
        if skill in text:
            found.add(skill)
    return found

# ---------------- INPUT ----------------
resume_file = st.file_uploader("📄 Upload Resume (PDF)", type="pdf")

job_mode = st.radio("Job Input Mode", ["Preset Role", "Custom JD"])

target_role = None
jd_text = ""

if job_mode == "Preset Role":
    target_role = st.selectbox("Select Role", list(ROLE_SKILLS.keys()))
else:
    jd_text = st.text_area("Paste Job Description")

name = st.text_input("Your Full Name")

# ---------------- PROCESS ----------------
if resume_file:
    with pdfplumber.open(resume_file) as pdf:
        resume_text = " ".join(page.extract_text() or "" for page in pdf.pages)

    resume_skills = extract_skills(resume_text)

    if job_mode == "Preset Role":
        required_skills = ROLE_SKILLS[target_role]
    else:
        required_skills = extract_skills(jd_text)

    matched = resume_skills & required_skills
    missing = required_skills - resume_skills

    ats_score = int((len(matched) / max(len(required_skills),1)) * 100)

    # ---------------- METRICS ----------------
    c1,c2,c3 = st.columns(3)
    c1.metric("🎯 ATS Readiness", f"{ats_score}%")
    c2.metric("💚 Skills Matched", len(matched))
    c3.metric("🌱 Skills Missing", len(missing))

    # ---------------- JOB ROLE RECOMMENDATION ----------------
    st.subheader("🏆 Job Roles That Fit You Best")
    for role,skills in ROLE_SKILLS.items():
        score = int((len(resume_skills & skills)/len(skills))*100)
        st.write(f"**{role}** — {score}% match")

    # ---------------- TABLE ----------------
    st.subheader("🧩 Skill Match & Gaps")
    col1,col2 = st.columns(2)
    with col1:
        st.success("💚 Strengths")
        for s in matched:
            st.write("•", s.title())
    with col2:
        st.warning("🌱 Improve Next")
        for s in missing:
            st.write("•", s.title())

    # ---------------- LEARNING ----------------
    st.subheader("📚 Learning Roadmap")
    for s in missing:
        st.write(f"📘 **{s.title()}** → {LEARNING_RESOURCES.get(s,'Industry resources')}")

    # ---------------- INTERVIEW ----------------
    st.subheader("🎤 Interview Talking Points")
    for s in matched:
        st.write(f"• I have hands-on experience with **{s}** through academic and personal projects.")
    if missing:
        st.write("• I am actively learning missing skills to become fully industry-ready.")

    # ---------------- RECRUITER ----------------
    st.subheader("👀 Recruiter View")
    st.info("Strong fundamentals, honest profile, motivated learner. Good internship/entry-level potential.")

    # ---------------- LINKEDIN ----------------
    st.subheader("💼 LinkedIn About")
    linkedin_text = (
        f"Aspiring {target_role or 'Software Developer'} with hands-on experience in "
        + ", ".join(matched)
        + ". Actively strengthening core technical skills and industry best practices."
    )
    st.code(linkedin_text)

    # ---------------- RESUME DOCX ----------------
    doc = Document()
    doc.add_heading(name, 0)
    doc.add_paragraph(f"Target Role: {target_role}")
    doc.add_heading("Skills", level=1)
    doc.add_paragraph(", ".join(resume_skills))
    doc.add_heading("Career Focus", level=1)
    doc.add_paragraph("Motivated student building real-world software skills.")

    tmp_docx = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    doc.save(tmp_docx.name)

    st.download_button("⬇ Download Resume (DOCX)", open(tmp_docx.name,"rb"),
                       file_name="resume.docx")

    # ---------------- PDF ----------------
    tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(tmp_pdf.name, pagesize=A4)
    c.setFont("Helvetica", 11)
    y = 800
    c.drawString(50,y,name); y-=30
    c.drawString(50,y,f"Target Role: {target_role}"); y-=30
    c.drawString(50,y,"Skills:"); y-=20
    for s in resume_skills:
        c.drawString(70,y,f"- {s}"); y-=15
    c.save()

    st.download_button("⬇ Download Resume (PDF)", open(tmp_pdf.name,"rb"),
                       file_name="resume.pdf")

    # ---------------- COVER LETTER ----------------
    st.subheader("✉ Premium Cover Letter")
    cover = f"""
Dear Hiring Manager,

I am applying for the {target_role} role. I bring hands-on experience in {", ".join(matched)}
and am actively strengthening my skills in {", ".join(missing)}.

I am eager to contribute, learn, and grow within your team.

Sincerely,
{name}
"""
    st.text_area("", cover, height=220)
