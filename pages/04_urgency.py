# pages/04_urgency.py

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from _sidebar import APPLE_CSS, render_sidebar

st.set_page_config(
    page_title="SkillDrift — Urgency Engine",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(APPLE_CSS, unsafe_allow_html=True)

if not st.session_state.get("student_name"):
    st.warning("Session not found. Please start from the beginning.")
    st.switch_page("pages/02_skill_input.py")

render_sidebar()

urgency_info    = st.session_state.get("urgency_info", {})
focus_debt_info = st.session_state.get("focus_debt_info", {})
semester        = st.session_state.get("semester", 4)
best_track      = st.session_state.get("best_track", "your best matching track")

if not urgency_info:
    st.warning("Urgency data not found. Please complete the quiz first.")
    st.stop()

urgency_level   = urgency_info.get("urgency_level", "Red")
urgency_message = urgency_info.get("urgency_message", "")
weeks_remaining = urgency_info.get("weeks_remaining", 0)

URGENCY_COLOR_MAP = {"Green": "#34C759", "Yellow": "#FF9500", "Red": "#FF3B30"}
urgency_color = URGENCY_COLOR_MAP.get(urgency_level, "#FF3B30")
level_labels  = {"Green": "Low Urgency", "Yellow": "Moderate Urgency", "Red": "High Urgency"}
level_display = level_labels.get(urgency_level, urgency_level)

st.markdown(f"""
<div style="margin-bottom:1.25rem;">
    <div style="font-size:1.6rem; font-weight:700; color:#1D1D1F;">Urgency Engine</div>
    <div style="font-size:0.88rem; color:#86868B; margin-top:0.2rem;">
        How much time you have left — and how much you have already spent off-track.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Urgency Banner ────────────────────────────────────────────
st.markdown(f"""
<div style="background:{urgency_color}14; border:2px solid {urgency_color};
            border-radius:12px; padding:1.25rem 1.5rem; margin-bottom:1.25rem;">
    <div style="font-size:1.1rem; font-weight:700; color:{urgency_color}; margin-bottom:0.3rem;">
        {level_display}
    </div>
    <div style="color:#1D1D1F; font-size:0.9rem; line-height:1.6;">
        {urgency_message}
    </div>
</div>
""", unsafe_allow_html=True)

# ── Countdown Cards ───────────────────────────────────────────
c1, c2, c3 = st.columns(3, gap="medium")

with c1:
    st.markdown(f"""
    <div style="background:#FFFFFF; border:1px solid #D2D2D7; border-radius:12px;
                padding:1.25rem; text-align:center;">
        <div style="color:#86868B; font-size:0.65rem; font-weight:600;
                    letter-spacing:0.9px; text-transform:uppercase;">Your Semester</div>
        <div style="font-size:3rem; font-weight:700; color:#6C63FF; margin:0.3rem 0;">{semester}</div>
        <div style="color:#86868B; font-size:0.82rem;">of 8 semesters</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    if semester >= 7:
        countdown_text = "Active"
        countdown_sub  = "Placement season is here"
    else:
        countdown_text = str(weeks_remaining)
        countdown_sub  = "weeks until Semester 7"

    st.markdown(f"""
    <div style="background:#FFFFFF; border:1px solid #D2D2D7; border-radius:12px;
                padding:1.25rem; text-align:center;">
        <div style="color:#86868B; font-size:0.65rem; font-weight:600;
                    letter-spacing:0.9px; text-transform:uppercase;">Time Remaining</div>
        <div style="font-size:3rem; font-weight:700; color:{urgency_color}; margin:0.3rem 0;">
            {countdown_text}
        </div>
        <div style="color:#86868B; font-size:0.82rem;">{countdown_sub}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    debt_hours = focus_debt_info.get("focus_debt_hours", 0)
    debt_color = "#FF3B30" if debt_hours > 90 else "#FF9500" if debt_hours > 30 else "#34C759"

    st.markdown(f"""
    <div style="background:#FFFFFF; border:1px solid #D2D2D7; border-radius:12px;
                padding:1.25rem; text-align:center;">
        <div style="color:#86868B; font-size:0.65rem; font-weight:600;
                    letter-spacing:0.9px; text-transform:uppercase;">Focus Debt</div>
        <div style="font-size:3rem; font-weight:700; color:{debt_color}; margin:0.3rem 0;">
            {debt_hours}
        </div>
        <div style="color:#86868B; font-size:0.82rem;">estimated hours off-track</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

# ── Focus Debt Explained ──────────────────────────────────────
daily_hours        = focus_debt_info.get("daily_hours", 2)
days_to_recover    = focus_debt_info.get("days_to_recover", 0)
distraction_skills = focus_debt_info.get("distraction_skills", [])
on_track_skills    = focus_debt_info.get("on_track_skills", [])

st.markdown(f"""
<div style="background:#FFFFFF; border:1px solid #D2D2D7; border-radius:12px;
            padding:1.25rem; font-size:0.88rem; color:#1D1D1F; line-height:1.65; margin-bottom:1rem;">
    <strong>Focus Debt</strong> = estimated hours you spent learning skills that do not
    contribute to <strong>{best_track}</strong>. Each off-track skill = ~30 hours of learning time.<br><br>
    <div style="background:#F5F5F7; border-radius:8px; padding:0.6rem 0.85rem;
                border-left:3px solid {debt_color};">
        You have <strong>{debt_hours} hours</strong> of focus debt.
        At {daily_hours} hrs/day, that is <strong>{days_to_recover} days</strong>
        of study time redirected away from your goal.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Skill Breakdown ───────────────────────────────────────────
ca, cb = st.columns(2, gap="medium")

with ca:
    st.markdown(f"""
    <div style="font-size:0.85rem; font-weight:600; color:#1D1D1F; margin-bottom:0.5rem;">
        On-Track Skills — {best_track}
    </div>
    """, unsafe_allow_html=True)
    if on_track_skills:
        items = "".join([
            f"<div style='background:#FFFFFF; border:1px solid #D2D2D7; border-left:3px solid #34C759; "
            f"border-radius:7px; padding:0.38rem 0.75rem; margin:0.2rem 0; "
            f"font-size:0.85rem; color:#1D1D1F;'>{s}</div>"
            for s in on_track_skills
        ])
        st.markdown(items, unsafe_allow_html=True)
    else:
        st.info("None of your verified skills match the required list for this track.")

with cb:
    st.markdown("""
    <div style="font-size:0.85rem; font-weight:600; color:#1D1D1F; margin-bottom:0.5rem;">
        Off-Track Skills (Focus Debt)
    </div>
    """, unsafe_allow_html=True)
    if distraction_skills:
        items = "".join([
            f"<div style='background:#FFFFFF; border:1px solid #D2D2D7; border-left:3px solid #FF3B30; "
            f"border-radius:7px; padding:0.38rem 0.75rem; margin:0.2rem 0; "
            f"font-size:0.85rem; color:#1D1D1F;'>{s} — 30 hrs est.</div>"
            for s in distraction_skills
        ])
        st.markdown(items, unsafe_allow_html=True)
    else:
        st.success("All your verified skills are on-track. No focus debt detected.")

st.markdown("<hr style='border:none; border-top:1px solid #D2D2D7; margin:1.5rem 0;'>",
            unsafe_allow_html=True)

# ── Focus Debt vs Available Time Chart ───────────────────────
st.markdown("""
<div style="font-size:0.88rem; font-weight:600; color:#1D1D1F; margin-bottom:0.75rem;">
    Focus Debt vs Available Study Time
</div>
""", unsafe_allow_html=True)

semesters_remaining = max(0, 8 - semester)
available_hours     = semesters_remaining * 20 * 5 * daily_hours

fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(
    name="Focus Debt (off-track hours)",
    x=["Your Situation"],
    y=[debt_hours],
    marker_color="#FF3B30",
    text=[f"{debt_hours} hrs"],
    textposition="outside",
    textfont=dict(color="#1D1D1F", size=12),
))
fig_bar.add_trace(go.Bar(
    name="Available Study Hours Remaining",
    x=["Your Situation"],
    y=[available_hours],
    marker_color="#34C759",
    text=[f"{available_hours} hrs"],
    textposition="outside",
    textfont=dict(color="#1D1D1F", size=12),
))
fig_bar.update_layout(
    barmode="group",
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#F5F5F7",
    font=dict(color="#1D1D1F", size=12),
    legend=dict(bgcolor="#FFFFFF", bordercolor="#D2D2D7", borderwidth=1, font=dict(size=11)),
    yaxis=dict(gridcolor="#D2D2D7", title="Hours", color="#86868B"),
    xaxis=dict(gridcolor="#D2D2D7", color="#86868B"),
    margin=dict(t=30, b=30),
    height=320,
)
st.plotly_chart(fig_bar, use_container_width=True)
st.markdown(
    f"<div style='font-size:0.78rem; color:#86868B;'>"
    f"Available hours: {semesters_remaining} semesters x 20 weeks x 5 days x {daily_hours} hrs/day</div>",
    unsafe_allow_html=True,
)

# ── Off-track Table ───────────────────────────────────────────
if distraction_skills:
    st.markdown("<hr style='border:none; border-top:1px solid #D2D2D7; margin:1.25rem 0;'>",
                unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.88rem; font-weight:600; color:#1D1D1F; margin-bottom:0.5rem;">
        Off-Track Skills Breakdown
    </div>
    """, unsafe_allow_html=True)
    dist_df = pd.DataFrame([
        {
            "Skill":                  skill,
            "Estimated Hours Spent":  30,
            "Relevant to Best Track": "No",
            "Recommendation":         "Deprioritise — focus on your track first",
        }
        for skill in distraction_skills
    ])
    st.dataframe(dist_df, use_container_width=True, hide_index=True)

st.markdown("<hr style='border:none; border-top:1px solid #D2D2D7; margin:1.5rem 0;'>",
            unsafe_allow_html=True)

col_prev, col_next = st.columns(2)
with col_prev:
    if st.button("Back — Drift Score", use_container_width=True):
        st.switch_page("pages/03_drift_score.py")
with col_next:
    if st.button("Next — Career Track Match", type="primary", use_container_width=True):
        st.switch_page("pages/05_career_match.py")
