import os
import json
import time
import random
import datetime
import streamlit as st
import google.genai as genai
from google.genai import types
from pydantic import BaseModel, Field
from PIL import Image

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="AS.Dev EduHub",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global API Key
API_KEY = "AQ.Ab8RN6IDiksTKMSDn1MSq9fPj1yTXpPYZrBYDTVKzW_6SO_YiQ"

# ==========================================
# SHARED PREMIUM GLASSMORPHIC CSS
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

    /* Sidebar background */
    section[data-testid="stSidebar"] {
        background-color: #0b0f19;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Glassmorphic cards */
    .glass-card {
        background: rgba(17, 24, 39, 0.55);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 12px 35px -10px rgba(0, 0, 0, 0.55);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .glass-card:hover {
        transform: translateY(-3px);
        border-color: rgba(20, 184, 166, 0.35);
        box-shadow: 0 16px 40px -10px rgba(20, 184, 166, 0.18);
    }
    
    /* Card accent borders */
    .card-teal { border-left: 6px solid #14b8a6; }
    .card-indigo { border-left: 6px solid #6366f1; }
    .card-purple { border-left: 6px solid #a855f7; }
    .card-orange { border-left: 6px solid #f59e0b; }
    .card-green { border-left: 6px solid #10b981; }
    .card-rose { border-left: 6px solid #f43f5e; }
    .teal-card { border-left: 5px solid #14b8a6; }
    .indigo-card { border-left: 5px solid #6366f1; }
    .purple-card { border-left: 5px solid #a855f7; }
    .orange-card { border-left: 5px solid #f59e0b; }
    .pink-card { border-left: 5px solid #ec4899; }

    /* Gradient header box */
    .header-box {
        background: linear-gradient(135deg, #090d16 0%, #1e1b4b 60%, #03201f 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 40px 30px;
        margin-bottom: 30px;
        text-align: center;
        position: relative;
        overflow: hidden;
        box-shadow: 0 15px 40px -15px rgba(0, 0, 0, 0.7);
    }
    
    .header-box::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(20, 184, 166, 0.08) 0%, transparent 60%);
        pointer-events: none;
    }
    
    .header-title {
        color: #f8fafc;
        margin: 0;
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(to right, #ffffff, #c7d2fe, #14b8a6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .header-subtitle {
        color: #94a3b8;
        margin: 12px 0 0 0;
        font-size: 1.25rem;
        font-weight: 400;
    }

    /* Badge indicators */
    .hub-badge {
        background: linear-gradient(135deg, #6366f1, #14b8a6);
        color: white;
        padding: 5px 12px;
        border-radius: 10px;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        display: inline-block;
        box-shadow: 0 4px 10px rgba(99, 102, 241, 0.25);
    }

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

    /* Bio page */
    .bio-container {
        background: rgba(30, 41, 59, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 30px;
        margin-top: 10px;
    }
    
    .profile-link a {
        color: #14b8a6;
        text-decoration: none;
        font-weight: 600;
        transition: color 0.2s;
    }
    .profile-link a:hover {
        color: #0d9488;
        text-decoration: underline;
    }

    /* Feature cards (Mentorship) */
    .feature-card {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
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

    /* Result states (DailyPractise) */
    .correct-card { border-left: 5px solid #10b981; background: rgba(16, 185, 129, 0.08); }
    .incorrect-card { border-left: 5px solid #ef4444; background: rgba(239, 68, 68, 0.08); }
    .unattempted-card { border-left: 5px solid #64748b; background: rgba(100, 116, 139, 0.08); }
    .badge { padding: 4px 10px; border-radius: 9999px; font-size: 0.8rem; font-weight: 600; display: inline-block; margin-bottom: 10px; }
    .badge-correct { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-incorrect { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
    .badge-unattempted { background: rgba(148, 163, 184, 0.2); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.3); }

    /* JEE CBT Styles */
    .cbt-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-bottom: 2px solid #3b82f6;
        padding: 15px 30px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .header-logo {
        font-size: 1.6rem;
        font-weight: 800;
        background: linear-gradient(to right, #60a5fa, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .header-info { font-size: 0.95rem; color: #94a3b8; }
    .question-box { background: rgba(15, 23, 42, 0.85); border-left: 4px solid #3b82f6; padding: 20px; border-radius: 8px; margin-bottom: 20px; line-height: 1.7; font-size: 1.1rem; }
    .passage-box { background: rgba(30, 41, 59, 0.4); border: 1px dashed rgba(255, 255, 255, 0.15); padding: 16px; border-radius: 8px; margin-bottom: 20px; font-size: 1rem; line-height: 1.6; }
    .status-badge { padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; display: inline-block; color: white; }
    .status-unvisited { background-color: #475569; }
    .status-not-answered { background-color: #dc2626; }
    .status-answered { background-color: #16a34a; }
    .status-marked { background-color: #8b5cf6; }
    .status-marked-answered { background-color: #8b5cf6; border: 2px solid #22c55e; }
    .palette-container { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; margin-top: 15px; }
    .palette-btn { height: 38px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.9rem; border-radius: 6px; color: white; cursor: pointer; text-decoration: none; transition: all 0.2s ease; border: none; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
    .palette-btn:hover { transform: translateY(-1px); filter: brightness(1.2); }
    .jee-badge { background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: white; padding: 4px 10px; border-radius: 8px; font-size: 0.75rem; font-weight: 700; display: inline-block; margin-bottom: 10px; }

    /* Primary button override for JEE CBT */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6) !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        transition: all 0.25s ease !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #2563eb, #7c3aed) !important;
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.45) !important;
        transform: translateY(-1px) !important;
    }

    /* Bordered containers for JEE CBT question/passage boxes */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(15, 23, 42, 0.75) !important;
        border: 1px solid rgba(59, 130, 246, 0.45) !important;
        border-radius: 10px !important;
    }
    div[data-testid="column"] div[data-testid="stVerticalBlockBorderWrapper"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0px !important;
    }
    div[data-testid="column"] div[data-testid="stCheckbox"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
    }
    div[data-testid="column"] div[data-testid="stCheckbox"] label {
        justify-content: center !important;
        width: auto !important;
    }

    /* Stepper (RoadmapIO) */
    .stepper-container { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; padding: 0 10px; }
    .stepper-item { flex: 1; text-align: center; position: relative; }
    .stepper-item::after { content: ''; position: absolute; top: 16px; left: 50%; width: 100%; height: 2px; background: rgba(255, 255, 255, 0.06); z-index: 1; }
    .stepper-item:last-child::after { content: none; }
    .stepper-circle { width: 32px; height: 32px; border-radius: 50%; background: #1e293b; border: 2px solid rgba(255, 255, 255, 0.08); color: #64748b; display: flex; align-items: center; justify-content: center; margin: 0 auto 8px auto; font-weight: 600; font-size: 0.9rem; position: relative; z-index: 2; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
    .stepper-item.active .stepper-circle { background: #4f46e5; border-color: #818cf8; color: #ffffff; box-shadow: 0 0 15px rgba(99, 102, 241, 0.35); }
    .stepper-item.completed .stepper-circle { background: #059669; border-color: #34d399; color: #ffffff; }
    .stepper-text { font-size: 0.8rem; color: #64748b; font-weight: 500; }
    .stepper-item.active .stepper-text { color: #a5b4fc; font-weight: 600; }
    .stepper-item.completed .stepper-text { color: #a7f3d0; }
</style>
""", unsafe_allow_html=True)


# ==========================================
# PYDANTIC SCHEMAS (RevisionIO)
# ==========================================
class PracticeQuestion(BaseModel):
    question: str = Field(description="A challenging practice question testing conceptual depth.")
    answer: str = Field(description="A detailed correct answer with explanation and shortcuts.")

class DayPlan(BaseModel):
    day: int = Field(description="The day number (1-indexed).")
    title: str = Field(description="Main focus of this day's revision.")
    key_topics: list[str] = Field(description="Core subtopics to cover on this day.")
    revision_bits: list[str] = Field(description="Concise, high-yield bullet notes and core fundamentals.")
    formulas_or_key_terms: list[str] = Field(description="Crucial formulas or key definitions.")
    exam_tips: list[str] = Field(description="Traps, common mistakes, Board/JEE/NEET scoring tips.")
    practice_questions: list[PracticeQuestion] = Field(description="Exactly 3 practice questions with detailed answers.")

class RevisionPlanSchema(BaseModel):
    subject: str = Field(description="Subject name.")
    topic: str = Field(description="The revised topic.")
    target_class: str = Field(description="Targeted competitive exam or class standard.")
    days: list[DayPlan] = Field(description="Daily revision plan.")


# ==========================================
# PYDANTIC SCHEMAS (RoadmapIO)
# ==========================================
class FollowUpSchema(BaseModel):
    questions: list[str] = Field(description="Exactly 3 highly targeted clarifying questions.")


# ==========================================
# PYDANTIC SCHEMAS (DailyPractise)
# ==========================================
class MCQQuestion(BaseModel):
    id: int = Field(description="Question index from 1 to 15")
    question: str = Field(description="The question statement with LaTeX.")
    option_a: str = Field(description="Option A.")
    option_b: str = Field(description="Option B.")
    option_c: str = Field(description="Option C.")
    option_d: str = Field(description="Option D.")
    correct_option: str = Field(description="One of: 'A', 'B', 'C', or 'D'")
    explanation: str = Field(description="Detailed step-by-step solution with LaTeX.")

class PracticeTestSchema(BaseModel):
    subject: str = Field(description="The subject.")
    chapter: str = Field(description="The chapter name.")
    questions: list[MCQQuestion] = Field(description="Exactly 15 MCQ questions.")


# ==========================================
# DATA: CBSE SUBJECTS & CHAPTERS (DailyPractise)
# ==========================================
DP_SUBJECTS_AND_CHAPTERS = {
    "Physics": [
        "Electric Charges and Fields", "Electrostatic Potential and Capacitance",
        "Current Electricity", "Moving Charges and Magnetism",
        "Magnetism and Matter", "Electromagnetic Induction",
        "Alternating Current", "Electromagnetic Waves",
        "Ray Optics and Optical Instruments", "Wave Optics",
        "Dual Nature of Radiation and Matter", "Atoms", "Nuclei",
        "Semiconductor Electronics: Materials, Devices and Simple Circuits"
    ],
    "Chemistry": [
        "Solutions", "Electrochemistry", "Chemical Kinetics",
        "d- and f-Block Elements", "Coordination Compounds",
        "Haloalkanes and Haloarenes", "Alcohols, Phenols and Ethers",
        "Aldehydes, Ketones and Carboxylic Acids", "Amines", "Biomolecules"
    ],
    "Maths": [
        "Relations and Functions", "Inverse Trigonometric Functions",
        "Matrices", "Determinants", "Continuity and Differentiability",
        "Application of Derivatives", "Integrals", "Application of Integrals",
        "Differential Equations", "Vector Algebra",
        "Three Dimensional Geometry", "Linear Programming", "Probability"
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
# DATA: JEE ADVANCED CHAPTER POOLS
# ==========================================
JEE_PHYSICS_CHAPTERS = [
    "Mechanics - Kinematics & Projectile Motion", "Newton's Laws & Friction",
    "Work, Energy & Power", "Rotational Motion, Torque & Angular Momentum",
    "Gravitation & Satellite Motion", "Simple Harmonic Motion & Oscillations",
    "Waves, Sound & Doppler Effect", "Fluid Mechanics & Bernoulli's Theorem",
    "Thermal Physics & Calorimetry", "Thermodynamics - Laws & Cycles",
    "Kinetic Theory of Gases", "Electrostatics & Gauss's Law",
    "Current Electricity & Kirchhoff's Laws", "Magnetism & Biot-Savart Law",
    "Electromagnetic Induction & Faraday's Law", "AC Circuits & LCR Resonance",
    "Ray Optics - Mirrors, Lenses & Prisms", "Wave Optics & Interference",
    "Modern Physics - Photoelectric & Compton Effect", "Nuclear Physics & Radioactivity"
]
JEE_CHEMISTRY_CHAPTERS = [
    "Atomic Structure & Quantum Numbers", "Chemical Bonding & VSEPR Theory",
    "Periodic Table & Periodicity", "Thermodynamics & Hess's Law",
    "Chemical Equilibrium & Le Chatelier's Principle", "Ionic Equilibrium & Buffer Solutions",
    "Electrochemistry & Nernst Equation", "Chemical Kinetics & Rate Laws",
    "Coordination Chemistry & Crystal Field Theory", "Solid State & Crystal Lattices",
    "Solutions & Colligative Properties", "Surface Chemistry & Adsorption",
    "p-Block Elements (Groups 15-18)", "d-Block & f-Block Elements",
    "Alcohols, Phenols & Ethers", "Carbonyl Compounds - Aldehydes & Ketones",
    "Carboxylic Acids & Derivatives", "Amines & Diazonium Salts",
    "Biomolecules - Proteins & Nucleic Acids", "Polymers & Named Reactions"
]
JEE_MATHS_CHAPTERS = [
    "Limits & Continuity", "Differentiation & Chain Rule",
    "Application of Derivatives - Maxima/Minima", "Integration by Parts & Substitution",
    "Definite Integration & Properties", "Area Under Curves",
    "Differential Equations", "Complex Numbers & Polar Form",
    "Matrices & Determinants", "Vector Algebra & Dot/Cross Products",
    "3D Geometry - Lines & Planes", "Probability & Conditional Probability",
    "Permutations & Combinations", "Binomial Theorem & Pascal's Triangle",
    "Sequences & Series - AP/GP/HP", "Conic Sections - Parabola, Ellipse & Hyperbola",
    "Circles & Tangents", "Trigonometric Identities & Equations",
    "Inverse Trigonometry", "Functions, Relations & Mathematical Induction"
]


# ==========================================
# JEE ADVANCED CBT FALLBACK QUESTION BANK
# ==========================================
JEE_FALLBACK_QUESTIONS = [
    {"id":1,"subject":"Physics","type":"Single Correct","paragraph_text":"","question_text":"A solid cylinder of mass $M$ and radius $R$ is rolling down an inclined plane of angle $\\\\theta$ without slipping. The acceleration of the center of mass of the cylinder is:","options":["A) $g \\\\sin \\\\theta$","B) $\\\\frac{2}{3} g \\\\sin \\\\theta$","C) $\\\\frac{1}{2} g \\\\sin \\\\theta$","D) $\\\\frac{3}{4} g \\\\sin \\\\theta$"],"correct_answer":"B","solution":"For rolling without slipping: $a = \\\\frac{g \\\\sin \\\\theta}{1 + I/(MR^2)}$. For a solid cylinder $I = \\\\frac{1}{2}MR^2$, so $a = \\\\frac{2}{3} g \\\\sin \\\\theta$. Option **B**."},
    {"id":2,"subject":"Physics","type":"Multi Correct","paragraph_text":"","question_text":"A conducting loop of radius $r$ is placed in a uniform magnetic field $B(t) = B_0 + \\\\alpha t$ perpendicular to the loop. Which statements are correct?","options":["A) EMF magnitude is $\\\\pi r^2 \\\\alpha$","B) Current is clockwise if $\\\\alpha > 0$ (looking down)","C) Current is counter-clockwise if $\\\\alpha > 0$","D) Heat dissipation rate is $\\\\frac{(\\\\pi r^2 \\\\alpha)^2}{R}$"],"correct_answer":["A","B","D"],"solution":"EMF = $\\\\pi r^2 \\\\alpha$ (A correct). By Lenz's law, clockwise (B correct, C wrong). Power = $V^2/R$ (D correct)."},
    {"id":3,"subject":"Physics","type":"Integer Type","paragraph_text":"","question_text":"Two point charges $+q$ and $+4q$ are separated by 12 cm. Find distance (cm) from $+q$ where net electric field is zero.","correct_answer":"4","solution":"$1/x = 2/(12-x)$, gives $x = 4$ cm."},
    {"id":4,"subject":"Physics","type":"Single Correct","paragraph_text":"","question_text":"Force on a dipole $\\\\vec{p} = p\\\\hat{i}$ in field $\\\\vec{E} = Ax\\\\hat{i}$:","options":["A) $Ap\\\\hat{i}$","B) $-Ap\\\\hat{i}$","C) Zero","D) $2Ap\\\\hat{i}$"],"correct_answer":"A","solution":"$F_x = p \\\\partial E_x/\\\\partial x = pA$. Option **A**."},
    {"id":5,"subject":"Physics","type":"Integer Type","paragraph_text":"","question_text":"Solid sphere rolls and collides elastically with wall. $|v_f/v_0|$ after rolling resumes? (2 decimal places)","correct_answer":"0.43","solution":"By angular momentum conservation about contact: $v_f = -3v_0/7$, ratio = 3/7 ≈ 0.43."},
    {"id":6,"subject":"Chemistry","type":"Single Correct","paragraph_text":"","question_text":"For a first-order reaction, $t_{99\\\\%}$ completion is how many times $t_{1/2}$?","options":["A) 2.0","B) 6.6","C) 10.0","D) 3.3"],"correct_answer":"B","solution":"$t_{99\\\\%}/t_{1/2} = 4.606/0.693 \\\\approx 6.64$. Option **B**."},
    {"id":7,"subject":"Chemistry","type":"Multi Correct","paragraph_text":"","question_text":"For $[Co(NH_3)_6]^{3+}$, which are correct?","options":["A) Inner orbital complex","B) Diamagnetic","C) $d^2sp^3$ hybridization","D) Outer orbital complex"],"correct_answer":["A","B","C"],"solution":"$Co^{3+}$ is $d^6$, $NH_3$ is strong field → pairing → $d^2sp^3$, inner orbital, diamagnetic. A, B, C correct."},
    {"id":8,"subject":"Chemistry","type":"Single Correct","paragraph_text":"","question_text":"Which coordination compound exhibits linkage isomerism?","options":["A) $[Co(NH_3)_5(NO_2)]Cl_2$","B) $[Co(NH_3)_6]Cl_3$","C) $[Co(NH_3)_5Cl]SO_4$","D) $[Co(en)_3]Cl_3$"],"correct_answer":"A","solution":"$NO_2^-$ is ambidentate (binds via N or O). Option **A**."},
    {"id":9,"subject":"Chemistry","type":"Integer Type","paragraph_text":"","question_text":"Standard reduction potential of $Cu^{2+} + e^- \\\\to Cu^+$ given $E^\\\\circ(Cu^{2+}/Cu) = 0.34$ V and $E^\\\\circ(Cu^+/Cu) = 0.52$ V.","correct_answer":"0.16","solution":"Using $\\\\Delta G$: $E_3 = (2 \\\\times 0.34 - 1 \\\\times 0.52)/1 = 0.16$ V."},
    {"id":10,"subject":"Chemistry","type":"Multi Correct","paragraph_text":"","question_text":"Which molecular species have planar geometry?","options":["A) $XeF_4$","B) $SF_4$","C) $BF_3$","D) $H_3O^+$"],"correct_answer":["A","C"],"solution":"$XeF_4$ is square planar, $BF_3$ is trigonal planar. A, C correct."},
    {"id":11,"subject":"Mathematics","type":"Single Correct","paragraph_text":"","question_text":"$\\\\lim_{x \\\\to 0} \\\\frac{e^{x^2} - \\\\cos x}{x^2}$","options":["A) $1$","B) $\\\\frac{3}{2}$","C) $\\\\frac{1}{2}$","D) $2$"],"correct_answer":"B","solution":"Taylor expansion gives $3x^2/2$ in numerator. Limit = $3/2$. Option **B**."},
    {"id":12,"subject":"Mathematics","type":"Multi Correct","paragraph_text":"","question_text":"$|z - 3 - 4i| = 2$. Which are correct?","options":["A) Max $|z|$ is 7","B) Min $|z|$ is 3","C) Circle centered at (3,4) with radius 2","D) Max $|z|$ is 5"],"correct_answer":["A","B","C"],"solution":"Center distance = 5, radius = 2. Max = 7, Min = 3. A, B, C correct."},
    {"id":13,"subject":"Mathematics","type":"Single Correct","paragraph_text":"","question_text":"Common tangent to $y^2 = 8x$ and $3x^2 - y^2 = 3$:","options":["A) $y = x + 2$","B) $y = 2x + 1$","C) $y = 3x - 1$","D) $y = x - 2$"],"correct_answer":"B","solution":"Tangent to parabola: $y = mx + 2/m$. Condition with hyperbola gives $m = 2$, $c = 1$. Option **B**."},
    {"id":14,"subject":"Mathematics","type":"Integer Type","paragraph_text":"","question_text":"Three dice rolled, sum = 6. $P = p/q$ coprime. Find $q - p$.","correct_answer":"103","solution":"Favorable = 10, total = 216. $P = 5/108$. $q - p = 103$."},
    {"id":15,"subject":"Mathematics","type":"Single Correct","paragraph_text":"","question_text":"$I_n + I_{n-2}$ where $I_n = \\\\int_0^{\\\\pi/4} \\\\tan^n x \\\\, dx$:","options":["A) $\\\\frac{1}{n-1}$","B) $\\\\frac{1}{n}$","C) $I_n - I_{n-2} = \\\\frac{1}{n-1}$","D) $\\\\frac{\\\\pi}{4(n-1)}$"],"correct_answer":"A","solution":"Using $\\\\tan^2 x + 1 = \\\\sec^2 x$ and substitution $u = \\\\tan x$: result is $1/(n-1)$. Option **A**."},
]


def jee_get_fallback_paper(qs_per_subject):
    """Shuffles and samples the offline fallback questions per subject."""
    by_subject = {"Physics": [], "Chemistry": [], "Mathematics": []}
    for q in JEE_FALLBACK_QUESTIONS:
        subj = q["subject"]
        if subj in by_subject:
            by_subject[subj].append(q)
    selected = []
    cid = 1
    for subj in ["Physics", "Chemistry", "Mathematics"]:
        pool = by_subject[subj].copy()
        random.shuffle(pool)
        sample_size = min(qs_per_subject, len(pool))
        for q in pool[:sample_size]:
            qc = q.copy()
            qc["id"] = cid
            selected.append(qc)
            cid += 1
    return selected


def jee_generate_questions_api(api_key, num_per_subject, topics):
    """Calls Gemini API to generate JEE Advanced questions."""
    if not api_key:
        return None
    client = genai.Client(api_key=api_key)
    all_questions = []
    cid = 1
    for subj in ["Physics", "Chemistry", "Mathematics"]:
        session_seed = random.randint(100000, 999999)
        if topics and topics.strip():
            chapter_context = f"{subj} topics related to: {topics.strip()}"
        else:
            if subj == "Physics":
                chapters = random.sample(JEE_PHYSICS_CHAPTERS, min(6, len(JEE_PHYSICS_CHAPTERS)))
            elif subj == "Chemistry":
                chapters = random.sample(JEE_CHEMISTRY_CHAPTERS, min(6, len(JEE_CHEMISTRY_CHAPTERS)))
            else:
                chapters = random.sample(JEE_MATHS_CHAPTERS, min(6, len(JEE_MATHS_CHAPTERS)))
            chapter_context = f"{subj} Chapters: " + ", ".join(chapters)
        prompt = f"""You are an elite IIT-JEE Advanced examiner designing the {subj} section.
Session seed: #{session_seed}.
Generate exactly {num_per_subject} questions for {subj} in JSON format.
Chapters: {chapter_context}
Distribute types evenly: "Single Correct", "Multi Correct", "Paragraph Based", "Integer Type", "Match the Column".
Return a single JSON object with a "questions" list. Do NOT wrap in markdown.
Each question has: id, subject, type, paragraph_text, question_text, options (4 items for SC/MC/PB, empty otherwise), column_A (4 items for MtC), column_B (5 items for MtC), correct_answer, solution."""
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=1.0,
                    thinking_config=types.ThinkingConfig(thinking_budget=0)
                )
            )
            data = json.loads(response.text)
            if "questions" in data and len(data["questions"]) > 0:
                for q in data["questions"]:
                    qc = q.copy()
                    qc["id"] = cid
                    qc["subject"] = subj
                    all_questions.append(qc)
                    cid += 1
            else:
                return None
        except Exception:
            return None
    if len(all_questions) == num_per_subject * 3:
        return all_questions
    return None


# ==========================================
# MAIN SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 15px 0;">
        <h2 style="color: #f8fafc; font-size: 2.2rem; margin-bottom: 2px;">EduHub 🎓</h2>
        <span class="hub-badge">AS.Dev Central Hub</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        options=[
            "🏠 Dashboard",
            "📝 NotesIO",
            "⚡ RevisionIO",
            "🗺️ RoadmapIO",
            "🎓 JEE Igniter",
            "✏️ DailyPractise",
            "🎯 JEE Advanced CBT",
            "🤖 AI Assistant",
            "📋 About Project",
            "👨‍💻 About Developer"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.subheader("⚙️ System Status")
    st.markdown(f"**Gemini AI:** `CONNECTED`")
    st.markdown(f"**Mode:** `Integrated`")


# ══════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════
if page == "🏠 Dashboard":
    st.markdown("""
    <div class="header-box">
        <h1 class="header-title">AS.Dev EduHub</h1>
        <p class="header-subtitle">Your Unified Portal for Academic AI Synthesis, Practice Exam CBTs, and Study Planning Suite</p>
    </div>
    """, unsafe_allow_html=True)

    projects = [
        {"name": "NotesIO", "desc": "Generative Study Notes & Code Architect. Synthesizes lecture topics, parses document uploads, and designs programming algorithms.", "nav": "📝 NotesIO", "style": "card-teal"},
        {"name": "RevisionIO", "desc": "Exam Revision Planner. Tailors customized revision calendars, highlights exam traps, and offers daily revision checkpoints.", "nav": "⚡ RevisionIO", "style": "card-indigo"},
        {"name": "RoadmapIO", "desc": "Curriculum Path Explorer. Maps out multi-stage visual learning pathways and lists conceptual checkpoints for technical skills.", "nav": "🗺️ RoadmapIO", "style": "card-purple"},
        {"name": "JEE Igniter", "desc": "24/7 AI Mentor & Doubt Solver. Explains challenging JEE subjects and solves study blockers with step-by-step guidance.", "nav": "🎓 JEE Igniter", "style": "card-orange"},
        {"name": "DailyPractise", "desc": "Exam Question Sheet Generator. Curates randomized, curriculum-aligned MCQ practice sheets with detailed LaTeX solutions.", "nav": "✏️ DailyPractise", "style": "card-green"},
        {"name": "JEE Advanced CBT", "desc": "Computer-Based Exam Engine. Mimics the official JEE Advanced interface, handles timers, and evaluates performance scores.", "nav": "🎯 JEE Advanced CBT", "style": "card-rose"},
    ]

    st.subheader("🚀 Suite Modules")
    col_idx = 0
    cols = st.columns(3)
    for idx, p in enumerate(projects):
        with cols[col_idx]:
            st.markdown(f"""
            <div class="glass-card {p['style']}">
                <h3 style="margin: 0; color: #f8fafc; font-size: 1.4rem;">{p['name']}</h3>
                <p style="color: #94a3b8; font-size: 0.95rem; height: 75px; line-height: 1.5; margin: 12px 0 20px 0;">{p['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
            st.button(f"Open {p['name']} 🔗", key=f"dash_open_{p['name']}", use_container_width=True, help=f"Select '{p['nav']}' from the sidebar to open.")
        col_idx = (col_idx + 1) % 3
        if col_idx == 0 and idx < len(projects) - 1:
            st.write("")


# ══════════════════════════════════════════
# PAGE: NOTES APP (NotesIO)
# ══════════════════════════════════════════
elif page == "📝 NotesIO":
    # Session state init
    if "notes_data" not in st.session_state:
        st.session_state.notes_data = None
    if "summary_data" not in st.session_state:
        st.session_state.summary_data = None
    if "code_data" not in st.session_state:
        st.session_state.code_data = None
    if "notes_history" not in st.session_state:
        st.session_state.notes_history = []

    def notes_add_history(action_type, title, payload):
        st.session_state.notes_history.append({"type": action_type, "title": title, "payload": payload})

    # Sidebar controls
    with st.sidebar:
        st.markdown("---")
        st.subheader("⚙️ NotesIO Settings")
        notes_api_key = st.text_input("Gemini API Key", value=API_KEY, type="password", key="notes_api")
        notes_model = st.selectbox("AI Engine Model", ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-flash"], index=0, key="notes_model")

    st.markdown("""
    <div class="header-box">
        <h1 class="header-title">NotesIO</h1>
        <p class="header-subtitle">Streamlined Note Synthesis, Smart Summarizations, and Dynamic Code Engineering</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📝 Note Generator Studio", "📁 Smart File Summarizer", "💻 Code Developer Engine"])

    # TAB 1: Note Generation
    with tab1:
        st.markdown('<div class="glass-card teal-card"><h3>📝 Generative Note Synthesis</h3><p style="color: #94a3b8; font-size: 0.9rem;">Architect rich, structured study resources on any subject.</p></div>', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("Configuration")
            topic_input = st.text_input("Topic of Interest", placeholder="e.g. Quantum Computing", key="nt_topic")
            subject_cat = st.text_input("Subject/Category (Optional)", placeholder="e.g. Computer Science", key="nt_subj")
            target_aud = st.selectbox("Target Audience Level", ["General Public", "High School Student", "Undergraduate", "Postgraduate / Professional"], index=2, key="nt_aud")
            note_depth = st.selectbox("Note Detail Level", ["High-Yield Summary", "Detailed Explanation (Recommended)", "Deep-Dive Comprehensive Guide"], index=1, key="nt_depth")
            note_tone = st.selectbox("Explanation Style & Tone", ["Academic & Analytical", "Simple & Analogous (ELI5)", "Bullet-pointed Revision", "Q&A Study Flashcards"], index=0, key="nt_tone")
            if st.button("Generate Notes ✨", use_container_width=True, key="nt_gen"):
                if not topic_input.strip():
                    st.warning("⚠️ Please specify the Topic of Interest.")
                elif not notes_api_key.strip():
                    st.warning("⚠️ Please provide a Gemini API Key.")
                else:
                    with st.spinner("Synthesizing comprehensive notes..."):
                        try:
                            client = genai.Client(api_key=notes_api_key.strip())
                            prompt = f"Generate Notes on '{topic_input}' in a detailed and structured way. Subject: {subject_cat or 'General'}. Audience: {target_aud}. Detail: {note_depth}. Style: {note_tone}. Output clean Markdown format. Start directly with the notes header."
                            response = client.models.generate_content(model=notes_model, contents=prompt)
                            st.session_state.notes_data = {"topic": topic_input, "content": response.text, "depth": note_depth, "tone": note_tone}
                            notes_add_history("📝 Notes", topic_input, st.session_state.notes_data)
                            st.toast("Notes synthesized! 🎉", icon="✅")
                        except Exception as e:
                            st.error(f"Error: {e}")
        with col2:
            st.subheader("Output Workspace")
            if st.session_state.notes_data:
                notes = st.session_state.notes_data
                st.markdown(f"**Topic**: `{notes['topic']}` | **Detail**: `{notes['depth']}` | **Style**: `{notes['tone']}`")
                st.download_button("Download Notes (.md) 📥", data=notes["content"], file_name=f"{notes['topic'].replace(' ', '_')}_Notes.md", mime="text/markdown", key="dl_notes")
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown(notes["content"])
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Configure settings on the left and click 'Generate Notes' to begin.")

    # TAB 2: File Summarizer
    with tab2:
        st.markdown('<div class="glass-card indigo-card"><h3>📁 AI File Summarization Engine</h3><p style="color: #94a3b8; font-size: 0.9rem;">Upload text-based files to generate summaries.</p></div>', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 2])
        with col1:
            uploaded_file = st.file_uploader("Upload Document", type=["txt", "md", "py", "json", "csv", "html", "css", "js", "yaml", "xml", "ini"], key="nt_upload")
            summary_style = st.selectbox("Summary Style", ["Key Bullet-Point Breakdown", "Concise Executive Brief", "Deep Technical Summary", "Action Items & Milestones"], key="nt_sum_style")
            file_text = ""
            if uploaded_file:
                try:
                    bytes_data = uploaded_file.read()
                    try:
                        file_text = bytes_data.decode("utf-8")
                    except UnicodeDecodeError:
                        file_text = bytes_data.decode("latin-1")
                    st.success("File uploaded!")
                    with st.expander("Preview"):
                        st.code(file_text[:1200] + ("\n... [Truncated]" if len(file_text) > 1200 else ""), language="text")
                except Exception as e:
                    st.error(f"Error: {e}")
            if st.button("Summarize Content ⚡", use_container_width=True, key="nt_sum_btn"):
                if not uploaded_file:
                    st.warning("⚠️ Upload a file first.")
                elif not file_text.strip():
                    st.warning("⚠️ File is empty.")
                elif not notes_api_key.strip():
                    st.warning("⚠️ Provide API Key.")
                else:
                    with st.spinner("Analyzing..."):
                        try:
                            client = genai.Client(api_key=notes_api_key.strip())
                            prompt = f"Summarize the following in style: {summary_style}.\nFile: {uploaded_file.name}\nContent:\n{file_text}"
                            response = client.models.generate_content(model=notes_model, contents=prompt)
                            st.session_state.summary_data = {"filename": uploaded_file.name, "style": summary_style, "content": response.text}
                            st.toast("Summarized! 🎉", icon="✅")
                        except Exception as e:
                            st.error(f"Error: {e}")
        with col2:
            st.subheader("Summary Result")
            if st.session_state.summary_data:
                s = st.session_state.summary_data
                st.markdown(f"**Source**: `{s['filename']}` | **Style**: `{s['style']}`")
                st.download_button("Download Summary (.md) 📥", data=s["content"], file_name=f"Summary_{s['filename'].split('.')[0]}.md", mime="text/markdown", key="dl_sum")
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown(s["content"])
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Upload a file and click 'Summarize Content'.")

    # TAB 3: Code Developer
    with tab3:
        st.markdown('<div class="glass-card purple-card"><h3>💻 AI Code Engineering Workspace</h3><p style="color: #94a3b8; font-size: 0.9rem;">Generate optimized, runnable source files.</p></div>', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 2])
        with col1:
            project_name = st.text_input("Project Name", placeholder="e.g. DataScraper", key="nt_proj")
            lang_map = {"Python": "py", "JavaScript": "js", "TypeScript": "ts", "HTML/CSS/JS": "html", "C++": "cpp", "Java": "java", "Rust": "rs", "Go": "go", "SQL": "sql", "Shell Script": "sh"}
            lang_selected = st.selectbox("Programming Language", list(lang_map.keys()), index=0, key="nt_lang")
            file_ext = st.text_input("File Extension", value=lang_map[lang_selected], key="nt_ext")
            code_style = st.selectbox("Code Pattern", ["Documented & Commented (Educational)", "Clean & Minimalist (Production)", "OOP", "Functional & Modular"], key="nt_code_style")
            project_desc = st.text_area("Project Description", placeholder="Describe the app/script...", height=180, key="nt_desc")
            if st.button("Generate Code 💻", use_container_width=True, key="nt_code_btn"):
                if not project_name.strip() or not project_desc.strip():
                    st.warning("⚠️ Provide project name and description.")
                elif not notes_api_key.strip():
                    st.warning("⚠️ Provide API Key.")
                else:
                    with st.spinner("Engineering source code..."):
                        try:
                            client = genai.Client(api_key=notes_api_key.strip())
                            prompt = f"Generate Code Only for '{project_desc}' in '.{file_ext}'. Language: {lang_selected}. Style: {code_style}. Output ONLY clean executable code."
                            response = client.models.generate_content(model=notes_model, contents=prompt)
                            code_output = response.text.strip()
                            if code_output.startswith("```"):
                                lines = code_output.splitlines()
                                if lines[0].startswith("```"):
                                    lines = lines[1:]
                                if lines and lines[-1].startswith("```"):
                                    lines = lines[:-1]
                                code_output = "\n".join(lines).strip()
                            st.session_state.code_data = {"name": project_name, "ext": file_ext, "lang": lang_selected, "style": code_style, "content": code_output}
                            st.toast("Code generated! 🚀", icon="✅")
                        except Exception as e:
                            st.error(f"Error: {e}")
        with col2:
            st.subheader("Source Code Editor View")
            if st.session_state.code_data:
                c = st.session_state.code_data
                st.download_button(f"Download {c['name']}.{c['ext']} 📥", data=c["content"], file_name=f"{c['name']}.{c['ext']}", mime="text/plain", key="dl_code")
                hl = c["lang"].lower()
                if "html" in hl: hl = "html"
                elif "javascript" in hl: hl = "javascript"
                elif "python" in hl: hl = "python"
                else: hl = c["ext"]
                st.code(c["content"], language=hl)
            else:
                st.info("Define requirements and click 'Generate Code'.")


# ══════════════════════════════════════════
# PAGE: REVISION IO
# ══════════════════════════════════════════
elif page == "⚡ RevisionIO":
    if "rev_plan_data" not in st.session_state:
        st.session_state.rev_plan_data = None
    if "rev_completed_days" not in st.session_state:
        st.session_state.rev_completed_days = {}
    if "rev_current_day" not in st.session_state:
        st.session_state.rev_current_day = 1

    def rev_run_generation(api_key, target_class, subject, topic, days, hours):
        try:
            client = genai.Client(api_key=api_key)
            prompt = f"You are a senior IIT/NEET faculty. Student prep: {target_class}. Subject: {subject}. Topic: {topic}. Duration: {days} days, {hours} hrs/day. Generate structured day-by-day revision plan matching NCERT. Return JSON matching the schema. Exactly {days} days."
            response = client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=RevisionPlanSchema, temperature=0.65)
            )
            return json.loads(response.text)
        except Exception as e:
            st.error(f"Gemini API Error: {e}")
            return None

    with st.sidebar:
        st.markdown("---")
        st.subheader("🎯 RevisionIO Config")
        rev_exam = st.selectbox("Target Exam", ["JEE Main (PCM)", "JEE Advanced (PCM)", "NEET Prep (PCB)", "CBSE Class 12 Boards"], key="rev_exam")
        rev_subject = st.text_input("Subject", placeholder="e.g. Physics", key="rev_subj")
        rev_topic = st.text_input("Topic to Revise", placeholder="e.g. Electrostatics", key="rev_topic")
        rev_days = st.slider("Revision Period (Days)", 1, 30, 5, key="rev_days")
        rev_hours = st.slider("Daily Hours", 1, 12, 3, key="rev_hours")
        if st.button("Generate Revision Plan ✨", use_container_width=True, key="rev_gen"):
            if not rev_subject.strip() or not rev_topic.strip():
                st.warning("⚠️ Provide subject and topic.")
            else:
                with st.spinner(f"Creating {rev_days}-day plan for '{rev_topic}'..."):
                    plan = rev_run_generation(API_KEY, rev_exam, rev_subject.strip(), rev_topic.strip(), rev_days, rev_hours)
                    if plan:
                        st.session_state.rev_plan_data = plan
                        st.session_state.rev_completed_days = {d["day"]: False for d in plan["days"]}
                        st.session_state.rev_current_day = 1
                        st.toast("Plan generated! ⚡", icon="🔥")
                        st.rerun()
        st.markdown("---")
        if st.session_state.rev_plan_data:
            pkg = {"plan": st.session_state.rev_plan_data, "completed_days": st.session_state.rev_completed_days, "view_day": st.session_state.rev_current_day}
            st.download_button("Save Plan 💾", json.dumps(pkg, indent=4), f"{st.session_state.rev_plan_data.get('topic','Revision')}_Plan.json", "application/json", use_container_width=True, key="rev_save")
        rev_upload = st.file_uploader("Load Plan 📂", type=["json"], key="rev_upload")
        if rev_upload:
            try:
                ld = json.load(rev_upload)
                if "plan" in ld:
                    st.session_state.rev_plan_data = ld["plan"]
                    st.session_state.rev_completed_days = {int(k): bool(v) for k, v in ld["completed_days"].items()}
                    st.session_state.rev_current_day = int(ld.get("view_day", 1))
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown('<div class="header-box"><h1 class="header-title">RevisionIO</h1><p style="color: #14b8a6; font-size: 1.15rem; font-weight: bold; margin-top: 5px;">⚡ Competitive Revision Engine ⚡</p></div>', unsafe_allow_html=True)

    if st.session_state.rev_plan_data is None:
        st.markdown('<div class="glass-card" style="text-align: center; max-width: 600px; margin: 40px auto; border-top: 4px solid #6366f1;"><h3 style="font-size: 1.8rem; color: #f8fafc;">No Plan Active</h3><p style="color: #94a3b8;">Configure in the sidebar and click Generate.</p></div>', unsafe_allow_html=True)
    else:
        plan = st.session_state.rev_plan_data
        total_days = len(plan["days"])
        st.markdown(f'<div class="glass-card"><h2 style="color: #f8fafc;">{plan.get("topic","")}</h2><span style="color: #14b8a6; font-weight: bold;">{plan.get("subject","")} | {plan.get("target_class","")} | {total_days} Days</span></div>', unsafe_allow_html=True)
        nc, pc = st.columns([3, 2])
        with nc:
            st.session_state.rev_current_day = st.slider("Navigate Days", 1, total_days, st.session_state.rev_current_day, key="rev_slider")
            day_num = st.session_state.rev_current_day
        with pc:
            if day_num not in st.session_state.rev_completed_days:
                st.session_state.rev_completed_days[day_num] = False
            is_done = st.checkbox(f"Mark Day {day_num} Completed", st.session_state.rev_completed_days.get(day_num, False), key=f"rev_comp_{day_num}")
            st.session_state.rev_completed_days[day_num] = is_done
            done_count = sum(1 for v in st.session_state.rev_completed_days.values() if v)
            st.progress(done_count / total_days)
            st.markdown(f"<div style='text-align: right; font-size: 0.85rem; color: #94a3b8;'>Progress: {done_count}/{total_days} ({int(done_count/total_days*100)}%)</div>", unsafe_allow_html=True)
            if all(st.session_state.rev_completed_days.get(d, False) for d in range(1, total_days + 1)):
                st.balloons()
                st.success("🏆 All days completed!")
        day_data = next((d for d in plan["days"] if d["day"] == day_num), None)
        if day_data:
            st.markdown(f'<div class="glass-card"><div style="font-size: 0.85rem; font-weight: bold; color: #14b8a6; text-transform: uppercase;">DAY {day_num}</div><h3 style="color: #f8fafc; margin-top: 4px;">{day_data.get("title","")}</h3></div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                topics_html = "".join([f"<li>{t}</li>" for t in day_data.get("key_topics", [])])
                st.markdown(f'<div class="glass-card indigo-card"><h4 style="color: #f8fafc;">🎯 Core Subtopics</h4><ul style="color: #94a3b8; padding-left: 20px;">{topics_html}</ul></div>', unsafe_allow_html=True)
            with c2:
                formulas_html = "".join([f"<div style='background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 10px; margin-bottom: 6px; font-family: monospace; color: #facc15; font-size: 0.85rem;'>{f}</div>" for f in day_data.get("formulas_or_key_terms", [])])
                st.markdown(f'<div class="glass-card orange-card"><h4 style="color: #f8fafc;">📝 Formulas & Terms</h4>{formulas_html}</div>', unsafe_allow_html=True)
            bits_html = "".join([f"<p style='margin-bottom: 8px;'>✦ {b}</p>" for b in day_data.get("revision_bits", [])])
            st.markdown(f'<div class="glass-card teal-card"><h4 style="color: #f8fafc;">💡 Revision Bits</h4><div style="color: #e2e8f0; font-size: 0.95rem;">{bits_html}</div></div>', unsafe_allow_html=True)
            tips_html = "".join([f"<p style='margin-bottom: 6px; color: #f43f5e;'>• {t}</p>" for t in day_data.get("exam_tips", [])])
            st.markdown(f'<div class="glass-card pink-card"><h4 style="color: #f8fafc;">⚠️ Exam Traps</h4>{tips_html}</div>', unsafe_allow_html=True)
            st.markdown("### 🔥 Daily Practice Challenges")
            for idx, q_item in enumerate(day_data.get("practice_questions", [])):
                st.markdown(f'<div style="background: rgba(30, 41, 59, 0.25); border-left: 4px solid #14b8a6; padding: 15px; border-radius: 8px; margin-bottom: 8px;"><div style="font-size: 0.8rem; font-weight: bold; color: #14b8a6;">PROBLEM {idx+1}</div><div style="font-weight: bold; color: #f8fafc;">{q_item.get("question","")}</div></div>', unsafe_allow_html=True)
                with st.expander("Reveal Solution 👁️"):
                    st.success(f"**Solution:**\n\n{q_item.get('answer', '')}")


# ══════════════════════════════════════════
# PAGE: ROADMAP IO
# ══════════════════════════════════════════
elif page == "🗺️ RoadmapIO":
    if "road_step" not in st.session_state:
        st.session_state.road_step = 0
    if "road_mode" not in st.session_state:
        st.session_state.road_mode = "Roadmap"
    if "road_query" not in st.session_state:
        st.session_state.road_query = ""
    if "road_suggested" not in st.session_state:
        st.session_state.road_suggested = ""
    if "road_followups" not in st.session_state:
        st.session_state.road_followups = []
    if "road_answers" not in st.session_state:
        st.session_state.road_answers = {}
    if "road_output" not in st.session_state:
        st.session_state.road_output = ""

    with st.sidebar:
        st.markdown("---")
        road_model = st.selectbox("Model", ["gemini-2.5-flash", "gemini-2.5-pro"], key="road_model")
        if st.button("🔄 Reset RoadmapIO", use_container_width=True, key="road_reset"):
            for k in ["road_step", "road_mode", "road_query", "road_suggested", "road_followups", "road_answers", "road_output"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

    def road_get_client():
        try:
            return genai.Client(api_key=API_KEY)
        except Exception as e:
            st.error(f"Client error: {e}")
            return None

    st.markdown('<div class="header-box"><h1 class="header-title">RoadmapIO</h1><p class="header-subtitle">Interactive tailored algorithms and learning paths powered by Gemini</p></div>', unsafe_allow_html=True)

    # Stepper
    step = st.session_state.road_step
    st.markdown(f"""<div class="stepper-container"><div class="stepper-item {'completed' if step > 0 else 'active'}"><div class="stepper-circle">{'✓' if step > 0 else '1'}</div><div class="stepper-text">Define Goal</div></div><div class="stepper-item {'completed' if step > 1 else ('active' if step == 1 else '')}"><div class="stepper-circle">{'✓' if step > 1 else '2'}</div><div class="stepper-text">Specify Context</div></div><div class="stepper-item {'active' if step == 2 else ''}"><div class="stepper-circle">3</div><div class="stepper-text">Tailored Plan</div></div></div>""", unsafe_allow_html=True)

    if st.session_state.road_step == 0:
        st.markdown("### 🗺️ Define Your Learning Path or Algorithm Goal")
        mode = st.radio("What do you want?", ["Roadmap 🗺️", "Algorithm ⚙️"], horizontal=True, key="road_mode_radio")
        st.session_state.road_mode = "Roadmap" if "Roadmap" in mode else "Algorithm"
        user_q = st.text_area("Enter your requirement:", value=st.session_state.road_suggested or "", placeholder="e.g. Master Go backend dev in 3 months", height=130, key="road_input")
        _, col_r = st.columns([4, 1])
        with col_r:
            if st.button("Next ➔", use_container_width=True, key="road_next"):
                if not user_q.strip():
                    st.warning("⚠️ Provide a requirement.")
                else:
                    st.session_state.road_query = user_q.strip()
                    client = road_get_client()
                    if client:
                        with st.spinner("Analyzing..."):
                            try:
                                prompt = f"Generate exactly 3 clarifying questions for a {st.session_state.road_mode} about: '{st.session_state.road_query}'"
                                response = client.models.generate_content(model=road_model, contents=prompt, config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=FollowUpSchema, temperature=0.7, thinking_config=types.ThinkingConfig(thinking_budget=0)))
                                st.session_state.road_followups = json.loads(response.text).get("questions", [])
                            except Exception:
                                st.session_state.road_followups = ["What is your target language?", "What is your experience level?", "What are your constraints?"]
                            st.session_state.road_step = 1
                            st.rerun()

    elif st.session_state.road_step == 1:
        st.markdown("### 🔍 Help us optimize your results")
        answers = {}
        with st.form("road_clarify"):
            for idx, q in enumerate(st.session_state.road_followups):
                st.markdown(f"**Question {idx+1}:** {q}")
                answers[q] = st.text_input("Your Answer:", key=f"road_ans_{idx}")
            c_l, c_r = st.columns([1, 4])
            with c_l:
                back = st.form_submit_button("⬅️ Back")
            with c_r:
                gen = st.form_submit_button("✨ Generate Output")
            if back:
                st.session_state.road_step = 0
                st.rerun()
            if gen:
                st.session_state.road_answers = answers
                client = road_get_client()
                if client:
                    with st.spinner("Synthesizing..."):
                        mode = st.session_state.road_mode
                        prompt = f"Generate a customized {mode} for: '{st.session_state.road_query}'. Answers:\n"
                        for q, a in answers.items():
                            prompt += f"- {q}: {a or 'No preference'}\n"
                        prompt += "\nUse clean Markdown with structured sections."
                        try:
                            response = client.models.generate_content(model=road_model, contents=prompt, config=types.GenerateContentConfig(temperature=0.7, thinking_config=types.ThinkingConfig(thinking_budget=0)))
                            st.session_state.road_output = response.text
                            st.session_state.road_step = 2
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

    elif st.session_state.road_step == 2:
        st.markdown("### 🎉 Your Optimized Plan is Ready!")
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(st.session_state.road_output)
        st.markdown('</div>', unsafe_allow_html=True)
        col_dl, col_rs = st.columns([3, 1])
        with col_dl:
            st.download_button("📥 Download Plan (.md)", st.session_state.road_output, f"{st.session_state.road_mode.lower()}_plan.md", "text/markdown", use_container_width=True, key="road_dl")
        with col_rs:
            if st.button("🔄 Create New", use_container_width=True, key="road_new"):
                st.session_state.road_step = 0
                st.session_state.road_query = ""
                st.session_state.road_followups = []
                st.session_state.road_answers = {}
                st.session_state.road_output = ""
                st.rerun()


# ══════════════════════════════════════════
# PAGE: JEE IGNITER (Mentorship)
# ══════════════════════════════════════════
elif page == "🎓 JEE Igniter":
    mentor_client = genai.Client(api_key=API_KEY) if API_KEY else None
    with st.sidebar:
        st.markdown("---")
        mentor_page = st.radio("JEE Module:", ["❓ Doubt Solver", "📅 Daily Planner", "🎓 Mentor AI"], key="mentor_nav")

    st.markdown('<div class="header-box"><h1 class="header-title">⚡ JEE Igniter AI</h1><p class="header-subtitle">Your personal 24/7 IITian Mentor, Doubt Solver, and Study Planner</p></div>', unsafe_allow_html=True)

    if mentor_page == "❓ Doubt Solver":
        st.header("❓ Multimodal Doubt Solver")
        col1, col2 = st.columns(2)
        with col1:
            m_subject = st.selectbox("Subject", ["Physics", "Chemistry", "Mathematics"], key="m_subj")
            m_diff = st.selectbox("Difficulty", ["JEE Main", "JEE Advanced"], key="m_diff")
            m_file = st.file_uploader("Upload Doubt Image", type=["png", "jpg", "jpeg"], key="m_img")
            m_image = None
            if m_file:
                m_image = Image.open(m_file)
                st.image(m_image, caption="Uploaded", use_container_width=True)
            m_text = st.text_area("Type your question:", key="m_text")
            m_solve = st.button("Solve Doubt ⚡", key="m_solve")
        with col2:
            if m_solve:
                if not mentor_client:
                    st.error("API Key missing.")
                elif not m_text and not m_file:
                    st.warning("Enter a question or upload an image.")
                else:
                    with st.spinner("Solving..."):
                        prompt = f"You are an elite JEE faculty for {m_subject} at {m_diff} level. Provide step-by-step solution with LaTeX."
                        contents = []
                        if m_image:
                            contents.append(m_image)
                        contents.append(f"Question: {m_text}\n\n{prompt}")
                        try:
                            response = mentor_client.models.generate_content(model="gemini-2.5-flash", contents=contents)
                            st.success("Solved!")
                            st.markdown(response.text)
                        except Exception as e:
                            st.error(f"Error: {e}")

    elif mentor_page == "📅 Daily Planner":
        st.header("📅 JEE Study Planner")
        col1, col2 = st.columns([1, 1.2])
        with col1:
            target_year = st.selectbox("Target Year", ["2026", "2027", "2028"], key="mp_yr")
            prep_mode = st.selectbox("Mode", ["Regular School", "Dummy School", "Dropper"], key="mp_mode")
            prep_level = st.select_slider("Level", ["Beginner", "Intermediate", "Advanced"], key="mp_lvl")
            study_hours = st.slider("Daily Hours", 4, 16, 10, key="mp_hrs")
            backlog = st.text_area("Weak Topics (comma separated)", key="mp_backlog")
            strong = st.multiselect("Strong Subjects", ["Physics", "Chemistry", "Mathematics"], default=["Physics"], key="mp_strong")
            gen_plan = st.button("Generate Study Plan 📅", key="mp_gen")
        with col2:
            if "mp_todo" not in st.session_state:
                st.session_state.mp_todo = [{"task": "Solve 15 PYQs", "done": False}, {"task": "Revise Inorganic 1hr", "done": False}]
            new_task = st.text_input("➕ Add task:", key="mp_new_task")
            if st.button("Add Task", key="mp_add"):
                if new_task:
                    st.session_state.mp_todo.append({"task": new_task, "done": False})
                    st.rerun()
            for i, item in enumerate(st.session_state.mp_todo):
                checked = st.checkbox(item["task"], value=item["done"], key=f"mp_todo_{i}")
                if checked != item["done"]:
                    st.session_state.mp_todo[i]["done"] = checked
                    st.rerun()
        if gen_plan and mentor_client:
            with st.spinner("Creating plan..."):
                prompt = f"Create 7-day JEE plan. Year: {target_year}, Mode: {prep_mode}, Level: {prep_level}, Hours: {study_hours}, Weak: {backlog}, Strong: {', '.join(strong)}. Use Markdown tables."
                try:
                    response = mentor_client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                    st.success("Plan Ready!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error: {e}")

    elif mentor_page == "🎓 Mentor AI":
        st.header("🎓 Ask an IITian - JEE Mentor AI")
        if "mentor_msgs" not in st.session_state:
            st.session_state.mentor_msgs = [{"role": "assistant", "content": "Hey champ! I cleared JEE Advanced. Ask me anything about strategy, motivation, or study tips!"}]
        for msg in st.session_state.mentor_msgs:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        if user_q := st.chat_input("Ask about revision, mock tests, motivation...", key="mentor_chat"):
            with st.chat_message("user"):
                st.markdown(user_q)
            st.session_state.mentor_msgs.append({"role": "user", "content": user_q})
            if mentor_client:
                with st.spinner("IITian Mentor typing..."):
                    sys_instr = "You are 'IITian Mentor', an elite JEE coach. Give practical, actionable advice. Use numbered lists."
                    chat_log = f"System: {sys_instr}\n\nHistory:\n"
                    for m in st.session_state.mentor_msgs:
                        chat_log += f"{'User' if m['role']=='user' else 'Mentor'}: {m['content']}\n"
                    chat_log += "Mentor:"
                    try:
                        response = mentor_client.models.generate_content(model="gemini-2.5-flash", contents=chat_log)
                        with st.chat_message("assistant"):
                            st.markdown(response.text)
                        st.session_state.mentor_msgs.append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"Error: {e}")


# ══════════════════════════════════════════
# PAGE: DAILY PRACTISE
# ══════════════════════════════════════════
elif page == "✏️ DailyPractise":
    if "dp_questions" not in st.session_state:
        st.session_state.dp_questions = None
    if "dp_answers" not in st.session_state:
        st.session_state.dp_answers = {}
    if "dp_submitted" not in st.session_state:
        st.session_state.dp_submitted = False
    if "dp_start_time" not in st.session_state:
        st.session_state.dp_start_time = None
    if "dp_token" not in st.session_state:
        st.session_state.dp_token = ""
    if "dp_subject" not in st.session_state:
        st.session_state.dp_subject = ""
    if "dp_chapter" not in st.session_state:
        st.session_state.dp_chapter = ""
    if "dp_time_spent" not in st.session_state:
        st.session_state.dp_time_spent = 0

    def dp_generate(api_key, subject, chapter):
        try:
            client = genai.Client(api_key=api_key)
            seed = random.randint(100000, 999999)
            prompt = f"CBSE Class 12 examiner. Create 15 MCQ for {subject} - {chapter}. LaTeX for math. Seed: {seed}. Return JSON."
            response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt, config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=PracticeTestSchema, temperature=0.85))
            return json.loads(response.text)
        except Exception as e:
            st.error(f"Error: {e}")
            return None

    with st.sidebar:
        st.markdown("---")
        st.subheader("✏️ DailyPractise")
        dp_subj = st.selectbox("Subject", list(DP_SUBJECTS_AND_CHAPTERS.keys()), key="dp_subj_sel", disabled=(st.session_state.dp_questions is not None and not st.session_state.dp_submitted))
        dp_chap = st.selectbox("Chapter", DP_SUBJECTS_AND_CHAPTERS[dp_subj], key="dp_chap_sel", disabled=(st.session_state.dp_questions is not None and not st.session_state.dp_submitted))
        if st.session_state.dp_questions is not None and not st.session_state.dp_submitted:
            if st.button("🔴 Quit Test", use_container_width=True, key="dp_quit"):
                st.session_state.dp_questions = None
                st.session_state.dp_answers = {}
                st.session_state.dp_submitted = False
                st.session_state.dp_start_time = None
                st.rerun()
        else:
            if st.button("🚀 Generate 1-Hour Test", use_container_width=True, key="dp_gen"):
                with st.spinner("Generating 15 MCQ..."):
                    data = dp_generate(API_KEY, dp_subj, dp_chap)
                    if data and "questions" in data and len(data["questions"]) == 15:
                        st.session_state.dp_questions = data["questions"]
                        st.session_state.dp_answers = {q["id"]: None for q in data["questions"]}
                        st.session_state.dp_submitted = False
                        st.session_state.dp_start_time = time.time()
                        st.session_state.dp_token = str(random.randint(1000, 9999))
                        st.session_state.dp_subject = dp_subj
                        st.session_state.dp_chapter = dp_chap
                        st.rerun()
                    else:
                        st.error("Failed. Try again.")

    # Landing
    if st.session_state.dp_questions is None:
        st.markdown('<div class="header-box"><h1 class="header-title">DailyPractise ✏️</h1><p class="header-subtitle">CBSE Class 12 MCQ Practice • 15 Problems • 1 Hour</p></div>', unsafe_allow_html=True)
        st.info("Select subject and chapter from the sidebar, then click 'Generate 1-Hour Test'.")

    # Running Test
    elif st.session_state.dp_questions is not None and not st.session_state.dp_submitted:
        elapsed = time.time() - st.session_state.dp_start_time
        remaining = max(0, 3600 - int(elapsed))
        if remaining <= 0:
            st.session_state.dp_submitted = True
            st.session_state.dp_time_spent = 3600
            st.rerun()

        st.markdown(f'<div class="header-box"><h2 class="header-title">{st.session_state.dp_subject} Practice Exam</h2><p class="header-subtitle">Topic: {st.session_state.dp_chapter} • MCQ • Single-Select</p></div>', unsafe_allow_html=True)
        for idx, q_dict in enumerate(st.session_state.dp_questions):
            st.markdown(f'<div class="glass-card"><div style="font-size: 0.9rem; color: #94a3b8; font-weight: 600;">QUESTION {q_dict["id"]} OF 15</div></div>', unsafe_allow_html=True)
            st.markdown(q_dict["question"])
            ca, cb = st.columns(2)
            with ca:
                st.markdown(f"**A)** {q_dict['option_a']}")
                st.markdown(f"**C)** {q_dict['option_c']}")
            with cb:
                st.markdown(f"**B)** {q_dict['option_b']}")
                st.markdown(f"**D)** {q_dict['option_d']}")
            curr = st.session_state.dp_answers.get(q_dict["id"])
            di = 0
            if curr == "A": di = 1
            elif curr == "B": di = 2
            elif curr == "C": di = 3
            elif curr == "D": di = 4
            sel = st.radio(f"Answer Q{q_dict['id']}:", ["Not Attempted", "A", "B", "C", "D"], index=di, horizontal=True, key=f"dp_r_{q_dict['id']}_{st.session_state.dp_token}")
            st.session_state.dp_answers[q_dict["id"]] = None if sel == "Not Attempted" else sel
            st.markdown("<br>", unsafe_allow_html=True)
        _, sc, _ = st.columns([1, 2, 1])
        with sc:
            if st.button("🎯 Submit Test", use_container_width=True, type="primary", key="dp_submit"):
                st.session_state.dp_submitted = True
                st.session_state.dp_time_spent = int(time.time() - st.session_state.dp_start_time)
                st.rerun()

    # Results
    else:
        questions = st.session_state.dp_questions
        ua = st.session_state.dp_answers
        correct = sum(1 for q in questions if ua.get(q["id"]) and ua[q["id"]].upper() == q["correct_option"].strip().upper())
        incorrect = sum(1 for q in questions if ua.get(q["id"]) and ua[q["id"]].upper() != q["correct_option"].strip().upper())
        unattempted = sum(1 for q in questions if ua.get(q["id"]) is None)
        pct = int(correct / 15 * 100)
        st.markdown(f'<div class="header-box"><h1 class="header-title">Post-Test Analysis</h1><p class="header-subtitle">{st.session_state.dp_subject} • {st.session_state.dp_chapter}</p></div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("Score", f"{correct}/15", f"{pct}%")
        c2.metric("Correct", correct)
        c3.metric("Incorrect / Skipped", f"{incorrect} / {unattempted}")
        st.markdown("## 📖 Solutions")
        for q in questions:
            user_a = ua.get(q["id"])
            correct_a = q["correct_option"].strip().upper()
            if user_a is None:
                badge = '<span class="badge badge-unattempted">Unattempted</span>'
            elif user_a.upper() == correct_a:
                badge = '<span class="badge badge-correct">Correct ✓</span>'
            else:
                badge = '<span class="badge badge-incorrect">Incorrect ✗</span>'
            st.markdown(f'<div class="glass-card"><div style="display: flex; justify-content: space-between;"><span style="color: #94a3b8; font-weight: 700;">Q{q["id"]}</span>{badge}</div></div>', unsafe_allow_html=True)
            st.markdown(q["question"])
            st.markdown(f"**Your Answer:** {user_a or 'None'} | **Correct:** {correct_a}")
            with st.expander("Show Solution"):
                st.markdown(q["explanation"])
        if st.button("🔄 Take Another Test", use_container_width=True, key="dp_retake"):
            st.session_state.dp_questions = None
            st.session_state.dp_answers = {}
            st.session_state.dp_submitted = False
            st.session_state.dp_start_time = None
            st.rerun()


# ══════════════════════════════════════════
# PAGE: JEE ADVANCED CBT
# ══════════════════════════════════════════
elif page == "🎯 JEE Advanced CBT":
    if "jee_state" not in st.session_state:
        st.session_state.jee_state = "welcome"
    if "jee_questions" not in st.session_state:
        st.session_state.jee_questions = []
    if "jee_responses" not in st.session_state:
        st.session_state.jee_responses = {}
    if "jee_status" not in st.session_state:
        st.session_state.jee_status = {}
    if "jee_start_time" not in st.session_state:
        st.session_state.jee_start_time = None
    if "jee_time_limit" not in st.session_state:
        st.session_state.jee_time_limit = 3 * 3600
    if "jee_curr_idx" not in st.session_state:
        st.session_state.jee_curr_idx = 0
    if "jee_subject" not in st.session_state:
        st.session_state.jee_subject = "Physics"
    if "jee_chat" not in st.session_state:
        st.session_state.jee_chat = []
    if "jee_fallback" not in st.session_state:
        st.session_state.jee_fallback = False
    if "jee_name" not in st.session_state:
        st.session_state.jee_name = ""
    if "jee_roll" not in st.session_state:
        st.session_state.jee_roll = ""

    def jee_start_test(qs, hours):
        st.session_state.jee_questions = qs
        st.session_state.jee_time_limit = int(hours * 3600)
        st.session_state.jee_start_time = time.time()
        st.session_state.jee_state = "test"
        st.session_state.jee_curr_idx = 0
        st.session_state.jee_subject = qs[0]["subject"]
        st.session_state.jee_responses = {}
        st.session_state.jee_status = {}
        for q in qs:
            qid = q["id"]
            st.session_state.jee_status[qid] = "unvisited"
            if q["type"] == "Multi Correct":
                st.session_state.jee_responses[qid] = []
            elif q["type"] == "Match the Column":
                st.session_state.jee_responses[qid] = {"A": [], "B": [], "C": [], "D": []}
            else:
                st.session_state.jee_responses[qid] = ""
        st.session_state.jee_status[qs[0]["id"]] = "not_answered"

    def jee_calc_score():
        total = 0
        subj_scores = {"Physics": 0, "Chemistry": 0, "Mathematics": 0}
        correct = incorrect = unattempted = 0
        details = []
        for q in st.session_state.jee_questions:
            qid = q["id"]
            subj = q["subject"]
            qtype = q["type"]
            ua = st.session_state.jee_responses.get(qid)
            ca = q["correct_answer"]
            score = 0
            status = "unattempted"
            if qtype in ["Single Correct", "Paragraph Based"]:
                if not ua or ua == "": unattempted += 1
                elif ua == ca: score = 3; status = "correct"; correct += 1
                else: score = -1; status = "incorrect"; incorrect += 1
            elif qtype == "Multi Correct":
                if not ua or len(ua) == 0: unattempted += 1
                else:
                    us, cs = set(ua), set(ca)
                    if us == cs: score = 4; status = "correct"; correct += 1
                    elif us.issubset(cs): score = len(ua); status = "partial"; correct += 1
                    else: score = -2; status = "incorrect"; incorrect += 1
            elif qtype == "Integer Type":
                if not ua or str(ua).strip() == "": unattempted += 1
                else:
                    try:
                        if float(str(ua).strip()) == float(str(ca).strip()): score = 3; status = "correct"; correct += 1
                        else: status = "incorrect"; incorrect += 1
                    except: status = "incorrect"; incorrect += 1
            elif qtype == "Match the Column":
                empty = all(len(ua[r]) == 0 for r in ["A","B","C","D"])
                if empty: unattempted += 1
                else:
                    all_correct = all(set(ua.get(r,[])) == set(ca.get(r,[])) for r in ["A","B","C","D"])
                    any_wrong = any(set(ua.get(r,[])) != set(ca.get(r,[])) and len(ua.get(r,[])) > 0 for r in ["A","B","C","D"])
                    if all_correct: score = 3; status = "correct"; correct += 1
                    elif any_wrong: score = -1; status = "incorrect"; incorrect += 1
                    else: score = sum(1 for r in ["A","B","C","D"] if set(ua.get(r,[])) == set(ca.get(r,[]))); status = "partial"; correct += 1
            total += score
            subj_scores[subj] = subj_scores.get(subj, 0) + score
            details.append({"id": qid, "subject": subj, "type": qtype, "user_response": ua, "correct_answer": ca, "score_earned": score, "status": status, "solution": q.get("solution","")})
        return {"total_score": total, "subject_scores": subj_scores, "correct_count": correct, "incorrect_count": incorrect, "unattempted_count": unattempted, "details": details}

    # WELCOME
    if st.session_state.jee_state == "welcome":
        st.markdown('<div style="text-align: center; margin-bottom: 30px;"><h1 style="font-size: 3rem; background: linear-gradient(135deg, #60a5fa, #3b82f6, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">AS.Developer Test Series</h1><p style="font-size: 1.3rem; color: #94a3b8;">JEE Advanced CBT Simulator with AI-Powered Insights</p></div>', unsafe_allow_html=True)
        _, nc, _ = st.columns([1, 2, 1])
        with nc:
            nv = st.text_input("👤 Your Full Name", value=st.session_state.jee_name, key="jee_name_input")
            st.session_state.jee_name = nv.strip()
        col1, col2 = st.columns([1.2, 1])
        with col1:
            st.markdown('<div class="glass-card"><h3>📝 Exam Guidelines</h3><ul><li><b>Single Correct</b>: +3, -1</li><li><b>Multi Correct</b>: +4 full, +1 partial, -2 wrong</li><li><b>Paragraph Based</b>: +3, -1</li><li><b>Integer Type</b>: +3, 0</li><li><b>Match the Column</b>: +3 full, +1 per row, -1 wrong</li></ul></div>', unsafe_allow_html=True)
        with col2:
            jee_time = st.slider("⏱️ Duration (Hours)", 0.5, 3.0, 3.0, 0.5, key="jee_time")
            jee_length = st.selectbox("📊 Test Length", ["Short (5/subject, 15 total)", "Medium (10/subject, 30 total)", "Full (18/subject, 54 total)"], key="jee_length")
            if "Short" in jee_length: jee_qps = 5
            elif "Medium" in jee_length: jee_qps = 10
            else: jee_qps = 18
            jee_topics = st.text_area("🎯 Custom Chapters (Optional)", key="jee_topics")
            if st.button("🚀 GENERATE & START EXAM", use_container_width=True, key="jee_start"):
                if not st.session_state.jee_name:
                    st.error("⚠️ Enter your name.")
                else:
                    st.session_state.jee_roll = f"AS-{random.randint(1000,9999)}-{datetime.datetime.now().year}"
                    with st.spinner("🚀 Generating paper via Gemini AI..."):
                        paper = jee_generate_questions_api(API_KEY, jee_qps, jee_topics)
                        if paper:
                            st.session_state.jee_fallback = False
                            jee_start_test(paper, jee_time)
                            st.rerun()
                        else:
                            st.session_state.jee_fallback = True
                            jee_start_test(jee_get_fallback_paper(jee_qps), jee_time)
                            st.rerun()

    # TEST
    elif st.session_state.jee_state == "test":
        elapsed = time.time() - st.session_state.jee_start_time
        remaining = st.session_state.jee_time_limit - elapsed
        if remaining <= 0:
            st.session_state.jee_state = "analysis"
            st.rerun()
        qs = st.session_state.jee_questions
        nq = len(qs)
        ci = st.session_state.jee_curr_idx
        cq = qs[ci]
        qid = cq["id"]
        st.markdown(f'<div class="cbt-header"><span class="header-logo">⚡ AS.Developer CBT</span><span class="header-info">Candidate: <b>{st.session_state.jee_name}</b> (Roll: {st.session_state.jee_roll})</span></div>', unsafe_allow_html=True)
        col_main, col_side = st.columns([4.2, 1.2])
        with col_main:
            present_subjs = list(dict.fromkeys([q["subject"] for q in qs]))
            scols = st.columns(len(present_subjs))
            for i, s in enumerate(present_subjs):
                with scols[i]:
                    if st.button(s.upper(), key=f"jee_tab_{s}", use_container_width=True, type="primary" if st.session_state.jee_subject == s else "secondary"):
                        st.session_state.jee_subject = s
                        for idx2, q2 in enumerate(qs):
                            if q2["subject"] == s:
                                st.session_state.jee_curr_idx = idx2
                                if st.session_state.jee_status[q2["id"]] == "unvisited":
                                    st.session_state.jee_status[q2["id"]] = "not_answered"
                                break
                        st.rerun()
            qtype = cq["type"]
            st.markdown(f"### {st.session_state.jee_subject} - Question {ci+1} of {nq}")
            with st.container(border=True):
                if qtype == "Paragraph Based" and cq.get("paragraph_text"):
                    st.markdown("##### 📖 Passage:")
                    st.markdown(cq["paragraph_text"])
                    st.markdown("---")
                st.markdown("##### Question:")
                st.markdown(cq["question_text"])
                st.markdown("---")
                st.markdown("##### Select Response:")
                uv = st.session_state.jee_responses[qid]
                if qtype in ["Single Correct", "Paragraph Based"]:
                    opts = cq.get("options", [])
                    si = None
                    if uv in ["A","B","C","D"]:
                        for ix, o in enumerate(opts):
                            if o.strip().startswith(uv): si = ix; break
                    choice = st.radio("Options:", opts, index=si, key=f"jee_radio_{qid}")
                    if choice:
                        st.session_state.jee_responses[qid] = choice.strip()[0]
                elif qtype == "Multi Correct":
                    opts = cq.get("options", [])
                    sel_letters = list(uv) if uv else []
                    temp = []
                    for o in opts:
                        letter = o.strip()[0]
                        if st.checkbox(o, value=letter in sel_letters, key=f"jee_chk_{qid}_{letter}"):
                            temp.append(letter)
                    st.session_state.jee_responses[qid] = temp
                elif qtype == "Integer Type":
                    tv = st.text_input("Enter numerical answer:", value=str(uv), key=f"jee_txt_{qid}")
                    st.session_state.jee_responses[qid] = tv.strip()
                elif qtype == "Match the Column":
                    for item in cq.get("column_A", []):
                        st.markdown(f"- {item}")
                    for item in cq.get("column_B", []):
                        st.markdown(f"- {item}")
                    st.write("---")
                    hcols = st.columns([1.5, 1, 1, 1, 1, 1])
                    hcols[0].write("")
                    for i, opt in enumerate(["P","Q","R","S","T"]):
                        hcols[i+1].markdown(f"<div style='text-align: center; font-weight: bold;'>{opt}</div>", unsafe_allow_html=True)
                    mr = uv if uv else {"A":[],"B":[],"C":[],"D":[]}
                    for rl in ["A","B","C","D"]:
                        rcols = st.columns([1.5, 1, 1, 1, 1, 1])
                        rcols[0].markdown(f"**({rl})**")
                        new_row = []
                        for ci2, cc in enumerate(["P","Q","R","S","T"]):
                            with rcols[ci2+1]:
                                if st.checkbox("", value=cc in mr.get(rl,[]), key=f"jee_mtx_{qid}_{rl}_{cc}", label_visibility="collapsed"):
                                    new_row.append(cc)
                        mr[rl] = new_row
                    st.session_state.jee_responses[qid] = mr
            # Nav buttons
            cp, cc, cm, cs = st.columns(4)
            with cp:
                if st.button("⬅️ PREVIOUS", use_container_width=True, disabled=(ci==0), key="jee_prev"):
                    st.session_state.jee_curr_idx = ci - 1
                    pq = qs[ci-1]
                    if st.session_state.jee_status[pq["id"]] == "unvisited":
                        st.session_state.jee_status[pq["id"]] = "not_answered"
                    st.session_state.jee_subject = pq["subject"]
                    st.rerun()
            with cc:
                if st.button("🧹 CLEAR", use_container_width=True, key="jee_clear"):
                    if qtype == "Multi Correct": st.session_state.jee_responses[qid] = []
                    elif qtype == "Match the Column": st.session_state.jee_responses[qid] = {"A":[],"B":[],"C":[],"D":[]}
                    else: st.session_state.jee_responses[qid] = ""
                    st.session_state.jee_status[qid] = "not_answered"
                    st.rerun()
            with cm:
                if st.button("🟣 MARK & NEXT", use_container_width=True, key="jee_mark"):
                    ans = st.session_state.jee_responses[qid]
                    has_ans = (isinstance(ans, list) and len(ans) > 0) or (isinstance(ans, dict) and any(len(ans[r]) > 0 for r in ["A","B","C","D"])) or (isinstance(ans, str) and ans != "")
                    st.session_state.jee_status[qid] = "answered_marked" if has_ans else "marked"
                    if ci < nq - 1:
                        st.session_state.jee_curr_idx = ci + 1
                        nxt = qs[ci+1]
                        if st.session_state.jee_status[nxt["id"]] == "unvisited":
                            st.session_state.jee_status[nxt["id"]] = "not_answered"
                        st.session_state.jee_subject = nxt["subject"]
                    st.rerun()
            with cs:
                if st.button("🟢 SAVE & NEXT ➡️", use_container_width=True, key="jee_save"):
                    ans = st.session_state.jee_responses[qid]
                    has_ans = (isinstance(ans, list) and len(ans) > 0) or (isinstance(ans, dict) and any(len(ans[r]) > 0 for r in ["A","B","C","D"])) or (isinstance(ans, str) and ans != "")
                    st.session_state.jee_status[qid] = "answered" if has_ans else "not_answered"
                    if ci < nq - 1:
                        st.session_state.jee_curr_idx = ci + 1
                        nxt = qs[ci+1]
                        if st.session_state.jee_status[nxt["id"]] == "unvisited":
                            st.session_state.jee_status[nxt["id"]] = "not_answered"
                        st.session_state.jee_subject = nxt["subject"]
                    st.rerun()
        with col_side:
            with st.container(border=True):
                st.markdown("#### ⏳ Time")
                st.components.v1.html(f'<div style="font-size: 26px; font-weight: bold; color: #60a5fa; text-align: center; font-family: monospace; background: #0f172a; padding: 10px; border-radius: 8px;" id="jt">--:--:--</div><script>var r={int(remaining)};var d=document.getElementById("jt");function u(){{if(r<=0){{d.innerHTML="TIME UP!";d.style.color="#ef4444";return;}}var h=Math.floor(r/3600);var m=Math.floor((r%3600)/60);var s=r%60;d.innerHTML=(h<10?"0"+h:h)+":"+(m<10?"0"+m:m)+":"+(s<10?"0"+s:s);r--;setTimeout(u,1000);}}u();</script>', height=65)
                st.markdown("---")
                st.markdown(f"**Name:** {st.session_state.jee_name}")
                st.markdown("---")
                sa = sum(1 for v in st.session_state.jee_status.values() if v == "answered")
                sna = sum(1 for v in st.session_state.jee_status.values() if v == "not_answered")
                st.markdown(f"🟢 Answered: {sa} | 🔴 Not Answered: {sna}")
                st.markdown("---")
                jq = st.selectbox("Jump to Q:", range(1, nq+1), index=ci, key="jee_jump")
                if jq - 1 != ci:
                    st.session_state.jee_curr_idx = jq - 1
                    tq = qs[jq - 1]
                    st.session_state.jee_subject = tq["subject"]
                    if st.session_state.jee_status[tq["id"]] == "unvisited":
                        st.session_state.jee_status[tq["id"]] = "not_answered"
                    st.rerun()
                st.markdown("---")
                confirm = st.checkbox("I want to submit.", key="jee_confirm")
                if st.button("🏆 SUBMIT PAPER", type="primary", use_container_width=True, disabled=not confirm, key="jee_submit"):
                    st.session_state.jee_state = "analysis"
                    st.rerun()

    # ANALYSIS
    elif st.session_state.jee_state == "analysis":
        st.markdown('<div style="text-align: center;"><h1 style="font-size: 2.8rem; background: linear-gradient(135deg, #4ad873, #3b82f6, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🏆 Test Results & Analysis</h1></div>', unsafe_allow_html=True)
        results = jee_calc_score()
        ts = results["total_score"]
        ss = results["subject_scores"]
        max_marks = sum(4 if q["type"] == "Multi Correct" else 3 for q in st.session_state.jee_questions)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total", f"{ts}/{max_marks}")
        c2.metric("Physics", ss.get("Physics", 0))
        c3.metric("Chemistry", ss.get("Chemistry", 0))
        c4.metric("Mathematics", ss.get("Mathematics", 0))
        st.markdown(f"✅ Correct: {results['correct_count']} | ❌ Incorrect: {results['incorrect_count']} | ⚪ Unattempted: {results['unattempted_count']}")
        attempts = results["correct_count"] + results["incorrect_count"]
        accuracy = (results["correct_count"] / attempts * 100) if attempts > 0 else 0
        st.markdown(f"**Accuracy: {accuracy:.1f}%**")
        st.markdown("### 🔍 Solutions")
        for idx, item in enumerate(results["details"]):
            oq = st.session_state.jee_questions[idx]
            with st.expander(f"Q{item['id']} [{oq['subject']}] - {oq['type']} - {item['score_earned']} marks"):
                st.markdown(oq["question_text"])
                st.markdown(f"**Your Answer:** {item['user_response']} | **Correct:** {item['correct_answer']}")
                st.markdown("---")
                st.markdown(item["solution"])
        st.markdown("---")
        if st.button("🔄 Take Another Exam", use_container_width=True, key="jee_retake"):
            st.session_state.jee_state = "welcome"
            st.session_state.jee_questions = []
            st.session_state.jee_responses = {}
            st.session_state.jee_status = {}
            st.session_state.jee_chat = []
            st.rerun()


# ══════════════════════════════════════════
# PAGE: AI ASSISTANT
# ══════════════════════════════════════════
elif page == "🤖 AI Assistant":
    st.markdown("""
    <div class="header-box">
        <h1 class="header-title">EduHub AI Companion</h1>
        <p class="header-subtitle">Your personal Class 12 Computer Science, Chemistry, Physics & Mathematics Assistant</p>
    </div>
    """, unsafe_allow_html=True)

    if "ai_messages" not in st.session_state:
        st.session_state.ai_messages = []

    system_instruction = "You are Antigravity-Edu, the AI Tutor in AS.Dev EduHub. Guide Class 12 CS (083) students, solve doubts in Python, MySQL, math, physics, chemistry. Use clean Markdown and LaTeX. Be encouraging and concise."
    client = genai.Client(api_key=API_KEY)

    _, col2 = st.columns([6, 1])
    with col2:
        if st.button("Clear Chat 🧹", use_container_width=True, key="ai_clear"):
            st.session_state.ai_messages = []
            st.rerun()

    if not st.session_state.ai_messages:
        st.session_state.ai_messages.append({"role": "assistant", "content": "Hello! I am your Antigravity-Edu tutor. How can I help you today? 🎓"})
    for msg in st.session_state.ai_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Type your doubt here...", key="ai_input"):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.ai_messages.append({"role": "user", "content": prompt})
        with st.chat_message("assistant"):
            ph = st.empty()
            with st.spinner("AI Tutor thinking..."):
                try:
                    history = [f"{'User' if m['role']=='user' else 'Tutor'}: {m['content']}" for m in st.session_state.ai_messages[:-1]]
                    full = f"System: {system_instruction}\n\nHistory:\n" + "\n".join(history) + f"\nUser: {prompt}\nTutor:"
                    response = client.models.generate_content(model="gemini-2.5-flash", contents=full)
                    ph.markdown(response.text)
                    st.session_state.ai_messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error: {e}")


# ══════════════════════════════════════════
# PAGE: ABOUT PROJECT
# ══════════════════════════════════════════
elif page == "📋 About Project":
    st.markdown("""
    <div class="header-box">
        <h1 class="header-title">About EduHub</h1>
        <p class="header-subtitle">Architecture and Functionality of the AS.Dev Suite</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ### 💻 System Overview
    **AS.Dev EduHub** is a premium Streamlit-based all-in-one educational AI application suite.
    
    ### 🔑 Core Functionalities
    1. **Integrated Single-App Architecture**: All 6 educational tools are hardcoded into a single Streamlit application with seamless sidebar navigation.
    2. **Single API Key Architecture**: Centralizes a secure Gemini API key across all modules.
    3. **AI Companion Backend**: Provides a global educational tutor with mathematical/LaTeX parsing using Google Gemini.
    
    ### 📦 Built-in Modules
    - **NotesIO**: Synthesizes notes, summarizes documents, and engineers code templates.
    - **RevisionIO**: Customizes revision schedules and NCERT checkpoints.
    - **RoadmapIO**: Maps detailed learning tracks with follow-up checkpoints.
    - **JEE Igniter**: Custom 24/7 AI mentor, doubt solver, and study planner.
    - **DailyPractise**: Curates randomized 15-question MCQ worksheets.
    - **JEE Advanced CBT**: Full-featured exam simulator mimicking the JEE Advanced interface.
    """)


# ══════════════════════════════════════════
# PAGE: ABOUT DEVELOPER
# ══════════════════════════════════════════
elif page == "👨‍💻 About Developer":
    st.markdown("""
    <div class="header-box">
        <h1 class="header-title">About Developer</h1>
        <p class="header-subtitle">Creator of AS.Dev EduHub Suite</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="bio-container">
        <h2 style="margin: 0; color: #14b8a6;">Aradhya (AS-Developer-17)</h2>
        <p style="color: #94a3b8; font-size: 1.1rem; margin-top: 5px;">Academic App Architect & Full-Stack Developer</p>
        <p style="color: #cbd5e1; line-height: 1.6; margin-top: 15px;">
            A passionate developer building advanced educational suites, exam preparation engines, and structured note generators. Combining sleek Streamlit interfaces with state-of-the-art AI (Google Gemini) to empower CBSE Class 11/12 students and competitive exam aspirants.
        </p>
        <hr style="border-color: rgba(255,255,255,0.08); margin: 20px 0;">
        <div style="display: flex; gap: 30px;">
            <div>
                <span style="color: #64748b; font-size: 0.85rem; font-weight: bold; text-transform: uppercase;">GitHub Reference:</span><br>
                <span class="profile-link" style="font-size: 1.1rem;">👉 <a href="https://github.com/AS-Developer-17" target="_blank">github.com/AS-Developer-17</a></span>
            </div>
            <div>
                <span style="color: #64748b; font-size: 0.85rem; font-weight: bold; text-transform: uppercase;">Academic Focus:</span><br>
                <span style="font-size: 1.1rem; color: #f8fafc;">CBSE Class 12 CS (083) / IIT JEE Advanced Prep</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
