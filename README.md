# AS.Dev EduHub 🎓

Welcome to **AS.Dev EduHub**—a unified premium Streamlit-based application suite that consolidates advanced educational tools, automated curriculum generators, and JEE prep simulator engines using **Google Gemini AI** as the core reasoning agent.

---

## 🚀 Key Modules Included

### 1. 🏠 Dashboard
A modern, glassmorphic central router that showcases all modular applications in the suite.

### 2. 📝 NotesIO
- **Note Generator Studio**: Generates highly detailed, structured revision notes.
- **Smart File Summarizer**: Generates executive briefs or deep technical outlines from text documents.
- **Code Developer Engine**: Translates logic instructions into modular, well-commented source code files.

### 3. ⚡ RevisionIO
- Generates tailored day-by-day study calendars based on CBSE/IIT-JEE/NEET syllabus guidelines.
- Provides interactive progress bars, NCERT core revision bits, key formulas, exam pitfalls, and practice questions.

### 4. 🗺️ RoadmapIO
- Maps multi-stage learning pathways with sequential progress checkpoints.
- Employs an interactive double-pass system with AI-driven clarifying questions.

### 5. 🎓 JEE Igniter
- **Doubt Solver**: Processes text/multimodal queries to explain tricky problems.
- **Study Planner**: Creates 7-day tables incorporating droppers/regular schedules.
- **IITian Mentor AI**: Context-aware chat coaching for strategies and motivation.

### 6. ✏️ DailyPractise
- Generates 15-question single-select MCQ practice worksheets matching CBSE Class 12 blueprints.
- Automatically grades responses and provides full LaTeX solutions.

### 7. 🎯 JEE Advanced CBT
- Emulates the official computer-based testing interface of the JEE Advanced examination.
- Features custom marking schemes, interactive navigational color-coded palettes, numerical integer pads, and matrix-style matching options.

---

## 🛠️ Getting Started & Installation

### 1. Prerequisites
- Python 3.9 or higher

### 2. Clone the Repository
```bash
git clone https://github.com/AS-Developer-17/Class-12-CS083.git
cd "Class-12-CS083/AS.Dev Edu Hub"
```

### 3. Install Dependencies
```bash
pip install streamlit google-genai pydantic pillow
```

### 4. Configuration
A preloaded API Key is configured in the code. To customize config parameters or provide a custom key, create a `.streamlit/secrets.toml` file in the project folder:
```toml
GEMINI_API_KEY = "YOUR_API_KEY_HERE"
```

### 5. Running the Application
To run the primary unified app:
```bash
streamlit run EduHub.py
```
Navigate to `http://localhost:8501` (or the console-printed port) in your web browser.

---

## 🎨 Technology Stack
- **Frontend Layer**: Streamlit (with Custom HSL gradients and Blur CSS overrides).
- **Core LLM**: Google Gemini (`gemini-2.5-flash` / `gemini-2.5-pro` via the `google-genai` SDK).
- **Data Validation**: Pydantic v2 schemas.
