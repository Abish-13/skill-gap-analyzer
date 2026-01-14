import streamlit as st
import pdfplumber
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import tempfile

# ---------------- PAGE CONFIG ----------------
st.set_page_config("CareerCraft AI", "✨", layout="wide")

# ---------------- UI THEME ----------------
st.markdown("""
<style>
body{
background:linear-gradient(135deg,#6366f1,#22c55e,#06b6d4);
}
.card{
background:rgba(255,255,255,0.94);
padding:1.7rem;
border-radius:22px;
box-shadow:0 18px 40px rgba(0,0,0,0.18);
margin-bottom:1.5rem;
}
.metric{
font-size:2.2rem;
font-weight:800;
color:#2563eb;
}
.soft{color:#334155;}
.badge{
display:inline-block;
padding:7px 16px;
border-radius:999px;
background:#e0f2fe;
color:#0369a1;
font-weight:600;
margin:6px 6px 0 0;
}
.small{
font-size:0.95rem;
color:#475569;
}
</style>
""", unsafe_allow_html=True)

# ---------------- DATA ----------------
SKILLS = [
    "python","java","sql","html","css","javascript","react",
    "node","git","docker","api","rest","ml","data analysis"
]

ROLE_PRESETS = {
    "Backend Developer": "python sql api rest docker git",
    "Frontend Developer": "html css javascript react",
    "Data Analyst": "python sql data analysis excel"
}

COURSES = {
    "sql": ("SQL for Data Analysis – Mode Analytics", "7 days"),
    "docker": ("Docker Essentials – IBM", "5 days"),
    "api": ("REST API Design – FreeCodeCamp", "4 days"),
    "git": ("Git & GitHub – Atlassian", "3 days"),
}

# ---------------- HELPERS ----------------
def extract_text(pdf):
    text = ""
    with pdfplumber.open(pdf) as p:
        for page in p.pages:
            text += page.extract_text() or ""
    return text.lower()

def extract_skills(text):
    return sorted({s for s in SKILLS if s in text})

def similarity(a, b):
    vec = CountVectorizer().fit_transform([a, b])
    return cosine_similarity(vec)[0][1]

# ---------------- RESUME DATA ----------------
def resume_data(name, role, skills, company):
    return {
        "name": name,
        "role": role,
        "summary": (
            f"{role} aspirant with hands-on exposure to "
            f"{', '.join(skills[:4])}. Actively building industry-relevant "
            f"skills and interested in contributing to {company}'s "
            f"engineering team while learning from real-world systems."
        ),
        "skills": skills,
        "projects": [
            f"Implemented backend logic using {skills[0]} with clean API design.",
            "Used Git for version control and collaborative development.",
            "Focused on writing readable, maintainable, and testable code."
        ],
        "portfolio": [
            "GitHub: https://github.com/your-username",
            "Live Project: https://your-project-link.com"
        ],
        "education": "Undergraduate Student / Bachelor’s Degree"
    }

# ---------------- RESUME PDF ----------------
def resume_pdf(r):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp.name, pagesize=A4)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Name", fontSize=22, alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="Sec", fontSize=13, textColor="#2563eb", spaceBefore=12))

    content = [
        Paragraph(r["name"], styles["Name"]),
        Paragraph(r["role"], styles["Heading2"]),
        Paragraph("PROFESSIONAL SUMMARY", styles["Sec"]),
        Paragraph(r["summary"], styles["Normal"]),
        Paragraph("SKILLS", styles["Sec"]),
        Paragraph(", ".join(r["skills"]), styles["Normal"]),
        Paragraph("PROJECT EXPERIENCE", styles["Sec"])
    ]

    for p in r["projects"]:
        content.append(Paragraph(f"- {p}", styles["Normal"]))

    content.append(Paragraph("PORTFOLIO", styles["Sec"]))
    for p in r["portfolio"]:
        content.append(Paragraph(p, styles["Normal"]))

    content.append(Paragraph("EDUCATION", styles["Sec"]))
    content.append(Paragraph(r["education"], styles["Normal"]))

    doc.build(content)
    return tmp.name

# ---------------- RESUME DOCX ----------------
def resume_docx(r):
    d = Document()
    p = d.add_paragraph(r["name"])
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].bold = True
    p.runs[0].font.size = Pt(22)

    d.add_paragraph(r["role"]).alignment = WD_ALIGN_PARAGRAPH.CENTER

    def sec(t):
        s = d.add_paragraph(t)
        s.runs[0].bold = True

    sec("PROFESSIONAL SUMMARY")
    d.add_paragraph(r["summary"])

    sec("SKILLS")
    d.add_paragraph(", ".join(r["skills"]))

    sec("PROJECT EXPERIENCE")
    for p in r["projects"]:
        d.add_paragraph(p, style="List Bullet")

    sec("PORTFOLIO")
    for p in r["portfolio"]:
        d.add_paragraph(p)

    sec("EDUCATION")
    d.add_paragraph(r["education"])

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    d.save(tmp.name)
    return tmp.name

# ---------------- COVER LETTER ----------------
def cover_letter(role, skills, company):
    return f"""
Dear Hiring Manager at {company},

I am writing to apply for the {role} role. My current experience with
{", ".join(skills[:4])} has helped me build a strong technical foundation,
and I am actively strengthening my skills to meet professional standards.

I am particularly interested in growing within {company}, learning from
real-world systems, and contributing with honesty and commitment.

Thank you for your time and consideration.

Sincerely,
Candidate
"""

# ---------------- INTERVIEW TALKING POINTS ----------------
def interview_points(skills, missing):
    points = []
    for s in skills[:3]:
        points.append(f"I have hands-on experience with {s} and understand how it is used in real projects.")
    if missing:
        points.append(
            f"I am currently improving my knowledge of {missing[0]}, focusing on practical usage."
        )
    return points

# ---------------- LINKEDIN ABOUT ----------------
def linkedin_about(role, skills):
    return (
        f"{role} aspirant with hands-on experience in "
        f"{', '.join(skills[:4])}. Passionate about building real-world "
        f"software, learning industry practices, and growing through "
        f"practical project work."
    )

# ---------------- UI ----------------
st.title("✨ CareerCraft AI")
st.caption("A career mentor for students — honest, guiding, and practical")

c1, c2 = st.columns(2)
pdf = c1.file_uploader("Upload your resume (PDF)", type="pdf")
mode = c2.radio("Job input mode", ["Preset Role", "Custom JD"])

if mode == "Preset Role":
    role = st.selectbox("Target role", ROLE_PRESETS)
    jd = ROLE_PRESETS[role]
else:
    role = st.text_input("Target role")
    jd = st.text_area("Paste job description")

company = st.text_input("Target company name")
name = st.text_input("Your full name")

# ---------------- ANALYSIS ----------------
if pdf and jd and name and company:
    text = extract_text(pdf)
    skills = extract_skills(text)
    raw = int(similarity(text, jd) * 100)
    readiness = max(50, raw + 30)

    required = set(jd.split())
    missing = [s for s in required if s not in skills and s in SKILLS]

    # ---- CAREER STAGE ----
    if readiness < 65:
        stage = "Foundation Stage"
        msg = "You are building strong fundamentals."
    elif readiness < 80:
        stage = "Growth Stage"
        msg = "You are close to being job-ready."
    else:
        stage = "Apply Stage"
        msg = "You can confidently apply."

    st.markdown(f"""
    <div class='card'>
    <h3>🎯 Career Stage</h3>
    <div class='metric'>{stage}</div>
    <p class='soft'>{msg}</p>
    </div>
    """, unsafe_allow_html=True)

    # ---- APPLY NOW ----
    st.markdown("""
    <div class='card'>
    <h3>✅ Roles you can apply for now</h3>
    <span class='badge'>Backend Intern</span>
    <span class='badge'>Junior Developer</span>
    <span class='badge'>Software Trainee</span>
    <p class='small'>These roles match your current skill level.</p>
    </div>
    """, unsafe_allow_html=True)

    # ---- RECRUITER VIEW ----
    st.markdown(f"""
    <div class='card'>
    <h3>👀 Recruiter View (External Perspective)</h3>
    <ul>
        <li>Honest student profile with clear fundamentals</li>
        <li>Practical exposure to APIs, Git, and data handling</li>
        <li>Needs production-level exposure in {", ".join(missing) if missing else "advanced topics"}</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    # ---- LEARNING PLAN ----
    st.subheader("📚 Focused learning plan")
    for s in missing:
        if s in COURSES:
            title, time = COURSES[s]
            st.markdown(f"""
            <div class='card'>
            <b>{s.upper()}</b><br>
            Course: {title}<br>
            Time required: {time}<br>
            Outcome: Interview confidence & practical understanding
            </div>
            """, unsafe_allow_html=True)

    # ---- INTERVIEW TALKING POINTS ----
    st.subheader("🎤 Interview talking points (use these safely)")
    for p in interview_points(skills, missing):
        st.markdown(f"- {p}")

    # ---- LINKEDIN ABOUT ----
    st.subheader("💼 LinkedIn About (copy & paste)")
    st.markdown(f"<div class='card'><pre>{linkedin_about(role, skills)}</pre></div>", unsafe_allow_html=True)

    # ---- RESUME ----
    r = resume_data(name, role, skills, company)
    st.subheader("📄 Company-tailored resume")

    with open(resume_pdf(r), "rb") as f:
        st.download_button("⬇ Download Resume (PDF)", f, "resume.pdf")

    with open(resume_docx(r), "rb") as f:
        st.download_button("⬇ Download Resume (DOCX)", f, "resume.docx")

    # ---- COVER LETTER ----
    cl = cover_letter(role, skills, company)
    st.subheader("✉ Company-specific cover letter")
    st.markdown(f"<div class='card'><pre>{cl}</pre></div>", unsafe_allow_html=True)

else:
    st.info("Upload resume and enter role + company details to begin.")
