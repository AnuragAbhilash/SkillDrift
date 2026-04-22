# pages/01_home.py

import streamlit as st

st.set_page_config(
    page_title="SkillDrift — Career Focus Analyzer",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    [data-testid="stSidebarNav"]     { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stExpandSidebar"]  { display: none !important; }
    [data-testid="stSidebarCollapseButton"] { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }
    header[data-testid="stHeader"] { display: none !important; }
    .stDeployButton { display: none !important; }
    #MainMenu { display: none !important; }
    footer { display: none !important; }

    .stApp { background-color: #F5F5F7; }
    .block-container { padding-top: 2.5rem; padding-bottom: 3rem; max-width: 1080px; }

    .stButton > button {
        border-radius: 8px;
        border: 1px solid #D2D2D7;
        background: #F5F5F7;
        color: #1D1D1F;
        font-weight: 500;
        font-size: 0.875rem;
        transition: all 0.12s ease;
    }
    .stButton > button:hover { background: #E8E8ED; }
    .stButton > button[kind="primary"] {
        background: #6C63FF;
        color: #FFFFFF;
        border-color: #6C63FF;
        font-size: 1rem;
        font-weight: 600;
        padding: 0.6rem 2.5rem;
        letter-spacing: 0.2px;
    }
    .stButton > button[kind="primary"]:hover { background: #5A52E0; border-color: #5A52E0; }

    .stat-card {
        background: #FFFFFF;
        border: 1px solid #D2D2D7;
        border-radius: 16px;
        padding: 1.75rem 1.5rem;
        text-align: center;
        box-shadow: 0 1px 8px rgba(0,0,0,0.05);
        height: 100%;
    }
    .stat-number {
        font-size: 3rem;
        font-weight: 700;
        color: #FF3B30;
        line-height: 1;
    }
    .stat-label {
        font-size: 1.05rem;
        color: #1D1D1F;
        margin-top: 0.6rem;
        line-height: 1.5;
    }
    .stat-source {
        font-size: 0.72rem;
        color: #86868B;
        margin-top: 0.5rem;
        font-style: italic;
    }
    .step-card {
        background: #FFFFFF;
        border: 1px solid #D2D2D7;
        border-radius: 12px;
        padding: 1.25rem;
        height: 140px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.04);
    }
    .step-number {
        font-size: 0.75rem;
        font-weight: 700;
        color: #6C63FF;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
    }
    .step-title {
        font-weight: 700;
        color: #1D1D1F;
        margin-bottom: 0.3rem;
        font-size: 0.92rem;
    }
    .step-desc {
        font-size: 0.9rem;
        color: #86868B;
        line-height: 1.45;
    }
    .section-label {
        font-size: 0.72rem;
        font-weight: 600;
        color: #86868B;
        letter-spacing: 1px;
        text-transform: uppercase;
        text-align: center;
        margin-bottom: 0.6rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Top-right Faculty Login ──────────────────────────────────
_, col_fac = st.columns([8, 2])
with col_fac:
    if st.button("Faculty / HOD Login", key="faculty_btn"):
        st.switch_page("pages/09_faculty.py")

# ── Hero ──────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 1.25rem 0 0.75rem 0;">
    <div style="font-size:2.8rem; font-weight:700; color:#1D1D1F; line-height:1.15;
                font-family:-apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;">
        Are You Drifting Toward Unemployment?
    </div>
    <div style="font-size:1.05rem; color:#86868B; margin-top:0.75rem; max-width:560px;
                margin-left:auto; margin-right:auto; line-height:1.65;">
        SkillDrift analyzes your B.Tech CSE skill pattern and tells you — with real data —
        whether you are on track for placement or heading toward a gap year.
    </div>
</div>
""", unsafe_allow_html=True)

# ── CTA — at the top, centre ──────────────────────────────────
st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
col_l, col_cta, col_r = st.columns([2, 3, 2])
with col_cta:
    if st.button("Analyze My Career Focus", type="primary", use_container_width=True, key="cta_top"):
        st.switch_page("pages/02_skill_input.py")

st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)
st.markdown("<hr style='border:none; border-top:1px solid #D2D2D7;'>", unsafe_allow_html=True)

# ── Stats ──────────────────────────────────────────────────────
st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-label">The Numbers India Does Not Talk About</div>',
            unsafe_allow_html=True)

c1, c2, c3 = st.columns(3, gap="medium")
with c1:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-number">57%</div>
        <div class="stat-label">of Indian CSE graduates are <strong>not hireable</strong> at graduation</div>
        <div class="stat-source">India Skills Report 2024 — Wheebox & Mercer Mettl</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-number">1M+</div>
        <div class="stat-label">tech jobs go unfilled because candidates lack <strong>depth in any one domain</strong></div>
        <div class="stat-source">NASSCOM Annual IT Industry Report 2024</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-number" style="font-size:2.2rem;">75% vs 35%</div>
        <div class="stat-label">Placement rate — <strong>focused students</strong> vs <strong>students who drifted</strong> across tracks</div>
        <div class="stat-source">AICTE Graduate Outcome Data 2023–24 & NASSCOM Skill-Depth Research</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
st.markdown("<hr style='border:none; border-top:1px solid #D2D2D7;'>", unsafe_allow_html=True)

# ── What is Skill Drift ────────────────────────────────────────
st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-label">What is Skill Drift?</div>', unsafe_allow_html=True)

ca, cb = st.columns(2, gap="large")
with ca:
    st.markdown("""
    <div style="background:#FFFFFF; border:1px solid #D2D2D7; border-radius:14px;
                padding:1.5rem; line-height:1.7; color:#1D1D1F; font-size:0.92rem;">
        <strong>Skill Drift</strong> happens when you switch technologies every semester
        without going deep in any one of them.<br><br>
        Sem 1 — Python basics. &nbsp; Sem 2 — Web dev. &nbsp; Sem 3 — ML.<br>
        Sem 5 — Cloud. &nbsp; <strong>Sem 8 — Touched 8 fields. Ready for none.</strong><br><br>
        <span style="color:#86868B;">Learning something new always feels like progress.
        That feeling is exactly why drift is dangerous.</span>
    </div>
    """, unsafe_allow_html=True)
with cb:
    st.markdown("""
    <div style="background:#FFFFFF; border:1px solid #D2D2D7; border-radius:14px;
                padding:1.5rem; line-height:1.7; color:#1D1D1F; font-size:0.92rem;">
        <strong>SkillDrift fixes this three ways:</strong><br><br>
        <span style="color:#6C63FF; font-weight:600;">Measures your scatter</span>
        as a number — the Drift Score and Entropy Score.<br><br>
        <span style="color:#6C63FF; font-weight:600;">Verifies your actual level</span>
        via a Gemini AI quiz before any analysis runs.<br><br>
        <span style="color:#6C63FF; font-weight:600;">Shows real consequences</span>
        using data from 794 Indian job postings across 8 CSE career tracks.
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
st.markdown("<hr style='border:none; border-top:1px solid #D2D2D7;'>", unsafe_allow_html=True)

# ── How It Works ──────────────────────────────────────────────
st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-label">How It Works</div>', unsafe_allow_html=True)

steps = st.columns(4, gap="medium")
step_data = [
    ("Step 1", "Enter Your Skills", "Select skills across 6 categories and rate your level honestly"),
    ("Step 2", "Take the Quiz", "Gemini AI asks questions per skill to verify what you actually know"),
    ("Step 3", "See Your Dashboard", "8 analysis pages show your Drift Score, career match, and action plan"),
    ("Step 4", "Download Report", "Get a CSV report to share with your placement cell or faculty"),
]
for col, (num, title, desc) in zip(steps, step_data):
    with col:
        st.markdown(f"""
        <div class="step-card">
            <div class="step-number">{num}</div>
            <div class="step-title">{title}</div>
            <div class="step-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────
st.markdown("""
<hr style="border: none; border-top: 1px solid #D2D2D7; margin: 0.5rem 0;">
<div style="text-align:center; color:#86868B; font-size:0.78rem; padding:0.75rem 0;">
    SkillDrift — Built for B.Tech CSE students in India &nbsp;|&nbsp;
    Data from Naukri.com, India Skills Report 2024, NASSCOM, AICTE &nbsp;|&nbsp;
    Powered by Google Gemini AI
</div>
""", unsafe_allow_html=True)
