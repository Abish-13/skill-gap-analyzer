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

# ---------------- CONFIG ----------------
st.set_page_config("CareerCraft AI", "✨", layout="wide")

# ---------------- UI ----------------
st.markdown("""
<style>
body{
background:linear-gradient(135deg,#667eea,#764ba2,#43cea2);
}
.card{
background:rgba(255,255,255,0.9);
padding:1.5rem;
border-radius:20px;
box-shadow:0 15px 35px rgba(0,0,0,0.15);
margin-bottom:1.2rem;
}
.big{
font-size:2.6rem;
font-weight:800;
color:#2563eb;
}
.good{color:#16a34a;}
.warn{color:#ea580c;}
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
    txt=""
    with pdfplumber.open(pdf) as p:
        for pg in p.pages:
            txt+=pg.extract_text() or ""
    return txt.lower()

def extract_skills(text):
    return sorted({s for s in SKILLS if s in text})

def similarity(a,b):
    vec=CountVectorizer().fit_transform([a,b])
    return cosine_similarity(vec)[0][1]

# ---------------- RESUME ----------------
def resume_data(name,role,skills):
    return {
        "name":name,
        "role":role,
        "summary":f"Aspiring {role} with hands-on experience in {', '.join(skills[:4])}. Strong problem-solving mindset and eagerness to work on real-world systems.",
        "skills":skills,
        "projects":[
            f"Developed backend logic using {skills[0]} with clean APIs.",
            "Implemented version control and collaboration using Git.",
            "Focused on scalability, readability and best practices."
        ],
        "education":"Undergraduate Student / Bachelor’s Degree"
    }

def resume_pdf(r):
    tmp=tempfile.NamedTemporaryFile(delete=False,suffix=".pdf")
    doc=SimpleDocTemplate(tmp.name,pagesize=A4)
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Name",fontSize=22,alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="Sec",fontSize=13,textColor="#2563eb",spaceBefore=12))
    content=[
        Paragraph(r["name"],styles["Name"]),
        Paragraph(r["role"],styles["Heading2"]),
        Paragraph("SUMMARY",styles["Sec"]),
        Paragraph(r["summary"],styles["Normal"]),
        Paragraph("SKILLS",styles["Sec"]),
        Paragraph(", ".join(r["skills"]),styles["Normal"]),
        Paragraph("PROJECTS",styles["Sec"])
    ]
    for p in r["projects"]:
        content.append(Paragraph(f"- {p}",styles["Normal"]))
    content.append(Paragraph("EDUCATION",styles["Sec"]))
    content.append(Paragraph(r["education"],styles["Normal"]))
    doc.build(content)
    return tmp.name

def resume_docx(r):
    d=Document()
    p=d.add_paragraph(r["name"])
    p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].bold=True
    p.runs[0].font.size=Pt(22)
    d.add_paragraph(r["role"]).alignment=WD_ALIGN_PARAGRAPH.CENTER
    def sec(t):
        s=d.add_paragraph(t); s.runs[0].bold=True
    sec("SUMMARY"); d.add_paragraph(r["summary"])
    sec("SKILLS"); d.add_paragraph(", ".join(r["skills"]))
    sec("PROJECTS")
    for x in r["projects"]: d.add_paragraph(x,style="List Bullet")
    sec("EDUCATION"); d.add_paragraph(r["education"])
    tmp=tempfile.NamedTemporaryFile(delete=False,suffix=".docx")
    d.save(tmp.name)
    return tmp.name

# ---------------- COVER LETTER ----------------
def cover(role,skills):
    return f"""
Dear Hiring Manager,

Based on your requirements for a {role}, my experience with {", ".join(skills[:4])} aligns strongly with the role.
I enjoy building practical solutions and continuously improving my technical depth.

I would love the opportunity to contribute and grow within your team.

Sincerely,
Candidate
"""

# ---------------- UI ----------------
st.title("✨ CareerCraft AI")
st.caption("Skill gap → learning plan → job-ready")

c1,c2=st.columns(2)
pdf=c1.file_uploader("Upload Resume (PDF)",type="pdf")
mode=c2.radio("Job Input Mode",["Preset Role","Custom JD"])

if mode=="Preset Role":
    role=st.selectbox("Select Role",ROLE_PRESETS)
    jd=ROLE_PRESETS[role]
else:
    role=st.text_input("Target Role")
    jd=st.text_area("Paste Job Description")

name=st.text_input("Your Full Name")

# ---------------- LOGIC ----------------
if pdf and jd and name:
    text=extract_text(pdf)
    skills=extract_skills(text)
    score=int(similarity(text,jd)*100)
    readiness=max(30,score+20)

    required=set(jd.split())
    missing=[s for s in required if s not in skills and s in SKILLS]

    # ---- METRICS ----
    a,b,c=st.columns(3)
    a.markdown(f"<div class='card'><h3>🎯 Career Readiness</h3><div class='big'>{readiness}%</div></div>",unsafe_allow_html=True)
    b.markdown(f"<div class='card'><h3>🧠 Skills Missing</h3><div class='big'>{len(missing)}</div></div>",unsafe_allow_html=True)
    c.markdown(f"<div class='card'><h3>Status</h3><div class='big {'good' if readiness>60 else 'warn'}'>{'APPLY SOON' if readiness>60 else 'IMPROVE'}</div></div>",unsafe_allow_html=True)

    # ---- VERDICT ----
    st.markdown(f"""
    <div class='card'>
    <h3>🧠 Career Insight</h3>
    You are <b>closer to becoming a {role}</b> than you think.
    Strengths found in your resume: <b>{", ".join(skills[:4])}</b><br>
    Focus on the missing skills below to cross <b>75% readiness</b>.
    </div>
    """,unsafe_allow_html=True)

    # ---- SKILL GRAPH ----
    st.subheader("📊 Skill Match Overview")
    fig=go.Figure(go.Bar(
        x=["Present","Missing"],
        y=[len(skills),len(missing)],
        marker_color=["#22c55e","#ef4444"]
    ))
    st.plotly_chart(fig,use_container_width=True)

    # ---- LEARNING PLAN ----
    st.subheader("📚 30-Day Learning Roadmap")
    for s in missing:
        if s in COURSES:
            title,time=COURSES[s]
            st.markdown(f"""
            <div class='card'>
            <b>📘 {s.upper()}</b><br>
            Course: {title}<br>
            Time Required: {time}<br>
            Outcome: Interview-ready confidence
            </div>
            """,unsafe_allow_html=True)

    # ---- RESUME ----
    r=resume_data(name,role,skills)
    st.subheader("📄 Generated Resume")
    with open(resume_pdf(r),"rb") as f:
        st.download_button("⬇ Resume PDF",f,"resume.pdf")
    with open(resume_docx(r),"rb") as f:
        st.download_button("⬇ Resume DOCX",f,"resume.docx")

    # ---- COVER ----
    cl=cover(role,skills)
    st.subheader("✉ Cover Letter")
    st.markdown(f"<div class='card'><pre>{cl}</pre></div>",unsafe_allow_html=True)

else:
    st.info("Upload resume and enter job details to continue.")
