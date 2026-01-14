import streamlit as st
import pdfplumber
import plotly.graph_objects as go
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import tempfile

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AI Career Intelligence", layout="wide")

# ---------------- THEME ----------------
st.markdown("""
<style>
body { background:#0f172a; color:#e5e7eb; }
.card {
 background:#020617; padding:1.5rem; border-radius:18px;
 box-shadow:0 0 30px rgba(56,189,248,.12); margin-bottom:1.2rem;
}
.metric { font-size:2.6rem; font-weight:700; color:#38bdf8; }
</style>
""", unsafe_allow_html=True)

# ---------------- DATA ----------------
SKILLS = ["python","java","sql","html","css","javascript","react",
          "node","git","docker","api","rest","ml","data analysis"]

ROLE_PRESETS = {
 "Backend Developer":"python sql api rest docker git",
 "Frontend Developer":"html css javascript react",
 "Data Analyst":"python sql data analysis excel"
}

# ---------------- UTILS ----------------
def extract_text(pdf):
 text=""
 with pdfplumber.open(pdf) as p:
  for pg in p.pages:
   text+=pg.extract_text() or ""
 return text.lower()

def extract_skills(text):
 return sorted([s for s in SKILLS if s in text])

def similarity(a,b):
 v=CountVectorizer().fit_transform([a,b])
 return cosine_similarity(v)[0][1]

def radar(user,jd):
 fig=go.Figure()
 fig.add_trace(go.Scatterpolar(r=[1 if s in user else 0 for s in SKILLS],
 theta=SKILLS,fill='toself',name="You"))
 fig.add_trace(go.Scatterpolar(r=[1 if s in jd else 0 for s in SKILLS],
 theta=SKILLS,fill='toself',name="JD"))
 fig.update_layout(paper_bgcolor="#020617",font_color="#e5e7eb")
 return fig

def roadmap_pdf(missing):
 tmp=tempfile.NamedTemporaryFile(delete=False,suffix=".pdf")
 doc=SimpleDocTemplate(tmp.name)
 styles=getSampleStyleSheet()
 content=[Paragraph("<b>30-Day Learning Roadmap</b>",styles['Title'])]
 for i,s in enumerate(missing,1):
  content.append(Paragraph(f"Week {i}: Learn {s}",styles['Normal']))
 doc.build(content)
 return tmp.name

# ---------------- UI ----------------
st.title("🧠 AI Career Intelligence Platform")

col1,col2=st.columns(2)
resume=col1.file_uploader("Upload Resume (PDF)",type="pdf")
mode=col2.radio("Job Input Mode",["Preset","Custom"])

if mode=="Preset":
 role=st.selectbox("Role",ROLE_PRESETS.keys())
 jd_text=ROLE_PRESETS[role]
else:
 role=st.text_input("Target Role")
 jd_text=st.text_area("Paste Job Description",height=180)

company=st.selectbox("Target Company Type",["Startup","MNC","Product"])

# ---------------- ANALYSIS ----------------
if resume and jd_text:
 rtext=extract_text(resume)
 rskills=extract_skills(rtext)
 jdskills=extract_skills(jd_text)

 ats=int(similarity(rtext,jd_text)*100)
 confidence=min(95,ats+len(rskills)*2)

 readiness="READY" if ats>75 else "ALMOST READY" if ats>50 else "NOT READY"

 c1,c2,c3=st.columns(3)
 c1.markdown(f"<div class='card'><h3>ATS Match</h3><div class='metric'>{ats}%</div></div>",unsafe_allow_html=True)
 c2.markdown(f"<div class='card'><h3>Resume Confidence</h3><div class='metric'>{confidence}%</div></div>",unsafe_allow_html=True)
 c3.markdown(f"<div class='card'><h3>Readiness</h3><div class='metric'>{readiness}</div></div>",unsafe_allow_html=True)

 # Radar
 st.subheader("Skill Radar")
 st.plotly_chart(radar(rskills,jdskills),use_container_width=True)

 # Gaps
 missing=sorted(set(jdskills)-set(rskills))
 st.markdown("<div class='card'><h3>Missing Skills</h3>"+", ".join(missing)+"</div>",unsafe_allow_html=True)

 # Trend
 st.subheader("Skill Gap Trend")
 fig=go.Figure(go.Scatter(y=[len(missing)+3,len(missing)+1,len(missing)],mode="lines+markers"))
 fig.update_layout(paper_bgcolor="#020617",font_color="#e5e7eb")
 st.plotly_chart(fig,use_container_width=True)

 # Rejection
 st.markdown("""
 <div class='card'><h3>Why You May Be Rejected</h3>
 <ul>
 <li>Missing JD-specific keywords</li>
 <li>Generic resume tone</li>
 <li>No quantified impact</li>
 </ul></div>""",unsafe_allow_html=True)

 # Interview
 st.markdown("""
 <div class='card'><h3>Likely Interview Questions</h3>
 <ul>
 <li>Explain REST APIs</li>
 <li>Describe a Git conflict</li>
 <li>Optimize a SQL query</li>
 </ul></div>""",unsafe_allow_html=True)

 # Resume comparison
 st.markdown("""
 <div class='card'><h3>Resume Version Comparison</h3>
 <b>Old:</b> Generic skills list<br>
 <b>Improved:</b> Role-aligned, quantified achievements
 </div>""",unsafe_allow_html=True)

 # Improved resume
 improved_resume=f"""
 {role} Resume
 Skills: {", ".join(rskills)}
 Added Keywords: {", ".join(missing)}
 Focus: Results + Impact
 """

 st.markdown(f"<div class='card'><h3>Improved Resume</h3><pre>{improved_resume}</pre></div>",unsafe_allow_html=True)

 # Cover letter
 st.markdown(f"""
 <div class='card'><h3>Cover Letter</h3>
 I am applying for {role}. My background in {", ".join(rskills[:4])}
 aligns with your requirements. I am eager to contribute.
 </div>""",unsafe_allow_html=True)

 # PDF
 pdf_path=roadmap_pdf(missing)
 with open(pdf_path,"rb") as f:
  st.download_button("📥 Download Learning Plan (PDF)",f,file_name="roadmap.pdf")

else:
 st.info("Upload resume and provide JD to start.")
