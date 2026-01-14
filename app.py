import streamlit as st
import pdfplumber
from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import tempfile
import re

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="CareerCraft AI", page_icon="✨", layout="wide")

# ---------------- STYLES ----------------
st.markdown("""
<style>
body { background:#f8fafc; }
.card {
    background:white;
    padding:1.4rem;
    border-radius:16px;
    box-shadow:0 10px 30px rgba(0,0,0,0.08);
    margin-bottom:1.2rem;
}
.badge {
    display:inline-block;
    padding:6px 14px;
    border-radius:999px;
    background:linear-gradient(135deg,#22c55e,#16a34a);
    color:white;
    margin:4px;
    font-size:13px;
}
.missing {
    background:linear-gradient(135deg,#f59e0b,#f97316);
}
.small { color:#475569; font-size:14px; }
</style>
""", unsafe_allow_html=True)

# ---------------- DATA ----------------
ROLE_SKILLS = {
    "Backend Developer": ["python", "sql", "api", "git", "docker"],
    "Frontend Developer": ["html", "css", "javascript", "react"],
    "Data Analyst": ["python", "sql", "excel", "statistics"]
}

COURSES = {
    "sql": "SQL for Data Analysis – Mode Analytics",
    "docker": "Docker Essentials – IBM",
    "react": "React Official Documentation",
    "statistics": "Statistics – Khan Academy",
    "excel": "Excel Skills – Coursera"
}

# ---------------- FUNCTIONS ----------------
def extract_text(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.lower()

def extract_skills(text, skills):
    return [s for s in skills if re.search(rf"\b{s}\b", text)]

def generate_resume_docx(name, role, found_skills):
    doc = Document()
    doc.add_heading(name, level=1)
    doc.add_paragraph(f"Aspiring {role}")
    
    doc.add_heading("Professional Summary", level=2)
    doc.add_paragraph(
        f"Motivated student with hands-on exposure to {', '.join(found_skills)}. "
        f"Actively building role-aligned skills to contribute effectively in entry-level {role} positions."
    )

    doc.add_heading("Core Skills", level=2)
    doc.add_paragraph(", ".join(found_skills))

    doc.add_heading("Projects & Experience", level=2)
    doc.add_paragraph(
        "• Academic and self-driven projects focused on practical application of core technologies.\n"
        "• Experience collaborating with code repositories and structured problem-solving."
    )

    doc.add_heading("Learning & Growth", level=2)
    doc.add_paragraph(
        "Currently strengthening advanced concepts and production-readiness for professional roles."
    )
    return doc

def generate_pdf_resume(name, role, skills):
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(temp.name, pagesize=A4)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 800, name)
    c.setFont("Helvetica", 12)
    c.drawString(50, 770, f"Aspiring {role}")
    c.drawString(50, 730, "Skills:")
    c.drawString(50, 710, ", ".join(skills))
    c.drawString(50, 680, "Focused on building role-aligned, real-world capabilities.")
    c.save()
    return temp.name

# ---------------- UI ----------------
st.title("✨ CareerCraft AI")
st.caption("Skill gap → learning plan → job-ready")

resume = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])

mode = st.radio("Job Input Mode", ["Preset Role", "Custom JD"])

if mode == "Preset Role":
    role = st.selectbox("Select Role", list(ROLE_SKILLS.keys()))
    role_skills = ROLE_SKILLS[role]
    jd_text = f"{role} position requiring skills in {', '.join(role_skills)}"
else:
    role = "Target Role"
    jd_text = st.text_area("Paste Job Description (used for tailoring)")
    role_skills = list(set(re.findall(r"[a-zA-Z]+", jd_text.lower())))

name = st.text_input("Your Full Name")

if resume and name and role_skills:
    resume_text = extract_text(resume)
    found = extract_skills(resume_text, role_skills)
    missing = list(set(role_skills) - set(found))

    # ---------------- CAREER STAGE ----------------
    st.subheader("🎯 Career Stage")
    stage = "Foundation Stage" if len(found) < len(role_skills) / 2 else "Growth Stage"
    st.success(f"{stage} — You are progressing toward {role} readiness.")

    # ---------------- SKILL MATCH TABLE ----------------
    st.subheader("🧩 Skill Matching & Growth Areas")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='card'><h4>💚 Skills Aligned with the Role</h4></div>", unsafe_allow_html=True)
        for s in found:
            st.markdown(f"<span class='badge'>{s}</span>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'><h4>🌱 Skills to Strengthen Next</h4></div>", unsafe_allow_html=True)
        for s in missing:
            st.markdown(f"<span class='badge missing'>{s}</span>", unsafe_allow_html=True)

    # ---------------- APPLY-NOW ROLES ----------------
    st.subheader("🚀 Roles You Can Apply For Now")
    st.info(f"Based on your profile, you are suitable for **{role} Intern**, **Trainee**, and **Junior-level roles**.")

    # ---------------- LEARNING PLAN ----------------
    st.subheader("📚 Targeted Learning Roadmap")
    for s in missing:
        st.markdown(f"**{s.upper()}** → {COURSES.get(s, 'Industry-standard learning resources')}")

    # ---------------- INTERVIEW TALKING POINTS ----------------
    st.subheader("🎤 Interview Talking Points")
    for s in found:
        st.markdown(
            f"• My experience with **{s}** aligns with the expectations of a {role}, "
            f"and I’ve applied it in practical projects."
        )

    # ---------------- RECRUITER VIEW ----------------
    st.subheader("👀 Recruiter View")
    st.success(
        f"Candidate shows a solid foundation relevant to {role}. "
        f"Profile demonstrates honesty, learning momentum, and internship readiness."
    )

    # ---------------- LINKEDIN ABOUT ----------------
    st.subheader("💼 LinkedIn About (Copy-Paste)")
    st.code(
        f"Aspiring {role} with hands-on experience in {', '.join(found)}. "
        f"Currently strengthening role-specific skills and seeking opportunities to grow in real-world environments."
    )

    # ---------------- RESUME DOWNLOAD ----------------
    st.subheader("📄 Generated Resume")
    doc = generate_resume_docx(name, role, found)
    doc_file = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    doc.save(doc_file.name)

    pdf_file = generate_pdf_resume(name, role, found)

    c1, c2 = st.columns(2)
    with c1:
        st.download_button("⬇ Download Resume (DOCX)", open(doc_file.name, "rb"), file_name="resume.docx")
    with c2:
        st.download_button("⬇ Download Resume (PDF)", open(pdf_file.name, "rb"), file_name="resume.pdf")

    # ---------------- COVER LETTER ----------------
    st.subheader("✉ Premium Cover Letter")
    st.text_area(
        "",
        f"""Dear Hiring Manager,

I am writing to express my interest in the {role} position. After reviewing the role requirements, I found a strong alignment with my experience in {', '.join(found)}.

I have actively applied these skills in academic and self-driven projects, and I am currently strengthening additional competencies required for professional excellence in this role. I value learning, adaptability, and ethical growth, and I am eager to contribute while continuing to improve.

Thank you for considering my application.

Sincerely,
{name}
""",
        height=260
    )
