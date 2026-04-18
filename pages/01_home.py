# Window 1 - Home Page 
# =============================================================
# pages/01_home.py — Window 1: Home Page
# Purpose: Create mindset shift using real statistics.
# No API calls. No session checks. Pure static content.
# =============================================================

import streamlit as st

st.set_page_config(
    page_title="SkillDrift — Are You Ready?",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide sidebar navigation on home page
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {display: none;}
    .block-container {padding-top: 2rem;}
    .stat-card {
        background: linear-gradient(135deg, #1A1D27 0%, #16192A 100%);
        border: 1px solid #2D3250;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        margin: 0.5rem 0;
    }
    .stat-number {
        font-size: 4rem;
        font-weight: 900;
        color: #E74C3C;
        line-height: 1;
    }
    .stat-label {
        font-size: 1.1rem;
        color: #BDC3C7;
        margin-top: 0.5rem;
    }
    .stat-source {
        font-size: 0.75rem;
        color: #7F8C8D;
        margin-top: 0.5rem;
        font-style: italic;
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #6C63FF, #E74C3C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
    }
    .hero-sub {
        font-size: 1.25rem;
        text-align: center;
        color: #BDC3C7;
        margin-top: 1rem;
    }
    .section-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: #FAFAFA;
        text-align: center;
        margin: 2rem 0 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ── Top right Faculty Login button ──────────────────────────
col_spacer, col_faculty_btn = st.columns([8, 2])
with col_faculty_btn:
    if st.button("🔐 Faculty / HOD Login", use_container_width=True):
        st.switch_page("pages/09_faculty.py")

# ── Hero Section ─────────────────────────────────────────────
st.markdown('<div class="hero-title">Are You Drifting Toward Unemployment?</div>',
            unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">'
    'SkillDrift analyzes your B.Tech CSE skill pattern and tells you — mathematically — '
    'whether you are on track for placement or heading toward a gap year.'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)

# ── Three Statistics Cards ────────────────────────────────────
st.markdown('<div class="section-title">The Numbers India Does Not Talk About</div>',
            unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-number">57%</div>
        <div class="stat-label">
            of Indian CSE graduates are <strong>not hireable</strong>
            at the time of graduation
        </div>
        <div class="stat-source">
            India Skills Report 2024 — Wheebox &amp;
            Mercer Mettl Graduate Skill Index 2024
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-number">1M+</div>
        <div class="stat-label">
            tech job vacancies remain <strong>unfilled</strong> because
            candidates lack sufficient depth in any specific skill domain
        </div>
        <div class="stat-source">
            NASSCOM Annual IT Industry Report 2024
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-number">75% vs 35%</div>
        <div class="stat-label">
            Placement rate of <strong>focused students</strong> (one track
            from semester 3) versus <strong>drifting students</strong>
            (multiple tracks, no depth)
        </div>
        <div class="stat-source">
            AICTE Graduate Outcome Data 2023–24 &amp; NASSCOM Skill-Depth Research
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── What is Skill Drift section ───────────────────────────────
st.markdown('<div class="section-title">What is Skill Drift?</div>',
            unsafe_allow_html=True)

col_a, col_b = st.columns([1, 1])

with col_a:
    st.markdown("""
    **Skill Drift** is what happens when a B.Tech CSE student keeps switching
    technologies every semester without ever going deep enough in any one of them.

    - Semester 1 → Python basics from YouTube
    - Semester 2 → Switched to web development
    - Semester 3 → Machine Learning is trending
    - Semester 5 → Everyone is talking about cloud
    - **Semester 8 → Touched 8 fields. Not ready for any.**

    Learning a new technology always *feels* like progress.
    That feeling is exactly why drift is dangerous.
    """)

with col_b:
    st.markdown("""
    **SkillDrift solves this in three ways:**

    ✅ **Measures your scatter pattern** as a number you cannot argue with —
    the Drift Score and Shannon Entropy Score

    ✅ **Verifies your actual skill levels** through a Gemini-powered quiz
    before any calculation runs — so the analysis is honest

    ✅ **Shows real consequences** using data from 794 actual Indian job postings
    collected from Naukri.com across 8 CSE career tracks
    """)

st.markdown("<br>", unsafe_allow_html=True)

# ── How it Works ──────────────────────────────────────────────
st.markdown('<div class="section-title">How SkillDrift Works</div>',
            unsafe_allow_html=True)

steps = st.columns(4)
step_data = [
    ("1️⃣", "Enter Your Skills",
     "Select your skills across 6 categories and rate your level honestly"),
    ("2️⃣", "Take the Verification Quiz",
     "Gemini AI asks you 2 questions per skill to verify what you actually know"),
    ("3️⃣", "See Your Dashboard",
     "8 analysis windows show your Drift Score, career match, market data, and action plan"),
    ("4️⃣", "Download Your Report",
     "Get a CSV report to share with your placement cell or faculty"),
]

for col, (icon, title, desc) in zip(steps, step_data):
    with col:
        st.markdown(f"""
        <div style="background:#1A1D27; border:1px solid #2D3250;
                    border-radius:10px; padding:1.5rem; text-align:center;
                    height:180px;">
            <div style="font-size:2rem;">{icon}</div>
            <div style="font-weight:700; margin:0.5rem 0; color:#6C63FF;">{title}</div>
            <div style="font-size:0.9rem; color:#BDC3C7;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ── Main CTA Button ───────────────────────────────────────────
col_left, col_cta, col_right = st.columns([2, 3, 2])
with col_cta:
    st.markdown("""
    <style>
    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #6C63FF, #E74C3C);
        border: none;
        font-size: 1.2rem;
        font-weight: 700;
        padding: 1rem 2rem;
        border-radius: 8px;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

    if st.button(
        "🎯 Analyze My Career Focus",
        type="primary",
        use_container_width=True,
    ):
        st.switch_page("pages/02_skill_input.py")

st.markdown("<br>", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────
st.markdown("""
<hr style="border-color:#2D3250; margin: 2rem 0;">
<div style="text-align:center; color:#7F8C8D; font-size:0.85rem;">
    SkillDrift — Built for B.Tech CSE students in India &nbsp;|&nbsp;
    Data sourced from Naukri.com, India Skills Report 2024, NASSCOM, AICTE &nbsp;|&nbsp;
    Powered by Google Gemini AI
</div>
""", unsafe_allow_html=True)