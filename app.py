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

def generate_resume_docx(name, role, skills):
    doc = Document()
    doc.add_heading(name, level=1)
    doc.add_paragraph(f"Aspiring {role}")

    doc.add_heading("Professional Summary", level=2)
    doc.add_paragraph(
        f"Motivated student with hands-on exposure to {', '.join(skills)} "
        f"and a strong interest in growing as a {role}."
    )

    doc.add_heading("Core Skills", level=2)
    doc.add_paragraph(", ".join(skills))

    doc.add_heading("Projects & Experience", level=2)
    doc.add_paragraph(
        "• Academic and personal projects demonstrating practical application\n"
        "• Experience with collaborative tools and structured problem-solving"
    )

    doc.add_heading("Learning Focus", level=2)
    doc.add_paragraph(
        "Actively strengthening role-specific and production-ready skills."
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
    c.drawString(50, 680, "Focused on building industry-ready capabilities.")
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
    role = "Target Role"
    jd_text = st.text_area("Paste Job Description")
    role_skills = list(set(re.findall(r"[a-zA-Z]+", jd_text.lower())))

name = st.text_input("Your Full Name")

if resume and name and role_skills:
    resume_text = extract_text(resume)
    found = extract_skills(resume_text, role_skills)
    missing = list(set(role_skills) - set(found))

    # ---------------- ATS SCORE ----------------
    ats_score = int((len(found) / len(role_skills)) * 100)

    st.subheader("🎯 ATS Readiness Score")
    if ats_score < 40:
        st.warning(f"{ats_score}% — Early stage (Best for internships & learning roles)")
    elif ats_score < 70:
        st.info(f"{ats_score}% — Interview-ready for entry-level roles")
    else:
        st.success(f"{ats_score}% — Strong ATS match for this role")

    # ---------------- SKILLS ----------------
    st.subheader("🧩 Skill Matching & Growth Areas")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("<div class='card'><h4>💚 Skills You Have</h4></div>", unsafe_allow_html=True)
        for s in found:
            st.markdown(f"<span class='badge'>{s}</span>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='card'><h4>🌱 Skills to Learn</h4></div>", unsafe_allow_html=True)
        for s in missing:
            st.markdown(f"<span class='badge missing'>{s}</span>", unsafe_allow_html=True)

    # ---------------- LEARNING ----------------
    st.subheader("📚 Learning Roadmap")
    for s in missing:
        st.markdown(f"**{s.upper()}** → {COURSES.get(s, 'Recommended industry resources')}")

    # ---------------- RESUME DOWNLOAD ----------------
    st.subheader("📄 Generated Resume")

    doc = generate_resume_docx(name, role, found)
    doc_path = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    doc.save(doc_path.name)

    pdf_path = generate_pdf_resume(name, role, found)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button("⬇ Download Resume (DOCX)", open(doc_path.name, "rb"), file_name="resume.docx")
    with col2:
        st.download_button("⬇ Download Resume (PDF)", open(pdf_path, "rb"), file_name="resume.pdf")

    # ---------------- COVER LETTER ----------------
    st.subheader("✉ Premium Cover Letter")
    st.text_area(
        "",
        f"""Dear Hiring Manager,

I am applying for the {role} position. My experience with {', '.join(found)} aligns well with the role’s expectations, and I am actively strengthening additional skills required for professional excellence.

I bring a strong learning mindset, honesty about my growth stage, and enthusiasm to contribute meaningfully.

Sincerely,
{name}
""",
        height=260
    )
