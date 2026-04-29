# pages/06_next_skill.py

import streamlit as st
from session_store import init_session
import plotly.graph_objects as go
from _sidebar import APPLE_CSS, render_sidebar

st.set_page_config(
    page_title="SkillDrift — Next Skill to Learn",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session()
st.session_state["_current_page"] = "next"
st.markdown(APPLE_CSS, unsafe_allow_html=True)
render_sidebar()

if not st.session_state.get("student_name"):
    st.warning("Session not found. Please start from the beginning.")
    st.switch_page("pages/02_skill_input.py")
    st.stop()

next_skill_info = st.session_state.get("next_skill_info", {})
readiness_score = st.session_state.get("readiness_score", 0.0) or 0.0
best_track      = st.session_state.get("best_track", "your best matching track")
career_matches  = st.session_state.get("career_matches", [])

if not next_skill_info and not career_matches:
    st.warning("Data not found. Please complete the quiz first.")
    st.stop()

# ── Page Title ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:1.25rem;">
    <div style="font-size:1.5rem;font-weight:800;color:#171c1f;font-family:'Manrope',sans-serif;">
        Next Skill to Learn
    </div>
    <div style="font-size:0.875rem;color:#515f74;margin-top:5px;">
        One skill. The highest-impact thing you can learn right now for your career track.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Next Skill Card ────────────────────────────────────────────────────────────
if next_skill_info:
    next_skill_name = next_skill_info.get("skill", "Unknown")
    next_skill_freq = next_skill_info.get("frequency_pct", 0.0)
    next_skill_why  = next_skill_info.get("reason", "")

    st.markdown(f"""
    <div style="background:#FFFFFF;border:2px solid #002c98;border-radius:16px;
                padding:1.75rem;margin-bottom:1.5rem;text-align:center;
                box-shadow:0 2px 14px rgba(0,44,152,0.08);">
        <div style="color:#002c98;font-size:0.68rem;font-weight:700;
                    letter-spacing:1.2px;text-transform:uppercase;margin-bottom:0.4rem;">
            Start Learning This Next
        </div>
        <div style="font-size:2.4rem;font-weight:800;color:#171c1f;margin-bottom:0.65rem;">
            {next_skill_name}
        </div>
        <div style="background:#f0f4ff;border-radius:8px;padding:0.5rem 1.1rem;
                    display:inline-block;color:#515f74;font-size:0.9rem;">
            Asked for in <strong style="color:#002c98;">{next_skill_freq:.1f}%</strong>
            of <strong style="color:#171c1f;">{best_track}</strong> job postings in India
        </div>
        <div style="color:#515f74;font-size:0.85rem;margin-top:0.85rem;
                    max-width:580px;margin-left:auto;margin-right:auto;line-height:1.6;">
            {next_skill_why}
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.success(f"You already have all required skills for **{best_track}**. Focus on getting to Advanced level in each one.")

# ── Job Readiness Gauge ─────────────────────────────────────────────────────────
st.markdown("""
<div style="font-size:0.95rem;font-weight:700;color:#171c1f;margin-bottom:4px;">
    Your Job Readiness Score
</div>
<div style="font-size:0.82rem;color:#515f74;margin-bottom:12px;">
    Calculated from how many required skills you have and at what level.
    Skills that appear more often in job postings count for more.
</div>
""", unsafe_allow_html=True)

gauge_color = (
    "#15803d" if readiness_score >= 70
    else "#d97706" if readiness_score >= 40
    else "#ba1a1a"
)
readiness_label = (
    "Job Ready"              if readiness_score >= 70
    else "Getting There"     if readiness_score >= 40
    else "Not Ready Yet"
)

fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=readiness_score,
    number={"suffix": "%", "font": {"size": 48, "color": "#171c1f", "family": "Manrope"}},
    gauge={
        "axis": {
            "range": [0, 100],
            "tickcolor": "#515f74",
            "tickfont": {"color": "#515f74", "size": 11},
        },
        "bar": {"color": gauge_color, "thickness": 0.7},
        "bgcolor": "#f8fafc",
        "bordercolor": "#e2e8f0",
        "steps": [
            {"range": [0,  40], "color": "rgba(186,26,26,0.06)"},
            {"range": [40, 70], "color": "rgba(217,119,6,0.06)"},
            {"range": [70, 100], "color": "rgba(21,128,61,0.06)"},
        ],
        "threshold": {
            "line": {"color": "#171c1f", "width": 2},
            "thickness": 0.85,
            "value": 70,
        },
    },
    title={"text": readiness_label, "font": {"size": 16, "color": gauge_color, "family": "Manrope"}},
))
fig_gauge.update_layout(
    paper_bgcolor="#FFFFFF",
    font=dict(color="#171c1f"),
    height=300,
    margin=dict(l=30, r=30, t=50, b=10),
)

col_gauge, col_meaning = st.columns([2, 1])
with col_gauge:
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_meaning:
    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#FFFFFF;border:1px solid #e2e8f0;border-radius:12px;padding:1.1rem;">
        <div style="color:#515f74;font-size:0.65rem;font-weight:600;
                    text-transform:uppercase;letter-spacing:0.8px;">Your Score</div>
        <div style="font-size:2.2rem;font-weight:800;color:{gauge_color};
                    font-family:'Manrope',sans-serif;">{readiness_score}%</div>
        <div style="color:#171c1f;font-weight:600;font-size:0.88rem;">{readiness_label}</div>
        <hr style="border:none;border-top:1px solid #e2e8f0;margin:0.65rem 0;">
        <div style="font-size:0.82rem;color:#515f74;line-height:1.8;">
            <strong style="color:#171c1f;">Target:</strong> 70% or above<br>
            <span style="color:#ba1a1a;">Below 40%</span> — Not yet competitive<br>
            <span style="color:#d97706;">40 to 70%</span> — Getting closer<br>
            <span style="color:#15803d;">70% and above</span> — Job ready
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:1.5rem 0;'>",
            unsafe_allow_html=True)

# ── Priority Queue ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="font-size:0.95rem;font-weight:700;color:#171c1f;margin-bottom:4px;">
    Full Learning Priority List for {best_track}
</div>
<div style="font-size:0.82rem;color:#515f74;margin-bottom:12px;">
    These are the skills you are still missing, ranked by how often they appear in job postings.
    Learn them in this order. Showing top 10 by job demand — focus on these before adding more.
</div>
""", unsafe_allow_html=True)

best_match_data = career_matches[0] if career_matches else {}
missing_skills  = best_match_data.get("missing_skills", [])

if missing_skills:
    priority_list = missing_skills[:10]
    rows_html = ""
    for rank, ms in enumerate(priority_list, start=1):
        skill_name = ms.get("skill", "Unknown")
        freq       = ms.get("frequency_pct", 0.0)

        rank_color = "#ba1a1a" if rank == 1 else "#d97706" if rank <= 3 else "#002c98"
        is_next    = rank == 1 and bool(next_skill_info)
        badge_html = (
            '<span style="background:#fff3cd;color:#856404;font-size:0.72rem;'
            'font-weight:700;padding:2px 8px;border-radius:20px;margin-left:8px;">'
            'Start Here</span>'
            if is_next else ""
        )

        rows_html += f"""
        <div style="background:#FFFFFF;border:1px solid #e2e8f0;border-radius:9px;
                    padding:0.75rem 1rem;margin:0.25rem 0;border-left:4px solid {rank_color};
                    display:flex;justify-content:space-between;align-items:center;">
            <div style="display:flex;align-items:center;gap:0.5rem;flex:1;">
                <span style="color:{rank_color};font-weight:700;font-size:0.95rem;
                             min-width:28px;">#{rank}</span>
                <span style="color:#171c1f;font-weight:600;font-size:0.9rem;">{skill_name}</span>
                {badge_html}
            </div>
            <div style="color:#515f74;font-size:0.82rem;white-space:nowrap;margin-left:1rem;">
                {freq:.1f}% of jobs ask for this
            </div>
        </div>
        """

    st.html(rows_html)
else:
    st.success(f"You already have all required skills for **{best_track}**. No missing skills found.")

st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:1.5rem 0;'>",
            unsafe_allow_html=True)

col_prev, col_next = st.columns(2)
with col_prev:
    if st.button("Back — Career Track Match", use_container_width=True):
        st.switch_page("pages/05_career_match.py")
with col_next:
    if st.button("Next — Placement Odds", type="primary", use_container_width=True):
        st.switch_page("pages/07_peer_mirror.py")
