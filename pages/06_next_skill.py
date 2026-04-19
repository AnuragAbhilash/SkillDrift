# Window 6 - Next Skill 
# =============================================================
# pages/06_next_skill.py — Window 6: Next Skill & Readiness Score
# Shows the single most important skill to learn and readiness gauge.
# =============================================================

import streamlit as st
import plotly.graph_objects as go
from brain import CAREER_TRACKS

st.set_page_config(
    page_title="SkillDrift — Next Skill",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session Guard ─────────────────────────────────────────────
if not st.session_state.get("student_name"):
    st.warning("⚠️ Session not found. Please start from the beginning.")
    st.switch_page("pages/02_skill_input.py")

# =============================================================
# SIDEBAR
# =============================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0;">
      <svg width="80" height="80" viewBox="0 0 80 80"
           xmlns="http://www.w3.org/2000/svg">
        <circle cx="40" cy="40" r="40" fill="#2D3250"/>
        <circle cx="40" cy="30" r="15" fill="#6C63FF"/>
        <ellipse cx="40" cy="65" rx="22" ry="15" fill="#6C63FF"/>
      </svg>
    </div>
    """, unsafe_allow_html=True)

    student_name = st.session_state.get("student_name", "Student")
    st.markdown(
        f"<div style='text-align:center; font-weight:700; "
        f"font-size:1.1rem; color:#FAFAFA;'>{student_name}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='text-align:center; color:#7F8C8D; font-size:0.85rem;'>"
        f"Semester {st.session_state.get('semester', '?')}</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    drift_score   = st.session_state.get("drift_score")
    drift_label   = st.session_state.get("drift_label", "")
    entropy_score = st.session_state.get("entropy_score")
    entropy_label = st.session_state.get("entropy_label", "")

    if drift_score is not None:
        drift_color = (
            "#2ECC71" if drift_score >= 60
            else "#F39C12" if drift_score >= 40
            else "#E74C3C"
        )
        st.markdown(f"""
        <div style="background:#1A1D27; border:1px solid #2D3250;
                    border-radius:8px; padding:1rem; margin-bottom:0.75rem;">
            <div style="color:#7F8C8D; font-size:0.8rem;">DRIFT SCORE</div>
            <div style="font-size:2rem; font-weight:900; color:{drift_color};">
                {drift_score}
            </div>
            <div style="color:#BDC3C7; font-size:0.85rem;">{drift_label}</div>
        </div>
        """, unsafe_allow_html=True)

        entropy_color = (
            "#2ECC71" if entropy_score < 1.2
            else "#F39C12" if entropy_score < 2.0
            else "#E74C3C"
        )
        st.markdown(f"""
        <div style="background:#1A1D27; border:1px solid #2D3250;
                    border-radius:8px; padding:1rem; margin-bottom:0.75rem;">
            <div style="color:#7F8C8D; font-size:0.8rem;">ENTROPY SCORE</div>
            <div style="font-size:2rem; font-weight:900; color:{entropy_color};">
                {entropy_score}
                <span style="font-size:1rem;">bits</span>
            </div>
            <div style="color:#BDC3C7; font-size:0.85rem;">{entropy_label}</div>
        </div>
        """, unsafe_allow_html=True)

        track_counts = st.session_state.get("track_counts", {})
        if track_counts:
            tracks  = list(track_counts.keys())
            counts  = list(track_counts.values())
            counts_closed = counts + [counts[0]]
            tracks_closed = tracks + [tracks[0]]

            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=counts_closed,
                theta=tracks_closed,
                fill="toself",
                fillcolor="rgba(108, 99, 255, 0.3)",
                line=dict(color="#6C63FF", width=2),
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, showticklabels=False,
                                    gridcolor="#2D3250"),
                    angularaxis=dict(tickfont=dict(size=9, color="#BDC3C7"),
                                     gridcolor="#2D3250"),
                    bgcolor="#0E1117",
                ),
                paper_bgcolor="#0E1117",
                showlegend=False,
                margin=dict(l=20, r=20, t=20, b=20),
                height=280,
            )
            st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("---")
    st.markdown("📊 **Your Dashboard**")
    nav_pages = [
        ("🎯 Drift & Entropy Scores",   "pages/03_drift_score.py"),
        ("⏰ Urgency Engine",            "pages/04_urgency.py"),
        ("🏆 Career Track Match",        "pages/05_career_match.py"),
        ("📚 Next Skill & Readiness",    "pages/06_next_skill.py"),
        ("👥 Peer Mirror",               "pages/07_peer_mirror.py"),
        ("🗺️ Market Intelligence",       "pages/08_market_intel.py"),
        ("📄 Final Report",              "pages/10_final_report.py"),
    ]
    for label, page in nav_pages:
        if st.button(label, use_container_width=True, key=f"nav_{page}"):
            st.switch_page(page)

    st.markdown("---")
    if st.button("🚪 Log Out", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("pages/01_home.py")

# =============================================================
# MAIN CONTENT
# =============================================================

st.title("📚 Next Skill & Readiness Score")
st.markdown(
    "One action. One reason. One priority. "
    "This window cuts through paralysis and tells you exactly what to study next."
)
st.markdown("---")

next_skill_info  = st.session_state.get("next_skill_info", {})
readiness_score  = st.session_state.get("readiness_score", 0.0)
best_track       = st.session_state.get("best_track", "your best matching track")
career_matches   = st.session_state.get("career_matches", [])

if not next_skill_info and not career_matches:
    st.warning("⚠️ Data not found. Please complete the quiz first.")
    st.stop()

# ── Next Skill Action Card ────────────────────────────────────
if next_skill_info:
    next_skill_name = next_skill_info.get("skill", "Unknown")
    next_skill_freq = next_skill_info.get("frequency_pct", 0.0)
    next_skill_why  = next_skill_info.get("reason", "")

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1A1D27, #16192A);
                border:2px solid #6C63FF; border-radius:14px;
                padding:2rem; margin-bottom:1.5rem; text-align:center;">
        <div style="color:#6C63FF; font-size:0.9rem; font-weight:700;
                    letter-spacing:2px; margin-bottom:0.5rem;">
            YOUR NEXT SKILL TO LEARN
        </div>
        <div style="font-size:3rem; font-weight:900; color:#FAFAFA;
                    margin-bottom:0.75rem;">
            {next_skill_name}
        </div>
        <div style="background:#6C63FF22; border-radius:8px;
                    padding:0.75rem 1.5rem; display:inline-block;
                    color:#BDC3C7; font-size:1rem;">
            Appears in <strong style="color:#6C63FF;">{next_skill_freq:.1f}%</strong>
            of <strong>{best_track}</strong> job postings in the Indian market
        </div>
        <div style="color:#BDC3C7; font-size:0.95rem; margin-top:1rem;
                    max-width:600px; margin-left:auto; margin-right:auto;">
            {next_skill_why}
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.success(
        f"✅ You already have all required skills for **{best_track}**. "
        "Focus on deepening your existing skills to Advanced level."
    )

# ── Readiness Gauge ───────────────────────────────────────────
st.subheader("🎯 Your Placement Readiness Score")
st.markdown(
    "This score is a weighted average across all required skills for your best track. "
    "Skills appearing more frequently in job postings carry higher weight."
)

gauge_color = (
    "#2ECC71" if readiness_score >= 70
    else "#F39C12" if readiness_score >= 40
    else "#E74C3C"
)

readiness_label = (
    "Placement Ready" if readiness_score >= 70
    else "Approaching Readiness" if readiness_score >= 40
    else "Not Yet Ready"
)

fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=readiness_score,
    number={"suffix": "%", "font": {"size": 48, "color": "#FAFAFA"}},
    delta={
        "reference": 70,
        "increasing": {"color": "#2ECC71"},
        "decreasing": {"color": "#E74C3C"},
        "suffix": "% from readiness threshold",
    },
    gauge={
        "axis": {
            "range": [0, 100],
            "tickcolor": "#BDC3C7",
            "tickfont": {"color": "#BDC3C7"},
        },
        "bar": {"color": gauge_color},
        "bgcolor": "#1A1D27",
        "bordercolor": "#2D3250",
        "steps": [
            {"range": [0,  40], "color": "rgba(231, 76, 60, 0.12)"},
            {"range": [40, 70], "color": "rgba(243, 156, 18, 0.12)"},
            {"range": [70, 100], "color": "rgba(46, 204, 113, 0.12)"},
        ],
        "threshold": {
            "line": {"color": "#FAFAFA", "width": 3},
            "thickness": 0.85,
            "value": 70,
        },
    },
    title={
        "text": f"{readiness_label}",
        "font": {"size": 20, "color": gauge_color},
    },
))

fig_gauge.update_layout(
    paper_bgcolor="#0E1117",
    font=dict(color="#BDC3C7"),
    height=380,
    margin=dict(l=40, r=40, t=60, b=20),
)

col_gauge, col_meaning = st.columns([2, 1])
with col_gauge:
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_meaning:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#1A1D27; border:1px solid #2D3250;
                border-radius:10px; padding:1.25rem;">
        <div style="color:#7F8C8D; font-size:0.8rem;">YOUR SCORE</div>
        <div style="font-size:2.5rem; font-weight:900; color:{gauge_color};">
            {readiness_score}%
        </div>
        <div style="color:#FAFAFA; font-weight:600;">{readiness_label}</div>
        <hr style="border-color:#2D3250; margin:0.75rem 0;">
        <div style="color:#BDC3C7; font-size:0.85rem;">
            <strong style="color:#FAFAFA;">Target:</strong> 70%+<br><br>
            <strong style="color:#FAFAFA;">Below 40%</strong> — Not competitive<br>
            <strong style="color:#F39C12;">40–70%</strong> — Approaching readiness<br>
            <strong style="color:#2ECC71;">70%+</strong> — Placement ready
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── Next 5 Skills Priority List ───────────────────────────────
st.subheader(f"📋 Your Full Skill Priority Queue for {best_track}")
st.markdown(
    "Missing skills ranked by how frequently they appear in Indian job postings. "
    "Learn them in this order."
)

best_match_data = career_matches[0] if career_matches else {}
missing_skills  = best_match_data.get("missing_skills", [])

if missing_skills:
    priority_list = missing_skills[:10]

    for rank, ms in enumerate(priority_list, start=1):
        skill_name = ms.get("skill", "Unknown")
        freq       = ms.get("frequency_pct", 0.0)

        bar_fill = int(freq)
        rank_color = (
            "#E74C3C" if rank == 1
            else "#F39C12" if rank <= 3
            else "#6C63FF"
        )

        is_next = rank == 1 and next_skill_info
        badge = " ← START HERE" if is_next else ""

        st.markdown(f"""
        <div style="background:#1A1D27; border:1px solid #2D3250;
                    border-radius:8px; padding:0.85rem 1rem; margin:0.35rem 0;
                    border-left:4px solid {rank_color};">
            <div style="display:flex; justify-content:space-between;
                        align-items:center;">
                <div>
                    <span style="color:{rank_color}; font-weight:900;
                                 font-size:1.1rem;">#{rank}</span>
                    <span style="color:#FAFAFA; font-weight:700;
                                 font-size:1rem; margin-left:0.75rem;">
                        {skill_name}
                    </span>
                    <span style="color:#F39C12; font-size:0.8rem;
                                 font-weight:700;">{badge}</span>
                </div>
                <div style="color:#BDC3C7; font-size:0.9rem;">
                    {freq:.1f}% of job postings
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.success(
        f"✅ You already have all required skills for **{best_track}**. "
        "No missing skills found in the priority queue."
    )

st.markdown("---")

# ── Navigation ────────────────────────────────────────────────
col_prev, col_next = st.columns(2)
with col_prev:
    if st.button("← Back to Career Track Match", use_container_width=True):
        st.switch_page("pages/05_career_match.py")
with col_next:
    if st.button("Next → Peer Mirror 👥", type="primary", use_container_width=True):
        st.switch_page("pages/07_peer_mirror.py")