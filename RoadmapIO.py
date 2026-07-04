import os
import json
import streamlit as st
import google.genai as genai
from google.genai import types
from pydantic import BaseModel, Field

# Set up page configuration
st.set_page_config(
    page_title="RoadmapIO - Tailored Learning & Algorithms",
    page_icon="🗺️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom Premium & Minimal Styling
st.markdown("""
<style>
    /* Import modern typography */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    /* Apply fonts globally */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    /* Minimal header container */
    .header-box {
        background: linear-gradient(135deg, rgba(20, 24, 33, 0.8) 0%, rgba(10, 12, 18, 0.95) 100%);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 35px 25px;
        margin-bottom: 25px;
        text-align: center;
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 30px -15px rgba(0, 0, 0, 0.6);
    }

    .header-box::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.08) 0%, transparent 60%);
        pointer-events: none;
    }
    
    .header-title {
        margin: 0;
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -1px;
        background: linear-gradient(to right, #ffffff, #c7d2fe, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .header-subtitle {
        color: #94a3b8;
        margin: 10px 0 0 0;
        font-size: 1.05rem;
        font-weight: 300;
    }

    /* Custom containers */
    .glass-card {
        background: rgba(30, 41, 59, 0.25);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.3);
    }
    
    /* Stepper progress indicator */
    .stepper-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 30px;
        padding: 0 10px;
    }
    
    .stepper-item {
        flex: 1;
        text-align: center;
        position: relative;
    }
    
    .stepper-item::after {
        content: '';
        position: absolute;
        top: 16px;
        left: 50%;
        width: 100%;
        height: 2px;
        background: rgba(255, 255, 255, 0.06);
        z-index: 1;
    }
    
    .stepper-item:last-child::after {
        content: none;
    }
    
    .stepper-circle {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #1e293b;
        border: 2px solid rgba(255, 255, 255, 0.08);
        color: #64748b;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 8px auto;
        font-weight: 600;
        font-size: 0.9rem;
        position: relative;
        z-index: 2;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stepper-item.active .stepper-circle {
        background: #4f46e5;
        border-color: #818cf8;
        color: #ffffff;
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.35);
    }
    
    .stepper-item.completed .stepper-circle {
        background: #059669;
        border-color: #34d399;
        color: #ffffff;
    }
    
    .stepper-text {
        font-size: 0.8rem;
        color: #64748b;
        font-weight: 500;
    }
    
    .stepper-item.active .stepper-text {
        color: #a5b4fc;
        font-weight: 600;
    }
    
    .stepper-item.completed .stepper-text {
        color: #a7f3d0;
    }

    /* Input focus borders */
    div[data-baseweb="textarea"] textarea, div[data-baseweb="input"] input {
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }
    
    div[data-baseweb="textarea"] textarea:focus, div[data-baseweb="input"] input:focus {
        border-color: rgba(99, 102, 241, 0.5) !important;
        box-shadow: 0 0 8px rgba(99, 102, 241, 0.15) !important;
    }
    
    /* Styled Markdown adjustments */
    .stMarkdown {
        line-height: 1.6;
    }
    
    /* Scrollbar minimal styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.1);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Resolve default API key
DEFAULT_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if not DEFAULT_API_KEY:
    try:
        DEFAULT_API_KEY = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GOOGLE_API_KEY", "")
    except Exception:
        DEFAULT_API_KEY = ""

# Sidebar - Settings & Config
with st.sidebar:
    st.markdown("### ⚙️ Engine Settings")
    
    custom_key = st.text_input(
        "Gemini API Key",
        value=st.session_state.get("api_key", DEFAULT_API_KEY),
        type="password",
        help="Provide your own Gemini API Key to bypass the default limitations."
    )
    
    st.session_state.api_key = custom_key.strip()
    
    st.markdown("---")
    st.markdown("### 🔍 Model Configuration")
    target_model = st.selectbox(
        "Select Model",
        options=["gemini-2.5-flash", "gemini-2.5-pro"],
        index=0,
        help="Flash is recommended for fast response times. Pro is ideal for complex algorithms."
    )
    
    st.markdown("---")
    if st.button("🔄 Clear System & Reset", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
        
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


# Header Section
st.markdown("""
<div class="header-box">
    <h1 class="header-title">RoadmapIO</h1>
    <p class="header-subtitle">Interactive tailored algorithms and learning paths powered by Gemini</p>
</div>
""", unsafe_allow_html=True)

# Define Pydantic Schema for structured follow-ups
class FollowUpSchema(BaseModel):
    questions: list[str] = Field(
        description="Exactly 3 highly targeted and specific clarifying questions to customize the final algorithm or roadmap."
    )

# Session State Initialization
if "step" not in st.session_state:
    st.session_state.step = 0
if "mode" not in st.session_state:
    st.session_state.mode = "Roadmap"
if "user_query" not in st.session_state:
    st.session_state.user_query = ""
if "suggested_query" not in st.session_state:
    st.session_state.suggested_query = ""
if "followups" not in st.session_state:
    st.session_state.followups = []
if "followup_answers" not in st.session_state:
    st.session_state.followup_answers = {}
if "final_output" not in st.session_state:
    st.session_state.final_output = ""

# Draw Stepper
draw_stepper = lambda step: st.markdown(f"""
<div class="stepper-container">
    <div class="stepper-item {'completed' if step > 0 else 'active'}">
        <div class="stepper-circle">{'✓' if step > 0 else '1'}</div>
        <div class="stepper-text">Define Goal</div>
    </div>
    <div class="stepper-item {'completed' if step > 1 else ('active' if step == 1 else '')}">
        <div class="stepper-circle">{'✓' if step > 1 else '2'}</div>
        <div class="stepper-text">Specify Context</div>
    </div>
    <div class="stepper-item {'active' if step == 2 else ''}">
        <div class="stepper-circle">3</div>
        <div class="stepper-text">Tailored Plan</div>
    </div>
</div>
""", unsafe_allow_html=True)

draw_stepper(st.session_state.step)

# Helper to fetch google genai client
def get_client():
    if not st.session_state.api_key:
        st.error("🔑 API Key is required. Please add your Gemini API Key in the sidebar.")
        return None
    try:
        return genai.Client(api_key=st.session_state.api_key)
    except Exception as e:
        st.error(f"Failed to initialize Gemini Client: {e}")
        return None

# ==========================================
# STEP 0: INITIALIZATION & GOAL SETTING
# ==========================================
if st.session_state.step == 0:
    st.markdown("### 🗺️ Define Your Learning Path or Algorithm Goal")
    
    # Selection Mode
    mode_selection = st.radio(
        "What do you want to generate?",
        options=["Roadmap 🗺️", "Algorithm ⚙️"],
        index=0 if st.session_state.mode == "Roadmap" else 1,
        horizontal=True,
        help="Select Roadmap to build structural learning modules/schedules. Select Algorithm for step-by-step engineering logic."
    )
    # Save selection back
    st.session_state.mode = "Roadmap" if "Roadmap" in mode_selection else "Algorithm"
    
    # Input Request
    initial_val = st.session_state.suggested_query if st.session_state.suggested_query else ""
    user_query = st.text_area(
        "Enter your requirement / subject / system architecture:",
        value=initial_val,
        placeholder="e.g. Master Go (Golang) backend dev in 3 months OR Design an LRU cache with expiration & disk write-back",
        height=130
    )
    
    # Suggestion chips
    st.markdown("##### 💡 Try these inspiration prompts:")
    sugs_roadmap = [
        ("Learn Rust & Systems Programming", "Roadmap"),
        ("Master Machine Learning Foundations", "Roadmap"),
        ("Become a fullstack Next.js developer", "Roadmap")
    ]
    sugs_algo = [
        ("LRU cache with time-expiry constraints", "Algorithm"),
        ("A* pathfinding with real-time dynamic traffic costs", "Algorithm"),
        ("Autocomplete trie search engine with prefix matching", "Algorithm")
    ]
    
    cols = st.columns(3)
    suggestions = sugs_roadmap if st.session_state.mode == "Roadmap" else sugs_algo
    
    for idx, (s_text, m_type) in enumerate(suggestions):
        with cols[idx]:
            if st.button(s_text, key=f"sug_btn_{idx}", use_container_width=True):
                st.session_state.suggested_query = s_text
                st.rerun()

    st.markdown("---")
    
    # Action buttons
    col_l, col_r = st.columns([4, 1])
    with col_r:
        if st.button("Next ➔", use_container_width=True):
            if not user_query.strip():
                st.warning("⚠️ Please provide a requirement or select a suggestion above.")
            else:
                st.session_state.user_query = user_query.strip()
                st.session_state.suggested_query = "" # Clear temporary value
                
                # Fetch clarifying questions
                client = get_client()
                if client:
                    with st.spinner("Analyzing requirements & tailoring questions..."):
                        prompt = f"""
                        You are a world-class {'tutor and technical mentor' if st.session_state.mode == 'Roadmap' else 'senior software engineer and algorithm expert'}.
                        The user has requested to generate a customized {st.session_state.mode} for:
                        "{st.session_state.user_query}"
                        
                        Before generating the final plan, you need to gather specific constraints or goals.
                        Generate exactly 3 highly relevant and concise clarifying questions.
                        
                        Example topics to ask about:
                        - For a Roadmap: user's current skill level/background, time commitment per week, preferred resources (hands-on coding, video resources, docs), or immediate target project.
                        - For an Algorithm: language preference, expected input size or scale, execution constraints (e.g. latency, memory limits), or error handling behavior.
                        
                        You must return the list of exactly 3 questions in a structured format.
                        """
                        try:
                            response = client.models.generate_content(
                                model=target_model,
                                contents=prompt,
                                config=types.GenerateContentConfig(
                                    response_mime_type="application/json",
                                    response_schema=FollowUpSchema,
                                    temperature=0.7,
                                    thinking_config=types.ThinkingConfig(thinking_budget=0)
                                )
                            )
                            data = json.loads(response.text)
                            st.session_state.followups = data.get("questions", [])
                            st.session_state.step = 1
                            st.rerun()
                        except Exception as e:
                            # Fallback if API fails or parse fails
                            st.session_state.followups = [
                                "What is your target programming language or tech stack preference?",
                                "What is your current experience level with this topic?",
                                "What are your primary constraints (e.g., time limit, scale of data, target goals)?"
                            ]
                            st.session_state.step = 1
                            st.rerun()

# ==========================================
# STEP 1: FOLLOW-UP CLARIFICATIONS
# ==========================================
elif st.session_state.step == 1:
    st.markdown("### 🔍 Help us optimize your results")
    st.info("Based on your goal, Gemini needs a bit more context to generate the most feasible and optimal plan.")
    
    # Render dynamic questions
    answers = {}
    with st.form("clarification_form"):
        for idx, question in enumerate(st.session_state.followups):
            st.markdown(f"**Question {idx+1}:** {question}")
            answers[question] = st.text_input(
                "Your Answer:",
                key=f"ans_input_{idx}",
                placeholder="Type your response here..."
            )
            st.write("") # Spacer
            
        st.markdown("---")
        
        c_left, c_right = st.columns([1, 4])
        with c_left:
            # Inside form, we can't easily trigger a rerun to change step without form submission
            back_clicked = st.form_submit_button("⬅️ Back")
        with c_right:
            generate_clicked = st.form_submit_button("✨ Generate Optimized Output")
            
        if back_clicked:
            st.session_state.step = 0
            st.rerun()
            
        if generate_clicked:
            # Save answers
            st.session_state.followup_answers = answers
            
            client = get_client()
            if client:
                with st.spinner("Synthesizing tailored information..."):
                    # Construct optimized prompts
                    mode = st.session_state.mode
                    prompt = f"""
                    You are a world-class {'tutor and technical mentor' if mode == 'Roadmap' else 'senior software engineer and algorithm expert'}.
                    
                    Generate a highly customized, feasible, and optimal {mode} for:
                    "{st.session_state.user_query}"
                    
                    Here are the answers to the clarifying questions to guide your design details:
                    """
                    for q, a in answers.items():
                        prompt += f"\n- Question: {q}\n  Answer: {a if a.strip() else 'No specific preference'}"
                    
                    if mode == "Algorithm":
                        prompt += """
                        
                        Please format the output using clean, beautiful Markdown with the following structured sections:
                        1. **Design Strategy & Objectives**: Provide a summary of the approach, algorithmic tradeoffs, and chosen data structures.
                        2. **Detailed Pseudocode**: Write clear, highly readable, structured pseudocode.
                        3. **Clean Code Implementation**: Provide a production-ready, fully-commented implementation in the user's preferred language (if not specified, default to Python). Ensure the code handles boundary conditions and error cases.
                        4. **Complexity Analysis**: Display Time and Space Complexity (Best, Average, Worst case) in a clean Markdown Table using Big-O notation. Explain why these complexities occur.
                        5. **Edge Cases & Failure Modes**: Highlight specific critical scenarios (e.g. empty values, integer overflow, concurrency conditions) and how the implementation handles them.
                        """
                    else: # Roadmap
                        prompt += """
                        
                        Please format the output using clean, beautiful Markdown with the following structured sections:
                        1. **Executive Overview**: Summarize the scope, prerequisites, and expected outcomes.
                        2. **Module/Phase Timeline**: Display a clear phase-by-phase schedule in a Markdown Table including estimated study hours.
                        3. **Phase Details (Milestones)**: For each phase:
                           - **Mastery Checklist**: Specific core concepts to understand.
                           - **Practical Project**: A realistic, hands-on coding task or mini-project to build.
                           - **Curated Resources**: Reference links, docs, or materials.
                        4. **Optimal Study & Practice Strategy**: Tips for code reviews, testing, retaining concepts, and debugging.
                        5. **Success Criteria**: Specific checkpoints to verify if they are ready to proceed to the next module.
                        """
                    
                    try:
                        response = client.models.generate_content(
                            model=target_model,
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                temperature=0.7,
                                thinking_config=types.ThinkingConfig(thinking_budget=0)
                            )
                        )
                        st.session_state.final_output = response.text
                        st.session_state.step = 2
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error during final roadmap generation: {e}")

# ==========================================
# STEP 2: DISPLAY FINAL TAILORED PLAN
# ==========================================
elif st.session_state.step == 2:
    st.markdown("### 🎉 Your Optimized Plan is Ready!")
    
    # Render final output
    st.markdown(f'<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(st.session_state.final_output)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Actions on result
    col_dl, col_rs = st.columns([3, 1])
    with col_dl:
        st.download_button(
            label="📥 Download Plan (.md)",
            data=st.session_state.final_output,
            file_name=f"{st.session_state.mode.lower()}_plan.md",
            mime="text/markdown",
            use_container_width=True
        )
    with col_rs:
        if st.button("🔄 Create New", use_container_width=True):
            st.session_state.step = 0
            st.session_state.user_query = ""
            st.session_state.followups = []
            st.session_state.followup_answers = {}
            st.session_state.final_output = ""
            st.rerun()
