import streamlit as st
import pdfplumber
import plotly.graph_objects as go
import numpy as np
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
background:rgba(255,255,255,0.92);
padding:1.6rem;
border-radius:22px;
box-shadow:0 20px 45px rgba(0,0,0,0.18);
margin-bottom:1.4rem;
}
.metric{
font-size:2.4rem;
font-weight:800;
color:#2563eb;
}
.soft{
color:#334155;
}
.badge{
display:inline-block;
padding:6px 14px;
border-radius:999px;
background:#e0f2fe;
color:#0369a1;
font-weight:600;
margin-right:8px;
}
.success{color:#16a34a;font-weight:700;}
.warn{color:#ea580c;font-weight:700;}
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
    text=""
    with pdfplumber.open(pdf) as p:
        for page in p.pages:
            text+=page.extract_text() or ""
    return text.lower()

def extract_skills(text):
    return sorted({s for s in SKILLS if s in text})

def similarity(a,b):
    vec=CountVectorizer().fit_transform([a,b])
    return cosine_similarity(vec)[0][1]

# ---------------- RESUME DATA ----------------
def resume_data(name,role,skills):
    return {
        "name":name,
        "role":role,
        "summary":f"Motivated {role} aspirant with hands-on exposure to {', '.join(skills[:4])}. Strong foundation in problem-solving, APIs, and data handling, eager to grow in real-world development environments.",
        "skills":skills,
        "projects":[
            f"Designed and implemented backend components using {skills[0]} with clean API structures.",
            "Collaborated using Git for version control and followed structured development practices.",
            "Focused on writing readable, maintainable, and scalable code."
        ],
        "education":"Undergraduate Student / Bachelor’s Degree"
    }

# ---------------- RESUME PDF ----------------
def resume_pdf(r):
    tmp=tempfile.NamedTemporaryFile(delete=False,suffix=".pdf")
    doc=SimpleDocTemplate(tmp.name,pagesize=A4)
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Name",fontSize=22,alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="Sec",fontSize=13,textColor="#2563eb",spaceBefore=12))
    content=[
        Paragraph(r["name"],styles["Name"]),
        Paragraph(r["role"],styles["Heading2"]),
        Paragraph("PROFESSIONAL SUMMARY",styles["Sec"]),
        Paragraph(r["summary"],styles["Normal"]),
        Paragraph("SKILLS",styles["Sec"]),
        Paragraph(", ".join(r["skills"]),styles["Normal"]),
        Paragraph("PROJECT EXPERIENCE",styles["Sec"])
    ]
    for p in r["projects"]:
        content.append(Paragraph(f"- {p}",styles["Normal"]))
    content.append(Paragraph("EDUCATION",styles["Sec"]))
    content.append(Paragraph(r["education"],styles["Normal"]))
    doc.build(content)
    return tmp.name

# ---------------- RESUME DOCX ----------------
def resume_docx(r):
    d=Document()
    p=d.add_paragraph(r["name"])
    p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].bold=True
    p.runs[0].font.size=Pt(22)
    d.add_paragraph(r["role"]).alignment=WD_ALIGN_PARAGRAPH.CENTER
    def sec(t):
        s=d.add_paragraph(t); s.runs[0].bold=True
    sec("PROFESSIONAL SUMMARY"); d.add_paragraph(r["summary"])
    sec("SKILLS"); d.add_paragraph(", ".join(r["skills"]))
    sec("PROJECT EXPERIENCE")
    for x in r["projects"]: d.add_paragraph(x,style="List Bullet")
    sec("EDUCATION"); d.add_paragraph(r["education"])
    tmp=tempfile.NamedTemporaryFile(delete=False,suffix=".docx")
    d.save(tmp.name)
    return tmp.name

# ---------------- COVER LETTER ----------------
def cover(role,skills):
    return f"""
Dear Hiring Manager,

I am applying for the {role} role with a strong interest in building reliable and well-structured software systems.

My current experience with {", ".join(skills[:4])} has helped me develop a solid technical foundation. I am actively strengthening my skills to align with industry expectations and would value the opportunity to grow within a professional team.

Thank you for considering my application.

Sincerely,
Candidate
"""

# ---------------- UI ----------------
st.title("✨ CareerCraft AI")
st.caption("Your personal career mentor — not just a resume checker")

c1,c2=st.columns(2)
pdf=c1.file_uploader("Upload your resume (PDF)",type="pdf")
mode=c2.radio("Job input mode",["Preset Role","Custom JD"])

if mode=="Preset Role":
    role=st.selectbox("Target role",ROLE_PRESETS)
    jd=ROLE_PRESETS[role]
else:
    role=st.text_input("Target role")
    jd=st.text_area("Paste job description")

name=st.text_input("Your full name")

# ---------------- ANALYSIS ----------------
if pdf and jd and name:
    text=extract_text(pdf)
    skills=extract_skills(text)
    raw=int(similarity(text,jd)*100)
    readiness=max(45,raw+25)

    required=set(jd.split())
    missing=[s for s in required if s not in skills and s in SKILLS]

    # ---- LEVEL SYSTEM ----
    if readiness < 55:
        level="Foundation Stage"
        msg="You are building your core technical base."
    elif readiness < 75:
        level="Growth Stage"
        msg="You are close to being job-ready."
    else:
        level="Apply Stage"
        msg="You can confidently start applying."

    # ---- METRICS ----
    a,b,c=st.columns(3)
    a.markdown(f"<div class='card'><h3>🎯 Career Stage</h3><div class='metric'>{level}</div><p class='soft'>{msg}</p></div>",unsafe_allow_html=True)
    b.markdown(f"<div class='card'><h3>🧠 Skills to Strengthen</h3><div class='metric'>{len(missing)}</div><p class='soft'>Clear & achievable gaps</p></div>",unsafe_allow_html=True)
    c.markdown(f"<div class='card'><h3>🚀 Readiness Score</h3><div class='metric'>{readiness}%</div><p class='soft'>Not a judgment — a direction</p></div>",unsafe_allow_html=True)

    # ---- APPLY NOW ----
    st.markdown("""
    <div class='card'>
    <h3>✅ Roles you can apply for NOW</h3>
    <span class='badge'>Backend Intern</span>
    <span class='badge'>Junior API Developer</span>
    <span class='badge'>Software Trainee</span>
    <br><br>
    <b>🔓 Roles unlocked after roadmap:</b><br>
    Backend Developer · Software Engineer
    </div>
    """,unsafe_allow_html=True)

    # ---- SKILL GRAPH ----
    st.subheader("📊 Skill readiness snapshot")
    fig=go.Figure(go.Bar(
        x=["Skills Present","Skills to Strengthen"],
        y=[len(skills),len(missing)],
        marker_color=["#22c55e","#f97316"]
    ))
    st.plotly_chart(fig,use_container_width=True)

    # ---- ROADMAP ----
    st.subheader("📚 Your guided learning mission")
    for s in missing:
        if s in COURSES:
            title,time=COURSES[s]
            st.markdown(f"""
            <div class='card'>
            <b>🎯 {s.upper()}</b><br>
            Course: {title}<br>
            Time: {time}<br>
            Why it matters: Required in real job workflows
            </div>
            """,unsafe_allow_html=True)

    # ---- RESUME ----
    r=resume_data(name,role,skills)
    st.subheader("📄 Your upgraded resume")
    st.caption("We improved clarity, role alignment, and ATS relevance")

    with open(resume_pdf(r),"rb") as f:
        st.download_button("⬇ Download Resume (PDF)",f,"resume.pdf")
    with open(resume_docx(r),"rb") as f:
        st.download_button("⬇ Download Resume (DOCX)",f,"resume.docx")

    # ---- COVER ----
    cl=cover(role,skills)
    st.subheader("✉ Your personalized cover letter")
    st.caption("Honest, student-appropriate, and professional")
    st.markdown(f"<div class='card'><pre>{cl}</pre></div>",unsafe_allow_html=True)

else:
    st.info("Upload your resume and choose a target role to begin your career analysis.")
