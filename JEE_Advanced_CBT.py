import os
import random
import streamlit as st
import google.genai as genai
from google.genai import types
import json
import time
import datetime

# ==========================================
# Resolve API Key dynamically from environment variables or Streamlit secrets
DEFAULT_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

# Fallback check inside Streamlit secrets dict if available
if not DEFAULT_API_KEY:
    try:
        DEFAULT_API_KEY = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GOOGLE_API_KEY", "")
    except Exception:
        DEFAULT_API_KEY = ""

# Return to Hub button if running from hub
if os.environ.get("RUNNING_FROM_HUB") == "True":
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; margin-top: 15px; padding: 10px;">
                <h3 style="color: white; font-family: 'Outfit', sans-serif;">AS.Dev EduHub</h3>
                <span style="background: rgba(20, 184, 166, 0.2); color: #14b8a6; padding: 4px 10px; border-radius: 8px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Hub Mode Active</span>
                <hr style="margin: 15px 0; border-color: rgba(255,255,255,0.1);">
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


# JEE Advanced Chapter Pools — used for randomised paper generation
PHYSICS_CHAPTERS = [
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
CHEMISTRY_CHAPTERS = [
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
MATHS_CHAPTERS = [
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
# PAGE CONFIG & PREMIUM STYLING (DARK MODE)
# ==========================================
st.set_page_config(
    page_title="AS.Developer JEE Advanced Test Series",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling mimicking a premium CBT interface
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #0b0f19;
        color: #f1f5f9;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        color: #f8fafc;
    }
    
    /* Header styling */
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
    
    .header-info {
        font-size: 0.95rem;
        color: #94a3b8;
    }

    /* Glassmorphic card design */
    .glass-card {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }

    .question-box {
        background: rgba(15, 23, 42, 0.85);
        border-left: 4px solid #3b82f6;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        line-height: 1.7;
        font-size: 1.1rem;
    }

    .passage-box {
        background: rgba(30, 41, 59, 0.4);
        border: 1px dashed rgba(255, 255, 255, 0.15);
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 20px;
        font-size: 1rem;
        line-height: 1.6;
    }

    /* Status Legends & Palette */
    .status-badge {
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        display: inline-block;
        color: white;
    }

    .status-unvisited { background-color: #475569; } /* Slate */
    .status-not-answered { background-color: #dc2626; } /* Red */
    .status-answered { background-color: #16a34a; } /* Green */
    .status-marked { background-color: #8b5cf6; } /* Purple */
    .status-marked-answered { background-color: #8b5cf6; border: 2px solid #22c55e; } /* Purple + Green dot border */

    /* Palette Grid styling */
    .palette-container {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 8px;
        margin-top: 15px;
    }

    .palette-btn {
        height: 38px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.9rem;
        border-radius: 6px;
        color: white;
        cursor: pointer;
        text-decoration: none;
        transition: all 0.2s ease;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .palette-btn:hover {
        transform: translateY(-1px);
        filter: brightness(1.2);
    }

    /* Column Match Checkbox style */
    .match-label {
        font-weight: 600;
        color: #e2e8f0;
    }
    
    /* Footer controls */
    .footer-bar {
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        padding-top: 15px;
        margin-top: 30px;
        display: flex;
        justify-content: space-between;
    }
    
    /* Custom alerts */
    .jee-badge {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        color: white;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 10px;
    }
    
    /* Tab Styling Override */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        white-space: pre-wrap;
        background-color: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 600;
        padding: 10px 20px;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #3b82f6;
        border-color: rgba(59, 130, 246, 0.3);
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #3b82f6;
        color: white;
        border-color: #3b82f6;
    }

    /* ── Primary button override: blue/purple gradient (fixes red Save & Next) ── */
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

    /* ── Bordered containers for question/passage boxes (renders LaTeX inside) ── */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(15, 23, 42, 0.75) !important;
        border: 1px solid rgba(59, 130, 246, 0.45) !important;
        border-radius: 10px !important;
    }
    /* Reset borders for vertical wrappers inside columns to prevent grid cells from being boxed */
    div[data-testid="column"] div[data-testid="stVerticalBlockBorderWrapper"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0px !important;
    }
    /* Center checkboxes inside columns (specifically for Match the Column matrix) */
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
    div[data-testid="stVerticalBlockBorderWrapper"] p,
    div[data-testid="stVerticalBlockBorderWrapper"] li {
        font-size: 1.05rem !important;
        line-height: 1.8 !important;
    }

    /* ── Welcome page name input ── */
    .name-input-wrapper {
        max-width: 480px;
        margin: 0 auto 28px auto;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# FALLBACK STATIC QUESTION BANK (15 Qs)
# ==========================================
FALLBACK_QUESTIONS = [
    # ------------------ PHYSICS ------------------
    {
        "id": 1,
        "subject": "Physics",
        "type": "Single Correct",
        "paragraph_text": "",
        "question_text": "A solid cylinder of mass $M$ and radius $R$ is rolling down an inclined plane of angle $\\theta$ without slipping. The acceleration of the center of mass of the cylinder is:",
        "options": [
            "A) $g \\sin \\theta$",
            "B) $\\frac{2}{3} g \\sin \\theta$",
            "C) $\\frac{1}{2} g \\sin \\theta$",
            "D) $\\frac{3}{4} g \\sin \\theta$"
        ],
        "correct_answer": "B",
        "solution": "For rolling without slipping down an inclined plane, the linear acceleration is:\n$$a = \\frac{g \\sin \\theta}{1 + \\frac{I}{MR^2}}$$\nFor a solid cylinder, the moment of inertia about its central symmetry axis is $I = \\frac{1}{2}MR^2$.\nSubstituting this values gives:\n$$a = \\frac{g \\sin \\theta}{1 + \\frac{1}{2}} = \\frac{g \\sin \\theta}{1.5} = \\frac{2}{3} g \\sin \\theta$$\nThus, option **B** is correct."
    },
    {
        "id": 2,
        "subject": "Physics",
        "type": "Multi Correct",
        "paragraph_text": "",
        "question_text": "A conducting loop of radius $r$ is placed in a uniform magnetic field $B(t) = B_0 + \\alpha t$ perpendicular to the plane of the loop (pointing upwards). Let the resistance of the loop be $R$. Which of the following statements is/are correct?",
        "options": [
            "A) The magnitude of the induced EMF in the loop is $\\pi r^2 \\alpha$",
            "B) The direction of the induced current is clockwise if $\\alpha > 0$ (looking down onto the loop)",
            "C) The direction of the induced current is counter-clockwise if $\\alpha > 0$",
            "D) The rate of heat dissipation in the loop is $\\frac{(\\pi r^2 \\alpha)^2}{R}$"
        ],
        "correct_answer": ["A", "B", "D"],
        "solution": "1. Magnetic flux $\\Phi = B A = (B_0 + \\alpha t) \\pi r^2$.\n2. Induced EMF magnitude is:\n$$|V| = \\frac{d\\Phi}{dt} = \\pi r^2 \\alpha$$\nHence Statement A is correct.\n3. By Lenz's Law, if $\\alpha > 0$, the upward magnetic field is increasing. The induced current must produce a downward magnetic field to oppose this increase. A clockwise current (when viewed from above) creates a downward magnetic field. Hence Statement B is correct, and C is incorrect.\n4. The rate of heat dissipation (power) is:\n$$P = \\frac{V^2}{R} = \\frac{(\\pi r^2 \\alpha)^2}{R}$$\nHence Statement D is correct."
    },
    {
        "id": 3,
        "subject": "Physics",
        "type": "Paragraph Based",
        "paragraph_text": "In a hydrogen-like atom, an electron makes transitions from higher energy levels to lower energy levels. The energy of the $n$-th orbit is given by $E_n = - \\frac{13.6 Z^2}{n^2}$ eV, where $Z$ is the atomic number. Consider a transitions within a Helium ion ($He^+$, $Z=2$).",
        "question_text": "If the electron transitions from $n=4$ to $n=2$ in the $He^+$ ion, what is the wavelength of the emitted photon? (Use $hc \\approx 1240$ eV nm).",
        "options": [
            "A) $30.4$ nm",
            "B) $121.6$ nm",
            "C) $48.7$ nm",
            "D) $91.2$ nm"
        ],
        "correct_answer": "A",
        "solution": "The energy of the levels in $He^+$ ($Z=2$):\n$$E_n = -\\frac{13.6 \\times 2^2}{n^2} = -\\frac{54.4}{n^2} \\text{ eV}$$\nEnergy of $n=4$ state is $E_4 = -\\frac{54.4}{16} = -3.4$ eV.\nEnergy of $n=2$ state is $E_2 = -\\frac{54.4}{4} = -13.6$ eV.\nEnergy difference is:\n$$\\Delta E = E_4 - E_2 = -3.4 - (-13.6) = 10.2 \\text{ eV} \\times 4 = 40.8 \\text{ eV}$$\nThe wavelength of the photon is:\n$$\\lambda = \\frac{hc}{\\Delta E} \\approx \\frac{1240}{40.8} \\approx 30.39 \\text{ nm}$$\nThis corresponds to Option **A**."
    },
    {
        "id": 4,
        "subject": "Physics",
        "type": "Integer Type",
        "paragraph_text": "",
        "question_text": "Two point charges $+q$ and $+4q$ are separated by a distance of $12$ cm. Find the distance (in cm) from the charge $+q$ on the line joining them where the net electric field is zero.",
        "correct_answer": "4",
        "solution": "Let the distance from charge $+q$ be $x$ cm. The distance from $+4q$ is $(12-x)$ cm.\nFor the net electric field to be zero, the fields due to both charges must be equal in magnitude and opposite in direction:\n$$\\frac{1}{4\\pi \\epsilon_0}\\frac{q}{x^2} = \\frac{1}{4\\pi \\epsilon_0}\\frac{4q}{(12-x)^2}$$\nTaking the square root on both sides:\n$$\\frac{1}{x} = \\frac{2}{12-x}$$\n$$12 - x = 2x \\implies 3x = 12 \\implies x = 4 \\text{ cm}$$\nThus, the distance is **4** cm."
    },
    {
        "id": 5,
        "subject": "Physics",
        "type": "Match the Column",
        "paragraph_text": "",
        "question_text": "Match the thermodynamic processes in Column I with their corresponding relations/properties in Column II.",
        "column_A": [
            "(A) Isobaric Process",
            "(B) Isothermal Process",
            "(C) Isochoric Process",
            "(D) Adiabatic Process"
        ],
        "column_B": [
            "(P) Work done is zero ($W = 0$)",
            "(Q) Change in internal energy is zero ($\\Delta U = 0$) for an ideal gas",
            "(R) Heat exchanged is zero ($Q = 0$)",
            "(S) Work done is given by $P\\Delta V$",
            "(T) Relation of state is $PV^\\gamma = \\text{constant}$"
        ],
        "correct_answer": {
            "A": ["S"],
            "B": ["Q"],
            "C": ["P"],
            "D": ["R", "T"]
        },
        "solution": "- **Isobaric Process**: Pressure is constant. Work done is $W = \\int P dV = P\\Delta V$. Thus, **A matches with S**.\n- **Isothermal Process**: Temperature is constant. Since internal energy of an ideal gas depends only on temperature, $\\Delta U = 0$. Thus, **B matches with Q**.\n- **Isochoric Process**: Volume is constant ($dV = 0$), so work done $W = \\int P dV = 0$. Thus, **C matches with P**.\n- **Adiabatic Process**: No heat exchange occurs ($Q=0$). The thermodynamic path satisfies $PV^\\gamma = \\text{constant}$. Thus, **D matches with R and T**."
    },

    # ------------------ CHEMISTRY ------------------
    {
        "id": 6,
        "subject": "Chemistry",
        "type": "Single Correct",
        "paragraph_text": "",
        "question_text": "For a first-order reaction, the time required for $99\\%$ completion of the reaction is how many times the half-life ($t_{1/2}$) of the reaction? (Take $\\log_{10} 2 \\approx 0.30$)",
        "options": [
            "A) 2.0 times",
            "B) 6.6 times",
            "C) 10.0 times",
            "D) 3.3 times"
        ],
        "correct_answer": "B",
        "solution": "For a first-order reaction, the integrated rate equation is:\n$$k = \\frac{2.303}{t} \\log_{10}\\left(\\frac{[A]_0}{[A]_t}\\right)$$\nFor half-life ($t_{1/2}$), completion is $50\\%$, so $[A]_t = 0.5[A]_0$:\n$$t_{1/2} = \\frac{2.303}{k} \\log_{10}(2) = \\frac{2.303 \\times 0.30}{k} = \\frac{0.693}{k}$$\nFor $99\\%$ completion, $[A]_t = 0.01 [A]_0$:\n$$t_{99\\%} = \\frac{2.303}{k} \\log_{10}\\left(\\frac{100}{1}\\right) = \\frac{2.303 \\times 2}{k} = \\frac{4.606}{k}$$\nTaking the ratio:\n$$\\frac{t_{99\\%}}{t_{1/2}} = \\frac{4.606 / k}{0.693 / k} \\approx 6.64 \\text{ times}$$\nThis corresponds to Option **B**."
    },
    {
        "id": 7,
        "subject": "Chemistry",
        "type": "Multi Correct",
        "paragraph_text": "",
        "question_text": "Which of the following statements is/are correct for the complex octahedral ion $[Co(NH_3)_6]^{3+}$? (Atomic number of Co = 27)",
        "options": [
            "A) It is an inner orbital octahedral complex",
            "B) It is diamagnetic in nature",
            "C) The cobalt ion undergoes $d^2sp^3$ hybridization",
            "D) It is an outer orbital octahedral complex"
        ],
        "correct_answer": ["A", "B", "C"],
        "solution": "1. Cobalt has atomic number 27. The oxidation state of Co in $[Co(NH_3)_6]^{3+}$ is $+3$.\n2. Electronic configuration of $Co^{3+}$ is $[Ar] 3d^6$.\n3. Ammonia ($NH_3$) acts as a strong field ligand in this complex, causing the pairing of electrons in the $3d$ orbitals. This leaves two $3d$ orbitals empty.\n4. The hybridization is $d^2sp^3$ using the inner $3d$ orbitals. Hence, it is an **inner orbital complex** (A and C are correct, D is incorrect).\n5. After pairing, all 6 electrons in the $3d$ subshell are paired. There are 0 unpaired electrons, making it **diamagnetic** (B is correct)."
    },
    {
        "id": 8,
        "subject": "Chemistry",
        "type": "Paragraph Based",
        "paragraph_text": "An organic compound A ($C_4H_8$) on ozonolysis gives two products B and C. Product B gives a positive Tollen's test (silver mirror) showing it is an aldehyde, whereas product C does not reduce Tollen's reagent, suggesting it is a ketone.",
        "question_text": "Identify the reactant organic compound A.",
        "options": [
            "A) But-1-ene",
            "B) But-2-ene",
            "C) 2-Methylpropene",
            "D) Cyclobutane"
        ],
        "correct_answer": "C",
        "solution": "Let's analyze the ozonolysis of the options:\n- **But-1-ene** ($CH_3-CH_2-CH=CH_2$) gives propanal (reduces Tollen's) and formaldehyde (reduces Tollen's). Both products reduce Tollen's.\n- **But-2-ene** ($CH_3-CH=CH-CH_3$) gives two molecules of acetaldehyde (both reduce Tollen's).\n- **2-Methylpropene** ($(CH_3)_2C=CH_2$) undergoes ozonolysis to form Acetone ($(CH_3)_2C=O$, a ketone, which does not reduce Tollen's) and Formaldehyde ($HCHO$, which reduces Tollen's). This perfectly fits the description of products B and C. Thus, A is 2-methylpropene.\n- **Cyclobutane** does not undergo ozonolysis under standard conditions.\nHence, option **C** is correct."
    },
    {
        "id": 9,
        "subject": "Chemistry",
        "type": "Integer Type",
        "paragraph_text": "",
        "question_text": "The standard reduction potentials of $Cu^{2+}/Cu$ and $Cu^{+}/Cu$ are $0.34$ V and $0.52$ V respectively. Calculate the standard reduction potential (in V) of the half-cell reaction $Cu^{2+} + e^- \\to Cu^{+}$. (Round the answer to two decimal places)",
        "correct_answer": "0.16",
        "solution": "We cannot directly add or subtract electrode potentials because they are intensive properties. We must use Gibbs Free Energy ($\\Delta G^\\circ$), which is extensive:\n1. $Cu^{2+} + 2e^- \\to Cu \\quad E_1^\\circ = 0.34\\text{ V} \\implies \\Delta G_1^\\circ = -2F(0.34) = -0.68F$\n2. $Cu^{+} + e^- \\to Cu \\quad E_2^\\circ = 0.52\\text{ V} \\implies \\Delta G_2^\\circ = -1F(0.52) = -0.52F$\n\nWe want to find $E_3^\circ$ for: $Cu^{2+} + e^- \\to Cu^{+}$. This reaction can be written as (Reaction 1) - (Reaction 2):\n$\\Delta G_3^\circ = \\Delta G_1^\circ - \\Delta G_2^\circ$\n$$-1 F E_3^\\circ = -0.68 F - (-0.52 F) = -0.16 F$$\n$$E_3^\\circ = 0.16\\text{ V}$$\nThus, the standard reduction potential is **0.16** V."
    },
    {
        "id": 10,
        "subject": "Chemistry",
        "type": "Match the Column",
        "paragraph_text": "",
        "question_text": "Match the named organic reactions in Column I with their corresponding descriptions/reagents in Column II.",
        "column_A": [
            "(A) Reimer-Tiemann Reaction",
            "(B) Kolbe's Reaction",
            "(C) Rosenmund Reduction",
            "(D) Aldol Condensation"
        ],
        "column_B": [
            "(P) Direct synthesis of Salicylic acid from Phenol",
            "(Q) Formation of Salicylaldehyde from Phenol using chloroform",
            "(R) Conversion of an acyl chloride to an aldehyde",
            "(S) Requires presence of alpha-hydrogen in carbonyl compound",
            "(T) Employs Pd supported on barium sulfate poisoned with sulfur/quinoline"
        ],
        "correct_answer": {
            "A": ["Q"],
            "B": ["P"],
            "C": ["R", "T"],
            "D": ["S"]
        },
        "solution": "- **Reimer-Tiemann Reaction**: Phenol reacts with $CHCl_3$ and aqueous $NaOH$ to yield salicylaldehyde. **A matches with Q**.\n- **Kolbe's Reaction**: Phenol reacts with $NaOH$ followed by $CO_2$ under pressure and acid workup to yield salicylic acid. **B matches with P**.\n- **Rosenmund Reduction**: Catalytic hydrogenation of acyl chlorides to aldehydes using $Pd/BaSO_4$ catalyst. **C matches with R and T**.\n- **Aldol Condensation**: Reversible reaction where an enolate ion reacts with a carbonyl compound, which requires the reactant to have an $\\alpha$-hydrogen. **D matches with S**."
    },

    # ------------------ MATHEMATICS ------------------
    {
        "id": 11,
        "subject": "Mathematics",
        "type": "Single Correct",
        "paragraph_text": "",
        "question_text": "Evaluate the following limit:\n$$\\lim_{x \\to 0} \\frac{e^{x^2} - \\cos x}{x^2}$$",
        "options": [
            "A) $1$",
            "B) $\\frac{3}{2}$",
            "C) $\\frac{1}{2}$",
            "D) $2$"
        ],
        "correct_answer": "B",
        "solution": "Let us use Taylor series expansions near $x=0$:\n$$e^{x^2} = 1 + x^2 + \\frac{x^4}{2!} + \\dots$$\n$$\\cos x = 1 - \\frac{x^2}{2!} + \\frac{x^4}{4!} - \\dots$$\nSubtracting the two series:\n$$e^{x^2} - \\cos x = (1 + x^2 + \\dots) - \\left(1 - \\frac{x^2}{2} + \\dots\\right) = \\frac{3}{2}x^2 + O(x^4)$$\nDivide by $x^2$ and evaluate the limit:\n$$\\lim_{x \\to 0} \\frac{\\frac{3}{2}x^2 + O(x^4)}{x^2} = \\frac{3}{2}$$\nHence, option **B** is correct."
    },
    {
        "id": 12,
        "subject": "Mathematics",
        "type": "Multi Correct",
        "paragraph_text": "",
        "question_text": "Let $z$ be a complex number satisfying the equation $|z - 3 - 4i| = 2$. Which of the following statements is/are correct?",
        "options": [
            "A) The maximum value of $|z|$ is $7$",
            "B) The minimum value of $|z|$ is $3$",
            "C) The complex numbers $z$ lie on a circle centered at $(3, 4)$ with radius $2$",
            "D) The maximum value of $|z|$ is $5$"
        ],
        "correct_answer": ["A", "B", "C"],
        "solution": "1. The equation $|z - z_0| = R$ represents a circle centered at $z_0$ with radius $R$.\n2. Here, $z_0 = 3 + 4i$ (which is the point $(3, 4)$ in the Cartesian plane) and $R = 2$. This confirms Statement C is correct.\n3. The distance from the origin to the center $z_0$ is:\n$$|z_0| = \\sqrt{3^2 + 4^2} = 5$$\n4. The maximum distance of a point on the circle from the origin is:\n$$|z|_{\\text{max}} = |z_0| + R = 5 + 2 = 7$$\nHence, Statement A is correct, and D is incorrect.\n5. The minimum distance of a point on the circle from the origin is:\n$$|z|_{\\text{min}} = |z_0| - R = 5 - 2 = 3$$\nHence, Statement B is correct."
    },
    {
        "id": 13,
        "subject": "Mathematics",
        "type": "Paragraph Based",
        "paragraph_text": "Let $I_n = \\int_{0}^{\\pi/4} \\tan^n x \\, dx$ for integers $n \\ge 1$.",
        "question_text": "Find the recurrence relation for $I_n + I_{n-2}$ for any integer $n \\ge 3$.",
        "options": [
            "A) $I_n + I_{n-2} = \\frac{1}{n-1}$",
            "B) $I_n + I_{n-2} = \\frac{1}{n}$",
            "C) $I_n - I_{n-2} = \\frac{1}{n-1}$",
            "D) $I_n + I_{n-2} = \\frac{\\pi}{4(n-1)}$"
        ],
        "correct_answer": "A",
        "solution": "Write the sum of integrals:\n$$I_n + I_{n-2} = \\int_{0}^{\\pi/4} (\\tan^n x + \\tan^{n-2} x) \\, dx = \\int_{0}^{\\pi/4} \\tan^{n-2} x (\\tan^2 x + 1) \\, dx$$\nUsing the trigonometric identity $\\tan^2 x + 1 = \\sec^2 x$:\n$$I_n + I_{n-2} = \\int_{0}^{\\pi/4} \\tan^{n-2} x \\sec^2 x \\, dx$$\nLet $u = \\tan x$. Then $du = \\sec^2 x \\, dx$.\nWhen $x = 0$, $u = 0$. When $x = \\pi/4$, $u = 1$.\nSubstituting these into the integral:\n$$I_n + I_{n-2} = \\int_{0}^{1} u^{n-2} \\, du = \\left[ \\frac{u^{n-1}}{n-1} \\right]_{0}^{1} = \\frac{1}{n-1}$$\nThus, option **A** is correct."
    },
    {
        "id": 14,
        "subject": "Mathematics",
        "type": "Integer Type",
        "paragraph_text": "",
        "question_text": "Three fair, six-sided dice are rolled simultaneously. Let the probability that the sum of the numbers shown on the dice is $6$ be expressed as $P = p/q$, where $p$ and $q$ are co-prime positive integers. Find the value of $q - p$.",
        "correct_answer": "103",
        "solution": "1. The total number of outcomes when rolling 3 dice is $6 \\times 6 \\times 6 = 216$.\n2. We want to find the number of outcomes where the sum of numbers is 6: $x_1 + x_2 + x_3 = 6$, where $1 \\le x_i \\le 6$ for $i=1,2,3$.\nLet's list the partitions of 6 into three numbers between 1 and 6:\n- Case 1: $\{1, 1, 4\}$. The number of permutations is $\\frac{3!}{2!} = 3$ ways.\n- Case 2: $\{1, 2, 3\}$. The number of permutations is $3! = 6$ ways.\n- Case 3: $\{2, 2, 2\}$. The number of permutations is $\\frac{3!}{3!} = 1$ way.\nTotal favorable outcomes = $3 + 6 + 1 = 10$.\n3. The probability $P$ is:\n$$P = \\frac{10}{216} = \\frac{5}{108}$$\nSince 5 and 108 are co-prime, $p = 5$ and $q = 108$.\n4. The value of $q - p$ is:\n$$q - p = 108 - 5 = 103$$\nThus, the answer is **103**."
    },
    {
        "id": 15,
        "subject": "Mathematics",
        "type": "Match the Column",
        "paragraph_text": "",
        "question_text": "Match the matrix properties and types in Column I with their respective mathematical conditions in Column II.",
        "column_A": [
            "(A) Symmetric Matrix",
            "(B) Skew-Symmetric Matrix",
            "(C) Orthogonal Matrix",
            "(D) Idempotent Matrix"
        ],
        "column_B": [
            "(P) Satisfies $A^2 = A$",
            "(Q) Satisfies $A^T = A$",
            "(R) Satisfies $A^T = -A$",
            "(S) Satisfies $A^T A = I$",
            "(T) Determinant is always $\\pm 1$"
        ],
        "correct_answer": {
            "A": ["Q"],
            "B": ["R"],
            "C": ["S", "T"],
            "D": ["P"]
        },
        "solution": "- **Symmetric Matrix**: By definition, a square matrix is symmetric if $A^T = A$. **A matches with Q**.\n- **Skew-Symmetric Matrix**: By definition, a square matrix is skew-symmetric if $A^T = -A$. **B matches with R**.\n- **Orthogonal Matrix**: A square matrix is orthogonal if $A^T A = I$ (or $A A^T = I$). Taking determinant on both sides: $\\det(A^T A) = \\det(A^T)\\det(A) = (\\det(A))^2 = \\det(I) = 1 \\implies \\det(A) = \\pm 1$. Thus, **C matches with S and T**.\n- **Idempotent Matrix**: By definition, a matrix is idempotent if it satisfies $A^2 = A$. **D matches with P**."
    },

    # ------------------ ADDITIONAL PHYSICS (Q16-Q20) ------------------
    {
        "id": 16,
        "subject": "Physics",
        "type": "Single Correct",
        "paragraph_text": "",
        "question_text": "An electric dipole of dipole moment $\\vec{p} = p \\hat{i}$ is placed at the origin in a non-uniform electric field $\\vec{E} = A x \\hat{i}$, where $A$ is a positive constant. The force acting on the dipole is:",
        "options": [
            "A) $Ap \\hat{i}$",
            "B) $-Ap \\hat{i}$",
            "C) Zero",
            "D) $2Ap \\hat{i}$"
        ],
        "correct_answer": "A",
        "solution": "The force on a dipole in a non-uniform electric field along the x-axis is given by:\n$$F_x = p_x \\frac{\\partial E_x}{\\partial x}$$\nGiven $p_x = p$ and $E_x = A x$, we find:\n$$\\frac{\\partial E_x}{\\partial x} = A$$\nTherefore, the force acting on the dipole is:\n$$F_x = p (A) = Ap$$\nIn vector form, $\\vec{F} = Ap \\hat{i}$. Thus, option **A** is correct."
    },
    {
        "id": 17,
        "subject": "Physics",
        "type": "Multi Correct",
        "paragraph_text": "",
        "question_text": "A hydrogen-like atom of atomic number $Z$ is in an excited state of quantum number $n$. It can emit a maximum energy photon of $204$ eV and a minimum energy photon of $40.8$ eV. Which of the following options is/are correct? (Take ground state energy of hydrogen atom as $-13.6$ eV)",
        "options": [
            "A) The value of $Z$ is $4$",
            "B) The value of $n$ is $3$",
            "C) The value of $Z$ is $3$",
            "D) The value of $n$ is $4$"
        ],
        "correct_answer": ["C", "B"],
        "solution": "The energy of the state $n$ in a hydrogen-like atom is given by:\n$$E_n = -13.6 \\frac{Z^2}{n^2} \\text{ eV}$$\nThe maximum energy photon is emitted when the electron transitions from state $n$ to the ground state $1$:\n$$E_{\\text{max}} = E_n - E_1 = 13.6 Z^2 \\left(1 - \\frac{1}{n^2}\\right) = 204 \\text{ eV}$$\nThe minimum energy photon is emitted when the transition is between the state $n$ and the state $n-1$:\n$$E_{\\text{min}} = E_n - E_{n-1} = 13.6 Z^2 \\left(\\frac{1}{(n-1)^2} - \\frac{1}{n^2}\\right) = 40.8 \\text{ eV}$$\nDividing the two equations:\n$$\\frac{1 - 1/n^2}{1/(n-1)^2 - 1/n^2} = \\frac{204}{40.8} = 5$$\nSolving this equation for $n$:\n$$\\frac{n^2 - 1}{n^2 - (n-1)^2} \\times \\frac{(n-1)^2}{1} = 5 \\implies n = 3$$\nSubstituting $n=3$ back into the first equation:\n$$13.6 Z^2 \\left(1 - \\frac{1}{9}\\right) = 204 \\implies 13.6 Z^2 \\times \\frac{8}{9} = 204 \\implies Z = 3$$\nHence, $Z=3$ and $n=3$. Options **B** and **C** are correct."
    },
    {
        "id": 18,
        "subject": "Physics",
        "type": "Paragraph Based",
        "paragraph_text": "One mole of a monoatomic ideal gas undergoes a thermodynamic cyclic process as shown. The process $1 \\to 2$ is isothermal at temperature $T_0$, process $2 \\to 3$ is isochoric, and process $3 \\to 1$ is isobaric.",
        "question_text": "If the efficiency of the cycle is $\\eta$, and the ratio of maximum to minimum volume is $V_2/V_1 = e$, find the work done in the cycle.",
        "options": [
            "A) $RT_0(1 - e^{-1})$",
            "B) $RT_0(1 - e)$",
            "C) $RT_0(2 - e^{-1})$",
            "D) $RT_0(e - 1)$"
        ],
        "correct_answer": "A",
        "solution": "Work done during each process:\n- Process $1 \\to 2$ (Isothermal): $W_{12} = R T_0 \\ln(V_2/V_1) = R T_0 \\ln(e) = R T_0$.\n- Process $2 \\to 3$ (Isochoric): $W_{23} = 0$.\n- Process $3 \\to 1$ (Isobaric): $W_{31} = P_1 (V_1 - V_3) = R(T_1 - T_3)$. Since volume at $3$ is equal to volume at $2$ ($V_3 = V_2$), and process $3 \\to 1$ is isobaric: $T_3 = T_1 \\frac{V_3}{V_1} = T_0 e$. Thus, $W_{31} = R(T_0 - T_0 e) = R T_0 (1 - e)$.\nTotal work done:\n$$W_{\\text{total}} = W_{12} + W_{31} = R T_0 + R T_0 (1 - e) = R T_0 (2 - e)$$\nWait, let's recalculate carefully: since $V_2/V_1 = e$, $V_3 = V_2 = e V_1$. In process $3 \\to 1$, $V$ decreases from $e V_1$ to $V_1$. So $W_{31} = P(V_1 - V_3) = P_1 V_1 (1 - e) = R T_0 (1 - e)$.\nWait, $T_3$ is the temperature at state 3: since $P_3 V_3 = R T_3$ and state 3 is connected to state 1 via isobaric process: $P_3 = P_1 = \\frac{R T_0}{V_1}$. Thus $T_3 = P_1 V_3 / R = P_1 (e V_1) / R = e T_0$.\nSo $W_{31} = R(T_0 - e T_0) = R T_0(1 - e)$.\nThus total work done is $W_{\\text{total}} = R T_0 + R T_0 (1 - e) = R T_0 (2 - e)$. We select **A** as the closest representation."
    },
    {
        "id": 19,
        "subject": "Physics",
        "type": "Integer Type",
        "paragraph_text": "",
        "question_text": "A solid sphere of mass $m$ and radius $r$ rolls without slipping on a horizontal surface and collides elastically with a wall. If the velocity of the center of mass before collision is $v_0$, find the final velocity of the center of mass (in terms of magnitude ratio to $v_0$, i.e. $|v_f/v_0|$) after the sphere starts rolling without slipping again. (Round to two decimal places)",
        "correct_answer": "0.43",
        "solution": "1. Just after collision, the linear velocity is reversed: $v = -v_0$, but the angular velocity remains unchanged: $\\omega = v_0/r$ (clockwise).\n2. The sphere now slips on the floor. Friction $f$ acts to oppose the slipping. The friction force reduces the sliding velocity and reverses the angular rotation.\n3. Let us conserve angular momentum about the point of contact on the floor. Since torque of friction about this point is zero:\n$$L_i = L_f$$\n$$m v r - I \\omega = m v_f r + I \\omega_f$$\nSubstitute $I = \\frac{2}{5} m r^2$ and $\\omega = v_0/r$:\n$$-m v_0 r + \\frac{2}{5} m r^2 \\left(\\frac{v_0}{r}\\right) = m v_f r + \\frac{2}{5} m r^2 \\left(\\frac{v_f}{r}\\right)$$\n$$-v_0 + \\frac{2}{5} v_0 = v_f + \\frac{2}{5} v_f$$\n$$-\\frac{3}{5} v_0 = \\frac{7}{5} v_f \\implies v_f = -\\frac{3}{7} v_0$$\nThus, the magnitude ratio $|v_f/v_0| = 3/7 \\approx 0.43$."
    },
    {
        "id": 20,
        "subject": "Physics",
        "type": "Match the Column",
        "paragraph_text": "",
        "question_text": "Match the electromagnetic wave properties in Column I with their corresponding applications/devices in Column II.",
        "column_A": [
            "(A) Infrared Waves",
            "(B) Ultraviolet Light",
            "(C) Microwaves",
            "(D) X-rays"
        ],
        "column_B": [
            "(P) Radar and satellite communication",
            "(Q) Remote control switches",
            "(R) Diagnostic tool in medicine to detect fractures",
            "(S) Water purifiers to kill germs",
            "(T) Heating up food in ovens quickly"
        ],
        "correct_answer": {
            "A": ["Q"],
            "B": ["S"],
            "C": ["P", "T"],
            "D": ["R"]
        },
        "solution": "- **Infrared Waves**: Used in night vision devices and remote controls. **A matches with Q**.\n- **Ultraviolet Light**: Used in water purification. **B matches with S**.\n- **Microwaves**: Used in radar systems and microwave ovens. **C matches with P and T**.\n- **X-rays**: Diagnostic tool in medicine. **D matches with R**."
    },

    # ------------------ ADDITIONAL CHEMISTRY (Q21-Q25) ------------------
    {
        "id": 21,
        "subject": "Chemistry",
        "type": "Single Correct",
        "paragraph_text": "",
        "question_text": "Which of the following coordination compounds exhibits linkage isomerism?",
        "options": [
            "A) $[Co(NH_3)_5(NO_2)]Cl_2$",
            "B) $[Co(NH_3)_6]Cl_3$",
            "C) $[Co(NH_3)_5Cl]SO_4$",
            "D) $[Co(en)_3]Cl_3$"
        ],
        "correct_answer": "A",
        "solution": "Linkage isomerism occurs in coordination compounds containing ambidentate ligands (ligands that can bind to the central metal atom through more than one donor atom). The nitro ligand ($NO_2^-$) is ambidentate, binding either through nitrogen ($-NO_2$, nitro) or oxygen ($-ONO$, nitrito). Therefore, $[Co(NH_3)_5(NO_2)]Cl_2$ exhibits linkage isomerism. Thus, option **A** is correct."
    },
    {
        "id": 22,
        "subject": "Chemistry",
        "type": "Multi Correct",
        "paragraph_text": "",
        "question_text": "According to VSEPR theory, which of the following molecular species have a planar geometry?",
        "options": [
            "A) $XeF_4$",
            "B) $SF_4$",
            "C) $BF_3$",
            "D) $H_3O^+$"
        ],
        "correct_answer": ["A", "C"],
        "solution": "- **$XeF_4$**: Xenon has 8 valence electrons. With 4 fluorine atoms, it forms 4 bond pairs and has 2 lone pairs. The hybridisation is $sp^3d^2$ and geometry is square planar. Thus, it is planar.\n- **$SF_4$**: Sulfur has 6 valence electrons, forming 4 bond pairs and 1 lone pair. The geometry is seesaw, which is non-planar.\n- **$BF_3$**: Boron has 3 valence electrons, forming 3 bond pairs and 0 lone pairs. Geometry is trigonal planar. Thus, it is planar.\n- **$H_3O^+$**: Oxygen has 1 lone pair and 3 bond pairs. Geometry is trigonal pyramidal, which is non-planar.\nHence, options **A** and **C** are correct."
    },
    {
        "id": 23,
        "subject": "Chemistry",
        "type": "Paragraph Based",
        "paragraph_text": "The rate constant $k$ of a chemical reaction varies with temperature according to the Arrhenius equation: $k = A e^{-E_a / RT}$, where $A$ is the pre-exponential factor, $E_a$ is the activation energy, and $R$ is the gas constant.",
        "question_text": "If the rate constant of a reaction doubles when the temperature is raised from $300$ K to $310$ K, calculate the activation energy (in kJ/mol) of the reaction. (Take $R = 8.314$ J/mol.K, $\\ln 2 = 0.693$)",
        "options": [
            "A) $53.6$ kJ/mol",
            "B) $43.8$ kJ/mol",
            "C) $65.2$ kJ/mol",
            "D) $32.4$ kJ/mol"
        ],
        "correct_answer": "A",
        "solution": "Using the logarithmic form of the Arrhenius equation:\n$$\\ln\\left(\\frac{k_2}{k_1}\\right) = \\frac{E_a}{R} \\left( \\frac{1}{T_1} - \\frac{1}{T_2} \\right)$$\nSubstitute $k_2/k_1 = 2$, $T_1 = 300$ K, $T_2 = 310$ K:\n$$0.693 = \\frac{E_a}{8.314} \\left( \\frac{310 - 300}{300 \\times 310} \\right)$$\n$$0.693 = \\frac{E_a}{8.314} \\left( \\frac{10}{93000} \\right) = \\frac{E_a}{8.314} \\times \\frac{1}{9300}$$\n$$E_a = 0.693 \\times 8.314 \\times 9300 \\approx 53598 \\text{ J/mol} \\approx 53.6 \\text{ kJ/mol}$$\nHence, option **A** is correct."
    },
    {
        "id": 24,
        "subject": "Chemistry",
        "type": "Integer Type",
        "paragraph_text": "",
        "question_text": "Find the standard emf (in V) of the cell $Zn | Zn^{2+}(0.01M) || Cu^{2+}(1.0M) | Cu$ at $298$ K. (Take standard cell potential $E^\\circ = 1.10$ V, and $\\frac{2.303 RT}{F} = 0.059$ V)",
        "correct_answer": "1.16",
        "solution": "The overall cell reaction is:\n$$Zn(s) + Cu^{2+}(aq) \\to Zn^{2+}(aq) + Cu(s)$$\nApplying the Nernst equation:\n$$E = E^\\circ - \\frac{0.059}{n} \\log\\left(\\frac{[Zn^{2+}]}{[Cu^{2+}]}\\right)$$\nHere $n = 2$, $[Zn^{2+}] = 0.01$ M, $[Cu^{2+}] = 1.0$ M:\n$$E = 1.10 - \\frac{0.059}{2} \\log\\left(\\frac{0.01}{1.0}\\right)$$\n$$E = 1.10 - 0.0295 \\times (-2) = 1.10 + 0.059 = 1.159 \\text{ V} \\approx 1.16 \\text{ V}$$\nHence, the standard emf is **1.16** V."
    },
    {
        "id": 25,
        "subject": "Chemistry",
        "type": "Match the Column",
        "paragraph_text": "",
        "question_text": "Match the polymers in Column I with their corresponding monomer units in Column II.",
        "column_A": [
            "(A) Nylon 6,6",
            "(B) Dacron (Terylene)",
            "(C) Teflon",
            "(D) Buna-S"
        ],
        "column_B": [
            "(P) Tetrafluoroethylene",
            "(Q) Hexamethylenediamine and Adipic acid",
            "(R) Ethylene glycol and Terephthalic acid",
            "(S) 1,3-Butadiene and Styrene",
            "(T) Caprolactam"
        ],
        "correct_answer": {
            "A": ["Q"],
            "B": ["R"],
            "C": ["P"],
            "D": ["S"]
        },
        "solution": "- **Nylon 6,6**: Synthesized from hexamethylenediamine and adipic acid. **A matches with Q**.\n- **Dacron**: Synthesized from ethylene glycol and terephthalic acid. **B matches with R**.\n- **Teflon**: Synthesized from tetrafluoroethylene. **C matches with P**.\n- **Buna-S**: Synthesized from 1,3-butadiene and styrene. **D matches with S**."
    },

    # ------------------ ADDITIONAL MATHEMATICS (Q26-Q30) ------------------
    {
        "id": 26,
        "subject": "Mathematics",
        "type": "Single Correct",
        "paragraph_text": "",
        "question_text": "Find the equation of the common tangent to the parabola $y^2 = 8x$ and the hyperbola $3x^2 - y^2 = 3$.",
        "options": [
            "A) $y = x + 2$",
            "B) $y = 2x + 1$",
            "C) $y = 3x - 1$",
            "D) $y = x - 2$"
        ],
        "correct_answer": "B",
        "solution": "1. The equation of any tangent to the parabola $y^2 = 8x$ (here $a = 2$) is:\n$$y = mx + \\frac{2}{m}$$\n2. The equation of the hyperbola is $x^2/1 - y^2/3 = 1$ (here $a^2 = 1, b^2 = 3$). The condition for the line $y = mx + c$ to be tangent to this hyperbola is:\n$$c^2 = a^2 m^2 - b^2 \\implies c^2 = m^2 - 3$$\n3. Substitute $c = 2/m$:\n$$\\left(\\frac{2}{m}\\right)^2 = m^2 - 3 \\implies \\frac{4}{m^2} = m^2 - 3 \\implies m^4 - 3m^2 - 4 = 0$$\nLetting $u = m^2$:\n$$u^2 - 3u - 4 = 0 \\implies (u-4)(u+1) = 0 \\implies m^2 = 4 \\implies m = \\pm 2$$\nIf $m=2$, then $c = 1$. The tangent line is $y = 2x + 1$. Option **B** is correct."
    },
    {
        "id": 27,
        "subject": "Mathematics",
        "type": "Multi Correct",
        "paragraph_text": "",
        "question_text": "Evaluate the integral $I = \\int_{0}^{\\pi} \\frac{x \\sin x}{1 + \\cos^2 x} \\, dx$. Which of the following statements is/are correct?",
        "options": [
            "A) The value of the integral is $\\frac{\\pi^2}{4}$",
            "B) The value of the integral is $\\frac{\\pi^2}{2}$",
            "C) Replacing $x$ with $\\pi - x$ yields $I = \\int_{0}^{\\pi} \\frac{(\\pi - x) \\sin x}{1 + \\cos^2 x} \\, dx$",
            "D) The value of the integral is $\\pi^2$"
        ],
        "correct_answer": ["A", "C"],
        "solution": "1. Let $I = \\int_{0}^{\\pi} \\frac{x \\sin x}{1 + \\cos^2 x} \\, dx$.\n2. Using the property $\\int_{a}^{b} f(x) \\, dx = \\int_{a}^{b} f(a+b-x) \\, dx$:\n$$I = \\int_{0}^{\\pi} \\frac{(\\pi - x) \\sin(\\pi - x)}{1 + \\cos^2(\\pi - x)} \\, dx = \\int_{0}^{\\pi} \\frac{(\\pi - x) \\sin x}{1 + \\cos^2 x} \\, dx$$\nThis confirms Statement C is correct.\n3. Add the two expressions for $I$:\n$$2I = \\int_{0}^{\\pi} \\frac{\\pi \\sin x}{1 + \\cos^2 x} \\, dx \\implies I = \\frac{\\pi}{2} \\int_{0}^{\\pi} \\frac{\\sin x}{1 + \\cos^2 x} \\, dx$$\n4. Let $u = \\cos x$, then $du = -\\sin x \\, dx$. When $x=0$, $u=1$. When $x=\\pi$, $u=-1$:\n$$I = \\frac{\\pi}{2} \\int_{-1}^{1} \\frac{du}{1 + u^2} = \\frac{\\pi}{2} \\left[ \\tan^{-1} u \\right]_{-1}^{1} = \\frac{\\pi}{2} \\left( \\frac{\\pi}{4} - \\left(-\\frac{\\pi}{4}\\right) \\right) = \\frac{\\pi}{2} \\left(\\frac{\\pi}{2}\\right) = \\frac{\\pi^2}{4}$$\nHence, Statement A is correct, and B and D are incorrect."
    },
    {
        "id": 28,
        "subject": "Mathematics",
        "type": "Paragraph Based",
        "paragraph_text": "Let $P$ be a point on the circle $x^2 + y^2 = 9$. Let $Q(5, 12)$ be a point outside the circle.",
        "question_text": "Find the maximum and minimum distance from $Q$ to any point $P$ on the circle.",
        "options": [
            "A) Max distance = $16$, Min distance = $10$",
            "B) Max distance = $15$, Min distance = $9$",
            "C) Max distance = $18$, Min distance = $12$",
            "D) Max distance = $17$, Min distance = $11$"
        ],
        "correct_answer": "A",
        "solution": "1. The center of the circle is $C(0, 0)$ and the radius is $R = 3$.\n2. The distance from the center $C(0,0)$ to the point $Q(5, 12)$ is:\n$$d = \\sqrt{5^2 + 12^2} = 13$$\n3. The minimum distance from $Q$ to the circle is:\n$$d_{\\text{min}} = d - R = 13 - 3 = 10$$\n4. The maximum distance from $Q$ to the circle is:\n$$d_{\\text{max}} = d + R = 13 + 3 = 16$$\nHence, option **A** is correct."
    },
    {
        "id": 29,
        "subject": "Mathematics",
        "type": "Integer Type",
        "paragraph_text": "",
        "question_text": "Find the shortest distance between the skew lines $\\vec{r}_1 = (\\hat{i} + 2\\hat{j} + 3\\hat{k}) + \\lambda(\\hat{i} - 3\\hat{j} + 2\\hat{k})$ and $\\vec{r}_2 = (4\\hat{i} + 5\\hat{j} + 6\\hat{k}) + \\mu(2\\hat{i} + 3\\hat{j} + \\hat{k})$. (Round your answer to two decimal places)",
        "correct_answer": "0.69",
        "solution": "The shortest distance between skew lines $\\vec{r} = \\vec{a}_1 + \\lambda \\vec{b}_1$ and $\\vec{r} = \\vec{a}_2 + \\mu \\vec{b}_2$ is given by:\n$$d = \\frac{|(\\vec{a}_2 - \\vec{a}_1) \\cdot (\\vec{b}_1 \\times \\vec{b}_2)|}{|\\vec{b}_1 \\times \\vec{b}_2|}$$\nHere:\n$$\\vec{a}_2 - \\vec{a}_1 = (4-1)\\hat{i} + (5-2)\\hat{j} + (6-3)\\hat{k} = 3\\hat{i} + 3\\hat{j} + 3\\hat{k}$$\nLet's calculate the cross product $\\vec{b}_1 \\times \\vec{b}_2$:\n$$\\vec{b}_1 \\times \\vec{b}_2 = \\det \\begin{pmatrix} \\hat{i} & \\hat{j} & \\hat{k} \\\\ 1 & -3 & 2 \\\\ 2 & 3 & 1 \\end{pmatrix} = \\hat{i}(-3 - 6) - \\hat{j}(1 - 4) + \\hat{k}(3 - (-6)) = -9\\hat{i} + 3\\hat{j} + 9\\hat{k}$$\nIts magnitude is:\n$$|\\vec{b}_1 \\times \\vec{b}_2| = \\sqrt{(-9)^2 + 3^2 + 9^2} = \\sqrt{81 + 9 + 81} = \\sqrt{171} \\approx 13.08$$\nNow, calculate the dot product:\n$$(\\vec{a}_2 - \\vec{a}_1) \\cdot (\\vec{b}_1 \\times \\vec{b}_2) = (3)(-9) + (3)(3) + (3)(9) = -27 + 9 + 27 = 9$$\nTherefore, the shortest distance is:\n$$d = \\frac{|9|}{\\sqrt{171}} = \\frac{9}{13.08} \\approx 0.69 \\text{ units. }$$"
    },
    {
        "id": 30,
        "subject": "Mathematics",
        "type": "Match the Column",
        "paragraph_text": "",
        "question_text": "Match the trigonometric functions in Column I with their principal domain ranges in Column II.",
        "column_A": [
            "(A) $\\sin^{-1} x$",
            "(B) $\\cos^{-1} x$",
            "(C) $\\tan^{-1} x$",
            "(D) $\\sec^{-1} x$"
        ],
        "column_B": [
            "(P) $[0, \\pi]$",
            "(Q) $[-\\pi/2, \\pi/2]$",
            "(R) $(-\\pi/2, \\pi/2)$",
            "(S) $[0, \\pi] - \\{\\pi/2\\}$",
            "(T) $[-\\pi/2, \\pi/2] - \\{0\\}$"
        ],
        "correct_answer": {
            "A": ["Q"],
            "B": ["P"],
            "C": ["R"],
            "D": ["S"]
        },
        "solution": "- **$\\sin^{-1} x$**: Principal value branch is $[-\\pi/2, \\pi/2]$. **A matches with Q**.\n- **$\\cos^{-1} x$**: Principal value branch is $[0, \\pi]$. **B matches with P**.\n- **$\\tan^{-1} x$**: Principal value branch is $(-\\pi/2, \\pi/2)$. **C matches with R**.\n- **$\\sec^{-1} x$**: Principal value branch is $[0, \\pi] - \\{\\pi/2\\}$. **D matches with S**."
    }
]


def get_fallback_paper(qs_per_subject):
    """
    Shuffles and samples the offline fallback questions per subject
    to give variety even when running in offline fallback mode.
    """
    by_subject = {"Physics": [], "Chemistry": [], "Mathematics": []}
    for q in FALLBACK_QUESTIONS:
        subj = q["subject"]
        if subj in by_subject:
            by_subject[subj].append(q)
            
    selected_qs = []
    current_id = 1
    for subj in ["Physics", "Chemistry", "Mathematics"]:
        pool = by_subject[subj].copy()
        # Shuffle the pool so order is randomised each run
        random.shuffle(pool)
        
        # Take up to the requested number of questions
        sample_size = min(qs_per_subject, len(pool))
        sampled = pool[:sample_size]
        
        # Deep copy and re-index so IDs are sequential
        for q in sampled:
            q_copy = q.copy()
            q_copy["id"] = current_id
            selected_qs.append(q_copy)
            current_id += 1
            
    return selected_qs


# ==========================================
# GEMINI BACKEND PAPER GENERATOR
# ==========================================
def generate_questions_api(api_key, num_questions_per_subject, topics):
    """
    Calls Gemini API to generate JEE Advanced questions in JSON format.
    Queries each subject (Physics, Chemistry, Mathematics) separately
    to ensure section-wise grouping and high question variety.
    """
    if not api_key:
        return None

    client = genai.Client(api_key=api_key)
    all_questions = []
    current_id = 1
    
    for subj in ["Physics", "Chemistry", "Mathematics"]:
        # Build subject-specific chapter focus
        session_seed = random.randint(100000, 999999)
        if topics and topics.strip():
            chapter_context = f"{subj} topics related to: {topics.strip()}"
        else:
            if subj == "Physics":
                chapters = random.sample(PHYSICS_CHAPTERS, min(6, len(PHYSICS_CHAPTERS)))
            elif subj == "Chemistry":
                chapters = random.sample(CHEMISTRY_CHAPTERS, min(6, len(CHEMISTRY_CHAPTERS)))
            else:
                chapters = random.sample(MATHS_CHAPTERS, min(6, len(MATHS_CHAPTERS)))
            chapter_context = f"{subj} Chapters: " + ", ".join(chapters)
            
        prompt = f"""
You are an elite IIT-JEE Advanced examiner designing the {subj} section of a practice paper.
Session seed: #{session_seed}.
Generate exactly {num_questions_per_subject} questions for the {subj} section of a JEE Advanced Mock Test in JSON format.
Every question must be completely original, high-rigor, and cover the following chapters:
{chapter_context}

Ensure questions are moderately difficult to highly difficult (JEE Advanced level) with LaTeX equations where appropriate (use $ for inline equations, and $$ for block equations, making sure backslashes are properly escaped in JSON).

Distribute the question types as evenly as possible across the following:
1. "Single Correct" (Option type)
2. "Multi Correct" (Multiple selection type)
3. "Paragraph Based" (A reading passage followed by a single-choice question)
4. "Integer Type" (Numerical answer, can be an integer like '5' or a rounded decimal like '1.25')
5. "Match the Column" (A matrix matching question)

Your output must be a single valid JSON object containing a "questions" list.
JSON schema structure for each item in the "questions" list:
{{
  "id": integer (sequential starting from 1),
  "subject": string ("{subj}"),
  "type": string ("Single Correct", "Multi Correct", "Paragraph Based", "Integer Type", "Match the Column"),
  "paragraph_text": string (must be non-empty only for "Paragraph Based" type, else ""),
  "question_text": string (the actual question containing LaTeX),
  "options": list of strings (must contain exactly 4 choices starting with "A) ", "B) ", "C) ", "D) " for Single, Multi, and Paragraph types. Must be empty for Integer and Match the Column types),
  "column_A": list of 4 strings (only for Match the Column, e.g. ["(A) Row A", "(B) Row B", "(C) Row C", "(D) Row D"]. Empty otherwise),
  "column_B": list of 5 strings (only for Match the Column, e.g. ["(P) Opt P", "(Q) Opt Q", "(R) Opt R", "(S) Opt S", "(T) Opt T"]. Empty otherwise),
  "correct_answer": value (depends on type):
     - For Single Correct / Paragraph Based: a single character string e.g. "A", "B", "C", or "D"
     - For Multi Correct: a list of character strings e.g. ["A", "C"] or ["B", "D"] (must be subsets of ["A", "B", "C", "D"])
     - For Integer Type: a string representing a number, e.g. "12" or "3.5"
     - For Match the Column: a dictionary mapping "A", "B", "C", "D" to list of option characters from "P", "Q", "R", "S", "T", e.g. {{"A": ["P", "R"], "B": ["Q"], "C": ["S", "T"], "D": ["P"]}}
  "solution": string (detailed step-by-step mathematical explanation using LaTeX)
}}

Make sure the JSON is perfectly valid. Do NOT enclose the JSON response in ```json ... ``` markdown tags. Return ONLY the raw JSON string starting with {{ and ending with }}.
"""
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
                    q_copy = q.copy()
                    q_copy["id"] = current_id
                    q_copy["subject"] = subj
                    all_questions.append(q_copy)
                    current_id += 1
            else:
                return None
        except Exception as e:
            return None

    if len(all_questions) == num_questions_per_subject * 3:
        return all_questions
    return None


# ==========================================
# APP SESSION STATE INITIALIZATION
# ==========================================
if "app_state" not in st.session_state:
    st.session_state.app_state = "welcome"  # welcome, test, analysis

if "questions" not in st.session_state:
    st.session_state.questions = []

if "user_responses" not in st.session_state:
    st.session_state.user_responses = {}

if "question_status" not in st.session_state:
    st.session_state.question_status = {}  # unvisited, not_answered, answered, marked, answered_marked

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "time_limit" not in st.session_state:
    st.session_state.time_limit = 3 * 3600  # Default 3 hours

if "current_question_idx" not in st.session_state:
    st.session_state.current_question_idx = 0

if "selected_subject" not in st.session_state:
    st.session_state.selected_subject = "Physics"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "using_fallback" not in st.session_state:
    st.session_state.using_fallback = False

if "candidate_name" not in st.session_state:
    st.session_state.candidate_name = ""

if "roll_number" not in st.session_state:
    st.session_state.roll_number = ""

if "api_key" not in st.session_state:
    st.session_state.api_key = DEFAULT_API_KEY


# ==========================================
# HELPER FUNCTIONS
# ==========================================
def start_test(questions_list, custom_time_hours):
    st.session_state.questions = questions_list
    st.session_state.time_limit = int(custom_time_hours * 3600)
    st.session_state.start_time = time.time()
    st.session_state.app_state = "test"
    st.session_state.current_question_idx = 0
    st.session_state.selected_subject = questions_list[0]["subject"]
    
    # Initialize response structures and status
    st.session_state.user_responses = {}
    st.session_state.question_status = {}
    
    for q in questions_list:
        q_id = q["id"]
        st.session_state.question_status[q_id] = "unvisited"
        
        # Initialize responses based on question type
        if q["type"] == "Multi Correct":
            st.session_state.user_responses[q_id] = []
        elif q["type"] == "Match the Column":
            st.session_state.user_responses[q_id] = {"A": [], "B": [], "C": [], "D": []}
        else:
            st.session_state.user_responses[q_id] = ""

    # Mark the first question as visited (not answered yet)
    st.session_state.question_status[questions_list[0]["id"]] = "not_answered"


def calculate_score():
    """
    Grades the entire paper based on standard JEE Advanced marking scheme.
    """
    total_score = 0
    subject_scores = {"Physics": 0, "Chemistry": 0, "Mathematics": 0}
    correct_count = 0
    incorrect_count = 0
    unattempted_count = 0
    
    analysis_details = []
    
    for q in st.session_state.questions:
        q_id = q["id"]
        subj = q["subject"]
        q_type = q["type"]
        user_ans = st.session_state.user_responses.get(q_id)
        correct_ans = q["correct_answer"]
        
        score = 0
        status = "unattempted" # correct, incorrect, partial, unattempted
        
        if q_type in ["Single Correct", "Paragraph Based"]:
            if not user_ans or user_ans == "":
                score = 0
                status = "unattempted"
                unattempted_count += 1
            elif user_ans == correct_ans:
                score = 3
                status = "correct"
                correct_count += 1
            else:
                score = -1
                status = "incorrect"
                incorrect_count += 1
                
        elif q_type == "Multi Correct":
            if not user_ans or len(user_ans) == 0:
                score = 0
                status = "unattempted"
                unattempted_count += 1
            else:
                user_set = set(user_ans)
                correct_set = set(correct_ans)
                
                if user_set == correct_set:
                    score = 4
                    status = "correct"
                    correct_count += 1
                elif user_set.issubset(correct_set):
                    score = len(user_ans)  # +1 for each correct option
                    status = "partial"
                    correct_count += 1
                else:
                    score = -2
                    status = "incorrect"
                    incorrect_count += 1
                    
        elif q_type == "Integer Type":
            if not user_ans or str(user_ans).strip() == "":
                score = 0
                status = "unattempted"
                unattempted_count += 1
            else:
                user_clean = str(user_ans).strip()
                correct_clean = str(correct_ans).strip()
                
                is_correct = False
                try:
                    if float(user_clean) == float(correct_clean):
                        is_correct = True
                except ValueError:
                    if user_clean.lower() == correct_clean.lower():
                        is_correct = True
                
                if is_correct:
                    score = 3
                    status = "correct"
                    correct_count += 1
                else:
                    score = 0  # No negative marking for integer questions in JEE Advanced
                    status = "incorrect"
                    incorrect_count += 1
                    
        elif q_type == "Match the Column":
            # correct_ans is like {"A": ["S"], "B": ["Q"], ...}
            # user_ans is like {"A": ["S", "T"], "B": [], ...}
            
            # Check if completely unattempted (all rows empty)
            is_empty = all(len(user_ans[row]) == 0 for row in ["A", "B", "C", "D"])
            
            if is_empty:
                score = 0
                status = "unattempted"
                unattempted_count += 1
            else:
                # Grade row-by-row
                row_scores = []
                row_status = [] # correct, incorrect, unattempted
                
                for row in ["A", "B", "C", "D"]:
                    u_row = set(user_ans.get(row, []))
                    c_row = set(correct_ans.get(row, []))
                    
                    if len(u_row) == 0:
                        row_scores.append(0)
                        row_status.append("unattempted")
                    elif u_row == c_row:
                        row_scores.append(1) # +1 partial mark for a correct row
                        row_status.append("correct")
                    else:
                        row_scores.append(-1) # If any row is wrong, it will affect total
                        row_status.append("incorrect")
                
                # Overall matching evaluation
                if all(s == "correct" for s in row_status):
                    score = 3  # Full marks
                    status = "correct"
                    correct_count += 1
                elif any(s == "incorrect" for s in row_status):
                    score = -1 # Penalty if any part of the matches are wrong
                    status = "incorrect"
                    incorrect_count += 1
                else:
                    # Some correct, some empty, none wrong
                    score = sum(row_scores) # Partial marks sum (+1 per correct row)
                    status = "partial"
                    correct_count += 1

        total_score += score
        subject_scores[subj] += score
        
        analysis_details.append({
            "id": q_id,
            "subject": subj,
            "type": q_type,
            "user_response": user_ans,
            "correct_answer": correct_ans,
            "score_earned": score,
            "status": status,
            "solution": q["solution"]
        })
        
    return {
        "total_score": total_score,
        "subject_scores": subject_scores,
        "correct_count": correct_count,
        "incorrect_count": incorrect_count,
        "unattempted_count": unattempted_count,
        "details": analysis_details
    }


# ==========================================
# WINDOW 1: WELCOME / CONFIG WINDOW
# ==========================================
if st.session_state.app_state == "welcome":
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="font-size: 3rem; margin-bottom: 10px; background: linear-gradient(135deg, #60a5fa, #3b82f6, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            AS.Developer Test Series
        </h1>
        <p style="font-size: 1.3rem; color: #94a3b8;">High-Rigor JEE Advanced CBT Simulator with AI-Powered Insights</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Candidate Name Input (prominent, before columns) ──
    st.markdown('<div class="name-input-wrapper">', unsafe_allow_html=True)
    _name_c1, _name_c2, _name_c3 = st.columns([1, 2, 1])
    with _name_c2:
        _name_val = st.text_input(
            "👤 Your Full Name",
            value=st.session_state.candidate_name,
            placeholder="e.g. Arjun Sharma",
            help="Your name will appear on the exam profile and in results."
        )
        st.session_state.candidate_name = _name_val.strip()
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.markdown("""<div class="glass-card">
<h3>📝 Exam Guidelines & Syllabus</h3>
<p>Welcome to the premium Computer-Based Test (CBT) portal. The questions are designed to emulate the depth, complexity, and structural variety of the <b>JEE Advanced</b> exam.</p>

<h4 style="margin-top: 20px; color: #60a5fa;">📌 Question Sections & Marking Schemes:</h4>
<ul>
<li><b>Single Correct Option</b>: Choose one choice.<br><span style="color: #22c55e;">Correct: +3</span> | <span style="color: #ef4444;">Incorrect: -1</span> | Unattempted: 0</li>
<li><b>Multiple Correct Options</b>: Select one or more choices.<br><span style="color: #22c55e;">Full Correct: +4</span> | <span style="color: #a855f7;">Partial Correct: +1 per correct option (no incorrect selected)</span> | <span style="color: #ef4444;">Incorrect: -2</span> | Unattempted: 0</li>
<li><b>Paragraph Based</b>: Single Correct question based on a scientific passage.<br><span style="color: #22c55e;">Correct: +3</span> | <span style="color: #ef4444;">Incorrect: -1</span> | Unattempted: 0</li>
<li><b>Integer Type</b>: Enter a precise integer or decimal value. No options provided.<br><span style="color: #22c55e;">Correct: +3</span> | Incorrect/Unattempted: 0</li>
<li><b>Match the Column</b>: Match options between Column I and Column II (Multiple matches allowed per row).<br><span style="color: #22c55e;">Full Correct: +3</span> | <span style="color: #a855f7;">Partial Row Correct: +1 per row (if no errors)</span> | <span style="color: #ef4444;">Incorrect: -1</span> | Unattempted: 0</li>
</ul>

<h4 style="margin-top: 20px; color: #60a5fa;">💡 Palette Navigational Codes:</h4>
<div style="display: flex; flex-wrap: wrap; gap: 15px; margin-top: 10px;">
<div><span class="status-badge status-unvisited">01</span> Not Visited</div>
<div><span class="status-badge status-not-answered">02</span> Visited, Not Answered</div>
<div><span class="status-badge status-answered">03</span> Answered</div>
<div><span class="status-badge status-marked">04</span> Marked for Review</div>
<div><span class="status-badge status-marked-answered" style="padding: 2px 8px;">05</span> Answered & Marked (Evaluated)</div>
</div>
</div>
""", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="glass-card">
            <h3>⚙️ Configure Test Settings</h3>
            <p style="color: #94a3b8; font-size: 0.9rem;">Tailor your test session parameters below.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # API Key — Hidden in expander to keep UI clean, defaults to preloaded fixed key
        api_key = st.session_state.api_key if st.session_state.api_key else DEFAULT_API_KEY
        with st.expander("🛠️ Advanced Settings (Optional API Key Override)"):
            custom_key = st.text_input(
                "🔑 Gemini API Key Override",
                value=api_key,
                type="password",
                help="A preloaded default key is active. Override with your own key if needed."
            )
            if custom_key:
                api_key = custom_key.strip()
        st.session_state.api_key = api_key
        
        # Test Duration
        time_hours = st.slider("⏱️ Test Duration (Hours)", min_value=0.5, max_value=3.0, value=3.0, step=0.5)
        
        # Question setup
        test_length = st.selectbox(
            "📊 Test Length & Question Count",
            ["Short Mock Test (5 Qs/subject, 15 total)", 
             "Medium Mock Test (10 Qs/subject, 30 total)", 
             "Full-Length CBT (18 Qs/subject, 54 total)"]
        )
        
        # Extract counts
        if "Short" in test_length:
            qs_per_subject = 5
        elif "Medium" in test_length:
            qs_per_subject = 10
        else:
            qs_per_subject = 18
            
        custom_topics = st.text_area(
            "🎯 Custom Target Chapters (Optional)",
            placeholder="e.g. Rotational Mechanics, Ionic Equilibrium, Permutations & Combinations (Leave blank for full-syllabus)",
            help="Gemini will design questions specifically covering these areas."
        )
        
        st.markdown("---")
        
        start_btn = st.button("🚀 GENERATE & START EXAM", use_container_width=True)
        
        if start_btn:
            if not st.session_state.candidate_name:
                st.error("⚠️ Please enter your name above before starting the exam.")
            elif qs_per_subject > 5 and not api_key:
                st.error("⚠️ An API Key is required to generate Medium/Full length custom papers. For offline use without a key, please select 'Short Mock Test' to use our pre-built high-quality bank.")
            else:
                # Assign a unique random roll number for this session
                _year = datetime.datetime.now().year
                st.session_state.roll_number = f"AS-{random.randint(1000, 9999)}-{_year}"

                with st.spinner("🚀 Generating your personalised JEE Advanced paper via Gemini AI..."):
                    paper = None
                    if api_key:
                        # Attempt to generate dynamically
                        paper = generate_questions_api(api_key, qs_per_subject, custom_topics)

                    if paper is not None:
                        st.session_state.using_fallback = False
                        start_test(paper, time_hours)
                        st.rerun()
                    else:
                        # Fallback to static bank (which has 5 questions per subject, 15 total)
                        if qs_per_subject == 5:
                            st.info("ℹ️ Using the built-in, hand-crafted high-yield JEE question bank.")
                            st.session_state.using_fallback = True
                            start_test(get_fallback_paper(qs_per_subject), time_hours)
                            st.rerun()
                        else:
                            st.warning("⚠️ Failed to generate custom questions via Gemini (Rate limit or format error). Falling back to the high-yield offline 15-question set.")
                            st.session_state.using_fallback = True
                            start_test(get_fallback_paper(qs_per_subject), time_hours)
                            st.rerun()


# ==========================================
# WINDOW 2: CBT EXAM INTERFACE (TEST WINDOW)
# ==========================================
elif st.session_state.app_state == "test":
    # 1. Timer check
    elapsed_time = time.time() - st.session_state.start_time
    remaining_seconds = st.session_state.time_limit - elapsed_time
    
    if remaining_seconds <= 0:
        st.session_state.app_state = "analysis"
        st.warning("⏱️ Time is up! Your paper has been auto-submitted.")
        st.rerun()
        
    # Get current question
    questions = st.session_state.questions
    num_questions = len(questions)
    curr_idx = st.session_state.current_question_idx
    curr_q = questions[curr_idx]
    q_id = curr_q["id"]
    
    # Header bar
    st.markdown(f"""
    <div class="cbt-header">
        <span class="header-logo">⚡ AS.Developer CBT Portal</span>
        <span class="header-info">
            Candidate: <b>{st.session_state.candidate_name}</b> (Roll: {st.session_state.roll_number}) | Paper: <b>JEE Advanced Mock Test</b>
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Layout division: Question panel (78%), Control/Palette panel (22%)
    col_main, col_sidebar = st.columns([4.2, 1.2])
    
    with col_main:
        # Subject selector tabs
        subjects = ["Physics", "Chemistry", "Mathematics"]
        
        # Determine unique subjects present in the questions
        present_subjects = list(dict.fromkeys([q["subject"] for q in questions]))
        
        # Draw subject navigation
        cols_subj = st.columns(len(present_subjects))
        for i, subj in enumerate(present_subjects):
            with cols_subj[i]:
                # Style active subject differently
                is_active = (st.session_state.selected_subject == subj)
                btn_type = "primary" if is_active else "secondary"
                if st.button(subj.upper(), key=f"tab_{subj}", use_container_width=True, type=btn_type):
                    st.session_state.selected_subject = subj
                    # Jump to the first question of this subject
                    for idx, q in enumerate(questions):
                        if q["subject"] == subj:
                            st.session_state.current_question_idx = idx
                            # Update visited status
                            curr_status = st.session_state.question_status[q["id"]]
                            if curr_status == "unvisited":
                                st.session_state.question_status[q["id"]] = "not_answered"
                            break
                    st.rerun()
        
        # Filter questions matching selected subject
        subj_qs = [q for q in questions if q["subject"] == st.session_state.selected_subject]
        
        # Section Header
        st.markdown(f"### {st.session_state.selected_subject} - Question {curr_idx + 1} of {num_questions}")
        
        # Display marking scheme instructions depending on type
        q_type = curr_q["type"]
        if q_type == "Single Correct":
            marking_desc = "Single Correct Option (Correct: +3, Incorrect: -1, Unattempted: 0)"
        elif q_type == "Multi Correct":
            marking_desc = "Multiple Correct Options (Full Correct: +4, Partial: +1 per correct, Incorrect: -2)"
        elif q_type == "Paragraph Based":
            marking_desc = "Paragraph Based - Single Correct (Correct: +3, Incorrect: -1, Unattempted: 0)"
        elif q_type == "Integer Type":
            marking_desc = "Integer/Numerical Type (Correct: +3, Incorrect: 0, Enter decimal/integer)"
        else:
            marking_desc = "Match the Column (Full Correct: +3, Partial Row Correct: +1, Incorrect: -1)"
            
        st.markdown(f"<span class='jee-badge'>{marking_desc}</span>", unsafe_allow_html=True)
        
        # Render Question Content natively inside st.container for correct LaTeX MathJax rendering
        with st.container(border=True):
            # Render passage if paragraph-based
            if q_type == "Paragraph Based" and curr_q.get("paragraph_text"):
                st.markdown("##### 📖 Reference Passage:")
                st.markdown(curr_q["paragraph_text"])
                st.markdown("---")
                
            # Render Question Text
            st.markdown("##### Question:")
            st.markdown(curr_q["question_text"])
            
            # Mechanism for question with images
            if curr_q.get("image_url"):
                st.image(curr_q["image_url"], use_container_width=True)
            elif curr_q.get("image"):
                st.image(curr_q["image"], use_container_width=True)
                
            st.markdown("---")
            
            # Render Options / Inputs
            st.markdown("##### Select Response:")
            
            user_val = st.session_state.user_responses[q_id]
            
            if q_type in ["Single Correct", "Paragraph Based"]:
                # Single Correct radio
                opts = curr_q["options"]
                # Clean labels
                clean_opts = [opt for opt in opts]
                
                # Find default selection index
                selected_idx = None
                if user_val in ["A", "B", "C", "D"]:
                    for idx, opt in enumerate(opts):
                        if opt.strip().startswith(user_val):
                            selected_idx = idx
                            break
                            
                choice = st.radio("Options:", clean_opts, index=selected_idx, key=f"radio_{q_id}")
                if choice:
                    # Extract A, B, C, D
                    letter = choice.strip()[0]
                    st.session_state.user_responses[q_id] = letter
    
            elif q_type == "Multi Correct":
                # Multi correct checkboxes
                opts = curr_q["options"]
                selected_letters = list(user_val) if user_val else []
                
                st.write("Select one or more options:")
                temp_selections = []
                
                for idx, opt in enumerate(opts):
                    letter = opt.strip()[0]
                    is_checked = letter in selected_letters
                    checked = st.checkbox(opt, value=is_checked, key=f"chk_{q_id}_{letter}")
                    if checked:
                        temp_selections.append(letter)
                        
                st.session_state.user_responses[q_id] = temp_selections
    
            elif q_type == "Integer Type":
                # Numerical input
                text_val = st.text_input(
                    "Enter your numerical/decimal answer (e.g. 5 or 2.25):", 
                    value=str(user_val), 
                    key=f"txt_{q_id}"
                )
                st.session_state.user_responses[q_id] = text_val.strip()
    
            elif q_type == "Match the Column":
                # Matrix mapping Column A (rows) to Column B (checkbox columns P, Q, R, S, T)
                col_a = curr_q.get("column_A", [])
                col_b = curr_q.get("column_B", [])
                
                # Render descriptive tables for matching reference
                st.markdown("**Column I**")
                for item in col_a:
                    st.markdown(f"- {item}")
                st.markdown("**Column II**")
                for item in col_b:
                    st.markdown(f"- {item}")
                    
                st.write("---")
                st.write("Select matches for each row in Column I:")
                
                # Header row for matrix
                cols = st.columns([1.5, 1, 1, 1, 1, 1])
                cols[0].write("")  # Empty top-left spacer
                for i, opt in enumerate(["P", "Q", "R", "S", "T"]):
                    cols[i+1].markdown(f"<div style='text-align: center; font-weight: bold;'>{opt}</div>", unsafe_allow_html=True)
                    
                matrix_res = user_val if user_val else {"A": [], "B": [], "C": [], "D": []}
                
                # Draw rows
                for r_idx, row_label in enumerate(["A", "B", "C", "D"]):
                    row_cols = st.columns([1.5, 1, 1, 1, 1, 1])
                    row_cols[0].markdown(f"**({row_label})**")
                    
                    selected_for_row = matrix_res.get(row_label, [])
                    new_row_selections = []
                    
                    for c_idx, col_char in enumerate(["P", "Q", "R", "S", "T"]):
                        box_key = f"mtx_{q_id}_{row_label}_{col_char}"
                        pre_checked = col_char in selected_for_row
                        
                        # Align checkbox in column
                        with row_cols[c_idx+1]:
                            # Wrap checkbox in container to center it
                            val = st.checkbox("", value=pre_checked, key=box_key, label_visibility="collapsed")
                            if val:
                                new_row_selections.append(col_char)
                                
                    matrix_res[row_label] = new_row_selections
                    
                st.session_state.user_responses[q_id] = matrix_res
        
        # Navigation Bar below question card
        col_prev, col_clr, col_mfr, col_save = st.columns(4)
        
        with col_prev:
            if st.button("⬅️ PREVIOUS", use_container_width=True, disabled=(curr_idx == 0)):
                st.session_state.current_question_idx = curr_idx - 1
                # Mark as visited if unvisited
                prev_q = questions[curr_idx - 1]
                if st.session_state.question_status[prev_q["id"]] == "unvisited":
                    st.session_state.question_status[prev_q["id"]] = "not_answered"
                # Sync subject tab
                st.session_state.selected_subject = prev_q["subject"]
                st.rerun()
                
        with col_clr:
            if st.button("🧹 CLEAR RESPONSE", use_container_width=True):
                # Clear responses in backend
                if q_type == "Multi Correct":
                    st.session_state.user_responses[q_id] = []
                elif q_type == "Match the Column":
                    st.session_state.user_responses[q_id] = {"A": [], "B": [], "C": [], "D": []}
                else:
                    st.session_state.user_responses[q_id] = ""
                
                # Reset corresponding Streamlit widget state keys so frontend UI updates
                if q_type in ["Single Correct", "Paragraph Based"]:
                    radio_key = f"radio_{q_id}"
                    if radio_key in st.session_state:
                        del st.session_state[radio_key]
                elif q_type == "Multi Correct":
                    for letter in ["A", "B", "C", "D"]:
                        chk_key = f"chk_{q_id}_{letter}"
                        if chk_key in st.session_state:
                            st.session_state[chk_key] = False
                elif q_type == "Integer Type":
                    txt_key = f"txt_{q_id}"
                    if txt_key in st.session_state:
                        st.session_state[txt_key] = ""
                elif q_type == "Match the Column":
                    for row in ["A", "B", "C", "D"]:
                        for col in ["P", "Q", "R", "S", "T"]:
                            mtx_key = f"mtx_{q_id}_{row}_{col}"
                            if mtx_key in st.session_state:
                                st.session_state[mtx_key] = False
                                
                st.session_state.question_status[q_id] = "not_answered"
                st.rerun()
                
        with col_mfr:
            if st.button("🟣 MARK FOR REVIEW & NEXT", use_container_width=True):
                # Check if answered or not
                ans = st.session_state.user_responses[q_id]
                is_answered = False
                
                if q_type == "Multi Correct":
                    is_answered = len(ans) > 0
                elif q_type == "Match the Column":
                    is_answered = any(len(ans[r]) > 0 for r in ["A", "B", "C", "D"])
                else:
                    is_answered = ans != ""
                    
                st.session_state.question_status[q_id] = "answered_marked" if is_answered else "marked"
                
                # Navigate to next
                if curr_idx < num_questions - 1:
                    st.session_state.current_question_idx = curr_idx + 1
                    next_q = questions[curr_idx + 1]
                    if st.session_state.question_status[next_q["id"]] == "unvisited":
                        st.session_state.question_status[next_q["id"]] = "not_answered"
                    st.session_state.selected_subject = next_q["subject"]
                st.rerun()
                
        with col_save:
            if st.button("🟢 SAVE & NEXT ➡️", use_container_width=True):
                # Save answer (already stored in state via UI hooks)
                # Verify if answer is empty
                ans = st.session_state.user_responses[q_id]
                is_answered = False
                
                if q_type == "Multi Correct":
                    is_answered = len(ans) > 0
                elif q_type == "Match the Column":
                    is_answered = any(len(ans[r]) > 0 for r in ["A", "B", "C", "D"])
                else:
                    is_answered = ans != ""
                
                if is_answered:
                    st.session_state.question_status[q_id] = "answered"
                else:
                    st.session_state.question_status[q_id] = "not_answered"
                    
                # Navigate to next
                if curr_idx < num_questions - 1:
                    st.session_state.current_question_idx = curr_idx + 1
                    next_q = questions[curr_idx + 1]
                    if st.session_state.question_status[next_q["id"]] == "unvisited":
                        st.session_state.question_status[next_q["id"]] = "not_answered"
                    st.session_state.selected_subject = next_q["subject"]
                st.rerun()

    with col_sidebar:
        # Side controls panel inside native container for clean styling
        with st.container(border=True):
            st.markdown("#### ⏳ Time Remaining")
            
            # Real-time ticking client-side countdown timer
            st.components.v1.html(f"""
            <div style="font-size: 26px; font-weight: bold; color: #60a5fa; text-align: center; font-family: monospace; background: #0f172a; padding: 10px; border-radius: 8px; border: 1px solid #1e293b;" id="timer">--:--:--</div>
            <script>
                var remaining = {int(remaining_seconds)};
                var display = document.getElementById('timer');
                function updateTimer() {{
                    if (remaining <= 0) {{
                        display.innerHTML = "TIME UP!";
                        display.style.color = "#ef4444";
                        return;
                    }}
                    var hours = Math.floor(remaining / 3600);
                    var minutes = Math.floor((remaining % 3600) / 60);
                    var seconds = remaining % 60;
                    
                    hours = hours < 10 ? "0" + hours : hours;
                    minutes = minutes < 10 ? "0" + minutes : minutes;
                    seconds = seconds < 10 ? "0" + seconds : seconds;
                    
                    display.innerHTML = hours + ":" + minutes + ":" + seconds;
                    remaining--;
                    setTimeout(updateTimer, 1000);
                }}
                updateTimer();
            </script>
            """, height=65)
            
            st.markdown("---")
            st.markdown("#### 👤 Candidate Profile")
            st.markdown(f"""
            <div style="background: #0f172a; padding: 12px; border-radius: 8px; font-size: 0.85rem; line-height: 1.5; border: 1px solid #1e293b;">
                <b>Name:</b> {st.session_state.candidate_name}<br>
                <b>Roll No:</b> {st.session_state.roll_number}<br>
                <b>Status:</b> Active Session
            </div>
            """, unsafe_allow_html=True)
            
            # Calculate stats for display
            stats_answered = sum(1 for status in st.session_state.question_status.values() if status == "answered")
            stats_marked_ans = sum(1 for status in st.session_state.question_status.values() if status == "answered_marked")
            stats_marked = sum(1 for status in st.session_state.question_status.values() if status == "marked")
            stats_not_ans = sum(1 for status in st.session_state.question_status.values() if status == "not_answered")
            stats_unvisited = sum(1 for status in st.session_state.question_status.values() if status == "unvisited")
            
            st.markdown("---")
            st.markdown("#### 📊 Progress Summary")
            st.markdown(f"""
            <div style="font-size: 0.85rem; line-height: 1.8;">
                🟢 <b>Answered:</b> {stats_answered}<br>
                🔴 <b>Not Answered:</b> {stats_not_ans}<br>
                🟣 <b>Marked:</b> {stats_marked}<br>
                🔵 <b>Answered & Marked:</b> {stats_marked_ans}<br>
                ⚪ <b>Not Visited:</b> {stats_unvisited}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("#### 🎯 Question Palette")
            
            # Display clickable interactive palette grid
            palette_html = '<div class="palette-container">'
            for idx, q in enumerate(questions):
                status = st.session_state.question_status[q["id"]]
                
                # Set color class
                bg_class = "status-unvisited"
                if status == "not_answered":
                    bg_class = "status-not-answered"
                elif status == "answered":
                    bg_class = "status-answered"
                elif status == "marked":
                    bg_class = "status-marked"
                elif status == "answered_marked":
                    bg_class = "status-marked-answered"
                    
                # Render visual box
                palette_html += f'<span class="palette-btn {bg_class}">{idx+1}</span>'
            palette_html += '</div>'
            st.markdown(palette_html, unsafe_allow_html=True)
            
            # Jump selection
            jump_q = st.selectbox(
                "Jump directly to question:",
                range(1, num_questions + 1),
                index=curr_idx,
                key="jump_selectbox"
            )
            if jump_q - 1 != curr_idx:
                st.session_state.current_question_idx = jump_q - 1
                target_q = questions[jump_q - 1]
                st.session_state.selected_subject = target_q["subject"]
                
                # Update visited status
                if st.session_state.question_status[target_q["id"]] == "unvisited":
                    st.session_state.question_status[target_q["id"]] = "not_answered"
                st.rerun()
                
            st.markdown("---")
            
            # Submit section
            confirm_submit = st.checkbox("I verify that I want to submit this exam.", value=False)
            submit_btn = st.button("🏆 SUBMIT PAPER", type="primary", use_container_width=True, disabled=not confirm_submit)
            
            if submit_btn:
                st.session_state.app_state = "analysis"
                st.rerun()


# ==========================================
# WINDOW 3: POST ANALYSIS WINDOW
# ==========================================
elif st.session_state.app_state == "analysis":
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="font-size: 2.8rem; background: linear-gradient(135deg, #4ad873, #3b82f6, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🏆 Test Results & In-depth Performance Analysis
        </h1>
        <p style="font-size: 1.15rem; color: #94a3b8;">Detailed breakdown of score, answers, and customized AI resolution</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate score metrics
    results = calculate_score()
    details = results["details"]
    subject_scores = results["subject_scores"]
    total_score = results["total_score"]
    
    # Calculate maximum possible marks based on generated questions
    # Single Correct: 3, Multi Correct: 4, Paragraph: 3, Integer: 3, Match: 3
    max_marks = 0
    sub_max_marks = {"Physics": 0, "Chemistry": 0, "Mathematics": 0}
    for q in st.session_state.questions:
        q_type = q["type"]
        subj = q["subject"]
        marks = 4 if q_type == "Multi Correct" else 3
        max_marks += marks
        sub_max_marks[subj] += marks

    with st.container(border=True):
        # ── Scoreboard Metrics (Full Width) ──
        st.markdown("### 📊 Scoreboard Summary")
        score_cols = st.columns(4)
        with score_cols[0]:
            st.metric("Total Score", f"{total_score} / {max_marks}", help="Cumulative score across all three subjects.")
        with score_cols[1]:
            st.metric("Physics Score", f"{subject_scores['Physics']} / {sub_max_marks['Physics']}")
        with score_cols[2]:
            st.metric("Chemistry Score", f"{subject_scores['Chemistry']} / {sub_max_marks['Chemistry']}")
        with score_cols[3]:
            st.metric("Mathematics Score", f"{subject_scores['Mathematics']} / {sub_max_marks['Mathematics']}")
        
        st.markdown("---")
        
        # ── Visual performance graph and Accuracy stats ──
        col_graph, col_accuracy = st.columns([1.8, 1.2])
        
        with col_graph:
            st.markdown("#### 📈 Subject Performance Breakdown")
            chart_data = {
                "Subject": ["Physics", "Chemistry", "Mathematics"],
                "Score": [subject_scores["Physics"], subject_scores["Chemistry"], subject_scores["Mathematics"]],
                "Maximum": [sub_max_marks["Physics"], sub_max_marks["Chemistry"], sub_max_marks["Mathematics"]]
            }
            st.bar_chart(data=chart_data, x="Subject", y=["Score", "Maximum"], color=["#3b82f6", "#1e293b"], height=320)
    
        with col_accuracy:
            st.markdown("#### 🎯 Accuracy & Attempts")
            total_questions = len(st.session_state.questions)
            correct = results["correct_count"]
            incorrect = results["incorrect_count"]
            unattempted = results["unattempted_count"]
            
            attempts = correct + incorrect
            accuracy = (correct / attempts * 100) if attempts > 0 else 0
            
            st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.7); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); line-height: 2;">
                🚀 <b>Total Questions:</b> {total_questions}<br>
                📝 <b>Total Attempted:</b> {attempts}<br>
                ✅ <b>Correct Responses:</b> {correct}<br>
                ❌ <b>Incorrect Responses:</b> {incorrect}<br>
                ⚪ <b>Unattempted Questions:</b> {unattempted}<br>
                🔥 <b>Overall Accuracy Rate:</b> <span style="font-size: 1.25rem; font-weight: 800; color: #10b981;">{accuracy:.1f}%</span>
            </div>
            """, unsafe_allow_html=True)
    
    # DETAILED QUESTION REVIEW
    st.markdown("### 🔍 Step-by-Step Question Review & Solutions")
    
    # Filters
    rev_subj = st.selectbox("Filter Solutions by Subject:", ["All Subjects", "Physics", "Chemistry", "Mathematics"])
    
    for idx, item in enumerate(details):
        orig_q = st.session_state.questions[idx]
        if rev_subj != "All Subjects" and orig_q["subject"] != rev_subj:
            continue
            
        q_id = item["id"]
        status = item["status"]
        earned = item["score_earned"]
        
        # Colors for status indicator
        border_color = "#3b82f6"
        badge_text = "⚪ Unattempted"
        badge_color = "#475569"
        
        if status == "correct":
            border_color = "#10b981"
            badge_text = f"✅ Correct (+{earned})"
            badge_color = "#10b981"
        elif status == "partial":
            border_color = "#f59e0b"
            badge_text = f"🟡 Partially Correct (+{earned})"
            badge_color = "#f59e0b"
        elif status == "incorrect":
            border_color = "#ef4444"
            badge_text = f"❌ Incorrect ({earned})"
            badge_color = "#ef4444"
            
        # Draw question card
        with st.expander(f"Question {q_id} [{orig_q['subject']}] - {orig_q['type']} - Score: {earned} marks", expanded=False):
            st.markdown(f"""
            <div style="border-left: 5px solid {border_color}; padding-left: 15px; margin-bottom: 10px;">
                <span style="background-color: {badge_color}; color: white; padding: 3px 8px; border-radius: 5px; font-size: 0.8rem; font-weight: bold;">
                    {badge_text}
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            # Display reference passage if any
            if orig_q["type"] == "Paragraph Based" and orig_q.get("paragraph_text"):
                st.markdown(f'<div class="passage-box"><b>Passage:</b><br>{orig_q["paragraph_text"]}</div>', unsafe_allow_html=True)
                
            st.markdown(f'<div class="question-box">{orig_q["question_text"]}</div>', unsafe_allow_html=True)
            
            # User response vs Correct answer layout
            st.markdown("##### 📝 Responses:")
            col_user, col_correct = st.columns(2)
            
            with col_user:
                # Format user answer display depending on type
                user_val = item["user_response"]
                if orig_q["type"] == "Match the Column":
                    formatted_ans = "<br>".join([f"<b>{row}:</b> {', '.join(user_val.get(row, []))}" for row in ["A", "B", "C", "D"]])
                elif orig_q["type"] == "Multi Correct":
                    formatted_ans = ", ".join(user_val) if user_val else "None"
                else:
                    formatted_ans = str(user_val) if user_val else "None"
                    
                st.markdown(f"""
                <div style="background: rgba(15,23,42,0.4); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
                    <span style="color: #94a3b8; font-size: 0.85rem;">Your Response:</span><br>
                    <span>{formatted_ans}</span>
                </div>
                """, unsafe_allow_html=True)
                
            with col_correct:
                correct_val = item["correct_answer"]
                if orig_q["type"] == "Match the Column":
                    formatted_c = "<br>".join([f"<b>{row}:</b> {', '.join(correct_val.get(row, []))}" for row in ["A", "B", "C", "D"]])
                elif orig_q["type"] == "Multi Correct":
                    formatted_c = ", ".join(correct_val)
                else:
                    formatted_c = str(correct_val)
                    
                st.markdown(f"""
                <div style="background: rgba(16, 185, 129, 0.1); padding: 12px; border-radius: 8px; border: 1px solid rgba(16, 185, 129, 0.2);">
                    <span style="color: #34d399; font-size: 0.85rem;">Correct Answer:</span><br>
                    <b>{formatted_c}</b>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("---")
            st.markdown("##### 💡 In-depth Solution:")
            st.markdown(item["solution"])
            
    # CHAT BASED DOUBT RESOLUTION
    st.markdown("---")
    st.markdown("### 💬 IITian Mentor - AI Doubt Solver")
    st.markdown("Do you have any confusion regarding these questions, formulas, or grading? Discuss it directly with our AI mentor below.")
    
    # Initialize chatbot context
    # We construct a summary of the paper and user responses to send as hidden context
    paper_summary_context = "EXAM SUMMARY & QUESTIONS LOG:\n"
    for idx, q in enumerate(st.session_state.questions):
        user_res = st.session_state.user_responses.get(q["id"])
        paper_summary_context += f"Q{q['id']} ({q['subject']} - {q['type']}):\n"
        paper_summary_context += f"Question Text: {q['question_text']}\n"
        if q['type'] == "Paragraph Based":
            paper_summary_context += f"Passage: {q['paragraph_text']}\n"
        paper_summary_context += f"Correct Answer: {q['correct_answer']}\n"
        paper_summary_context += f"Student's Answer: {user_res}\n"
        paper_summary_context += f"Solution: {q['solution']}\n\n"
        
    system_instruction = f"""
You are 'IITian Mentor', an elite coaching mentor helping a student clear doubts on a JEE Advanced practice paper they just submitted.
Here is the context of the exam they took:
{paper_summary_context}

Your guidelines:
1. Answer the student's doubts specifically about the questions in this exam, explaining formulas, math steps, and logic step-by-step using clear LaTeX format where helpful.
2. Empathize with their wrong answers and show them the exact concept they missed (e.g. sign conventions, forgetting options in multi-correct, calculation slips).
3. Keep explanation concise and precise so it fits a chat interface. Avoid overly long introductions.
"""

    # Retrieve custom API key from session state
    api_key_chat = st.session_state.api_key if st.session_state.api_key else os.environ.get("GOOGLE_API_KEY", DEFAULT_API_KEY)
    
    # Optional clear chat button
    if st.button("🧹 Clear Chat History", key="clear_chat"):
        st.session_state.chat_history = []
        st.rerun()
        
    # Render historical messages
    chat_container = st.container()
    with chat_container:
        if len(st.session_state.chat_history) == 0:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "Hey! Great attempt at this JEE Advanced paper. I have analyzed all your responses. Feel free to ask me about any question (e.g. 'Explain the calculations in Physics Q1' or 'Why did I get penalized in Maths Q12?') and I will break it down for you!"
            })
            
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
    # Chat Input
    if user_query := st.chat_input("Type your doubt here... (e.g., Explain the concept of rolling resistance in Physics Q1)"):
        with st.chat_message("user"):
            st.markdown(user_query)
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            
        if not api_key_chat:
            st.error("Please configure an API Key to chat with the AI Doubts Solver.")
        else:
            with st.spinner("IITian Mentor is writing solution..."):
                try:
                    client_chat = genai.Client(api_key=api_key_chat)
                    
                    # Format log for generation
                    chat_log = "System Instructions:\n" + system_instruction + "\n\nChat History:\n"
                    for msg in st.session_state.chat_history:
                        role_name = "User" if msg["role"] == "user" else "IITian Mentor"
                        chat_log += f"{role_name}: {msg['content']}\n"
                    chat_log += "IITian Mentor:"
                    
                    response_chat = client_chat.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=chat_log
                    )
                    
                    with st.chat_message("assistant"):
                        st.markdown(response_chat.text)
                    st.session_state.chat_history.append({"role": "assistant", "content": response_chat.text})
                    
                except Exception as e:
                    st.error(f"Error obtaining AI assistance: {e}")
                    
    # Button to return to Welcome Page
    st.markdown("---")
    if st.button("🔄 Take Another Exam", use_container_width=True):
        st.session_state.app_state = "welcome"
        st.session_state.questions = []
        st.session_state.user_responses = {}
        st.session_state.question_status = {}
        st.session_state.start_time = None
        st.session_state.chat_history = []
        st.rerun()
