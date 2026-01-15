import streamlit as st
import pdfplumber
import re
from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
import tempfile

# ---------------- UI ----------------
st.set_page_config(page_title="CareerCraft AI", layout="wide")

st.markdown("""
<style>
body { background-color: #f8fbff; }
h1 { color:#2563eb; }
</style>
""", unsafe_allow_html=True)

st.title("✨ CareerCraft AI")
st.caption("Skill gap → learning plan → job-ready")

# ---------------- SKILL LOGIC ----------------
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
    return {skill for skill in VALID_SKILLS if skill in text}

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

    role_scores = {}
    for role, skills in ROLE_SKILLS.items():
        role_scores[role] = len(resume_skills & skills)

    best_fit_role = max(role_scores, key=role_scores.get)
    display_role = target_role if target_role else best_fit_role

    required_skills = ROLE_SKILLS[display_role]
    matched = resume_skills & required_skills
    missing = required_skills - resume_skills

    ats_score = int((len(matched) / max(len(required_skills), 1)) * 100)

    # ---------------- METRICS ----------------
    c1, c2, c3 = st.columns(3)
    c1.metric("🎯 ATS Readiness", f"{ats_score}%")
    c2.metric("💚 Skills Matched", len(matched))
    c3.metric("🌱 Skills Missing", len(missing))

    # ---------------- ROLE FIT ----------------
    st.subheader("🏆 Job Roles That Fit You Best")
    for role, score in sorted(role_scores.items(), key=lambda x: -x[1]):
        percent = int((score / len(ROLE_SKILLS[role])) * 100)
        st.write(f"**{role}** — {percent}% match")

    # ---------------- SKILLS ----------------
    st.subheader("🧩 Skill Match & Gaps")
    col1, col2 = st.columns(2)
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
        st.write(f"📘 **{s.title()}** → {LEARNING_RESOURCES[s]}")

    # ---------------- INTERVIEW ----------------
    st.subheader("🎤 Interview Talking Points")
    for s in matched:
        st.write(f"• I have hands-on experience with **{s}** through academic and personal projects.")
    st.write("• I am actively strengthening missing skills to become industry-ready.")

    # ---------------- LINKEDIN ----------------
    st.subheader("💼 LinkedIn About")
    linkedin = (
        f"Aspiring {display_role} with hands-on experience in "
        f"{', '.join(matched)}. Actively building strong foundations and real-world skills."
    )
    st.code(linkedin)

    # ---------------- DOCX RESUME ----------------
    doc = Document()
    doc.add_heading(name.upper(), 0).alignment = 1
    doc.add_paragraph(display_role).alignment = 1

    doc.add_heading("Professional Summary", 1)
    doc.add_paragraph(
        f"Motivated student aspiring {display_role} with hands-on experience in "
        f"{', '.join(matched)}."
    )

    doc.add_heading("Technical Skills", 1)
    doc.add_paragraph(", ".join(resume_skills))

    doc.add_heading("Learning Focus", 1)
    for s in missing:
        doc.add_paragraph(f"• {s.title()}")

    tmp_docx = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    doc.save(tmp_docx.name)
    st.download_button("⬇ Download Resume (DOCX)", open(tmp_docx.name, "rb"), "CareerCraft_Resume.docx")

    # ---------------- PDF RESUME ----------------
    tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    styles = getSampleStyleSheet()
    pdf = SimpleDocTemplate(tmp_pdf.name, pagesize=A4, rightMargin=40, leftMargin=40)

    elements = [
        Paragraph(f"<b><font size=18>{name}</font></b>", styles["Title"]),
        Paragraph(display_role, styles["Normal"]),
        Spacer(1, 12),
        Paragraph("<b>Professional Summary</b>", styles["Heading2"]),
        Paragraph(
            f"Motivated student aspiring {display_role} with hands-on experience in "
            f"{', '.join(matched)}.",
            styles["Normal"]
        ),
        Spacer(1, 12),
        Paragraph("<b>Technical Skills</b>", styles["Heading2"]),
        Paragraph(", ".join(resume_skills), styles["Normal"]),
        Spacer(1, 12),
        Paragraph("<b>Learning Focus</b>", styles["Heading2"]),
        ListFlowable(
            [ListItem(Paragraph(s.title(), styles["Normal"])) for s in missing],
            bulletType="bullet"
        )
    ]

    pdf.build(elements)
    st.download_button("⬇ Download Resume (PDF)", open(tmp_pdf.name, "rb"), "CareerCraft_Resume.pdf")
