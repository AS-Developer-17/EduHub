import os
import streamlit as st
import google.genai as genai
from PIL import Image
import json

# Set up Streamlit Page Configuration
st.set_page_config(
    page_title="JEE Igniter - AI Mentorship & Doubt Solver",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling (Dark Mode, Glassmorphism, Custom Cards)
st.markdown("""
<style>
    /* Main body background & typography */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
    }

    /* Gradient header banner */
    .header-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #042f2e 100%);
        padding: 35px 25px;
        border-radius: 20px;
        margin-bottom: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.7);
        text-align: center;
        position: relative;
        overflow: hidden;
    }

    .header-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, transparent 60%);
        pointer-events: none;
    }

    .header-title {
        color: #f8fafc;
        margin: 0;
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(to right, #ffffff, #c7d2fe, #38bdf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .header-subtitle {
        color: #94a3b8;
        margin: 10px 0 0 0;
        font-size: 1.15rem;
        font-weight: 400;
    }

    /* Styled cards */
    .feature-card {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.3);
    }

    .card-title {
        color: #e2e8f0;
        font-size: 1.25rem;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .card-content {
        color: #94a3b8;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    /* Custom labels and alerts */
    .jee-badge {
        background: linear-gradient(135deg, #4f46e5, #06b6d4);
        color: white;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 10px;
    }

    /* Sidebar updates */
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Styled buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 10px;
        padding: 10px 24px;
        transition: all 0.3s ease;
    }

    div.stButton > button:hover {
        background: linear-gradient(135deg, #4338ca 0%, #2563eb 100%);
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.4);
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# Define default API Key from environment variables or Streamlit secrets
DEFAULT_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if not DEFAULT_API_KEY:
    try:
        DEFAULT_API_KEY = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GOOGLE_API_KEY", "")
    except Exception:
        DEFAULT_API_KEY = ""

# Sidebar Configuration
st.sidebar.markdown("""
<div style="text-align: center; padding: 15px 0;">
    <h2 style="color: #f8fafc; font-size: 1.8rem; margin-bottom: 5px;">⚡ JEE Igniter</h2>
    <span class="jee-badge">Aspirant Workspace</span>
</div>
""", unsafe_allow_html=True)

# API key selection in sidebar
custom_api_key = st.sidebar.text_input(
    "Gemini API Key",
    value=DEFAULT_API_KEY,
    type="password",
    help="Provide your Gemini API Key here or set the GEMINI_API_KEY environment variable."
)

# Initialize GenAI Client
if custom_api_key:
    client = genai.Client(api_key=custom_api_key)
else:
    client = None
    st.sidebar.warning("⚠️ API Key missing! AI functions will be disabled.")

# Sidebar Navigation Panel
st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Navigation Modules")
page = st.sidebar.radio(
    "Choose a Module:",
    ["❓ Doubt Solver", "📅 Daily Planner", "🎓 JEE Mentor AI"],
    label_visibility="collapsed"
)

# Quick stats card in Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div class="feature-card" style="padding: 15px;">
    <div style="color: #e2e8f0; font-size: 0.9rem; font-weight: 700; margin-bottom: 8px;">⏳ Exam Target Status</div>
    <div style="font-size: 0.8rem; color: #94a3b8;">
        Targeting: <b>JEE 2026/2027</b><br>
        Daily Goal: <b>10-12 Study Hours</b><br>
        Key focus: <b>Concept Rigor & PYQs</b>
    </div>
</div>
""", unsafe_allow_html=True)

# Return to Hub button if running from hub
if os.environ.get("RUNNING_FROM_HUB") == "True":
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
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


# App Header
st.markdown("""
<div class="header-container">
    <h1 class="header-title">⚡ JEE Igniter AI</h1>
    <p class="header-subtitle">Your personal 24/7 IITian Mentor, Doubt Solver, and Study Planner</p>
</div>
""", unsafe_allow_html=True)

# Page 1: Doubt Solver
if page == "❓ Doubt Solver":
    st.header("❓ Multimodal Doubt Solver")
    st.markdown("Upload a photo of your handwritten/printed question, or type it out. Get detailed step-by-step solutions with concepts explained.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="card-title">📝 Doubt Details</div>
            <div class="card-content">Fill in the options below to tailor the explanations.</div>
        </div>
        """, unsafe_allow_html=True)
        
        subject = st.selectbox("Select Subject", ["Physics", "Chemistry", "Mathematics"])
        difficulty = st.selectbox("Target Exam Difficulty", ["JEE Main", "JEE Advanced"])
        
        uploaded_file = st.file_uploader("Upload Doubt Image (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Doubt Image", use_container_width=True)
        
        text_question = st.text_area("Type your question or copy-paste text doubt:")
        
        solve_button = st.button("Solve Doubt ⚡")
        
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="card-title">💡 Explanation Output</div>
            <div class="card-content">Your detailed solution will appear here.</div>
        </div>
        """, unsafe_allow_html=True)
        
        if solve_button:
            if not client:
                st.error("Please configure a valid API key in the sidebar.")
            elif not text_question and uploaded_file is None:
                st.warning("Please enter a question or upload an image first!")
            else:
                with st.spinner("Analyzing and solving your doubt..."):
                    # Construct Prompt
                    prompt = f"""
                    You are an elite JEE (Joint Entrance Examination) faculty member specializing in {subject}.
                    A student has submitted a doubt at the {difficulty} level.
                    Provide a highly detailed, pedagogically sound, step-by-step solution.
                    
                    Please format your response strictly using this structure:
                    
                    ### 🎯 1. Core Concept
                    Briefly explain the underlying concepts, theorems, or formulas required to solve this problem.
                    
                    ### ✏️ 2. Step-by-Step Solution
                    Write the complete derivation or mathematical steps in a highly readable format. Show all calculations.
                    
                    ### ⚠️ 3. Common Student Mistakes (Pitfalls)
                    What are the common errors students make while attempting this specific type of question? (e.g. sign conventions, unit mismatch, invalid assumptions)
                    
                    ### 💡 4. Shortcut / Alternate Method
                    If applicable, provide a time-saving tip or alternate perspective suitable for a timed exam environment.
                    
                    Ensure all mathematical equations are formatted cleanly in LaTeX (using $ for inline and $$ for block equations) so they render correctly.
                    """
                    
                    try:
                        contents = []
                        if uploaded_file is not None:
                            contents.append(image)
                        
                        contents.append(f"Question text/context: {text_question}\n\nInstructions:\n{prompt}")
                        
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=contents
                        )
                        st.success("Doubt Solved Successfully!")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"An error occurred while generating the solution: {e}")

# Page 2: Daily Planner
elif page == "📅 Daily Planner":
    st.header("📅 JEE Study Planner & Schedule")
    st.markdown("Configure your preparation profile and get a customized 7-day study schedule tailored for JEE Mains & Advanced.")
    
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="card-title">⚙️ Preparation Profile</div>
            <div class="card-content">Customize your inputs to generate a study routine that fits your needs.</div>
        </div>
        """, unsafe_allow_html=True)
        
        target_year = st.selectbox("Target JEE Year", ["2026", "2027", "2028"])
        prep_mode = st.selectbox("Schooling Mode", ["Regular School (75% Attendance)", "Dummy/Non-attending School", "Dropper (Full-time Prep)"])
        prep_level = st.select_slider("Current Preparation Level", options=["Beginner (Starting off)", "Intermediate (Moderate hold)", "Advanced (Strong command)"])
        study_hours = st.slider("Target Daily Study Hours", min_value=4, max_value=16, value=10)
        
        backlog_topics = st.text_area(
            "Backlog / Weak Topics (Comma separated)",
            placeholder="e.g., Rotational Mechanics, Ionic Equilibrium, Permutations & Combinations"
        )
        
        strong_subjects = st.multiselect(
            "Select your Strong Subject(s)",
            ["Physics", "Chemistry", "Mathematics"],
            default=["Physics"]
        )
        
        generate_planner = st.button("Generate Study Plan 📅")

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="card-title">📝 My Daily Study Checklist</div>
            <div class="card-content">Tick off tasks as you finish them today. Retained during your session.</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Stateful Task Tracker using session_state
        if "todo_list" not in st.session_state:
            st.session_state.todo_list = [
                {"task": "Solve 15 PYQs of Physics (Weak area)", "done": False},
                {"task": "Revise Inorganic Chemistry reactions for 1 hour", "done": False},
                {"task": "Attempt a timed Mathematics topic test (45 mins)", "done": False},
                {"task": "Analyze mock test mistakes & log them", "done": False}
            ]
            
        new_task = st.text_input("➕ Add a custom task to your checklist:")
        if st.button("Add Task"):
            if new_task:
                st.session_state.todo_list.append({"task": new_task, "done": False})
                st.rerun()
                
        # Render checklist items
        for i, item in enumerate(st.session_state.todo_list):
            checked = st.checkbox(item["task"], value=item["done"], key=f"todo_{i}")
            if checked != item["done"]:
                st.session_state.todo_list[i]["done"] = checked
                st.rerun()
        
        if st.button("Clear Completed Tasks"):
            st.session_state.todo_list = [item for item in st.session_state.todo_list if not item["done"]]
            st.rerun()

    # Plan generation section (full width below profile columns)
    if generate_planner:
        if not client:
            st.error("Please configure a valid API key in the sidebar.")
        else:
            with st.spinner("Creating your custom JEE Study Plan..."):
                planner_prompt = f"""
                You are a highly efficient JEE exam planner who has designed timetables for students securing top 100 ranks.
                Create a customized, realistic 7-day study plan based on this student profile:
                - Target JEE Year: {target_year}
                - Preparation Mode: {prep_mode}
                - Prep Level: {prep_level}
                - Available Daily Study Hours: {study_hours} hours
                - Backlogs/Weak Areas: {backlog_topics}
                - Strong Subject(s): {', '.join(strong_subjects)}
                
                Please structure the timetable such that:
                1. It allocates sufficient time for Physics, Chemistry, and Mathematics daily.
                2. It gives extra focus to clearing the backlogs: {backlog_topics}.
                3. It balances concept learning, problem-solving, and revision.
                4. Give realistic hourly slots depending on the prep mode ({prep_mode}).
                
                Format the schedule beautifully using Markdown tables for each day, detailing slot times, subjects, tasks, and recommended focus. Include a quick summary of general strategy at the end.
                """
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=planner_prompt
                    )
                    st.success("Your Personalized 7-Day Plan is Ready!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error generating study plan: {e}")

# Page 3: Mentorship AI
elif page == "🎓 JEE Mentor AI":
    st.header("🎓 Ask an IITian - JEE Mentor AI")
    st.markdown("Get strategic guidance, study advice, revision roadmaps, and motivation from an AI bot trained on the mindsets of JEE toppers.")
    
    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hey champ! I cleared JEE Advanced and completed my B.Tech from IIT. I know how stressful and demanding this preparation is. Ask me anything about mock test strategies, backlog clearance, handling stress, revision tips, or motivational slumps. Let's crack this together!"}
        ]
        
    # Option to clear chat
    if st.sidebar.button("Clear Chat History"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Hey champ! Chat history cleared. What strategy or motivation topic shall we discuss now?"}
        ]
        st.rerun()

    # Display past messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Process user input
    if user_query := st.chat_input("Ask about revision, mock tests, physics/chemistry/math study tips, motivation..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_query)
        st.session_state.messages.append({"role": "user", "content": user_query})
        
        if not client:
            st.error("Please configure a valid API key in the sidebar.")
        else:
            with st.spinner("IITian Mentor is typing..."):
                # Construct conversation context
                system_instruction = """
                You are 'IITian Mentor', an elite academic coach who cleared JEE Advanced with a rank in the top 500.
                You are extremely empathetic, encouraging, practical, and direct. You understand the JEE journey inside out:
                the mock test scores, the pressure of dummy schools vs regular schools, the stress, and the struggle to complete the vast syllabus.
                
                Guidelines for your responses:
                1. Empathize with the student but provide very practical, actionable advice.
                2. Do NOT write generic motivational lines. Give concrete strategies (e.g., 'Do the 3-column test analysis', 'Start with high-weightage chapters like modern physics', 'Use the pomodoro method for organic revision').
                3. Break down complex advice into clear, numbered lists or bullet points.
                4. Encourage them to keep going, but maintain an authoritative, mentor-like stance.
                """
                
                # Format conversation history for Gemini API
                chat_log = "System Instructions:\n" + system_instruction + "\n\nChat History:\n"
                for msg in st.session_state.messages:
                    role_name = "User" if msg["role"] == "user" else "IITian Mentor"
                    chat_log += f"{role_name}: {msg['content']}\n"
                chat_log += "IITian Mentor:"
                
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=chat_log
                    )
                    
                    # Display assistant response
                    with st.chat_message("assistant"):
                        st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error obtaining mentor advice: {e}")




