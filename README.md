# ✨ CareerCraft AI — Skill Gap Analyzer & Resume Builder

CareerCraft AI is a **student-first career readiness platform** that transforms a resume into a **job-ready profile**.  
It helps students understand **where they stand**, **which roles suit them best**, and **what to improve next** — while generating **premium resumes and cover letters**.

> Skill gap → learning plan → job-ready

---

## 🚀 Key Features

### 🎯 Skill Matching & ATS Readiness
- Upload resume (PDF)
- Choose a preset role **or paste a custom Job Description**
- Get:
  - ATS match percentage
  - Skill match & missing skills table
  - Career readiness score

---

### 🧠 Best-Fit Job Role Recommendations
- Suggests roles that best match current skills
- Helps students discover **realistic & achievable career paths**
- Reduces confusion for early-stage learners

---

### 📊 Skill Match & Missing Skills Table
- Clear table showing:
  - ✅ Skills present
  - ❌ Skills missing
- Easy to understand and action-oriented

---

### 📚 Personalized Learning Roadmap
- Curated learning sources for missing skills
- Beginner-friendly courses
- Clear outcomes and confidence-building guidance

---

### 📄 Premium Resume Generator (DOCX & PDF)
- Professionally structured resume sections
- ATS-friendly formatting
- Content dynamically adapts to:
  - Selected job role
  - Job description
- Download as:
  - 📄 DOCX (editable)
  - 📄 PDF (clean & polished)

---

### ✉ Premium Cover Letter Generator
- Role-specific and JD-aware
- Natural, confident, student-friendly tone
- Ready to submit with applications

---

### 🎤 Interview Talking Points
- Auto-generated points students can say in interviews
- Helps explain:
  - Skills
  - Learning mindset
  - Internship readiness

---

### 👀 Recruiter View
- Shows how a recruiter may perceive the profile
- Builds confidence and self-awareness

---

### 💼 LinkedIn “About” Section
- Clean, professional summary
- Copy-paste ready
- Optimized for recruiters & early-career roles

---

### 🧩 Portfolio Section Generator
- Auto-suggested project descriptions
- Helps students showcase skills professionally

---

## 🛠 Tech Stack

- **Frontend & App Framework:** Streamlit
- **Resume Parsing:** pdfplumber
- **Resume Generation:** python-docx, reportlab
- **Logic Engine:** Keyword extraction + role-skill mapping
- **UI:** Custom CSS with bright, confidence-boosting design

---

## 📦 Project Structure
skill-gap-analyzer/
│
├── app.py # Main Streamlit application
├── requirements.txt # Dependencies
└── README.md # Documentation


---

## ⚙️ Installation & Run

```bash
pip install -r requirements.txt
streamlit run app.py
