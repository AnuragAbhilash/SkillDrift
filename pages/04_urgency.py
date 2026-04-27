# pages/04_urgency.py

import streamlit as st
from session_store import init_session
import plotly.graph_objects as go
import pandas as pd
from _sidebar import APPLE_CSS, render_sidebar

st.set_page_config(
    page_title="SkillDrift — Urgency Engine",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session()
st.session_state["_current_page"] = "urgency"
st.markdown(APPLE_CSS, unsafe_allow_html=True)
render_sidebar()

if not st.session_state.get("student_name"):
    st.warning("Session not found. Please start from the beginning.")
    st.switch_page("pages/02_skill_input.py")

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

URGENCY_COLOR_MAP = {"Green": "#15803d", "Yellow": "#d97706", "Red": "#ba1a1a"}
URGENCY_BG_MAP    = {"Green": "#f0fdf4", "Yellow": "#fffbeb", "Red": "#fff5f5"}
urgency_color  = URGENCY_COLOR_MAP.get(urgency_level, "#ba1a1a")
urgency_bg     = URGENCY_BG_MAP.get(urgency_level, "#fff5f5")
level_labels   = {"Green": "Low Urgency", "Yellow": "Moderate Urgency", "Red": "High Urgency"}
level_display  = level_labels.get(urgency_level, urgency_level)

# ── Page title ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:28px;">
    <div style="font-family:'Manrope',sans-serif;font-size:1.5rem;font-weight:800;color:#171c1f;">
        Urgency Engine
    </div>
    <div style="font-size:0.875rem;color:#515f74;margin-top:5px;">
        How much time you have left — and how much you have already spent off-track.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Urgency banner ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:{urgency_bg};border:1.5px solid {urgency_color};
            border-left:5px solid {urgency_color};
            border-radius:12px;padding:20px 24px;margin-bottom:28px;">
    <div style="font-family:'Manrope',sans-serif;font-size:1rem;font-weight:800;
                color:{urgency_color};margin-bottom:6px;">
        {level_display}
    </div>
    <div style="font-size:0.9rem;color:#171c1f;line-height:1.65;">
        {urgency_message}
    </div>
</div>
""", unsafe_allow_html=True)

# ── Countdown cards ────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3, gap="medium")

with c1:
    st.markdown(f"""
    <div class="sd-metric">
        <div class="sd-metric-label">Your Semester</div>
        <div class="sd-metric-value" style="color:#002c98;">{semester}</div>
        <div class="sd-metric-sub">of 8 semesters</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    if semester >= 7:
        countdown_text = "Now"
        countdown_sub  = "Placement season is active"
    else:
        countdown_text = str(weeks_remaining)
        countdown_sub  = "weeks until Semester 7"

    st.markdown(f"""
    <div class="sd-metric">
        <div class="sd-metric-label">Time Remaining</div>
        <div class="sd-metric-value" style="color:{urgency_color};">{countdown_text}</div>
        <div class="sd-metric-sub">{countdown_sub}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    debt_hours = focus_debt_info.get("focus_debt_hours", 0)
    debt_color = "#ba1a1a" if debt_hours > 90 else "#d97706" if debt_hours > 30 else "#15803d"

    st.markdown(f"""
    <div class="sd-metric">
        <div class="sd-metric-label">Focus Debt</div>
        <div class="sd-metric-value" style="color:{debt_color};">{debt_hours}</div>
        <div class="sd-metric-sub">estimated hours off-track</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

# ── Focus Debt explained ───────────────────────────────────────────────────────
daily_hours        = focus_debt_info.get("daily_hours", 2)
days_to_recover    = focus_debt_info.get("days_to_recover", 0)
distraction_skills = focus_debt_info.get("distraction_skills", [])
on_track_skills    = focus_debt_info.get("on_track_skills", [])

st.markdown(f"""
<div class="sd-card" style="margin-bottom:20px;">
    <div style="font-family:'Manrope',sans-serif;font-size:1rem;font-weight:700;
                color:#171c1f;margin-bottom:12px;">What is Focus Debt?</div>
    <div style="font-size:0.9rem;color:#171c1f;line-height:1.7;">
        <strong>Focus Debt</strong> is the estimated hours you spent learning skills that do not
        contribute to <strong>{best_track}</strong>. Each off-track skill costs roughly 30 hours of learning time.
    </div>
    <div style="background:#f6fafe;border-radius:8px;padding:12px 14px;
                border-left:3px solid {debt_color};margin-top:16px;
                font-size:0.9rem;color:#515f74;line-height:1.55;">
        You have <strong style="color:#171c1f;">{debt_hours} hours</strong> of focus debt.
        At {daily_hours} hrs/day, that is <strong style="color:#171c1f;">{days_to_recover} days</strong>
        of study time redirected away from your goal.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Skill breakdown ────────────────────────────────────────────────────────────
ca, cb = st.columns(2, gap="medium")

with ca:
    st.markdown(f"""
    <div style="font-family:'Manrope',sans-serif;font-size:0.95rem;font-weight:700;
                color:#171c1f;margin-bottom:10px;">
        On-Track Skills — {best_track}
    </div>
    """, unsafe_allow_html=True)
    if on_track_skills:
        items = "".join([
            f"<div style='background:#f0fdf4;border:1px solid #bbf7d0;border-left:3px solid #15803d;"
            f"border-radius:8px;padding:9px 14px;margin:5px 0;"
            f"font-size:0.88rem;color:#171c1f;font-family:Inter,sans-serif;'>{s}</div>"
            for s in on_track_skills
        ])
        st.markdown(items, unsafe_allow_html=True)
    else:
        st.info("None of your verified skills match the required list for this track.")

with cb:
    st.markdown("""
    <div style="font-family:'Manrope',sans-serif;font-size:0.95rem;font-weight:700;
                color:#171c1f;margin-bottom:10px;">
        Off-Track Skills (Focus Debt)
    </div>
    """, unsafe_allow_html=True)
    if distraction_skills:
        items = "".join([
            f"<div style='background:#fff5f5;border:1px solid #fecaca;border-left:3px solid #ba1a1a;"
            f"border-radius:8px;padding:9px 14px;margin:5px 0;"
            f"font-size:0.88rem;color:#171c1f;font-family:Inter,sans-serif;'>"
            f"{s} <span style='color:#94a3b8;font-size:0.8rem;'>— 30 hrs est.</span></div>"
            for s in distraction_skills
        ])
        st.markdown(items, unsafe_allow_html=True)
    else:
        st.success("All your verified skills are on-track. No focus debt detected.")

st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:28px 0;'>", unsafe_allow_html=True)

# ── Chart ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="font-family:'Manrope',sans-serif;font-size:1rem;font-weight:700;
            color:#171c1f;margin-bottom:16px;">
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
    marker_color="#ba1a1a",
    text=[f"{debt_hours} hrs"],
    textposition="outside",
    textfont=dict(color="#171c1f", size=13, family="Manrope"),
))
fig_bar.add_trace(go.Bar(
    name="Available Study Hours Remaining",
    x=["Your Situation"],
    y=[available_hours],
    marker_color="#15803d",
    text=[f"{available_hours} hrs"],
    textposition="outside",
    textfont=dict(color="#171c1f", size=13, family="Manrope"),
))
fig_bar.update_layout(
    barmode="group",
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#f8fafc",
    font=dict(color="#515f74", size=12, family="Inter"),
    legend=dict(
        bgcolor="#FFFFFF",
        bordercolor="#e2e8f0",
        borderwidth=1,
        font=dict(size=12),
    ),
    yaxis=dict(gridcolor="#e2e8f0", title="Hours", color="#515f74", gridwidth=1),
    xaxis=dict(gridcolor="#e2e8f0", color="#515f74"),
    margin=dict(t=36, b=36, l=16, r=16),
    height=320,
    bargap=0.3,
    bargroupgap=0.08,
)
st.plotly_chart(fig_bar, use_container_width=True)
st.markdown(
    f"<div style='font-size:0.8rem;color:#94a3b8;margin-top:-8px;'>"
    f"Available hours: {semesters_remaining} semesters x 20 weeks x 5 days x {daily_hours} hrs/day</div>",
    unsafe_allow_html=True,
)

# ── Off-track table ────────────────────────────────────────────────────────────
if distraction_skills:
    st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:24px 0;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'Manrope',sans-serif;font-size:1rem;font-weight:700;
                color:#171c1f;margin-bottom:12px;">
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

st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:28px 0;'>", unsafe_allow_html=True)

col_prev, col_next = st.columns(2)
with col_prev:
    if st.button("Back — Drift Score", use_container_width=True):
        st.switch_page("pages/03_drift_score.py")
with col_next:
    if st.button("Next — Career Track Match", type="primary", use_container_width=True):
        st.switch_page("pages/05_career_match.py")
