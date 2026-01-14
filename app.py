import streamlit as st
import pdfplumber
from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import tempfile, re

# ---------------- CONFIG ----------------
st.set_page_config(page_title="CareerCraft AI", page_icon="✨", layout="wide")

# ---------------- STYLES ----------------
st.markdown("""
<style>
body { background:#f8fafc; }
.card {
    background:white;
    padding:1.6rem;
    border-radius:18px;
    box-shadow:0 12px 32px rgba(0,0,0,0.08);
    margin-bottom:1.4rem;
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
h1,h2,h3 { color:#0f172a; }
.small { color:#475569; }
</style>
""", unsafe_allow_html=True)

# ---------------- DATA ----------------
ROLE_SKILLS = {
    "Backend Developer": ["python", "sql", "api", "git", "docker"],
    "Frontend Developer": ["html", "css", "javascript", "react"],
    "Data Analyst": ["python", "sql", "excel", "statistics"],
    "Software Engineer": ["python", "git", "problem solving", "api"]
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

def job_fit_scores(found):
    scores = {}
    for role, skills in ROLE_SKILLS.items():
        scores[role] = int((len(set(found) & set(skills)) / len(skills)) * 100)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

def generate_beautiful_resume_docx(name, role, skills):
    doc = Document()

    doc.add_heading(name, 0)
    doc.add_paragraph(f"Aspiring {role} | Entry-Level Candidate")

    doc.add_heading("Professional Summary", level=1)
    doc.add_paragraph(
        f"Motivated and detail-oriented student aspiring {role} with hands-on experience in "
        f"{', '.join(skills)}. Passionate about building real-world solutions, learning continuously, "
        f"and contributing responsibly in professional environments."
    )

    doc.add_heading("Core Skills", level=1)
    doc.add_paragraph(", ".join(skills))

    doc.add_heading("Projects & Practical Experience", level=1)
    doc.add_paragraph(
        "• Academic and personal projects demonstrating practical use of technologies\n"
        "• Experience applying concepts through hands-on problem solving\n"
        "• Familiarity with collaborative coding practices"
    )

    doc.add_heading("Learning & Growth", level=1)
    doc.add_paragraph(
        "Actively strengthening advanced concepts, production readiness, and industry best practices."
    )

    return doc

def generate_pdf_resume(name, role, skills):
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(temp.name, pagesize=A4)

    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, 800, name)

    c.setFont("Helvetica", 12)
    c.drawString(50, 770, f"Aspiring {role}")

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 730, "Professional Summary")
    c.setFont("Helvetica", 11)
    c.drawString(50, 710, f"Student with experience in {', '.join(skills)} seeking entry-level opportunities.")

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 670, "Skills")
    c.setFont("Helvetica", 11)
    c.drawString(50, 650, ", ".join(skills))

    c.save()
    return temp.name

# ---------------- UI ----------------
st.title("✨ CareerCraft AI")
st.caption("Skill gap → learning plan → job-ready")

resume = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])
mode = st.radio("Job Input Mode", ["Preset Role", "Custom JD"])

if mode == "Preset Role":
    role = st.selectbox("Select Target Role", list(ROLE_SKILLS.keys()))
    role_skills = ROLE_SKILLS[role]
else:
    role = "Target Role"
    jd = st.text_area("Paste Job Description")
    role_skills = list(set(re.findall(r"[a-zA-Z]+", jd.lower())))

name = st.text_input("Your Full Name")

if resume and name and role_skills:
    text = extract_text(resume)
    found = extract_skills(text, role_skills)
    missing = list(set(role_skills) - set(found))

    ats = int((len(found) / len(role_skills)) * 100)

    st.subheader("🎯 ATS Readiness")
    st.success(f"{ats}% match for {role}")

    # -------- BEST FIT ROLES --------
    st.subheader("🏆 Job Roles That Fit You Best")
    fits = job_fit_scores(found)
    for r, s in fits[:3]:
        st.markdown(f"**{r}** — {s}% match")

    # -------- SKILLS --------
    st.subheader("🧩 Skill Match & Gaps")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='card'><h4>💚 Strengths</h4></div>", unsafe_allow_html=True)
        for s in found:
            st.markdown(f"<span class='badge'>{s}</span>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='card'><h4>🌱 Improve Next</h4></div>", unsafe_allow_html=True)
        for s in missing:
            st.markdown(f"<span class='badge missing'>{s}</span>", unsafe_allow_html=True)

    # -------- LEARNING --------
    st.subheader("📚 Learning Roadmap")
    for s in missing:
        st.markdown(f"**{s.upper()}** → {COURSES.get(s,'Industry resources')}")

    # -------- INTERVIEW --------
    st.subheader("🎤 Interview Talking Points")
    for s in found:
        st.markdown(f"• I have practical experience with **{s}**, aligned with {role} expectations.")

    # -------- RECRUITER VIEW --------
    st.subheader("👀 Recruiter View")
    st.info(f"Strong foundation for {role}. Honest profile with clear growth trajectory.")

    # -------- LINKEDIN --------
    st.subheader("💼 LinkedIn About")
    st.code(
        f"Aspiring {role} with hands-on experience in {', '.join(found)}. "
        f"Focused on building real-world skills and growing professionally."
    )

    # -------- RESUME DOWNLOAD --------
    st.subheader("📄 Beautiful Resume")
    doc = generate_beautiful_resume_docx(name, role, found)
    doc_path = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    doc.save(doc_path.name)

    pdf_path = generate_pdf_resume(name, role, found)

    c1, c2 = st.columns(2)
    with c1:
        st.download_button("⬇ Resume (DOCX)", open(doc_path.name, "rb"), file_name="resume.docx")
    with c2:
        st.download_button("⬇ Resume (PDF)", open(pdf_path, "rb"), file_name="resume.pdf")

    # -------- COVER LETTER --------
    st.subheader("✉ Premium Cover Letter")
    st.text_area(
        "",
        f"""Dear Hiring Manager,

I am excited to apply for the {role} position. My experience in {', '.join(found)} has given me a strong foundation, and I am actively strengthening additional skills required for professional excellence.

I bring curiosity, honesty, and a strong willingness to learn. I would love the opportunity to grow and contribute meaningfully within your team.

Sincerely,
{name}
""",
        height=260
    )
