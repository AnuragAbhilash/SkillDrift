# pages/01_home.py

import streamlit as st
from session_store import init_session

st.set_page_config(
    page_title="SkillDrift — Career Focus Analyzer",
    page_icon="assets/logo.png",
    layout="centered",
    initial_sidebar_state="collapsed",
)

init_session()

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800;900&family=Inter:wght@400;500;600;700&display=swap');

    [data-testid="stSidebarNav"]            { display: none !important; }
    [data-testid="collapsedControl"]        { display: none !important; }
    [data-testid="stExpandSidebar"]         { display: none !important; }
    [data-testid="stSidebarCollapseButton"] { display: none !important; }
    section[data-testid="stSidebar"]        { display: none !important; }
    header[data-testid="stHeader"]          { display: none !important; }
    .stDeployButton  { display: none !important; }
    #MainMenu        { display: none !important; }
    footer           { display: none !important; }

    :root {
        --blue:    #002c98;
        --blue-lt: #eef2ff;
        --text:    #171c1f;
        --muted:   #515f74;
        --border:  #e2e8f0;
        --surface: #f6fafe;
        --card:    #ffffff;
    }

    html, body, .stApp { background-color: var(--surface) !important; font-family: 'Inter', sans-serif; }

    .block-container {
        padding-top:    0         !important;
        padding-bottom: 3rem      !important;
        max-width:      960px     !important;
        margin-left:    auto      !important;
        margin-right:   auto      !important;
        padding-left:   2rem      !important;
        padding-right:  2rem      !important;
    }

    /* Top bar */
    .home-topbar {
        display:         flex;
        justify-content: space-between;
        align-items:     center;
        padding:         18px 0 18px 0;
        border-bottom:   1px solid var(--border);
        margin-bottom:   56px;
        background:      transparent;
    }
    .home-logo {
        font-family:    'Manrope', sans-serif;
        font-size:      1.2rem;
        font-weight:    800;
        color:          var(--blue);
        letter-spacing: -0.02em;
    }

    /* Main buttons */
    .stButton > button {
        border-radius:  8px;
        border:         1.5px solid var(--border);
        background:     var(--card);
        color:          var(--text);
        font-weight:    600;
        font-size:      0.9rem;
        font-family:    'Inter', sans-serif;
        padding:        0.5rem 1.25rem;
        transition:     all 0.12s ease;
    }
    .stButton > button:hover { background: #f0f4f8; }
    .stButton > button[kind="primary"] {
        background:   var(--blue);
        color:        #fff;
        border-color: var(--blue);
        font-weight:  700;
        font-size:    1rem;
        padding:      0.75rem 2.5rem;
        box-shadow:   0 6px 20px rgba(0,44,152,0.2);
    }
    .stButton > button[kind="primary"]:hover {
        background:   #0038bf;
        border-color: #0038bf;
        box-shadow:   0 10px 28px rgba(0,44,152,0.28);
    }

    /* Hero */
    .home-hero {
        text-align:    center;
        margin-bottom: 60px;
    }
    .home-hero h1 {
        font-family:    'Manrope', sans-serif !important;
        font-size:      clamp(2rem, 5vw, 3.2rem) !important;
        font-weight:    900 !important;
        color:          var(--text) !important;
        line-height:    1.15 !important;
        margin-bottom:  18px !important;
    }
    .hero-accent { color: var(--blue); }
    .home-sub {
        font-size:   1.05rem;
        color:       var(--muted);
        max-width:   520px;
        margin:      0 auto 32px;
        line-height: 1.65;
    }

    /* Stats */
    .stat-card {
        background:    var(--card);
        border:        1px solid var(--border);
        border-radius: 16px;
        padding:       28px 24px;
        box-shadow:    0 2px 16px rgba(23,28,31,.04);
        height:        100%;
    }
    .stat-icon-wrap {
        width:         44px;
        height:        44px;
        border-radius: 50%;
        display:       flex;
        align-items:   center;
        justify-content: center;
        margin-bottom: 18px;
        font-size:     20px;
    }
    .stat-num {
        font-family:   'Manrope', sans-serif;
        font-size:     2.75rem;
        font-weight:   800;
        color:         var(--blue);
        line-height:   1;
        margin-bottom: 10px;
    }
    .stat-desc {
        font-size:   0.9rem;
        color:       var(--muted);
        line-height: 1.55;
    }
    .stat-source {
        font-size:   0.72rem;
        color:       #94a3b8;
        margin-top:  10px;
    }

    /* Section label */
    .section-label {
        font-size:      0.72rem;
        font-weight:    700;
        color:          var(--muted);
        letter-spacing: 0.1em;
        text-transform: uppercase;
        text-align:     center;
        margin-bottom:  20px;
        font-family:    'Inter', sans-serif;
    }

    /* Skill drift explainer */
    .explain-card {
        background:    var(--card);
        border:        1px solid var(--border);
        border-radius: 14px;
        padding:       24px;
        line-height:   1.7;
        color:         var(--text);
        font-size:     0.92rem;
        height:        100%;
    }
    .explain-card strong { color: var(--text); }
    .explain-card .accent { color: var(--blue); font-weight: 700; }

    /* Steps */
    .step-card {
        background:    var(--card);
        border:        1px solid var(--border);
        border-radius: 12px;
        padding:       22px 18px;
        height:        100%;
        box-shadow:    0 1px 6px rgba(0,0,0,0.03);
    }
    .step-num {
        font-size:      0.72rem;
        font-weight:    700;
        color:          var(--blue);
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom:  8px;
        font-family:    'Inter', sans-serif;
    }
    .step-title {
        font-family:   'Manrope', sans-serif;
        font-weight:   700;
        color:         var(--text);
        margin-bottom: 6px;
        font-size:     0.95rem;
    }
    .step-desc {
        font-size:   0.88rem;
        color:       var(--muted);
        line-height: 1.5;
    }

    /* Divider */
    .sd-divider {
        border:     none;
        border-top: 1px solid var(--border);
        margin:     2.5rem 0;
    }

    /* Footer */
    .home-footer {
        text-align:  center;
        color:       #94a3b8;
        font-size:   0.78rem;
        padding-top: 0.5rem;
        line-height: 1.6;
        font-family: 'Inter', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# ── Top bar ──────────────────────────────────────────────────────────────────
col_logo, col_fac = st.columns([6, 2])
with col_logo:
    st.markdown("<div style='padding-top:20px;'><span class='home-logo' style='font-family:Manrope,sans-serif;font-size:1.2rem;font-weight:800;color:#002c98;letter-spacing:-0.02em;'>SkillDrift</span></div>", unsafe_allow_html=True)
with col_fac:
    st.markdown("<div style='padding-top:14px;'>", unsafe_allow_html=True)
    if st.button("Faculty Login", key="faculty_btn"):
        st.switch_page("pages/09_faculty.py")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr class='sd-divider' style='margin-top:0.5rem;margin-bottom:3rem;'>", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="home-hero">
    <h1>Are You Drifting Toward<br><span class="hero-accent">Unemployment?</span></h1>
    <div class="home-sub">
        SkillDrift measures your B.Tech CSE skill pattern and tells you — with real data —
        whether you are on track for placement or heading toward a gap year.
    </div>
</div>
""", unsafe_allow_html=True)

_, col_cta, _ = st.columns([1, 2, 1])
with col_cta:
    if st.button("Analyze My Career Focus", type="primary", use_container_width=True, key="cta_top"):
        st.switch_page("pages/02_skill_input.py")

st.markdown("<hr class='sd-divider'>", unsafe_allow_html=True)

# ── Stats ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">The Numbers India Does Not Talk About</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3, gap="medium")
with c1:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-icon-wrap" style="background:#ffdad6;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ba1a1a" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        </div>
        <div class="stat-num">57%</div>
        <div class="stat-desc">of Indian CSE graduates are <strong>not hireable</strong> at graduation</div>
        <div class="stat-source">India Skills Report 2024 — Wheebox & Mercer Mettl</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-icon-wrap" style="background:#d5e3fc;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#002c98" stroke-width="2.5"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/></svg>
        </div>
        <div class="stat-num">1M+</div>
        <div class="stat-desc">tech jobs go unfilled because candidates lack <strong>depth in any one domain</strong></div>
        <div class="stat-source">NASSCOM Annual IT Industry Report 2024</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-icon-wrap" style="background:#dcfce7;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#15803d" stroke-width="2.5"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>
        </div>
        <div class="stat-num" style="font-size:2rem;">75% vs 35%</div>
        <div class="stat-desc">Placement rate — <strong>focused</strong> vs <strong>drifted</strong> students</div>
        <div class="stat-source">AICTE Graduate Outcome Data 2023–24 & NASSCOM</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr class='sd-divider'>", unsafe_allow_html=True)

# ── What is Skill Drift ───────────────────────────────────────────────────────
st.markdown('<div class="section-label">What is Skill Drift?</div>', unsafe_allow_html=True)

ca, cb = st.columns(2, gap="large")
with ca:
    st.markdown("""
    <div class="explain-card">
        <strong>Skill Drift</strong> happens when you switch technologies every semester
        without going deep in any one of them.<br><br>
        Sem 1 — Python. &nbsp; Sem 2 — Web dev. &nbsp; Sem 3 — ML.<br>
        Sem 5 — Cloud. &nbsp; <strong>Sem 8 — Touched 8 fields. Ready for none.</strong><br><br>
        <span style="color:#515f74;">Learning something new always feels like progress.
        That feeling is exactly why drift is dangerous.</span>
    </div>
    """, unsafe_allow_html=True)
with cb:
    st.markdown("""
    <div class="explain-card">
        <strong>SkillDrift fixes this in three ways:</strong><br><br>
        <span class="accent">Measures your scatter</span> as a number — the Drift Score and Entropy Score.<br><br>
        <span class="accent">Verifies your actual level</span> via a Gemini AI quiz before any analysis runs.<br><br>
        <span class="accent">Shows real consequences</span> using data from 794 Indian job postings across 8 CSE career tracks.
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr class='sd-divider'>", unsafe_allow_html=True)

# ── How It Works ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">How It Works</div>', unsafe_allow_html=True)

step_data = [
    ("Step 1", "Enter Your Skills",    "Select skills across 6 categories and rate your level honestly."),
    ("Step 2", "Take the Quiz",        "Gemini AI asks questions per skill to verify what you actually know."),
    ("Step 3", "See Your Dashboard",   "8 analysis pages show your Drift Score, career match, and action plan."),
    ("Step 4", "Download Report",      "Get a CSV report to share with your placement cell or faculty."),
]

cols = st.columns(4, gap="medium")
for col, (num, title, desc) in zip(cols, step_data):
    with col:
        st.markdown(f"""
        <div class="step-card">
            <div class="step-num">{num}</div>
            <div class="step-title">{title}</div>
            <div class="step-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:2.5rem;'></div>", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<hr style="border:none;border-top:1px solid #e2e8f0;">
<div class="home-footer">
    SkillDrift — Built for B.Tech CSE students in India &nbsp;·&nbsp;
    Data: Naukri.com, India Skills Report 2024, NASSCOM, AICTE &nbsp;·&nbsp;
    Powered by Google Gemini AI
</div>
""", unsafe_allow_html=True)
