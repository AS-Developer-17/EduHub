import os
import json
import streamlit as st
from pydantic import BaseModel, Field
import google.genai as genai
from google.genai import types

# Resolve default API key dynamically from environment or local secrets
DEFAULT_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if not DEFAULT_API_KEY:
    try:
        DEFAULT_API_KEY = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GOOGLE_API_KEY", "")
    except Exception:
        DEFAULT_API_KEY = ""

# Fallback: check local .streamlit/secrets.toml manually if st.secrets fails or is empty
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

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="RevisionIO - Competitive Exam Planner",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Premium Dark Mode Style & Typography
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

    /* Custom cards styling */
    .glass-card {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }
    
    /* Left accent borders for specific sections */
    .indigo-card {
        border-left: 5px solid #6366f1;
    }
    .teal-card {
        border-left: 5px solid #14b8a6;
    }
    .orange-card {
        border-left: 5px solid #f59e0b;
    }
    .pink-card {
        border-left: 5px solid #ec4899;
    }

    /* Gradient header box */
    .header-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #042f2e 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 30px 25px;
        margin-bottom: 25px;
        text-align: center;
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 30px -15px rgba(0, 0, 0, 0.6);
    }
    
    .header-title {
        color: #f8fafc;
        margin: 0;
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(to right, #ffffff, #c7d2fe, #14b8a6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .header-subtitle {
        color: #94a3b8;
        margin: 8px 0 0 0;
        font-size: 1.05rem;
        font-weight: 400;
    }

    /* Style the sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# PYDANTIC SCHEMA FOR STRUCTURED OUTPUT
# ==========================================
class PracticeQuestion(BaseModel):
    question: str = Field(description="A challenging practice question testing conceptual depth.")
    answer: str = Field(description="A detailed correct answer with explanation and shortcuts.")

class DayPlan(BaseModel):
    day: int = Field(description="The day number (1-indexed).")
    title: str = Field(description="Main focus of this day's revision.")
    key_topics: list[str] = Field(description="Core subtopics to cover on this day.")
    revision_bits: list[str] = Field(description="Concise, high-yield bullet notes, concepts, and NCERT-based core fundamentals.")
    formulas_or_key_terms: list[str] = Field(description="Crucial formulas (ASCII text format) or key glossary definitions.")
    exam_tips: list[str] = Field(description="Traps, common mistakes, Board/JEE/NEET scoring tips, or NCERT specific caveats.")
    practice_questions: list[PracticeQuestion] = Field(description="Exactly 3 practice questions with detailed answers.")

class RevisionPlanSchema(BaseModel):
    subject: str = Field(description="Subject name.")
    topic: str = Field(description="The revised topic.")
    target_class: str = Field(description="Targeted competitive exam or class standard.")
    days: list[DayPlan] = Field(description="Daily revision plan, exactly matching the requested duration.")


# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if "plan_data" not in st.session_state:
    st.session_state.plan_data = None
if "completed_days" not in st.session_state:
    st.session_state.completed_days = {}
if "current_view_day" not in st.session_state:
    st.session_state.current_view_day = 1


# ==========================================
# BACKEND API CALL
# ==========================================
def run_generation(api_key, target_class, subject, topic, days, hours):
    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        You are a premier senior IIT/NEET faculty member and academic revision architect.
        The student is preparing for the competitive exam / standard: {target_class}.
        The subject is: {subject}.
        The topic to revise: {topic}.
        The total revision window: {days} days.
        Student dedicates {hours} hours daily for this topic.

        Generate a highly structured, day-by-day revision syllabus matching the NCERT syllabus as the primary base, enhanced for competitive standards (detailed conceptual shortcuts, vital formulas, exam pitfalls, and standard high-yield questions).
        Each day must cover a sensible and distinct chunk that can be fully reviewed in {hours} hours.
        Make sure the mathematical formulas are clearly rendered in readable plain ASCII.
        You must output exactly {days} days in the JSON array.
        
        Return the output strictly in JSON format matching the schema.
        """
        
        # Using model gemini-2.5-flash as standard for high speed and reliable structure output
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RevisionPlanSchema,
                temperature=0.65
            )
        )
        
        plan_dict = json.loads(response.text)
        return plan_dict
        
    except Exception as e:
        st.sidebar.error(f"Gemini API Error: {e}")
        return None


# ==========================================
# SIDEBAR (INPUT & PLAN MANAGEMENT)
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px 0;">
        <h2 style="color: #f8fafc; font-size: 1.8rem; margin-bottom: 2px;">RevisionIO ⚡</h2>
        <span style="background: linear-gradient(135deg, #6366f1, #14b8a6); color: white; padding: 4px 10px; border-radius: 8px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Revision Engine</span>
    </div>
    <p style="text-align: center; color: #94a3b8; font-size: 0.85rem; margin-top: 5px;">Competitive Exam Daily Planner</p>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🎯 Configure Inputs")
    
    # 1. Target Exam Standard
    exam_options = [
        "JEE Main (PCM)",
        "JEE Advanced (PCM)",
        "NEET Prep (PCB)",
        "CUET Science (PCM/PCB)",
        "CUET Commerce (Accountancy/BST/Economics)",
        "CBSE Class 12 Boards + Competitive",
        "CBSE Class 11 Boards + Competitive",
        "CBSE Class 10 Boards + NTSE Foundation",
        "CBSE Class 9 Boards + Olympiad Prep",
        "Olympiad Foundation (Classes 6-8)"
    ]
    target_class = st.selectbox("Target Standard / Exam", options=exam_options, index=0)
    
    # 2. Subject Input
    subject_input = st.text_input("Subject", placeholder="e.g. Physics")
    
    # 3. Topic Input
    topic_input = st.text_input("Topic to Revise", placeholder="e.g. Electrostatics")
    
    # 4. Days Scale
    days_input = st.slider("Revision Period (Days)", min_value=1, max_value=30, value=5)
    
    # 5. Dedicated Hours
    hours_input = st.slider("Daily Study Commitment (Hours)", min_value=1, max_value=12, value=3)
    
    # 6. API Key Override
    api_key_override = st.text_input("Gemini API Key", value=DEFAULT_API_KEY, type="password", help="Overrides environment or secret config.")
    
    # Action Button: Generate
    if st.button("Generate Revision Plan ✨", use_container_width=True):
        if not subject_input.strip():
            st.warning("⚠️ Please specify the Subject.")
        elif not topic_input.strip():
            st.warning("⚠️ Please specify the Topic.")
        elif not api_key_override.strip():
            st.warning("⚠️ Please provide a Gemini API Key.")
        else:
            with st.spinner(f"Curating a tailored {days_input}-day plan for '{topic_input}' optimized for {target_class}..."):
                plan = run_generation(api_key_override.strip(), target_class, subject_input.strip(), topic_input.strip(), days_input, hours_input)
                if plan:
                    st.session_state.plan_data = plan
                    st.session_state.completed_days = {d["day"]: False for d in plan["days"]}
                    st.session_state.current_view_day = 1
                    st.toast("Revision plan generated successfully! ⚡", icon="🔥")
                    st.rerun()

    st.markdown("---")
    st.subheader("💾 Plan Storage")
    
    # Save button
    if st.session_state.plan_data is not None:
        packaged_data = {
            "plan": st.session_state.plan_data,
            "completed_days": st.session_state.completed_days,
            "view_day": st.session_state.current_view_day
        }
        json_str = json.dumps(packaged_data, indent=4, ensure_ascii=False)
        st.download_button(
            label="Save Plan to Disk 💾",
            data=json_str,
            file_name=f"{st.session_state.plan_data.get('topic', 'Revision')}_Plan.json",
            mime="application/json",
            use_container_width=True
        )
        
    # Load File Uploader
    uploaded_file = st.file_uploader("Load Plan from Disk 📂", type=["json"])
    if uploaded_file is not None:
        try:
            loaded_data = json.load(uploaded_file)
            if "plan" in loaded_data and "completed_days" in loaded_data:
                st.session_state.plan_data = loaded_data["plan"]
                st.session_state.completed_days = {int(k): bool(v) for k, v in loaded_data["completed_days"].items()}
                st.session_state.current_view_day = int(loaded_data.get("view_day", 1))
                st.toast("Plan successfully restored! 🎉", icon="✅")
                st.rerun()
            else:
                st.error("Invalid file format standard.")
        except Exception as e:
            st.error(f"Error loading: {e}")
            
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
# MAIN DASHBOARD PANEL
# ==========================================
st.markdown("""
<div class="header-box">
    <h1 class="header-title">RevisionIO</h1>
    <p style="color: #14b8a6; font-size: 1.15rem; font-weight: bold; margin-top: 5px; margin-bottom: 0;">⚡ Competitive Revision Engine ⚡</p>
</div>
""", unsafe_allow_html=True)

if st.session_state.plan_data is None:
    st.markdown("""
    <div class="glass-card" style="text-align: center; max-width: 600px; margin: 40px auto; border-top: 4px solid #6366f1;">
        <h3 style="font-size: 1.8rem; color: #f8fafc; margin-bottom: 10px;">No Plan Active</h3>
        <p style="color: #94a3b8; font-size: 0.95rem; line-height: 1.6; margin-bottom: 20px;">
            Configure your target exam, subject, and topic on the left sidebar, then click <b>'Generate Revision Plan'</b> to create a comprehensive daily revision schedule.
        </p>
        <p style="color: #64748b; font-size: 0.85rem; margin-top: 5px;">
            Or, reload an existing plan using the <b>'Load Plan from Disk'</b> section in the sidebar.
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Plan info header card
    plan = st.session_state.plan_data
    topic = plan.get("topic", "N/A")
    subject = plan.get("subject", "N/A")
    cls_standard = plan.get("target_class", "N/A")
    total_days = len(plan["days"])
    
    st.markdown(f"""
    <div class="glass-card" style="padding: 20px 25px; margin-bottom: 15px;">
        <h2 style="color: #f8fafc; font-size: 1.5rem; margin-bottom: 5px;">Roadmap: {topic}</h2>
        <span style="color: #14b8a6; font-weight: bold; font-size: 0.95rem;">
            Subject: {subject} &nbsp;|&nbsp; Target: {cls_standard} &nbsp;|&nbsp; Duration: {total_days} Days
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress & Day Navigation Row
    nav_col, prog_col = st.columns([3, 2], vertical_alignment="center")
    
    with nav_col:
        st.session_state.current_view_day = st.slider(
            "Navigate Days",
            min_value=1,
            max_value=total_days,
            value=st.session_state.current_view_day,
            step=1
        )
        day_num = st.session_state.current_view_day
        
    with prog_col:
        # Checkbox completion for this day
        if day_num not in st.session_state.completed_days:
            st.session_state.completed_days[day_num] = False
            
        is_completed = st.checkbox(
            f"Mark Day {day_num} as Completed",
            value=st.session_state.completed_days.get(day_num, False),
            key=f"comp_check_{day_num}"
        )
        st.session_state.completed_days[day_num] = is_completed
        
        # Draw progress bar
        completed_days_count = sum(1 for val in st.session_state.completed_days.values() if val)
        progress_fraction = completed_days_count / total_days
        st.progress(progress_fraction)
        st.markdown(f"<div style='text-align: right; font-size: 0.85rem; color: #94a3b8; font-weight: bold;'>Progress: {completed_days_count}/{total_days} Days Completed ({int(progress_fraction * 100)}%)</div>", unsafe_allow_html=True)
        
        # Celebration trigger
        if all(st.session_state.completed_days.get(d, False) for d in range(1, total_days + 1)):
            st.balloons()
            st.success("🏆 **Excellent!** You have successfully completed your entire revision plan! 🎓")

    # Render day contents
    day_data = next((d for d in plan["days"] if d["day"] == day_num), None)
    if day_data:
        st.markdown(f"""
        <div class="glass-card" style="margin-bottom: 20px;">
            <div style="font-size: 0.85rem; font-weight: bold; color: #14b8a6; text-transform: uppercase;">DAY {day_num} FOCUS</div>
            <h3 style="color: #f8fafc; font-size: 1.35rem; margin-top: 4px; margin-bottom: 0;">{day_data.get('title', '')}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Layout divisions
        c1, c2 = st.columns(2)
        
        with c1:
            # 1. Subtopics Card
            topics_html = "".join([f"<li>{t}</li>" for t in day_data.get("key_topics", [])])
            st.markdown(f"""
            <div class="glass-card indigo-card" style="height: 100%;">
                <h4 style="color: #f8fafc; font-size: 1.05rem; margin-top: 0; margin-bottom: 12px;">🎯 Core Subtopics to Cover</h4>
                <ul style="color: #94a3b8; font-size: 0.9rem; padding-left: 20px;">
                    {topics_html}
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
        with c2:
            # 2. Formulas/Terms Card
            formulas_html = "".join([
                f"<div style='background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 10px; margin-bottom: 6px; font-family: monospace; color: #facc15; font-size: 0.85rem;'>{f}</div>"
                for f in day_data.get("formulas_or_key_terms", [])
            ])
            st.markdown(f"""
            <div class="glass-card orange-card" style="height: 100%;">
                <h4 style="color: #f8fafc; font-size: 1.05rem; margin-top: 0; margin-bottom: 12px;">📝 Crucial Formulas & Terms</h4>
                {formulas_html}
            </div>
            """, unsafe_allow_html=True)
            
        st.write("") # Spacer
        
        # 3. Revision Bits (Concept Notes)
        bits_html = "".join([f"<p style='margin-bottom: 8px;'>✦ {b}</p>" for b in day_data.get("revision_bits", [])])
        st.markdown(f"""
        <div class="glass-card teal-card">
            <h4 style="color: #f8fafc; font-size: 1.05rem; margin-top: 0; margin-bottom: 12px;">💡 Revision Bits (High-Yield Concept Notes)</h4>
            <div style="color: #e2e8f0; font-size: 0.95rem; line-height: 1.6;">
                {bits_html}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 4. Exam Traps & NCERT Guidance
        tips_html = "".join([f"<p style='margin-bottom: 6px; color: #f43f5e;'>• {t}</p>" for t in day_data.get("exam_tips", [])])
        st.markdown(f"""
        <div class="glass-card pink-card">
            <h4 style="color: #f8fafc; font-size: 1.05rem; margin-top: 0; margin-bottom: 12px;">⚠️ Competitive Exam Traps & NCERT Core Guidance</h4>
            <div style="font-size: 0.95rem; line-height: 1.6;">
                {tips_html}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 5. Practice Challenges
        st.markdown("### 🔥 Daily Practice Challenges")
        for idx, q_item in enumerate(day_data.get("practice_questions", [])):
            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.25); border: 1px solid rgba(255,255,255,0.05); border-left: 4px solid #14b8a6; padding: 15px; border-radius: 8px; margin-bottom: 8px;">
                <div style="font-size: 0.8rem; font-weight: bold; color: #14b8a6; text-transform: uppercase;">Problem {idx+1}</div>
                <div style="font-weight: bold; color: #f8fafc; font-size: 0.95rem; margin-top: 2px;">{q_item.get('question', '')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("Reveal Detailed Solution 👁️"):
                st.success(f"**Detailed Solution:**\n\n{q_item.get('answer', '')}")
