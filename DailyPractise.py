import os
import json
import time
import random
import streamlit as st
from pydantic import BaseModel, Field
import google.genai as genai
from google.genai import types

# ==========================================
# API KEY RESOLUTION (SECURE & HIDDEN)
# ==========================================
DEFAULT_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if not DEFAULT_API_KEY:
    try:
        DEFAULT_API_KEY = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GOOGLE_API_KEY", "")
    except Exception:
        DEFAULT_API_KEY = ""

if not DEFAULT_API_KEY:
    try:
        secrets_path = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
        if os.path.exists(secrets_path):
            with open(secrets_path, "r", encoding="utf-8") as f:
                for line in f:
                    if "GEMINI_API_KEY" in line or "GOOGLE_API_KEY" in line:
                        parts = line.split("=")
                        if len(parts) == 2:
                            DEFAULT_API_KEY = parts[1].replace('"', '').replace("'", "").strip()
                            break
    except Exception:
        pass

# ==========================================
# PAGE CONFIG & PREMIUM CUSTOM STYLING
# ==========================================
st.set_page_config(
    page_title="DailyPractise - CBSE Class 12 MCQ practice",
    page_icon="✏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    /* Glassmorphism card container */
    .glass-card {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }
    
    /* Result states highlights */
    .correct-card {
        border-left: 5px solid #10b981;
        background: rgba(16, 185, 129, 0.08);
    }
    
    .incorrect-card {
        border-left: 5px solid #ef4444;
        background: rgba(239, 68, 68, 0.08);
    }

    .unattempted-card {
        border-left: 5px solid #64748b;
        background: rgba(100, 116, 139, 0.08);
    }

    /* Elegant gradient title header */
    .header-box {
        background: linear-gradient(135deg, #090d16 0%, #1e1b4b 50%, #064e3b 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 35px 25px;
        margin-bottom: 30px;
        text-align: center;
        position: relative;
        overflow: hidden;
        box-shadow: 0 15px 35px -15px rgba(0, 0, 0, 0.7);
    }
    
    .header-title {
        color: #f8fafc;
        margin: 0;
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(to right, #ffffff, #c7d2fe, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .header-subtitle {
        color: #94a3b8;
        margin: 10px 0 0 0;
        font-size: 1.1rem;
        font-weight: 400;
    }

    /* Style the sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0c111d;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Options design enhancements */
    .option-text {
        font-size: 1.05rem;
        color: #e2e8f0;
        margin-bottom: 6px;
    }

    /* Badge indicators */
    .badge {
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 10px;
    }
    .badge-correct {
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .badge-incorrect {
        background: rgba(239, 68, 68, 0.2);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .badge-unattempted {
        background: rgba(148, 163, 184, 0.2);
        color: #cbd5e1;
        border: 1px solid rgba(148, 163, 184, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SUBJECT & CHAPTER SYLLABUS MAPPING (CBSE 12)
# ==========================================
SUBJECTS_AND_CHAPTERS = {
    "Physics": [
        "Electric Charges and Fields",
        "Electrostatic Potential and Capacitance",
        "Current Electricity",
        "Moving Charges and Magnetism",
        "Magnetism and Matter",
        "Electromagnetic Induction",
        "Alternating Current",
        "Electromagnetic Waves",
        "Ray Optics and Optical Instruments",
        "Wave Optics",
        "Dual Nature of Radiation and Matter",
        "Atoms",
        "Nuclei",
        "Semiconductor Electronics: Materials, Devices and Simple Circuits"
    ],
    "Chemistry": [
        "Solutions",
        "Electrochemistry",
        "Chemical Kinetics",
        "d- and f-Block Elements",
        "Coordination Compounds",
        "Haloalkanes and Haloarenes",
        "Alcohols, Phenols and Ethers",
        "Aldehydes, Ketones and Carboxylic Acids",
        "Amines",
        "Biomolecules"
    ],
    "Maths": [
        "Relations and Functions",
        "Inverse Trigonometric Functions",
        "Matrices",
        "Determinants",
        "Continuity and Differentiability",
        "Application of Derivatives",
        "Integrals",
        "Application of Integrals",
        "Differential Equations",
        "Vector Algebra",
        "Three Dimensional Geometry",
        "Linear Programming",
        "Probability"
    ],
    "Painting": [
        "Rajasthani and Pahari Schools of Miniature Painting",
        "Mughal and Deccan Schools of Miniature Painting",
        "Bengal School of Painting and the Modern Trends in Indian Art"
    ],
    "English": [
        "Flamingo (Prose) - The Last Lesson & Lost Spring",
        "Flamingo (Prose) - Deep Water & The Rattrap",
        "Flamingo (Prose) - Indigo & Poets and Pancakes",
        "Flamingo (Prose) - The Interview & Going Places",
        "Flamingo (Poetry) - My Mother at Sixty-six & Keeping Quiet",
        "Flamingo (Poetry) - A Thing of Beauty & A Roadside Stand",
        "Flamingo (Poetry) - Aunt Jennifer's Tigers",
        "Vistas - The Third Level & The Tiger King",
        "Vistas - Journey to the End of the Earth & The Enemy",
        "Vistas - On the Face of It & Memories of Childhood",
        "Writing Skills - Notice, Invitations & Replies",
        "Writing Skills - Letter Writing & Article/Report Writing"
    ],
    "Computer Science": [
        "Computational Thinking and Programming - Python Revision Tour & Functions",
        "Computational Thinking and Programming - File Handling (Text, Binary, CSV)",
        "Computer Networks - Structure, Protocols, and Devices",
        "Database Management - SQL Commands and Python-SQL Connectivity"
    ]
}

# ==========================================
# PYDANTIC SCHEMAS FOR STRUCTURED OUTPUT
# ==========================================
class MCQQuestion(BaseModel):
    id: int = Field(description="Question index strictly from 1 to 15")
    question: str = Field(description="The question statement. Write math formulas, equations, or chemical symbols in clean LaTeX format using $...$ for inline or $$...$$ for block notation.")
    option_a: str = Field(description="Option A choice. Use LaTeX if math is present.")
    option_b: str = Field(description="Option B choice. Use LaTeX if math is present.")
    option_c: str = Field(description="Option C choice. Use LaTeX if math is present.")
    option_d: str = Field(description="Option D choice. Use LaTeX if math is present.")
    correct_option: str = Field(description="The correct option, which must strictly be one of: 'A', 'B', 'C', or 'D'")
    explanation: str = Field(description="Detailed step-by-step solution. Always write formulas, equations, and mathematical derivations in clean LaTeX format using $...$ or $$...$$.")

class PracticeTest(BaseModel):
    subject: str = Field(description="The subject of the test.")
    chapter: str = Field(description="The chapter name.")
    questions: list[MCQQuestion] = Field(description="A list containing exactly 15 randomized MCQ questions.")

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if "test_questions" not in st.session_state:
    st.session_state.test_questions = None
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "test_start_token" not in st.session_state:
    st.session_state.test_start_token = ""
if "active_subject" not in st.session_state:
    st.session_state.active_subject = ""
if "active_chapter" not in st.session_state:
    st.session_state.active_chapter = ""
if "time_spent_secs" not in st.session_state:
    st.session_state.time_spent_secs = 0

# ==========================================
# BACKEND GENERATION FUNCTION
# ==========================================
def generate_questions(api_key, subject, chapter):
    try:
        client = genai.Client(api_key=api_key)
        
        # Inject seed/timestamp to completely bypass local/server caching & ensure random questions
        rand_seed = random.randint(100000, 999999)
        curr_time = time.time()
        
        prompt = f"""
        You are a highly experienced CBSE Class 12 examiner and educator.
        Create an elegant practice exam of exactly 15 MCQ questions for:
        - Subject: {subject}
        - Chapter: {chapter}

        INSTRUCTIONS FOR QUESTION POOL GENERATION:
        1. Base all questions strictly on the CBSE Class 12 Syllabus.
        2. Ensure questions vary in difficulty: Easy (~30%), Medium (~40%), Hard (~30%).
        3. Make the questions diverse, covering different parts of the chapter.
        4. Questions must be single-select with 4 option choices (A, B, C, D).
        5. IMPORTANT FOR MATH & FORMULAS: You MUST format all mathematical expressions, equations, symbols, fractions, variables, matrices, exponents, integrations, derivatives, chemical reactions, and structures using standard LaTeX notation. 
           - Use single dollar signs ($...$) for inline math.
           - Use double dollar signs ($$...$$) for block equations/derivations.
           - Examples: $x^2 + y^2 = r^2$, $\\int_a^b f(x) dx$, $Fe^{{2+}}$, $A \\times B$.
           - This rule applies to: the question text, all option choices (A, B, C, D), and the detailed explanations.
        6. Avoid plain-text approximations like 'x^2' or 'integrate x'. Always use clean LaTeX: $x^2$ or $\\int x \\, dx$.
        7. Ensure the test questions are randomized. Seed: {rand_seed}, Timestamp: {curr_time}.
        
        Generate exactly 15 questions.
        Return the result strictly as JSON conforming to the schema.
        """
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=PracticeTest,
                temperature=0.85
            )
        )
        
        test_dict = json.loads(response.text)
        return test_dict
        
    except Exception as e:
        st.sidebar.error(f"Error calling Gemini API: {e}")
        return None

# ==========================================
# SIDEBAR CONTROLS
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px 0;">
        <h2 style="color: #f8fafc; font-size: 2rem; margin-bottom: 2px;">DailyPractise ✏️</h2>
        <p style="color: #64748b; font-size: 0.85rem;">CBSE Class 12 Test PortaL</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # API key selection & hiding
    api_key_input = st.text_input(
        "Gemini API Key",
        value=DEFAULT_API_KEY,
        type="password",
        help="Input your Gemini API Key here. It remains secure in the browser session memory and won't be pushed to GitHub."
    )
    
    if not api_key_input:
        st.warning("⚠️ Enter an API key in the sidebar to start.")
        
    st.markdown("---")
    
    # Subject & Chapter dynamic selector
    subject_selected = st.selectbox(
        "Select Subject",
        options=list(SUBJECTS_AND_CHAPTERS.keys()),
        index=0,
        disabled=(st.session_state.test_questions is not None and not st.session_state.submitted)
    )
    
    chapter_selected = st.selectbox(
        "Select Chapter",
        options=SUBJECTS_AND_CHAPTERS[subject_selected],
        index=0,
        disabled=(st.session_state.test_questions is not None and not st.session_state.submitted)
    )
    
    st.markdown("---")
    
    # Action Button
    if st.session_state.test_questions is not None and not st.session_state.submitted:
        # Reset button when test is ongoing
        if st.button("🔴 Quit and Reset Test", use_container_width=True):
            st.session_state.test_questions = None
            st.session_state.user_answers = {}
            st.session_state.submitted = False
            st.session_state.start_time = None
            st.session_state.test_start_token = ""
            st.rerun()
    else:
        # Generate button
        generate_btn = st.button(
            "🚀 Generate 1-Hour Test",
            use_container_width=True,
            disabled=not api_key_input
        )
        
        if generate_btn:
            with st.spinner("Generating 15 randomized MCQ problems..."):
                test_data = generate_questions(api_key_input, subject_selected, chapter_selected)
                if test_data and "questions" in test_data and len(test_data["questions"]) == 15:
                    st.session_state.test_questions = test_data["questions"]
                    st.session_state.user_answers = {q["id"]: None for q in test_data["questions"]}
                    st.session_state.submitted = False
                    st.session_state.start_time = time.time()
                    st.session_state.test_start_token = str(random.randint(1000, 9999))
                    st.session_state.active_subject = subject_selected
                    st.session_state.active_chapter = chapter_selected
                    st.session_state.time_spent_secs = 0
                    st.rerun()
                else:
                    st.error("Failed to generate test. Please try again or verify your API key.")
                    
    # Return to Hub button if running from hub
    if os.environ.get("RUNNING_FROM_HUB") == "True":
        st.markdown("---")
        st.markdown("""
            <div style="text-align: center; margin-top: 15px;">
                <a href="http://localhost:8500" target="_self" style="
                    text-decoration: none; 
                    color: #ffffff; 
                    background: linear-gradient(135deg, #14b8a6, #0d9488); 
                    padding: 10px 20px; 
                    border-radius: 8px; 
                    display: block; 
                    font-weight: bold;
                    text-align: center;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.2);
                ">🔙 Return to EduHub</a>
            </div>
        """, unsafe_allow_html=True)


# ==========================================
# MAIN APP BODY
# ==========================================

# 1. LANDING PAGE VIEW
if st.session_state.test_questions is None:
    st.markdown(f"""
    <div class="header-box">
        <h1 class="header-title">DailyPractise ✏️</h1>
        <p class="header-subtitle">CBSE Class 12 MCQ Practice Platform • 15 Problems • 1 Hour</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="glass-card">
            <h3>⚡ Test Parameters</h3>
            <ul>
                <li><b>Subjects Covered:</b> Physics, Chemistry, Maths, Painting, English, Computer Science.</li>
                <li><b>CBSE Class 12 Syllabus:</b> Questions align with standard curriculum concepts and blueprints.</li>
                <li><b>Structured Layout:</b> Exactly 15 randomized single-select MCQs.</li>
                <li><b>Target Duration:</b> 60 Minutes (suggested speed: 4 mins per question).</li>
                <li><b>API Key Protected:</b> Read from system environment or safely supplied in the sidebar without git risks.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="glass-card">
            <h3>📖 Instructions</h3>
            <ol>
                <li>Input your Gemini API key in the sidebar.</li>
                <li>Select the subject and specific chapter.</li>
                <li>Click <b>Generate 1-Hour Test</b> to fetch a new set of 15 randomized questions.</li>
                <li>Keep track of the local sidebar timer.</li>
                <li>Review detailed formulas and reactions rendered beautifully in LaTeX.</li>
                <li>Submit to view a comprehensive score dashboard and step-by-step solutions!</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

# 2. RUNNING TEST ENVIRONMENT
elif st.session_state.test_questions is not None and not st.session_state.submitted:
    # Compute and enforce timer
    elapsed_time = time.time() - st.session_state.start_time
    remaining_secs = max(0, 3600 - int(elapsed_time))
    
    # Auto-submit if time runs out
    if remaining_secs <= 0:
        st.session_state.submitted = True
        st.session_state.time_spent_secs = 3600
        st.warning("⏱️ Time limit of 1 hour exceeded! Your test is automatically submitted.")
        st.rerun()
        
    # Render countdown timer inside sidebar (isolated JS runtime to avoid Streamlit page redraws)
    with st.sidebar:
        st.markdown("### ⏱️ Test Timer")
        timer_html = f"""
        <div style="text-align: center; font-family: 'Outfit', sans-serif; background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255,255,255,0.08); padding: 15px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.35);">
            <div style="font-size: 0.85rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;">Time Remaining</div>
            <div id="timer-display" style="font-size: 2.2rem; font-weight: 800; color: #10b981; text-shadow: 0 0 10px rgba(16, 185, 129, 0.2);">60:00</div>
        </div>
        <script>
            var secondsLeft = {remaining_secs};
            var timerDisplay = document.getElementById('timer-display');
            
            function updateTimer() {{
                if (secondsLeft <= 0) {{
                    timerDisplay.innerHTML = "00:00";
                    timerDisplay.style.color = "#ef4444";
                    timerDisplay.style.animation = "pulse 1s infinite";
                    return;
                }}
                secondsLeft--;
                var mins = Math.floor(secondsLeft / 60);
                var secs = secondsLeft % 60;
                timerDisplay.innerHTML = 
                    (mins < 10 ? "0" + mins : mins) + ":" + 
                    (secs < 10 ? "0" + secs : secs);
                    
                if (secondsLeft < 300) {{ // < 5 mins
                    timerDisplay.style.color = "#ef4444";
                }} else if (secondsLeft < 900) {{ // < 15 mins
                    timerDisplay.style.color = "#f59e0b";
                }} else {{
                    timerDisplay.style.color = "#10b981";
                }}
            }}
            
            setInterval(updateTimer, 1000);
            updateTimer();
        </script>
        <style>
            @keyframes pulse {{
                0% {{ opacity: 1; }}
                50% {{ opacity: 0.4; }}
                100% {{ opacity: 1; }}
            }}
        </style>
        """
        st.components.v1.html(timer_html, height=110)
        
        st.markdown("---")
        # Visual progress representation
        attempted_count = sum(1 for ans in st.session_state.user_answers.values() if ans is not None)
        st.metric("Attempted Questions", f"{attempted_count} / 15")
        st.progress(attempted_count / 15)

    # Core quiz UI
    st.markdown(f"""
    <div class="header-box">
        <h2 class="header-title">{st.session_state.active_subject} Practice Exam</h2>
        <p class="header-subtitle">Topic: {st.session_state.active_chapter} • MCQ Format • Single-Select</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")

    # Render questions
    for idx, q_dict in enumerate(st.session_state.test_questions):
        # Convert to object to handle safely
        class Struct:
            def __init__(self, **entries):
                self.__dict__.update(entries)
        q = Struct(**q_dict)
        
        with st.container():
            st.markdown(f"""
            <div class="glass-card">
                <div style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 5px; font-weight: 600;">QUESTION {q.id} OF 15</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display Question and Choices in standard markdown to support LaTeX equations
            st.markdown(q.question)
            
            # Display Choices clearly
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**A)** {q.option_a}")
                st.markdown(f"**C)** {q.option_c}")
            with col_b:
                st.markdown(f"**B)** {q.option_b}")
                st.markdown(f"**D)** {q.option_d}")
            
            # Use horizontal radio button with selection characters to record input
            current_ans = st.session_state.user_answers.get(q.id)
            default_idx = 0
            if current_ans == "A": default_idx = 1
            elif current_ans == "B": default_idx = 2
            elif current_ans == "C": default_idx = 3
            elif current_ans == "D": default_idx = 4
            
            selected_choice = st.radio(
                f"Your Answer for Question {q.id}:",
                options=["Not Attempted", "A", "B", "C", "D"],
                index=default_idx,
                horizontal=True,
                key=f"radio_{q.id}_{st.session_state.test_start_token}"
            )
            
            # Save selection to session_state
            if selected_choice == "Not Attempted":
                st.session_state.user_answers[q.id] = None
            else:
                st.session_state.user_answers[q.id] = selected_choice
                
            st.markdown("<br>", unsafe_allow_html=True)

    st.write("---")
    
    # Submission Button
    submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
    with submit_col2:
        if st.button("🎯 Submit Practice Test", use_container_width=True, type="primary"):
            st.session_state.submitted = True
            st.session_state.time_spent_secs = int(time.time() - st.session_state.start_time)
            st.rerun()

# 3. POST ANALYSIS VIEW
else:
    # Calculations
    questions = st.session_state.test_questions
    user_answers = st.session_state.user_answers
    
    correct_count = 0
    incorrect_count = 0
    unattempted_count = 0
    
    for q_dict in questions:
        q_id = q_dict["id"]
        correct_ans = q_dict["correct_option"].strip().upper()
        user_ans = user_answers.get(q_id)
        
        if user_ans is None:
            unattempted_count += 1
        elif user_ans.strip().upper() == correct_ans:
            correct_count += 1
        else:
            incorrect_count += 1
            
    score_pct = int((correct_count / 15) * 100)
    
    # Format elapsed time
    spent_mins = st.session_state.time_spent_secs // 60
    spent_secs = st.session_state.time_spent_secs % 60
    time_str = f"{spent_mins}m {spent_secs}s" if spent_mins > 0 else f"{spent_secs}s"
    
    # Dashboard Header
    st.markdown(f"""
    <div class="header-box">
        <h1 class="header-title">Post-Test Analysis</h1>
        <p class="header-subtitle">{st.session_state.active_subject} • {st.session_state.active_chapter}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Results KPI layout
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Score", f"{correct_count} / 15", f"{score_pct}% Success")
    with col2:
        st.metric("Correct Answers", f"{correct_count}", delta_color="normal")
    with col3:
        st.metric("Incorrect / Skipped", f"{incorrect_count} / {unattempted_count}")
    with col4:
        st.metric("Time Taken", time_str, "Limit: 60 mins")
        
    st.write("---")
    
    # Performance Summary Card
    feedback_msg = ""
    feedback_color = ""
    if score_pct >= 85:
        feedback_msg = "Outstanding Performance! You have a solid grasp of this chapter's concepts. Ready for the Boards!"
        feedback_color = "#10b981"
    elif score_pct >= 60:
        feedback_msg = "Good Attempt! Most core concepts are clear, but review your weak points to maximize score potential."
        feedback_color = "#f59e0b"
    else:
        feedback_msg = "Additional Practice Needed! Focus on understanding the core formulas, definitions, and theory before retaking."
        feedback_color = "#ef4444"
        
    st.markdown(f"""
    <div class="glass-card" style="border-left: 6px solid {feedback_color};">
        <h3>📊 Performance Assessment</h3>
        <p style="font-size: 1.1rem; color: #f1f5f9;">{feedback_msg}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Solutions manual
    st.markdown("## 📖 Solution Manual & Detailed Explanations")
    
    for idx, q_dict in enumerate(questions):
        q_id = q_dict["id"]
        correct_ans = q_dict["correct_option"].strip().upper()
        user_ans = user_answers.get(q_id)
        
        status_class = ""
        badge_html = ""
        
        if user_ans is None:
            status_class = "unattempted-card"
            badge_html = '<span class="badge badge-unattempted">Unattempted</span>'
            user_display = "No selection"
        elif user_ans.strip().upper() == correct_ans:
            status_class = "correct-card"
            badge_html = '<span class="badge badge-correct">Correct ✓</span>'
            user_display = f"Option {user_ans}"
        else:
            status_class = "incorrect-card"
            badge_html = '<span class="badge badge-incorrect">Incorrect ✗</span>'
            user_display = f"Option {user_ans}"
            
        with st.container():
            st.markdown(f"""
            <div class="glass-card {status_class}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <div style="font-size: 0.95rem; color: #94a3b8; font-weight: 700;">QUESTION {q_id}</div>
                    <div>{badge_html}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show the question and options
            st.markdown(q_dict["question"])
            
            col_sa, col_sb = st.columns(2)
            with col_sa:
                st.markdown(f"**A)** {q_dict['option_a']}")
                st.markdown(f"**C)** {q_dict['option_c']}")
            with col_sb:
                st.markdown(f"**B)** {q_dict['option_b']}")
                st.markdown(f"**D)** {q_dict['option_d']}")
                
            # Responses comparison
            st.markdown(f"""
            <div style="margin-top: 10px; margin-bottom: 10px; font-size: 0.95rem;">
                <strong>Your Selected Answer:</strong> {user_display} &nbsp;|&nbsp; 
                <strong>Correct Answer:</strong> Option {correct_ans}
            </div>
            """, unsafe_allow_html=True)
            
            # Explanations container
            with st.expander("Show Step-by-Step Solution & Concept Explanation"):
                st.markdown("#### Solution:")
                st.markdown(q_dict["explanation"])
                
            st.markdown("<br>", unsafe_allow_html=True)
            
    # Retake options
    st.write("---")
    col_retake1, col_retake2, col_retake3 = st.columns([1, 2, 1])
    with col_retake2:
        if st.button("🔄 Take Another Practice Test", use_container_width=True, type="primary"):
            # Clear state to return to settings menu
            st.session_state.test_questions = None
            st.session_state.user_answers = {}
            st.session_state.submitted = False
            st.session_state.start_time = None
            st.session_state.test_start_token = ""
            st.rerun()
