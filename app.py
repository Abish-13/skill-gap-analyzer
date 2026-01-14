import streamlit as st
import pdfplumber
import plotly.graph_objects as go
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
st.set_page_config(
    page_title="CareerCraft AI",
    page_icon="✨",
    layout="wide"
)

# ---------------- BRIGHT UI THEME ----------------
st.markdown("""
<style>
body {
 background: linear-gradient(135deg,#667eea,#764ba2,#43cea2);
 color: #0f172a;
}
.glass {
 background: rgba(255,255,255,0.85);
 padding: 1.6rem;
 border-radius: 20px;
 box-shadow: 0 20px 40px rgba(0,0,0,0.15);
 margin-bottom: 1.5rem;
}
.metric {
 font-size: 2.7rem;
 font-weight: 800;
 color: #2563eb;
}
h1,h2,h3 {
 color:#0f172a;
}
label, p, small {
 color:#1e293b !important;
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

# ---------------- UTIL FUNCTIONS ----------------
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

# ---------------- RESUME BUILD ----------------
def build_resume(name, role, skills):
    return {
        "name": name,
        "role": role,
        "summary": f"Motivated candidate seeking a {role} position with strong skills in "
                   f"{', '.join(skills[:4])}. Passionate about real-world problem solving "
                   f"and continuous learning.",
        "skills": skills,
        "projects": [
            f"Built a real-world project using {skills[0]} with clean and scalable code.",
            "Collaborated using Git and followed best development practices.",
            "Focused on performance, readability, and maintainability."
        ],
        "education": "Bachelor’s Degree / Undergraduate Student"
    }

# ---------------- PDF RESUME ----------------
def resume_pdf(resume):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp.name, pagesize=A4, rightMargin=40,leftMargin=40)
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="Name",
        fontSize=22,
        alignment=TA_CENTER,
        spaceAfter=14
    ))
    styles.add(ParagraphStyle(
        name="Section",
        fontSize=13,
        spaceBefore=14,
        spaceAfter=6,
        textColor="#2563eb"
    ))

    content = []
    content.append(Paragraph(resume["name"], styles["Name"]))
    content.append(Paragraph(resume["role"], styles["Heading2"]))

    content.append(Paragraph("PROFESSIONAL SUMMARY", styles["Section"]))
    content.append(Paragraph(resume["summary"], styles["Normal"]))

    content.append(Paragraph("SKILLS", styles["Section"]))
    content.append(Paragraph(", ".join(resume["skills"]), styles["Normal"]))

    content.append(Paragraph("PROJECTS / EXPERIENCE", styles["Section"]))
    for p in resume["projects"]:
        content.append(Paragraph(f"- {p}", styles["Normal"]))

    content.append(Paragraph("EDUCATION", styles["Section"]))
    content.append(Paragraph(resume["education"], styles["Normal"]))

    doc.build(content)
    return tmp.name

# ---------------- DOCX RESUME ----------------
def resume_docx(resume):
    doc = Document()

    name = doc.add_paragraph(resume["name"])
    name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    name.runs[0].bold = True
    name.runs[0].font.size = Pt(22)

    role = doc.add_paragraph(resume["role"])
    role.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def section(title):
        p = doc.add_paragraph(title)
        p.runs[0].bold = True
        p.space_before = Pt(14)

    section("PROFESSIONAL SUMMARY")
    doc.add_paragraph(resume["summary"])

    section("SKILLS")
    doc.add_paragraph(", ".join(resume["skills"]))

    section("PROJECTS / EXPERIENCE")
    for p in resume["projects"]:
        doc.add_paragraph(p, style="List Bullet")

    section("EDUCATION")
    doc.add_paragraph(resume["education"])

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    doc.save(tmp.name)
    return tmp.name

# ---------------- COVER LETTER ----------------
def cover_letter(role, skills):
    return f"""
Dear Hiring Manager,

I am excited to apply for the {role} position. My experience with
{", ".join(skills[:4])} aligns well with your requirements.

I am eager to contribute my skills, learn continuously, and add value
to your team.

Sincerely,
Candidate
"""

def cover_pdf(text):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp.name)
    styles = getSampleStyleSheet()
    doc.build([Paragraph(t, styles["Normal"]) for t in text.split("\n")])
    return tmp.name

def cover_docx(text):
    doc = Document()
    for line in text.split("\n"):
        doc.add_paragraph(line)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    doc.save(tmp.name)
    return tmp.name

# ---------------- UI ----------------
st.title("✨ CareerCraft AI")
st.caption("Build a job-ready resume in minutes")

c1, c2 = st.columns(2)
resume_file = c1.file_uploader("Upload Resume (PDF)", type="pdf")
mode = c2.radio("Job Description Mode", ["Preset Role", "Custom JD"])

if mode == "Preset Role":
    role = st.selectbox("Select Role", ROLE_PRESETS.keys())
    jd = ROLE_PRESETS[role]
else:
    role = st.text_input("Target Job Role")
    jd = st.text_area("Paste Job Description", height=180)

name = st.text_input("Your Full Name")

# ---------------- ANALYSIS ----------------
if resume_file and jd and name:
    rtext = extract_text(resume_file)
    rskills = extract_skills(rtext)

    ats = int(similarity(rtext, jd) * 100)

    col1, col2, col3 = st.columns(3)
    col1.markdown(f"<div class='glass'><h3>ATS Match</h3><div class='metric'>{ats}%</div></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='glass'><h3>Resume Confidence</h3><div class='metric'>{min(95, ats+10)}%</div></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='glass'><h3>Status</h3><div class='metric'>{'READY' if ats>70 else 'IMPROVE'}</div></div>", unsafe_allow_html=True)

    resume_data = build_resume(name, role, rskills)

    st.subheader("📄 Generated Resume")
    pdf_path = resume_pdf(resume_data)
    docx_path = resume_docx(resume_data)

    with open(pdf_path, "rb") as f:
        st.download_button("⬇ Download Resume (PDF)", f, "resume.pdf")
    with open(docx_path, "rb") as f:
        st.download_button("⬇ Download Resume (DOCX)", f, "resume.docx")

    st.subheader("✉ Cover Letter")
    cl = cover_letter(role, rskills)
    st.markdown(f"<div class='glass'><pre>{cl}</pre></div>", unsafe_allow_html=True)

    with open(cover_pdf(cl), "rb") as f:
        st.download_button("⬇ Download Cover Letter (PDF)", f, "cover_letter.pdf")
    with open(cover_docx(cl), "rb") as f:
        st.download_button("⬇ Download Cover Letter (DOCX)", f, "cover_letter.docx")

else:
    st.info("Upload resume, enter name & job role to generate outputs.")
