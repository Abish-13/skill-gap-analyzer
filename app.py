import streamlit as st
import pdfplumber
import re
from docx import Document
from docx.shared import Pt
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

# ---------------- LOGIC ----------------
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

    required_skills = ROLE_SKILLS[target_role] if job_mode == "Preset Role" else extract_skills(jd_text)

    matched = resume_skills & required_skills
    missing = required_skills - resume_skills

    ats_score = int((len(matched) / max(len(required_skills),1)) * 100)

    # ---------------- METRICS ----------------
    c1,c2,c3 = st.columns(3)
    c1.metric("🎯 ATS Readiness", f"{ats_score}%")
    c2.metric("💚 Skills Matched", len(matched))
    c3.metric("🌱 Skills Missing", len(missing))

    # ---------------- ROLE FIT ----------------
    st.subheader("🏆 Job Roles That Fit You Best")
    for role,skills in ROLE_SKILLS.items():
        score = int((len(resume_skills & skills)/len(skills))*100)
        st.write(f"**{role}** — {score}% match")

    # ---------------- SKILLS TABLE ----------------
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
        st.write(f"📘 **{s.title()}** → {LEARNING_RESOURCES.get(s)}")

    # ---------------- INTERVIEW ----------------
    st.subheader("🎤 Interview Talking Points")
    for s in matched:
        st.write(f"• I have hands-on experience with **{s}** through academic and personal projects.")
    if missing:
        st.write("• I am actively strengthening my missing skills to become industry-ready.")

    # ---------------- LINKEDIN ----------------
    st.subheader("💼 LinkedIn About")
    linkedin = (
        f"Aspiring {target_role} with hands-on experience in "
        + ", ".join(matched)
        + ". Actively building strong foundations and real-world skills."
    )
    st.code(linkedin)

    # =====================================================================
    # ✅ ONLY FIXED SECTION: BEAUTIFUL RESUME (DOCX + PDF)
    # =====================================================================

    # -------- DOCX --------
    doc = Document()

    name_h = doc.add_heading(name.upper(), 0)
    name_h.alignment = 1

    role_p = doc.add_paragraph(target_role)
    role_p.alignment = 1

    doc.add_paragraph()

    doc.add_heading("PROFESSIONAL SUMMARY", level=1)
    doc.add_paragraph(
        f"Motivated student aspiring {target_role} with hands-on experience in "
        f"{', '.join(matched)}. Actively learning {', '.join(missing)}."
    )

    doc.add_heading("TECHNICAL SKILLS", level=1)
    doc.add_paragraph(", ".join(resume_skills))

    doc.add_heading("PROJECT EXPERIENCE", level=1)
    doc.add_paragraph(
        "• Academic and personal projects applying programming, problem-solving, and debugging skills."
    )

    doc.add_heading("LEARNING FOCUS", level=1)
    for s in missing:
        doc.add_paragraph(f"• {s.title()}")

    tmp_docx = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    doc.save(tmp_docx.name)

    st.download_button("⬇ Download Resume (DOCX)",
                       open(tmp_docx.name,"rb"),
                       file_name="CareerCraft_Resume.docx")

    # -------- PDF --------
    tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    styles = getSampleStyleSheet()
    pdf = SimpleDocTemplate(tmp_pdf.name, pagesize=A4, rightMargin=40, leftMargin=40)

    elements = []
    elements.append(Paragraph(f"<b><font size=18>{name}</font></b>", styles["Title"]))
    elements.append(Paragraph(target_role, styles["Normal"]))
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("<b>PROFESSIONAL SUMMARY</b>", styles["Heading2"]))
    elements.append(Paragraph(
        f"Motivated student aspiring {target_role} with hands-on experience in "
        f"{', '.join(matched)} and actively learning {', '.join(missing)}.",
        styles["Normal"]
    ))

    elements.append(Spacer(1, 12))
    elements.append(Paragraph("<b>TECHNICAL SKILLS</b>", styles["Heading2"]))
    elements.append(Paragraph(", ".join(resume_skills), styles["Normal"]))

    elements.append(Spacer(1, 12))
    elements.append(Paragraph("<b>PROJECT EXPERIENCE</b>", styles["Heading2"]))
    elements.append(Paragraph(
        "Academic and personal projects applying programming, debugging, and problem-solving skills.",
        styles["Normal"]
    ))

    elements.append(Spacer(1, 12))
    elements.append(Paragraph("<b>LEARNING FOCUS</b>", styles["Heading2"]))
    elements.append(ListFlowable(
        [ListItem(Paragraph(s.title(), styles["Normal"])) for s in missing],
        bulletType="bullet"
    ))

    pdf.build(elements)

    st.download_button("⬇ Download Resume (PDF)",
                       open(tmp_pdf.name,"rb"),
                       file_name="CareerCraft_Resume.pdf")

    # ---------------- COVER LETTER ----------------
    st.subheader("✉ Premium Cover Letter")
    cover = f"""
Dear Hiring Manager,

I am applying for the {target_role} role. I bring hands-on experience in {", ".join(matched)}
and am actively strengthening my skills in {", ".join(missing)}.

I am eager to learn, contribute, and grow within your organization.

Sincerely,
{name}
"""
    st.text_area("", cover, height=220)
