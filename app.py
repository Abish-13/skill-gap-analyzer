import streamlit as st
import pdfplumber
from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import tempfile
import re

# ---------------- CONFIG ----------------
st.set_page_config(page_title="CareerCraft AI", page_icon="✨", layout="wide")

# ---------------- STYLES ----------------
st.markdown("""
<style>
body { background-color:#f8fafc; }
.card {
    background:white;
    padding:1.2rem;
    border-radius:14px;
    box-shadow:0 10px 30px rgba(0,0,0,0.06);
    margin-bottom:1rem;
}
.badge {
    display:inline-block;
    padding:6px 12px;
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
h1,h2,h3 { color:#0f172a; }
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
    "react": "React Official Docs",
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

def generate_resume_docx(name, role, skills):
    doc = Document()
    doc.add_heading(name, level=1)
    doc.add_paragraph(role)
    doc.add_heading("Skills", level=2)
    doc.add_paragraph(", ".join(skills))
    doc.add_heading("Projects", level=2)
    doc.add_paragraph("• Built academic and personal projects aligned with role requirements.")
    doc.add_heading("Learning Focus", level=2)
    doc.add_paragraph("Actively strengthening backend fundamentals and deployment skills.")
    return doc

def generate_pdf_resume(name, role, skills):
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(temp.name, pagesize=A4)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 800, name)
    c.setFont("Helvetica", 12)
    c.drawString(50, 770, role)
    c.drawString(50, 730, "Skills:")
    c.drawString(50, 710, ", ".join(skills))
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
else:
    role = "Custom Role"
    jd = st.text_area("Paste Job Description")
    role_skills = list(set(re.findall(r"[a-zA-Z]+", jd.lower())))

name = st.text_input("Your Full Name")

if resume and name:
    text = extract_text(resume)
    found = extract_skills(text, role_skills)
    missing = list(set(role_skills) - set(found))

    st.subheader("🎯 Career Readiness")
    stage = "Foundation Stage" if len(found) < 3 else "Growth Stage"
    st.markdown(f"**{stage}** — You are building toward professional readiness.")

    st.subheader("🧩 Skill Matching & Growth Areas")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='card'><h4>💚 Skills You Already Have</h4></div>", unsafe_allow_html=True)
        for s in found:
            st.markdown(f"<span class='badge'>{s}</span>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'><h4>🌱 Skills To Learn Next</h4></div>", unsafe_allow_html=True)
        for s in missing:
            st.markdown(f"<span class='badge missing'>{s}</span>", unsafe_allow_html=True)

    st.subheader("🚀 Roles You Can Apply For Now")
    st.success("Backend Intern • Software Trainee • Junior Developer")

    st.subheader("📚 30-Day Learning Roadmap")
    for s in missing:
        st.markdown(f"**{s.upper()}** — {COURSES.get(s, 'Industry standard resources')}")

    st.subheader("🎤 Interview Talking Points")
    for s in found:
        st.markdown(f"• I have hands-on experience with **{s}** through academic and personal projects.")

    st.subheader("👀 Recruiter View")
    st.info("Strong foundation, honest profile, learning mindset. Good internship potential.")

    st.subheader("💼 LinkedIn About (Copy-Paste)")
    st.code(f"Student developer with experience in {', '.join(found)} actively building industry-ready skills.")

    st.subheader("📄 Generated Resume")
    doc = generate_resume_docx(name, role, found)
    doc_file = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    doc.save(doc_file.name)

    pdf_file = generate_pdf_resume(name, role, found)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button("⬇ Download Resume (DOCX)", open(doc_file.name, "rb"), file_name="resume.docx")
    with col2:
        st.download_button("⬇ Download Resume (PDF)", open(pdf_file, "rb"), file_name="resume.pdf")

    st.subheader("✉ Premium Cover Letter")
    st.text_area(
        "",
        f"""Dear Hiring Manager,

I am applying for the {role} role. My background in {', '.join(found)} has helped me build a strong technical foundation, and I am actively strengthening my remaining skills to become industry-ready.

I am motivated, honest about my learning journey, and eager to grow within a professional environment.

Sincerely,
{name}""",
        height=220
    )
