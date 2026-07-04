import os
import json
import streamlit as st
import google.genai as genai
from google.genai import types

# Set page configurations
st.set_page_config(
    page_title="NotesIO - Smart Notes & Code Architect",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# ==========================================
# CUSTOM PREMIUM CSS STYLING
# ==========================================
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

    /* Style the sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Glassmorphic cards styling */
    .glass-card {
        background: rgba(30, 41, 59, 0.35);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-2px);
        border-color: rgba(20, 184, 166, 0.3);
        box-shadow: 0 15px 35px -10px rgba(20, 184, 166, 0.15);
    }
    
    /* Left accent borders for specific sections */
    .teal-card {
        border-left: 5px solid #14b8a6;
    }
    .indigo-card {
        border-left: 5px solid #6366f1;
    }
    .purple-card {
        border-left: 5px solid #a855f7;
    }

    /* Gradient header box */
    .header-box {
        background: linear-gradient(135deg, #090d16 0%, #1e1b4b 60%, #03201f 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 35px 25px;
        margin-bottom: 30px;
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
        background: radial-gradient(circle, rgba(20, 184, 166, 0.06) 0%, transparent 60%);
        pointer-events: none;
    }
    
    .header-title {
        color: #f8fafc;
        margin: 0;
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(to right, #ffffff, #c7d2fe, #14b8a6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .header-subtitle {
        color: #94a3b8;
        margin: 10px 0 0 0;
        font-size: 1.1rem;
        font-weight: 400;
    }

    /* Badge indicators */
    .accent-badge {
        background: linear-gradient(135deg, #6366f1, #14b8a6);
        color: white;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if "notes_data" not in st.session_state:
    st.session_state.notes_data = None
if "summary_data" not in st.session_state:
    st.session_state.summary_data = None
if "code_data" not in st.session_state:
    st.session_state.code_data = None
if "history" not in st.session_state:
    st.session_state.history = []

# Helper to append to history
def add_to_history(action_type, title, payload):
    st.session_state.history.append({
        "type": action_type,
        "title": title,
        "payload": payload
    })

# ==========================================
# MAIN SIDEBAR PANEL
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px 0;">
        <h2 style="color: #f8fafc; font-size: 1.8rem; margin-bottom: 2px;">NotesIO 📝</h2>
        <span class="accent-badge">AI Synthesis Suite</span>
    </div>
    <p style="text-align: center; color: #94a3b8; font-size: 0.85rem; margin-top: 5px;">Notes & Code Architect</p>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("⚙️ Global Settings")
    
    # API Key configuration
    api_key_override = st.text_input(
        "Gemini API Key",
        value=DEFAULT_API_KEY,
        type="password",
        help="Overrides environment variables or local secrets."
    )
    
    # Model Selection
    model_options = [
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-pro"
    ]
    selected_model = st.selectbox(
        "AI Engine Model",
        options=model_options,
        index=0,
        help="gemini-2.5-flash is optimized for speed and instruction following."
    )
    
    st.markdown("---")
    st.subheader("📜 Session History")
    
    if st.session_state.history:
        for idx, item in enumerate(reversed(st.session_state.history)):
            btn_label = f"{item['type']} - {item['title']}"
            # Shorten label if too long
            if len(btn_label) > 28:
                btn_label = btn_label[:25] + "..."
                
            if st.button(btn_label, key=f"hist_{idx}_{item['title']}", use_container_width=True):
                if item["type"] == "📝 Notes":
                    st.session_state.notes_data = item["payload"]
                    st.toast("Restored notes from history!", icon="📝")
                elif item["type"] == "📁 Summary":
                    st.session_state.summary_data = item["payload"]
                    st.toast("Restored summary from history!", icon="📁")
                elif item["type"] == "💻 Code":
                    st.session_state.code_data = item["payload"]
                    st.toast("Restored code generation from history!", icon="💻")
                    
        if st.button("Clear History 🗑️", use_container_width=True):
            st.session_state.history = []
            st.toast("Session history cleared.", icon="🧹")
            st.rerun()
    else:
        st.info("No items in session history yet.")
        
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
# HEADER CONTAINER
# ==========================================
st.markdown("""
<div class="header-box">
    <h1 class="header-title">NotesIO</h1>
    <p class="header-subtitle">Streamlined Note Synthesis, Smart Summarizations, and Dynamic Code Engineering</p>
</div>
""", unsafe_allow_html=True)

# Create layout tabs
tab1, tab2, tab3 = st.tabs([
    "📝 Note Generator Studio",
    "📁 Smart File Summarizer",
    "💻 Code Developer Engine"
])

# ==========================================
# TAB 1: NOTE GENERATION STUDIO
# ==========================================
with tab1:
    st.markdown("""
    <div class="glass-card teal-card">
        <h3>📝 Generative Note Synthesis</h3>
        <p style="color: #94a3b8; font-size: 0.9rem;">Architect rich, structured study resources, lecture briefs, or specialized reference documentation on any subject.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Configuration")
        topic_input = st.text_input("Topic of Interest", placeholder="e.g. Quantum Computing or Photosynthesis")
        subject_cat = st.text_input("Subject/Category (Optional)", placeholder="e.g. Computer Science, Biology")
        
        target_aud = st.selectbox(
            "Target Audience Level",
            options=["General Public", "High School Student", "Undergraduate", "Postgraduate / Professional"],
            index=2
        )
        
        note_depth = st.selectbox(
            "Note Detail Level",
            options=["High-Yield Summary", "Detailed Explanation (Recommended)", "Deep-Dive Comprehensive Guide"],
            index=1
        )
        
        note_tone = st.selectbox(
            "Explanation Style & Tone",
            options=["Academic & Analytical", "Simple & Analogous (ELI5)", "Bullet-pointed Revision", "Q&A Study Flashcards"],
            index=0
        )
        
        if st.button("Generate Notes ✨", use_container_width=True):
            if not topic_input.strip():
                st.warning("⚠️ Please specify the Topic of Interest.")
            elif not api_key_override.strip():
                st.warning("⚠️ Please provide a Gemini API Key in the sidebar.")
            else:
                with st.spinner("Synthesizing comprehensive notes..."):
                    try:
                        client = genai.Client(api_key=api_key_override.strip())
                        
                        prompt = f"""
                        Generate Notes on the topic '{topic_input}' in a detailed and structured way.
                        Include key points, examples, explanations, and key takeaways.
                        
                        Contextual Specifications:
                        - Subject/Category: {subject_cat if subject_cat.strip() else 'General Science/Interdisciplinary'}
                        - Target Audience Level: {target_aud}
                        - Note Detail Level: {note_depth}
                        - Explanation Style & Tone: {note_tone}
                        
                        Ensure the output is clean Markdown format. Use headers, bold terms, list items, code snippets, or markdown tables where appropriate to improve readability. Do not output conversational introductory meta-text. Start directly with the notes header.
                        """
                        
                        response = client.models.generate_content(
                            model=selected_model,
                            contents=prompt
                        )
                        
                        notes_result = {
                            "topic": topic_input,
                            "content": response.text,
                            "depth": note_depth,
                            "tone": note_tone
                        }
                        st.session_state.notes_data = notes_result
                        add_to_history("📝 Notes", topic_input, notes_result)
                        st.toast("Notes synthesized successfully! 🎉", icon="✅")
                    except Exception as e:
                        st.error(f"Error during note generation: {e}")
                        
    with col2:
        st.subheader("Output Workspace")
        if st.session_state.notes_data:
            notes = st.session_state.notes_data
            
            st.markdown(f"**Topic**: `{notes['topic']}` | **Detail**: `{notes['depth']}` | **Style**: `{notes['tone']}`")
            
            # Action controls
            st.download_button(
                label="Download Notes (.md) 📥",
                data=notes["content"],
                file_name=f"{notes['topic'].replace(' ', '_')}_Notes.md",
                mime="text/markdown",
                key="dl_notes"
            )
            
            # Display rendered notes
            st.markdown("""<div class="glass-card">""", unsafe_allow_html=True)
            st.markdown(notes["content"])
            st.markdown("""</div>""", unsafe_allow_html=True)
            
        else:
            st.info("Provide your configuration settings on the left and click 'Generate Notes' to begin.")

# ==========================================
# TAB 2: SMART FILE SUMMARIZER
# ==========================================
with tab2:
    st.markdown("""
    <div class="glass-card indigo-card">
        <h3>📁 AI File Summarization Engine</h3>
        <p style="color: #94a3b8; font-size: 0.9rem;">Upload text-based logs, code, reports, or text datasets to generate summaries tailored to your preferred format.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Source Input")
        uploaded_file = st.file_uploader(
            "Upload Document",
            type=["txt", "md", "py", "json", "csv", "html", "css", "js", "yaml", "xml", "ini"]
        )
        
        summary_style = st.selectbox(
            "Summary Style Format",
            options=[
                "Key Bullet-Point Breakdown",
                "Concise Executive Brief (1-2 Paragraphs)",
                "Deep Technical Summary",
                "Action Items & Actionable Milestones"
            ],
            index=0
        )
        
        file_text = ""
        if uploaded_file is not None:
            try:
                bytes_data = uploaded_file.read()
                # Attempt to decode as UTF-8, fallback to Latin-1
                try:
                    file_text = bytes_data.decode("utf-8")
                except UnicodeDecodeError:
                    file_text = bytes_data.decode("latin-1")
                
                # Metadata display
                file_size_kb = len(bytes_data) / 1024
                lines_count = len(file_text.splitlines())
                words_count = len(file_text.split())
                
                st.success("File uploaded successfully!")
                st.markdown(f"""
                **File Info**:
                - Name: `{uploaded_file.name}`
                - Size: `{file_size_kb:.2f} KB`
                - Lines: `{lines_count}`
                - Words: `{words_count}`
                """)
                
                # File Preview
                with st.expander("Preview File Source Content"):
                    st.code(file_text[:1200] + ("\n... [Truncated due to size]" if len(file_text) > 1200 else ""), language="text")
                    
            except Exception as e:
                st.error(f"Error reading file contents: {e}")
                
        if st.button("Summarize Content ⚡", use_container_width=True):
            if uploaded_file is None:
                st.warning("⚠️ Please upload a text file to summarize.")
            elif not file_text.strip():
                st.warning("⚠️ The uploaded file appears to be empty.")
            elif not api_key_override.strip():
                st.warning("⚠️ Please provide a Gemini API Key in the sidebar.")
            else:
                with st.spinner("Analyzing and summarizing file contents..."):
                    try:
                        client = genai.Client(api_key=api_key_override.strip())
                        
                        prompt = f"""
                        Summarize the following content in a concise and clear manner, conforming to this style: {summary_style}.
                        Identify the key themes, conclusions, and any secondary important findings.
                        
                        Source File Name: {uploaded_file.name}
                        
                        Source Content:
                        {file_text}
                        """
                        
                        response = client.models.generate_content(
                            model=selected_model,
                            contents=prompt
                        )
                        
                        summary_result = {
                            "filename": uploaded_file.name,
                            "style": summary_style,
                            "content": response.text
                        }
                        
                        st.session_state.summary_data = summary_result
                        add_to_history("📁 Summary", uploaded_file.name, summary_result)
                        st.toast("File summarized successfully! 🎉", icon="✅")
                    except Exception as e:
                        st.error(f"Error during summarization: {e}")
                        
    with col2:
        st.subheader("Summary Result Workspace")
        if st.session_state.summary_data:
            summary = st.session_state.summary_data
            
            st.markdown(f"**Source File**: `{summary['filename']}` | **Format Style**: `{summary['style']}`")
            
            st.download_button(
                label="Download Summary (.md) 📥",
                data=summary["content"],
                file_name=f"Summary_{summary['filename'].split('.')[0]}.md",
                mime="text/markdown",
                key="dl_summary"
            )
            
            st.markdown("""<div class="glass-card">""", unsafe_allow_html=True)
            st.markdown(summary["content"])
            st.markdown("""</div>""", unsafe_allow_html=True)
        else:
            st.info("Upload a file, configure the format, and click 'Summarize Content' to see results.")

# ==========================================
# TAB 3: CODE DEVELOPER ENGINE
# ==========================================
with tab3:
    st.markdown("""
    <div class="glass-card purple-card">
        <h3>💻 AI Code Engineering Workspace</h3>
        <p style="color: #94a3b8; font-size: 0.9rem;">Generate optimized, clean, and directly runnable source files matching your strict specifications.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Project Specs")
        project_name = st.text_input("Project Name", placeholder="e.g. DataScraper or AuthSystem")
        
        # Languages and common extensions mapping
        lang_map = {
            "Python": "py",
            "JavaScript": "js",
            "TypeScript": "ts",
            "HTML/CSS/JS (Single-page Web App)": "html",
            "C++": "cpp",
            "Java": "java",
            "Rust": "rs",
            "Go": "go",
            "SQL Query": "sql",
            "Shell Script (Bash)": "sh",
            "Other (Custom Extension)": "txt"
        }
        
        lang_selected = st.selectbox("Programming Language", options=list(lang_map.keys()), index=0)
        
        # Determine default file extension
        default_ext = lang_map[lang_selected]
        
        file_ext = st.text_input("File Extension Override", value=default_ext, help="Do not include the dot (e.g. use 'py', not '.py')")
        
        code_style = st.selectbox(
            "Code Construction Pattern",
            options=[
                "Documented & Fully Commented (Educational)",
                "Clean, Compact & Minimalist (Production)",
                "Object Oriented Programming (OOP)",
                "Functional & Modular Hooks"
            ],
            index=0
        )
        
        project_desc = st.text_area(
            "Project Description / Prompt Rules",
            placeholder="Describe the app/script. Be specific about input/output requirements, logic steps, libraries to use, etc.",
            height=180
        )
        
        if st.button("Generate Code 💻", use_container_width=True):
            if not project_name.strip():
                st.warning("⚠️ Please provide a Project Name.")
            elif not project_desc.strip():
                st.warning("⚠️ Please provide a detailed Project Description.")
            elif not api_key_override.strip():
                st.warning("⚠️ Please provide a Gemini API Key in the sidebar.")
            else:
                with st.spinner("Engineering source code files..."):
                    try:
                        client = genai.Client(api_key=api_key_override.strip())
                        
                        prompt = f"""
                        Generate Code Only that is directly runnable on '{project_desc}' in '.{file_ext}' format.
                        
                        Specifications:
                        - Project File Name: {project_name}.{file_ext}
                        - Programming Language: {lang_selected}
                        - Architecture Style: {code_style}
                        
                        Instructions:
                        - Output ONLY the clean executable code.
                        - Do NOT wrap it with conversational summaries, introductions, or closing remarks.
                        - Include necessary imports and comments explaining key sections of the code.
                        - The code should be fully complete and ready to run.
                        """
                        
                        response = client.models.generate_content(
                            model=selected_model,
                            contents=prompt
                        )
                        
                        # Clean markdown code fences if outputted
                        code_output = response.text.strip()
                        if code_output.startswith("```"):
                            lines = code_output.splitlines()
                            if lines[0].startswith("```"):
                                lines = lines[1:]
                            if lines and lines[-1].startswith("```"):
                                lines = lines[:-1]
                            code_output = "\n".join(lines).strip()
                            
                        code_result = {
                            "name": project_name,
                            "ext": file_ext,
                            "lang": lang_selected,
                            "style": code_style,
                            "content": code_output
                        }
                        
                        st.session_state.code_data = code_result
                        add_to_history("💻 Code", f"{project_name}.{file_ext}", code_result)
                        st.toast("Code file engineered successfully! 🚀", icon="✅")
                    except Exception as e:
                        st.error(f"Error during code generation: {e}")
                        
    with col2:
        st.subheader("Source Code Editor View")
        if st.session_state.code_data:
            code_res = st.session_state.code_data
            
            st.markdown(f"**Target File**: `{code_res['name']}_Notes.{code_res['ext']}` | **Language**: `{code_res['lang']}`")
            
            # Download file matching original spec name
            st.download_button(
                label=f"Download {code_res['name']}_Notes.{code_res['ext']} 📥",
                data=code_res["content"],
                file_name=f"{code_res['name']}_Notes.{code_res['ext']}",
                mime="text/plain",
                key="dl_code"
            )
            
            # Map selected language to syntax highlighter alias
            highlighter_lang = code_res["lang"].lower()
            if "html" in highlighter_lang:
                highlighter_lang = "html"
            elif "javascript" in highlighter_lang:
                highlighter_lang = "javascript"
            elif "typescript" in highlighter_lang:
                highlighter_lang = "typescript"
            elif "sql" in highlighter_lang:
                highlighter_lang = "sql"
            elif "python" in highlighter_lang:
                highlighter_lang = "python"
            else:
                highlighter_lang = code_res["ext"]
                
            st.code(code_res["content"], language=highlighter_lang)
        else:
            st.info("Define your project requirements on the left and click 'Generate Code' to construct source files.")