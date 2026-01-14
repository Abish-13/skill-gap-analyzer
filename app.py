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
st.set_page_config("CareerCraft AI", "✨", layout="wide")

# ---------------- BRIGHT UI ----------------
st.markdown("""
<style>
body {
 background: linear-gradient(135deg,#667eea,#764ba2,#43cea2);
 color:#0f172a;
}
.glass {
 background: rgba(255,255,255,0.9);
 padding: 1.6rem;
 border-radius: 20px;
 box-shadow: 0 15px 40px rgba(0,0,0,0.15);
 margin-bottom: 1.5rem;
}
.metric {
 font-size: 2.7rem;
 font-weight: 800;
 color: #2563eb;
}
h1,h2,h3 { color:#0f172a; }
</style>
""", unsafe_allow_html=True)

# ---------------- SKILLS & COURSES ----------------
SKILLS = [
 "python","java","sql","html","css","javascript","react",
 "node","git","docker","api","rest","ml","data analysis"
]

COURSES = {
 "python": "Python for Everybody – Coursera",
 "java": "Java Programming – NPTEL",
 "sql": "SQL for Data Analysis – Mode Analytics",
 "html": "HTML & CSS – freeCodeCamp",
 "css": "CSS Complete Guide – freeCodeCamp",
 "javascript": "JavaScript Algorithms – freeCodeCamp",
 "react": "React Basics – Scrimba",
 "node": "Node.js – freeCodeCamp",
 "git": "Git & GitHub – Atlassian",
 "docker": "Docker Essentials – IBM",
 "api": "REST APIs – Postman Academy",
 "rest": "RESTful Services – Coursera",
 "ml": "Machine Learning – Andrew Ng",
 "data analysis": "Data Analysis – Google"
}

ROLE_PRESETS = {
 "Backend Developer": "python sql api rest docker git",
 "Frontend Developer": "html css javascript react",
 "Data Analyst": "python sql data analysis"
}

# ---------------- UTILS ----------------
def extract_text(pdf):
 text=""
 with pdfplumber.open(pdf) as p:
  for page in p.pages:
   text+=page.extract_text() or ""
 return text.lower()

def extract_skills(text):
 return sorted([s for s in SKILLS if s in text])

def similarity(a,b):
 v=CountVectorizer().fit_transform([a,b])
 return cosine_similarity(v)[0][1]

# ---------------- RESUME BUILD ----------------
def build_resume(name, role, skills):
 return {
  "name": name,
  "role": role,
  "summary": f"Motivated candidate seeking a {role} role with strengths in {', '.join(skills[:4])}.",
  "skills": skills,
  "projects": [
   f"Built real-world projects using {skills[0]}",
   "Used Git for version control",
   "Focused on clean and scalable code"
  ],
  "education": "Bachelor’s Degree / Student"
 }

# ---------------- PDF RESUME ----------------
def resume_pdf(res):
 tmp=tempfile.NamedTemporaryFile(delete=False,suffix=".pdf")
 doc=SimpleDocTemplate(tmp.name,pagesize=A4)
 styles=getSampleStyleSheet()

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
  textColor="#2563eb"
 ))

 c=[]
 c.append(Paragraph(res["name"],styles["Name"]))
 c.append(Paragraph(res["role"],styles["Heading2"]))
 c.append(Paragraph("SUMMARY",styles["Section"]))
 c.append(Paragraph(res["summary"],styles["Normal"]))
 c.append(Paragraph("SKILLS",styles["Section"]))
 c.append(Paragraph(", ".join(res["skills"]),styles["Normal"]))
 c.append(Paragraph("PROJECTS",styles["Section"]))
 for p in res["projects"]:
  c.append(Paragraph(f"- {p}",styles["Normal"]))
 c.append(Paragraph("EDUCATION",styles["Section"]))
 c.append(Paragraph(res["education"],styles["Normal"]))
 doc.build(c)
 return tmp.name

# ---------------- DOCX RESUME ----------------
def resume_docx(res):
 doc=Document()
 h=doc.add_heading(res["name"],0)
 h.alignment=WD_ALIGN_PARAGRAPH.CENTER
 doc.add_heading(res["role"],level=2)

 def sec(t):
  p=doc.add_paragraph(t)
  p.runs[0].bold=True

 sec("SUMMARY")
 doc.add_paragraph(res["summary"])
 sec("SKILLS")
 doc.add_paragraph(", ".join(res["skills"]))
 sec("PROJECTS")
 for p in res["projects"]:
  doc.add_paragraph(p,style="List Bullet")
 sec("EDUCATION")
 doc.add_paragraph(res["education"])

 tmp=tempfile.NamedTemporaryFile(delete=False,suffix=".docx")
 doc.save(tmp.name)
 return tmp.name

# ---------------- COVER LETTER ----------------
def cover_letter(role,skills):
 return f"""Dear Hiring Manager,

I am applying for the {role} role. My skills in {", ".join(skills[:4])}
match well with your requirements. I am eager to contribute and grow.

Sincerely,
Candidate
"""

def cover_pdf(text):
 tmp=tempfile.NamedTemporaryFile(delete=False,suffix=".pdf")
 doc=SimpleDocTemplate(tmp.name)
 styles=getSampleStyleSheet()
 doc.build([Paragraph(t,styles["Normal"]) for t in text.split("\n")])
 return tmp.name

def cover_docx(text):
 doc=Document()
 for line in text.split("\n"):
  doc.add_paragraph(line)
 tmp=tempfile.NamedTemporaryFile(delete=False,suffix=".docx")
 doc.save(tmp.name)
 return tmp.name

# ---------------- UI ----------------
st.title("✨ CareerCraft AI")
st.caption("Skill gap → learning plan → job-ready")

c1,c2=st.columns(2)
resume=c1.file_uploader("Upload Resume (PDF)",type="pdf")
mode=c2.radio("Job Input Mode",["Preset Role","Custom JD"])

if mode=="Preset Role":
 role=st.selectbox("Select Role",ROLE_PRESETS.keys())
 jd=ROLE_PRESETS[role]
else:
 role=st.text_input("Target Role")
 jd=st.text_area("Paste Job Description",height=180)

name=st.text_input("Your Full Name")

# ---------------- ANALYSIS ----------------
if resume and jd and name:
 text=extract_text(resume)
 rskills=extract_skills(text)
 jdskills=extract_skills(jd)

 missing=list(set(jdskills)-set(rskills))
 ats=int(similarity(text,jd)*100)

 c1,c2,c3=st.columns(3)
 c1.markdown(f"<div class='glass'><h3>ATS Match</h3><div class='metric'>{ats}%</div></div>",unsafe_allow_html=True)
 c2.markdown(f"<div class='glass'><h3>Skills Missing</h3><div class='metric'>{len(missing)}</div></div>",unsafe_allow_html=True)
 c3.markdown(f"<div class='glass'><h3>Status</h3><div class='metric'>{'READY' if ats>70 else 'IMPROVE'}</div></div>",unsafe_allow_html=True)

 # --------- SKILL MATCH GRAPH ---------
 st.subheader("📊 Skill Match Overview")
 fig=go.Figure()
 fig.add_bar(x=["Have","Missing"],y=[len(rskills),len(missing)],marker_color=["#22c55e","#ef4444"])
 fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
 st.plotly_chart(fig,use_container_width=True)

 # --------- LEARNING PLAN ---------
 st.subheader("📚 Learning Plan – Where to Study")
 plan=[]
 for i,s in enumerate(missing,1):
  course=COURSES.get(s,"Online resources")
  plan.append(f"Week {i}: Learn {s} → {course}")
  st.markdown(f"<div class='glass'>📘 <b>{s}</b><br>Source: {course}</div>",unsafe_allow_html=True)

 # --------- DOWNLOAD LEARNING PLAN PDF ---------
 if plan:
  tmp=tempfile.NamedTemporaryFile(delete=False,suffix=".pdf")
  doc=SimpleDocTemplate(tmp.name)
  styles=getSampleStyleSheet()
  doc.build([Paragraph(p,styles["Normal"]) for p in plan])
  with open(tmp.name,"rb") as f:
   st.download_button("⬇ Download Learning Plan (PDF)",f,"learning_plan.pdf")

 # --------- RESUME & COVER ---------
 resume_data=build_resume(name,role,rskills)

 st.subheader("📄 Generated Resume")
 with open(resume_pdf(resume_data),"rb") as f:
  st.download_button("Download Resume (PDF)",f,"resume.pdf")
 with open(resume_docx(resume_data),"rb") as f:
  st.download_button("Download Resume (DOCX)",f,"resume.docx")

 st.subheader("✉ Cover Letter")
 cl=cover_letter(role,rskills)
 st.markdown(f"<div class='glass'><pre>{cl}</pre></div>",unsafe_allow_html=True)

 with open(cover_pdf(cl),"rb") as f:
  st.download_button("Download Cover Letter (PDF)",f,"cover_letter.pdf")
 with open(cover_docx(cl),"rb") as f:
  st.download_button("Download Cover Letter (DOCX)",f,"cover_letter.docx")

else:
 st.info("Upload resume, enter name & job role to start.")
