import streamlit as st
import pdfplumber
import plotly.graph_objects as go
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from docx import Document
import tempfile

# ---------------- PAGE CONFIG ----------------
st.set_page_config("AI Career Intelligence", "🧠", layout="wide")

# ---------------- PREMIUM UI ----------------
st.markdown("""
<style>
body {
 background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
 color:#e5e7eb;
}
.glass {
 background: rgba(255,255,255,0.08);
 backdrop-filter: blur(12px);
 padding: 1.5rem;
 border-radius: 18px;
 box-shadow: 0 10px 40px rgba(0,0,0,.35);
 margin-bottom: 1.5rem;
}
.metric {
 font-size: 2.8rem;
 font-weight: 700;
 color: #38bdf8;
}
h1,h2,h3 { color:#f9fafb; }
small { color:#9ca3af; }
</style>
""", unsafe_allow_html=True)

# ---------------- DATA ----------------
SKILLS = ["python","java","sql","html","css","javascript","react",
          "node","git","docker","api","rest","ml","data analysis"]

ROLES = {
 "Backend Developer":"python sql api rest docker git",
 "Frontend Developer":"html css javascript react",
 "Data Analyst":"python sql data analysis excel"
}

# ---------------- FUNCTIONS ----------------
def extract_text(pdf):
 text=""
 with pdfplumber.open(pdf) as p:
  for pg in p.pages:
   text+=pg.extract_text() or ""
 return text.lower()

def skills(text):
 return [s for s in SKILLS if s in text]

def similarity(a,b):
 v=CountVectorizer().fit_transform([a,b])
 return cosine_similarity(v)[0][1]

def radar(user,jd):
 fig=go.Figure()
 fig.add_trace(go.Scatterpolar(r=[1 if s in user else 0 for s in SKILLS],
 theta=SKILLS,fill='toself',name="You"))
 fig.add_trace(go.Scatterpolar(r=[1 if s in jd else 0 for s in SKILLS],
 theta=SKILLS,fill='toself',name="Job"))
 fig.update_layout(
  paper_bgcolor="rgba(0,0,0,0)",
  font_color="#e5e7eb"
 )
 return fig

def generate_resume_pdf(name, role, skills):
 tmp=tempfile.NamedTemporaryFile(delete=False,suffix=".pdf")
 doc=SimpleDocTemplate(tmp.name)
 styles=getSampleStyleSheet()
 content=[
  Paragraph(f"<b>{name}</b>",styles['Title']),
  Paragraph(role,styles['Heading2']),
  Paragraph("<b>Skills</b>: "+", ".join(skills),styles['Normal']),
  Paragraph("<b>Summary</b>: Motivated candidate aligned with job requirements.",styles['Normal'])
 ]
 doc.build(content)
 return tmp.name

def generate_resume_docx(name, role, skills):
 doc=Document()
 doc.add_heading(name,0)
 doc.add_heading(role,level=2)
 doc.add_paragraph("Skills: "+", ".join(skills))
 doc.add_paragraph("Summary: Motivated candidate aligned with job requirements.")
 tmp=tempfile.NamedTemporaryFile(delete=False,suffix=".docx")
 doc.save(tmp.name)
 return tmp.name

def generate_cover_letter(role, skills):
 return f"""
Dear Hiring Manager,

I am applying for the {role} position. My experience with
{", ".join(skills[:4])} closely aligns with your requirements.

I am eager to contribute and grow with your organization.

Sincerely,
Candidate
"""

def cover_letter_pdf(text):
 tmp=tempfile.NamedTemporaryFile(delete=False,suffix=".pdf")
 doc=SimpleDocTemplate(tmp.name)
 styles=getSampleStyleSheet()
 doc.build([Paragraph(t,styles['Normal']) for t in text.split("\n")])
 return tmp.name

def cover_letter_docx(text):
 doc=Document()
 for line in text.split("\n"):
  doc.add_paragraph(line)
 tmp=tempfile.NamedTemporaryFile(delete=False,suffix=".docx")
 doc.save(tmp.name)
 return tmp.name

# ---------------- UI ----------------
st.title("🧠 AI Career Intelligence Platform")
st.caption("From resume → job-ready. Instantly.")

col1,col2=st.columns(2)
resume=col1.file_uploader("Upload Resume (PDF)",type="pdf")
mode=col2.radio("Job Input Mode",["Preset Role","Custom JD"])

if mode=="Preset Role":
 role=st.selectbox("Target Role",ROLES.keys())
 jd=ROLES[role]
else:
 role=st.text_input("Target Role")
 jd=st.text_area("Paste Job Description",height=180)

name=st.text_input("Your Name")

# ---------------- ANALYSIS ----------------
if resume and jd and name:
 rtext=extract_text(resume)
 rskills=skills(rtext)
 jdskills=skills(jd)

 ats=int(similarity(rtext,jd)*100)

 c1,c2,c3=st.columns(3)
 c1.markdown(f"<div class='glass'><h3>ATS Match</h3><div class='metric'>{ats}%</div></div>",unsafe_allow_html=True)
 c2.markdown(f"<div class='glass'><h3>Resume Confidence</h3><div class='metric'>{min(95,ats+10)}%</div></div>",unsafe_allow_html=True)
 c3.markdown(f"<div class='glass'><h3>Status</h3><div class='metric'>{'READY' if ats>70 else 'IMPROVE'}</div></div>",unsafe_allow_html=True)

 st.subheader("Skill Radar")
 st.plotly_chart(radar(rskills,jdskills),use_container_width=True)

 # Resume generation
 st.subheader("📄 Generated Resume")
 pdf_path=generate_resume_pdf(name,role,rskills)
 docx_path=generate_resume_docx(name,role,rskills)

 with open(pdf_path,"rb") as f:
  st.download_button("Download Resume (PDF)",f,file_name="resume.pdf")
 with open(docx_path,"rb") as f:
  st.download_button("Download Resume (DOCX)",f,file_name="resume.docx")

 # Cover letter
 st.subheader("✉️ Cover Letter")
 cl=generate_cover_letter(role,rskills)
 st.markdown(f"<div class='glass'><pre>{cl}</pre></div>",unsafe_allow_html=True)

 cl_pdf=cover_letter_pdf(cl)
 cl_docx=cover_letter_docx(cl)

 with open(cl_pdf,"rb") as f:
  st.download_button("Download Cover Letter (PDF)",f,file_name="cover_letter.pdf")
 with open(cl_docx,"rb") as f:
  st.download_button("Download Cover Letter (DOCX)",f,file_name="cover_letter.docx")

else:
 st.info("Upload resume, enter role & name to generate outputs.")
