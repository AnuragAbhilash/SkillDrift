# pages/06_next_skill.py

import streamlit as st
import plotly.graph_objects as go
from _sidebar import APPLE_CSS, render_sidebar

st.set_page_config(
    page_title="SkillDrift — Next Skill",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.session_state["_current_page"] = "next"
st.markdown(APPLE_CSS, unsafe_allow_html=True)
render_sidebar()

if not st.session_state.get("student_name"):
    st.warning("Session not found. Please start from the beginning.")
    st.switch_page("pages/02_skill_input.py")


next_skill_info = st.session_state.get("next_skill_info", {})
readiness_score = st.session_state.get("readiness_score", 0.0) or 0.0
best_track      = st.session_state.get("best_track", "your best matching track")
career_matches  = st.session_state.get("career_matches", [])

if not next_skill_info and not career_matches:
    st.warning("Data not found. Please complete the quiz first.")
    st.stop()

st.markdown("""
<div style="margin-bottom:1.25rem;">
    <div style="font-size:1.6rem; font-weight:700; color:#1D1D1F;">Next Skill & Readiness Score</div>
    <div style="font-size:0.88rem; color:#86868B; margin-top:0.2rem;">
        One action. One priority. Exactly what to study next — and how close you are to placement readiness.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Next Skill Action Card ────────────────────────────────────
if next_skill_info:
    next_skill_name = next_skill_info.get("skill", "Unknown")
    next_skill_freq = next_skill_info.get("frequency_pct", 0.0)
    next_skill_why  = next_skill_info.get("reason", "")

    st.markdown(f"""
    <div style="background:#FFFFFF; border:2px solid #6C63FF; border-radius:16px;
                padding:1.75rem; margin-bottom:1.5rem; text-align:center;
                box-shadow:0 2px 14px rgba(108,99,255,0.1);">
        <div style="color:#6C63FF; font-size:0.65rem; font-weight:700;
                    letter-spacing:1.2px; text-transform:uppercase; margin-bottom:0.4rem;">
            Your Next Skill to Learn
        </div>
        <div style="font-size:2.4rem; font-weight:700; color:#1D1D1F; margin-bottom:0.65rem;">
            {next_skill_name}
        </div>
        <div style="background:#F0EFFF; border-radius:8px; padding:0.5rem 1.1rem;
                    display:inline-block; color:#86868B; font-size:0.9rem;">
            Appears in <strong style="color:#6C63FF;">{next_skill_freq:.1f}%</strong>
            of <strong style="color:#1D1D1F;">{best_track}</strong> job postings in the Indian market
        </div>
        <div style="color:#86868B; font-size:0.85rem; margin-top:0.85rem;
                    max-width:580px; margin-left:auto; margin-right:auto; line-height:1.6;">
            {next_skill_why}
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.success(f"You already have all required skills for **{best_track}**. Focus on deepening to Advanced level.")

# ── Readiness Gauge ───────────────────────────────────────────
st.markdown("""
<div style="font-size:0.88rem; font-weight:600; color:#1D1D1F; margin-bottom:0.3rem;">
    Placement Readiness Score
</div>
<div style="font-size:0.82rem; color:#86868B; margin-bottom:0.75rem;">
    Weighted average across all required skills for your best track.
    Skills appearing more in job postings carry higher weight.
</div>
""", unsafe_allow_html=True)

gauge_color = (
    "#34C759" if readiness_score >= 70
    else "#FF9500" if readiness_score >= 40
    else "#FF3B30"
)
readiness_label = (
    "Placement Ready"         if readiness_score >= 70
    else "Approaching Readiness" if readiness_score >= 40
    else "Not Yet Ready"
)

fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=readiness_score,
    number={"suffix": "%", "font": {"size": 44, "color": "#1D1D1F"}},
    delta={
        "reference": 70,
        "increasing": {"color": "#34C759"},
        "decreasing": {"color": "#FF3B30"},
        "suffix": "% from target",
    },
    gauge={
        "axis": {"range": [0, 100], "tickcolor": "#86868B", "tickfont": {"color": "#86868B", "size": 11}},
        "bar": {"color": gauge_color},
        "bgcolor": "#F5F5F7",
        "bordercolor": "#D2D2D7",
        "steps": [
            {"range": [0,  40], "color": "rgba(255, 59, 48, 0.07)"},
            {"range": [40, 70], "color": "rgba(255, 149, 0, 0.07)"},
            {"range": [70, 100], "color": "rgba(52, 199, 89, 0.07)"},
        ],
        "threshold": {"line": {"color": "#1D1D1F", "width": 2}, "thickness": 0.85, "value": 70},
    },
    title={"text": readiness_label, "font": {"size": 16, "color": gauge_color}},
))
fig_gauge.update_layout(
    paper_bgcolor="#FFFFFF",
    font=dict(color="#1D1D1F"),
    height=320,
    margin=dict(l=30, r=30, t=50, b=15),
)

col_gauge, col_meaning = st.columns([2, 1])
with col_gauge:
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_meaning:
    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#FFFFFF; border:1px solid #D2D2D7; border-radius:12px; padding:1.1rem;">
        <div style="color:#86868B; font-size:0.65rem; font-weight:600; text-transform:uppercase; letter-spacing:0.8px;">
            Your Score
        </div>
        <div style="font-size:2.2rem; font-weight:700; color:{gauge_color};">{readiness_score}%</div>
        <div style="color:#1D1D1F; font-weight:600; font-size:0.88rem;">{readiness_label}</div>
        <hr style="border:none; border-top:1px solid #D2D2D7; margin:0.65rem 0;">
        <div style="font-size:0.82rem; color:#86868B; line-height:1.7;">
            <strong style="color:#1D1D1F;">Target:</strong> 70% or above<br>
            <span style="color:#FF3B30;">Below 40%</span> — Not competitive<br>
            <span style="color:#FF9500;">40–70%</span> — Approaching readiness<br>
            <span style="color:#34C759;">70%+</span> — Placement ready
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border:none; border-top:1px solid #D2D2D7; margin:1.5rem 0;'>",
            unsafe_allow_html=True)

# ── Priority Queue ────────────────────────────────────────────
st.markdown(f"""
<div style="font-size:0.88rem; font-weight:600; color:#1D1D1F; margin-bottom:0.3rem;">
    Full Skill Priority Queue for {best_track}
</div>
<div style="font-size:0.82rem; color:#86868B; margin-bottom:0.75rem;">
    Missing skills ranked by how often they appear in Indian job postings. Learn in this order.
</div>
""", unsafe_allow_html=True)

best_match_data = career_matches[0] if career_matches else {}
missing_skills  = best_match_data.get("missing_skills", [])

if missing_skills:
    priority_list = missing_skills[:10]

    # Build all rows into a single HTML block to avoid Streamlit markdown parsing issues
    rows_html = ""
    for rank, ms in enumerate(priority_list, start=1):
        skill_name = ms.get("skill", "Unknown")
        freq       = ms.get("frequency_pct", 0.0)

        rank_color = "#FF3B30" if rank == 1 else "#FF9500" if rank <= 3 else "#6C63FF"
        is_next    = rank == 1 and bool(next_skill_info)
        badge_html = (
            f'<span style="color:#FF9500; font-size:0.75rem; font-weight:600; '
            f'margin-left:0.5rem;">Start Here</span>'
            if is_next else ""
        )

        rows_html += f"""
        <div style="background:#FFFFFF; border:1px solid #D2D2D7; border-radius:9px;
                    padding:0.75rem 1rem; margin:0.25rem 0; border-left:4px solid {rank_color};
                    display:flex; justify-content:space-between; align-items:center;">
            <div style="display:flex; align-items:center; gap:0.5rem; flex:1;">
                <span style="color:{rank_color}; font-weight:700; font-size:0.95rem; min-width:28px;">#{rank}</span>
                <span style="color:#1D1D1F; font-weight:600; font-size:0.9rem;">{skill_name}</span>
                {badge_html}
            </div>
            <div style="color:#86868B; font-size:0.85rem; white-space:nowrap; margin-left:1rem;">
                {freq:.1f}% of job postings
            </div>
        </div>
        """

    st.html(rows_html)
else:
    st.success(f"You already have all required skills for **{best_track}**. No missing skills found.")

st.markdown("<hr style='border:none; border-top:1px solid #D2D2D7; margin:1.5rem 0;'>",
            unsafe_allow_html=True)

col_prev, col_next = st.columns(2)
with col_prev:
    if st.button("Back — Career Track Match", use_container_width=True):
        st.switch_page("pages/05_career_match.py")
with col_next:
    if st.button("Next — Peer Mirror", type="primary", use_container_width=True):
        st.switch_page("pages/07_peer_mirror.py")
