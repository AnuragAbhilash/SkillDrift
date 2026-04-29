# pages/09b_student_view.py — Faculty Per-Student View
# FIX 5: Sign Out uses st.button — no broken href routing
# All routing: "All Students" -> 09c_batch_results.py

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title="SkillDrift — Student View",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800;900&family=Inter:wght@400;500;600;700&display=swap');

    [data-testid="stSidebarNav"]            { display: none !important; }
    [data-testid="collapsedControl"]        { display: none !important; }
    [data-testid="stExpandSidebar"]         { display: none !important; }
    [data-testid="stSidebarCollapseButton"] { display: none !important; }
    section[data-testid="stSidebar"]        { display: none !important; }
    header[data-testid="stHeader"]          { display: none !important; }
    .stDeployButton                         { display: none !important; }
    #MainMenu                               { display: none !important; }
    footer                                  { display: none !important; }

    :root {
        --blue:    #002c98;
        --text:    #171c1f;
        --muted:   #515f74;
        --surface: #f6fafe;
        --card:    #ffffff;
        --border:  #e2e8f0;
        --green:   #15803d;
        --red:     #ba1a1a;
        --amber:   #d97706;
    }

    html, body, .stApp {
        background-color: var(--surface) !important;
        font-family: 'Inter', sans-serif;
        color: var(--text);
    }
    .block-container {
        padding-top:    0         !important;
        padding-bottom: 3rem      !important;
        max-width:      1000px    !important;
        margin-left:    auto      !important;
        margin-right:   auto      !important;
        padding-left:   2rem      !important;
        padding-right:  2rem      !important;
    }

    h1, h2, h3, h4 {
        font-family: 'Manrope', sans-serif !important;
        color: var(--text) !important;
    }

    .stButton > button {
        border-radius:  8px;
        border:         1.5px solid var(--border);
        background:     var(--card);
        color:          var(--text);
        font-weight:    600;
        font-size:      0.88rem;
        font-family:    'Inter', sans-serif;
        padding:        0.45rem 1rem;
        transition:     all 0.12s ease;
    }
    .stButton > button:hover { background: #f0f4f8; border-color: #c2cad4; }
    .stButton > button[kind="primary"] {
        background:   var(--blue);
        color:        #ffffff;
        border-color: var(--blue);
        font-weight:  700;
    }
    .stButton > button[kind="primary"]:hover {
        background:   #0038bf;
        border-color: #0038bf;
    }

    .stAlert { border-radius: 10px; font-family: 'Inter', sans-serif; }

    .stDataFrame thead tr th {
        background-color: #f8fafc !important;
        color:            var(--muted) !important;
        font-size:        0.7rem !important;
        font-weight:      700 !important;
        letter-spacing:   0.06em !important;
        text-transform:   uppercase !important;
        font-family:      'Inter', sans-serif !important;
    }

    .sd-metric {
        background:    var(--card);
        border:        1px solid var(--border);
        border-radius: 12px;
        padding:       20px 18px;
        height:        100%;
        box-sizing:    border-box;
    }
    .sd-metric-label {
        font-size:      0.65rem;
        font-weight:    700;
        color:          var(--muted);
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-family:    'Inter', sans-serif;
        margin-bottom:  8px;
        white-space:    nowrap;
    }
    .sd-metric-value {
        font-size:   1.9rem;
        font-weight: 800;
        font-family: 'Manrope', sans-serif;
        line-height: 1;
        white-space: nowrap;
    }
    .sd-metric-sub {
        font-size:   0.8rem;
        color:       var(--muted);
        margin-top:  6px;
        font-family: 'Inter', sans-serif;
        line-height: 1.45;
    }

    .sd-card {
        background:    var(--card);
        border:        1px solid var(--border);
        border-radius: 12px;
        padding:       20px 18px;
        box-shadow:    0 2px 12px rgba(23,28,31,.04);
        height:        100%;
        box-sizing:    border-box;
    }

    .sd-section-label {
        font-family:    'Manrope', sans-serif;
        font-size:      1rem;
        font-weight:    700;
        color:          var(--text);
        margin:         0 0 12px 0;
    }

    .sd-divider {
        border:     none;
        border-top: 1px solid var(--border);
        margin:     1.5rem 0;
    }

    .fac-logo {
        font-family:    'Manrope', sans-serif;
        font-size:      1.15rem;
        font-weight:    800;
        color:          var(--blue);
        letter-spacing: -0.02em;
    }
    .fac-subtitle {
        font-family: 'Inter', sans-serif;
        font-size:   0.8rem;
        color:       var(--muted);
        margin-top:  2px;
    }

    .row-item {
        display:         flex;
        justify-content: space-between;
        align-items:     center;
        padding:         0.42rem 0;
        border-bottom:   1px solid var(--border);
    }
    .row-label { color: var(--muted); font-size: 0.85rem; font-family: 'Inter', sans-serif; }
    .row-val   { color: var(--text); font-weight: 600; font-size: 0.85rem; font-family: 'Inter', sans-serif; }

    /* Sign Out red tint */
    .signout-btn > button {
        border-color: #fca5a5 !important;
        color:        #ba1a1a !important;
        background:   #fff5f5 !important;
    }
    .signout-btn > button:hover {
        background: #fef2f2 !important;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def do_signout():
    keys_to_clear = [k for k in st.session_state.keys() if k.startswith("faculty")]
    for k in keys_to_clear:
        del st.session_state[k]
    st.switch_page("pages/09_faculty.py")


# ─────────────────────────────────────────────────────────────────────────────
# GUARD
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.get("faculty_logged_in"):
    st.error("Access denied. Please log in via the Faculty Dashboard.")
    if st.button("Go to Faculty Login", key="guard_login"):
        st.switch_page("pages/09_faculty.py")
    st.stop()

selected_name  = st.session_state.get("faculty_viewing_student")
student_lookup = st.session_state.get("faculty_student_lookup", {})

if not selected_name or selected_name not in student_lookup:
    st.warning("No student selected. Go back and click View on a student record.")
    if st.button("All Students", key="guard_back"):
        st.switch_page("pages/09c_batch_results.py")
    st.stop()

a = student_lookup[selected_name]

# Unpack
student_name       = a["student_name"]
semester           = a["semester"]
verified_skills    = a["verified_skills"]
drift_score        = a["drift_score"]
drift_label        = a["drift_label"]
track_counts       = a["track_counts"]
entropy_score      = a["entropy_score"]
entropy_label      = a["entropy_label"]
career_matches     = a["career_matches"]
best_track         = a["best_track"]
match_pct          = a["match_pct"]
readiness_score    = a["readiness_score"]
next_skill_info    = a["next_skill_info"]
urgency_info       = a["urgency_info"]
focus_debt_info    = a["focus_debt_info"]
peer_info          = a["peer_info"]

next_skill         = next_skill_info.get("skill", "N/A") if next_skill_info else "N/A"
urgency_level      = urgency_info.get("urgency_level", "Unknown") if urgency_info else "Unknown"
urgency_message    = urgency_info.get("urgency_message", "") if urgency_info else ""
days_remaining     = urgency_info.get("days_remaining", 0) if urgency_info else 0
focus_debt_hours   = focus_debt_info.get("focus_debt_hours", 0) if focus_debt_info else 0
days_to_recover    = focus_debt_info.get("days_to_recover", 0) if focus_debt_info else 0
distraction_skills = focus_debt_info.get("distraction_skills", []) if focus_debt_info else []
on_track_skills    = focus_debt_info.get("on_track_skills", []) if focus_debt_info else []
student_rate       = peer_info.get("student_placement_rate", "N/A") if peer_info else "N/A"
focused_rate       = peer_info.get("focused_placement_rate", "N/A") if peer_info else "N/A"
survival_rates     = peer_info.get("survival_rates", {}) if peer_info else {}
best_match_data    = career_matches[0] if career_matches else {}
missing_skills     = best_match_data.get("missing_skills", [])

URGENCY_COLORS = {"Red": "#ba1a1a", "Yellow": "#d97706", "Green": "#15803d"}
URGENCY_BG     = {"Red": "#ffdad6", "Yellow": "#fef3c7", "Green": "#dcfce7"}
urgency_color  = URGENCY_COLORS.get(urgency_level, "#002c98")
urgency_bg     = URGENCY_BG.get(urgency_level, "#e8edf4")

ds_color = "#15803d" if drift_score <= 20 else "#d97706" if drift_score <= 60 else "#ba1a1a"
es_color = "#15803d" if entropy_score < 1.2 else "#d97706" if entropy_score < 2.0 else "#ba1a1a"
rs_color = "#15803d" if readiness_score >= 70 else "#d97706" if readiness_score >= 40 else "#ba1a1a"

faculty_name = st.session_state.get("faculty_name", "Faculty")

# ─────────────────────────────────────────────────────────────────────────────
# TOP NAV BAR
# ─────────────────────────────────────────────────────────────────────────────
col_logo, col_nav = st.columns([7, 3])
with col_logo:
    st.markdown(
        "<div style='padding:16px 0 0;'>"
        "<div class='fac-logo'>SkillDrift</div>"
        "<div class='fac-subtitle'>Faculty Dashboard &mdash; " + faculty_name + "</div>"
        "</div>",
        unsafe_allow_html=True,
    )
with col_nav:
    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    nav_c1, nav_c2 = st.columns(2)
    with nav_c1:
        if st.button("Home", use_container_width=True, key="topnav_home"):
            st.switch_page("pages/01_home.py")
    with nav_c2:
        # FIX 5: Streamlit button — not an href
        st.markdown("<div class='signout-btn'>", unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True, key="topnav_signout"):
            do_signout()
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:0 0 14px 0;'>",
            unsafe_allow_html=True)

# ── BACK + ALL STUDENTS BUTTON ────────────────────────────────────────────────
col_back, _ = st.columns([2, 10])
with col_back:
    if st.button("All Students", use_container_width=True, key="nav_all_students"):
        st.switch_page("pages/09c_batch_results.py")

# ── STUDENT HEADER CARD ───────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;
            padding:16px 20px;margin-bottom:20px;
            display:flex;align-items:center;gap:14px;
            box-shadow:0 2px 10px rgba(23,28,31,.04);">
    <div style="width:46px;height:46px;border-radius:50%;background:#e8edf4;
                display:flex;align-items:center;justify-content:center;flex-shrink:0;">
        <svg width="26" height="26" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
            <circle cx="40" cy="28" r="18" fill="#a3b1c6"/>
            <ellipse cx="40" cy="66" rx="26" ry="17" fill="#a3b1c6"/>
        </svg>
    </div>
    <div style="flex:1;min-width:0;">
        <div style="font-family:Manrope,sans-serif;font-size:1.2rem;font-weight:800;
                    color:#171c1f;line-height:1.2;">{student_name}</div>
        <div style="font-size:0.8rem;color:#515f74;margin-top:3px;font-family:Inter,sans-serif;">
            Semester {semester} &nbsp;&middot;&nbsp;
            {len(verified_skills)} verified skills &nbsp;&middot;&nbsp;
            <span style="background:{urgency_bg};color:{urgency_color};
                         border-radius:5px;padding:1px 8px;font-weight:700;font-size:0.73rem;">
                {urgency_level} Urgency
            </span>
        </div>
    </div>
    <div style="text-align:right;flex-shrink:0;">
        <div style="font-size:0.7rem;color:#515f74;font-family:Inter,sans-serif;">Read-only view</div>
        <div style="font-size:0.78rem;color:#002c98;font-weight:600;font-family:Inter,sans-serif;">SkillDrift Analysis</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — DRIFT SCORE AND ENTROPY
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="sd-section-label">Drift Score and Entropy</div>', unsafe_allow_html=True)

col_ds, col_ent, col_radar = st.columns([2, 2, 4], gap="medium")

with col_ds:
    st.markdown(f"""
    <div class="sd-metric" style="border-top:3px solid {ds_color};">
        <div class="sd-metric-label">Drift Score</div>
        <div class="sd-metric-value" style="color:{ds_color};">{drift_score}</div>
        <div class="sd-metric-sub">{drift_label}</div>
        <div style="margin-top:6px;font-size:0.76rem;color:#515f74;font-family:Inter,sans-serif;">
            0 = no drift &nbsp;&middot;&nbsp; 100 = max scatter
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_ent:
    st.markdown(f"""
    <div class="sd-metric" style="border-top:3px solid {es_color};">
        <div class="sd-metric-label">Entropy Score</div>
        <div class="sd-metric-value" style="color:{es_color};">{entropy_score} bits</div>
        <div class="sd-metric-sub">{entropy_label}</div>
        <div style="margin-top:6px;font-size:0.76rem;color:#515f74;font-family:Inter,sans-serif;">
            0 = focused &nbsp;&middot;&nbsp; ~3 = max disorder
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_radar:
    if track_counts:
        tracks = list(track_counts.keys())
        counts = list(track_counts.values())
        fig_radar = go.Figure(go.Scatterpolar(
            r=counts + [counts[0]],
            theta=tracks + [tracks[0]],
            fill="toself",
            fillcolor="rgba(0,44,152,0.10)",
            line=dict(color="#002c98", width=2),
        ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor="#f6fafe",
                radialaxis=dict(visible=True, color="#515f74", gridcolor="#e2e8f0",
                                showticklabels=False),
                angularaxis=dict(color="#171c1f", tickfont=dict(size=9, family="Inter")),
            ),
            paper_bgcolor="#ffffff",
            font=dict(color="#515f74", size=10, family="Inter"),
            showlegend=False,
            margin=dict(t=28, b=28, l=28, r=28),
            height=250,
        )
        st.plotly_chart(fig_radar, use_container_width=True, key="sv_radar")

st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — URGENCY
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="sd-section-label">Urgency Level</div>', unsafe_allow_html=True)

col_u1, col_u2 = st.columns([3, 5], gap="medium")
with col_u1:
    st.markdown(f"""
    <div class="sd-metric" style="border-top:3px solid {urgency_color};">
        <div class="sd-metric-label">Urgency</div>
        <div class="sd-metric-value" style="color:{urgency_color};">{urgency_level}</div>
        <div class="sd-metric-sub">Semester {semester}</div>
        <div style="margin-top:14px;">
            <div class="sd-metric-label">Days to Placement Season</div>
            <div style="font-size:1.25rem;font-weight:800;font-family:Manrope,sans-serif;
                        color:#171c1f;">{days_remaining}</div>
        </div>
        <div style="margin-top:12px;">
            <div class="sd-metric-label">Focus Debt</div>
            <div style="font-size:1.25rem;font-weight:800;font-family:Manrope,sans-serif;
                        color:#ba1a1a;">{focus_debt_hours} hrs</div>
            <div class="sd-metric-sub">{days_to_recover} days at 2 hrs/day</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_u2:
    distraction_html = ""
    if distraction_skills:
        distraction_html = (
            "<div style='font-size:0.82rem;color:#ba1a1a;margin-top:10px;"
            "font-family:Inter,sans-serif;'>"
            "Distraction skills: " + ", ".join(distraction_skills[:8])
            + ("..." if len(distraction_skills) > 8 else "") + "</div>"
        )
    st.markdown(f"""
    <div class="sd-card">
        <div style="font-family:Manrope,sans-serif;font-weight:700;font-size:0.9rem;
                    color:{urgency_color};margin-bottom:10px;">Urgency Assessment</div>
        <div style="color:#171c1f;line-height:1.65;font-size:0.88rem;
                    font-family:Inter,sans-serif;">{urgency_message}</div>
        <div style="margin-top:12px;font-size:0.8rem;color:#515f74;font-family:Inter,sans-serif;">
            On-track skills: {len(on_track_skills)} &nbsp;&middot;&nbsp;
            Distraction skills: {len(distraction_skills)}
        </div>
        {distraction_html}
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — CAREER TRACK MATCH
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="sd-section-label">Career Track Match</div>', unsafe_allow_html=True)

col_match_chart, col_gap = st.columns([5, 4], gap="medium")

with col_match_chart:
    if career_matches:
        fig_match = go.Figure(go.Bar(
            x=[m["match_pct"] for m in career_matches],
            y=[m["track"] for m in career_matches],
            orientation="h",
            marker=dict(
                color=["#002c98" if m["track"] == best_track else "#c7d5f5"
                       for m in career_matches],
                line=dict(color="rgba(0,0,0,0)"),
            ),
            text=[f"{m['match_pct']}%" for m in career_matches],
            textposition="outside",
            textfont=dict(color="#515f74", size=10, family="Inter"),
            hovertemplate="%{y}<br>Match: %{x}%<extra></extra>",
        ))
        fig_match.update_layout(
            paper_bgcolor="#ffffff", plot_bgcolor="#f6fafe",
            font=dict(color="#515f74", family="Inter"),
            xaxis=dict(gridcolor="#e2e8f0", color="#515f74", range=[0, 115], zeroline=False),
            yaxis=dict(color="#171c1f", automargin=True, showgrid=False),
            margin=dict(t=10, b=10, l=10, r=50), height=280,
        )
        st.plotly_chart(fig_match, use_container_width=True, key="sv_career_match")

with col_gap:
    st.markdown(f"""
    <div class="sd-card">
        <div style="font-family:Manrope,sans-serif;font-weight:700;color:#002c98;
                    margin-bottom:12px;font-size:0.9rem;">
            Best match: {best_track} ({match_pct}%)
        </div>
    """, unsafe_allow_html=True)

    for ms in missing_skills[:8]:
        freq  = ms["frequency_pct"]
        color = "#ba1a1a" if freq >= 70 else "#d97706" if freq >= 40 else "#515f74"
        st.markdown(f"""
        <div class="row-item">
            <span class="row-label">{ms['skill']}</span>
            <span class="row-val" style="color:{color};">{freq:.0f}% of JDs</span>
        </div>
        """, unsafe_allow_html=True)

    if not missing_skills:
        st.markdown(
            "<div style='color:#15803d;font-weight:600;font-size:0.88rem;"
            "font-family:Inter,sans-serif;margin-top:4px;'>All required skills verified.</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 — READINESS AND NEXT SKILL
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="sd-section-label">Readiness and Next Skill</div>', unsafe_allow_html=True)

col_gauge, col_next = st.columns(2, gap="medium")

with col_gauge:
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=readiness_score,
        title={"text": f"Readiness for {best_track}",
               "font": {"color": "#171c1f", "size": 12, "family": "Inter"}},
        number={"suffix": "%", "font": {"color": "#171c1f", "size": 26, "family": "Manrope"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#515f74"},
            "bar": {"color": rs_color},
            "bgcolor": "#f6fafe",
            "steps": [
                {"range": [0, 40],   "color": "#ffdad6"},
                {"range": [40, 70],  "color": "#fef3c7"},
                {"range": [70, 100], "color": "#dcfce7"},
            ],
            "threshold": {
                "line": {"color": "#171c1f", "width": 2},
                "thickness": 0.75, "value": 70,
            },
        },
    ))
    fig_gauge.update_layout(
        paper_bgcolor="#ffffff",
        font=dict(color="#515f74", family="Inter"),
        margin=dict(t=40, b=20, l=20, r=20), height=230,
    )
    st.plotly_chart(fig_gauge, use_container_width=True, key="sv_gauge")

with col_next:
    if next_skill_info:
        reason = next_skill_info.get("reason", "")
        freq   = next_skill_info.get("frequency_pct", 0)
        st.markdown(f"""
        <div class="sd-card">
            <div class="sd-metric-label">Next Skill to Learn</div>
            <div style="font-family:Manrope,sans-serif;font-size:1.35rem;font-weight:800;
                        color:#d97706;margin-bottom:8px;">{next_skill}</div>
            <div style="font-size:0.8rem;color:#515f74;margin-bottom:8px;
                        font-family:Inter,sans-serif;">
                Appears in <strong style="color:#171c1f;">{freq:.0f}%</strong>
                of {best_track} job postings
            </div>
            <div style="font-size:0.85rem;color:#171c1f;line-height:1.6;
                        font-family:Inter,sans-serif;">{reason}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5 — PEER COMPARISON
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="sd-section-label">Peer Comparison</div>', unsafe_allow_html=True)

col_peer1, col_peer2 = st.columns(2, gap="medium")

with col_peer1:
    try:
        rate_num   = float(str(student_rate).replace("%", ""))
        rate_color = "#15803d" if rate_num >= 60 else "#d97706" if rate_num >= 40 else "#ba1a1a"
    except Exception:
        rate_color = "#515f74"

    st.markdown(f"""
    <div class="sd-card">
        <div style="display:flex;gap:2rem;align-items:center;flex-wrap:wrap;">
            <div style="text-align:center;">
                <div class="sd-metric-label">This student</div>
                <div style="font-family:Manrope,sans-serif;font-size:2rem;font-weight:800;
                            color:{rate_color};">{student_rate}%</div>
                <div style="font-size:0.74rem;color:#515f74;font-family:Inter,sans-serif;">
                    est. placement rate
                </div>
            </div>
            <div style="text-align:center;">
                <div class="sd-metric-label">Focused {best_track}</div>
                <div style="font-family:Manrope,sans-serif;font-size:2rem;font-weight:800;
                            color:#15803d;">{focused_rate}%</div>
                <div style="font-size:0.74rem;color:#515f74;font-family:Inter,sans-serif;">
                    est. placement rate
                </div>
            </div>
        </div>
        <div style="font-size:0.76rem;color:#515f74;margin-top:12px;font-family:Inter,sans-serif;">
            Based on NASSCOM and AICTE published outcome data.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_peer2:
    if survival_rates:
        tracks_sr = list(survival_rates.keys())
        rates_sr  = list(survival_rates.values())
        fig_sr = go.Figure(go.Bar(
            x=rates_sr, y=tracks_sr, orientation="h",
            marker=dict(
                color=["#002c98" if t == best_track else "#c7d5f5" for t in tracks_sr],
                line=dict(color="rgba(0,0,0,0)"),
            ),
            text=[f"{r}%" for r in rates_sr], textposition="outside",
            textfont=dict(color="#515f74", size=10, family="Inter"),
            hovertemplate="%{y}<br>%{x}%<extra></extra>",
        ))
        fig_sr.update_layout(
            paper_bgcolor="#ffffff", plot_bgcolor="#f6fafe",
            title=dict(text="Track Survival Rates",
                       font=dict(color="#171c1f", size=11, family="Manrope")),
            font=dict(color="#515f74", family="Inter"),
            xaxis=dict(gridcolor="#e2e8f0", range=[0, 115], zeroline=False),
            yaxis=dict(showgrid=False, automargin=True),
            margin=dict(t=32, b=10, l=10, r=50), height=250,
        )
        st.plotly_chart(fig_sr, use_container_width=True, key="sv_survival")

st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6 — VERIFIED SKILLS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="sd-section-label">Verified Skills Profile</div>', unsafe_allow_html=True)

if verified_skills:
    skill_rows = []
    for skill, level in verified_skills.items():
        on_track = skill in on_track_skills
        skill_rows.append({
            "Skill":          skill,
            "Level":          level,
            "On-Track":       "Yes" if on_track else "No",
        })
    skills_df = pd.DataFrame(skill_rows)

    def _style_on_track(val):
        if val == "Yes": return "color: #15803d; font-weight: 700;"
        return "color: #d97706; font-weight: 600;"

    def _style_level(val):
        if val == "Advanced":     return "color: #002c98; font-weight: 700;"
        if val == "Intermediate": return "color: #15803d; font-weight: 600;"
        return "color: #515f74;"

    styled_skills = (
        skills_df.style
        .map(_style_on_track, subset=["On-Track"])
        .map(_style_level,    subset=["Level"])
    )
    st.dataframe(styled_skills, use_container_width=True, hide_index=True)
else:
    st.warning("No verified skills found for this student.")

st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7 — FACULTY RECOMMENDATION (plain text, no alert boxes)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="sd-section-label">Faculty Recommendation</div>', unsafe_allow_html=True)

if readiness_score >= 70:
    rec_color  = "#15803d"
    rec_bg     = "#f0fdf4"
    rec_border = "#bbf7d0"
    rec_tag    = "On Track"
    rec_text   = (
        f"{student_name} is approaching placement readiness for {best_track}. "
        f"At {readiness_score}% readiness, they are ahead of most peers. "
        f"Encourage them to deepen skills to Advanced level and build a strong portfolio project."
    )
elif readiness_score >= 40:
    rec_color  = "#d97706"
    rec_bg     = "#fffbeb"
    rec_border = "#fde68a"
    rec_tag    = "Needs Focus"
    rec_text   = (
        f"{student_name} is partially ready for {best_track} at {readiness_score}% readiness. "
        f"Next priority: {next_skill}. "
        f"Advise them to stop adding new technologies until readiness crosses 70%."
    )
else:
    rec_color  = "#ba1a1a"
    rec_bg     = "#fff5f5"
    rec_border = "#fecaca"
    rec_tag    = "Urgent"
    rec_text   = (
        f"{student_name} requires immediate attention. At {readiness_score}% readiness, "
        f"they are not yet competitive for {best_track} placements. "
        f"Recommend a focused 30-day plan starting with {next_skill}. "
        f"Schedule a one-on-one mentoring session."
    )

st.markdown(f"""
<div style="background:{rec_bg};border:1px solid {rec_border};border-radius:12px;
            padding:18px 20px;font-family:Inter,sans-serif;">
    <div style="font-size:0.68rem;font-weight:700;color:{rec_color};
                letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px;">
        {rec_tag}
    </div>
    <div style="font-size:0.9rem;color:#171c1f;line-height:1.65;">
        {rec_text}
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

# Bottom navigation — routes to batch results
col_back2, _ = st.columns([2, 6])
with col_back2:
    if st.button("All Students", type="primary", use_container_width=True, key="back_bottom"):
        st.switch_page("pages/09c_batch_results.py")
