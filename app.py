import streamlit as st
import pdfplumber
import re
import time
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Skill Gap Analyzer", page_icon="📊")

# ---------------- DARK MODE ----------------
dark = st.sidebar.toggle("🌙 Dark Mode")

bg = "#020617" if dark else "#f8fafc"
card = "#020617" if dark else "#ffffff"
text = "#e5e7eb" if dark else "#0f172a"

st.markdown(f"""
<style>
body {{ background:{bg}; color:{text}; }}
.card {{
    background:{card};
    padding:20px;
    border-radius:14px;
    margin-bottom:20px;
}}
.good {{ color:#22c55e; font-weight:600; }}
.bad {{ color:#ef4444; font-weight:600; }}
</style>
""", unsafe_allow_html=True)

# ---------------- DATA ----------------
SKILLS = {
    "python": ["python"],
    "sql": ["sql"],
    "excel": ["excel"],
    "power bi": ["power bi"],
    "git": ["git", "github"],
    "java": ["java"],
    "machine learning": ["machine learning", "ml"],
    "html": ["html"],
    "css": ["css"],
    "javascript": ["javascript", "js"],
    "communication": ["communication"],
    "problem solving": ["problem solving"]
}

WEIGHT = {
    "python": 3, "sql": 3, "java": 3, "machine learning": 3,
    "excel": 2, "power bi": 2, "git": 2,
    "html": 2, "css": 2, "javascript": 2,
    "communication": 1, "problem solving": 1
}

ROLE_JD = {
    "Data Analyst": "sql excel python power bi data analysis problem solving",
    "Software Developer": "python java git html css javascript problem solving",
    "ML Intern": "python machine learning sql data analysis git"
}

PLAN = {
    1: ["sql", "excel"],
    2: ["python", "html"],
    3: ["git", "css"],
    4: ["javascript", "machine learning"]
}

IMPROVEMENT_TIPS = {
    "sql": "Add SQL queries or database projects.",
    "python": "Mention Python projects with real datasets.",
    "git": "Add GitHub repository links.",
    "machine learning": "Include a mini ML project.",
    "excel": "Highlight Excel dashboards.",
    "power bi": "Add Power BI report screenshots.",
    "html": "Showcase frontend projects.",
    "css": "Mention responsive UI work.",
    "javascript": "Add interactive JS features."
}

# ---------------- FUNCTIONS ----------------
def extract_text(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.lower()

def detect_skills(text):
    found = set()
    for s, keys in SKILLS.items():
        for k in keys:
            if re.search(rf"\b{k}\b", text):
                found.add(s)
    return found

def score_calc(match, req):
    total = sum(WEIGHT.get(s, 1) for s in req)
    have = sum(WEIGHT.get(s, 1) for s in match)
    return int((have / total) * 100) if total else 0

def generate_pdf(role, missing):
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"<b>{role} – 4 Week Learning Plan</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    for w, skills in PLAN.items():
        wk = [s for s in skills if s in missing]
        if wk:
            elements.append(Paragraph(f"Week {w}", styles["Heading2"]))
            elements.append(ListFlowable(
                [ListItem(Paragraph(s.title(), styles["Normal"])) for s in wk]
            ))

    doc.build(elements)
    buf.seek(0)
    return buf

# ---------------- UI ----------------
st.markdown("## 📊 Skill Gap Analyzer")

tab1, tab2 = st.tabs(["🔍 Resume Analysis", "🔄 Resume Version Comparison"])

# ---------------- TAB 1 ----------------
with tab1:
    resume = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])
    roles = st.multiselect("🎯 Select Job Roles", list(ROLE_JD.keys()), default=["Data Analyst"])
    analyze = st.button("Analyze Resume", disabled=not (resume and roles))

    if analyze:
        with st.spinner("Analyzing resume..."):
            time.sleep(1)
            resume_text = extract_text(resume)
            resume_skills = detect_skills(resume_text)

        scores = {}

        for role in roles:
            jd_skills = detect_skills(ROLE_JD[role])
            matched = resume_skills & jd_skills
            missing = jd_skills - resume_skills
            score = score_calc(matched, jd_skills)
            scores[role] = score

            st.markdown(f"<div class='card'><h3>{role}</h3>", unsafe_allow_html=True)
            st.progress(score / 100)
            st.write(f"**Readiness Score: {score}%**")

            st.write("❌ Missing Skills")
            for s in missing:
                st.markdown(f"<span class='bad'>• {s.title()}</span>", unsafe_allow_html=True)

            st.write("🛠 Resume Improvement Suggestions")
            for s in missing:
                if s in IMPROVEMENT_TIPS:
                    st.write(f"- {IMPROVEMENT_TIPS[s]}")

            pdf = generate_pdf(role, missing)
            st.download_button(
                f"📥 Download {role} Learning Plan",
                pdf,
                f"{role}_learning_plan.pdf",
                "application/pdf"
            )

            st.markdown("</div>", unsafe_allow_html=True)

        best = max(scores, key=scores.get)
        st.success(f"🏆 Best Matching Role: {best} ({scores[best]}%)")

# ---------------- TAB 2: VERSION COMPARISON ----------------
with tab2:
    st.markdown("### 🔄 Resume Version Comparison (Old vs New)")

    old_resume = st.file_uploader("📄 Upload OLD Resume", type=["pdf"], key="old")
    new_resume = st.file_uploader("📄 Upload NEW Resume", type=["pdf"], key="new")
    role = st.selectbox("🎯 Select Job Role", list(ROLE_JD.keys()))

    compare = st.button("Compare Versions", disabled=not (old_resume and new_resume))

    if compare:
        with st.spinner("Comparing resumes..."):
            old_text = extract_text(old_resume)
            new_text = extract_text(new_resume)

        jd_skills = detect_skills(ROLE_JD[role])

        old_skills = detect_skills(old_text)
        new_skills = detect_skills(new_text)

        old_score = score_calc(old_skills & jd_skills, jd_skills)
        new_score = score_calc(new_skills & jd_skills, jd_skills)

        st.markdown("### 📊 Readiness Score Comparison")
        fig, ax = plt.subplots()
        ax.bar(["Old Resume", "New Resume"], [old_score, new_score])
        ax.set_ylim(0, 100)
        st.pyplot(fig)

        st.markdown("### 🆕 New Skills Added")
        added = new_skills - old_skills
        for s in added:
            st.markdown(f"<span class='good'>• {s.title()}</span>", unsafe_allow_html=True)

        st.markdown("### 🎯 Improvement Summary")
        st.write(f"Score improved by **{new_score - old_score}%**")

        if new_score > old_score:
            st.success("Great improvement! Your resume is now more aligned with the role.")
        else:
            st.warning("No significant improvement detected. Consider updating skills/projects.")
