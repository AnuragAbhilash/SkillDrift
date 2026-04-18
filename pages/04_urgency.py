# Window 4 - Urgency Engine 

# =============================================================
# pages/04_urgency.py — Window 4: Urgency Engine
# Shows semester-based urgency level and focus debt calculation.
# =============================================================

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from brain import CAREER_TRACKS

st.set_page_config(
    page_title="SkillDrift — Urgency Engine",
    page_icon="⏰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session Guard ─────────────────────────────────────────────
if not st.session_state.get("student_name"):
    st.warning("⚠️ Session not found. Please start from the beginning.")
    st.switch_page("pages/02_skill_input.py")

# =============================================================
# SIDEBAR — identical block used across all dashboard pages
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

    drift_score  = st.session_state.get("drift_score")
    drift_label  = st.session_state.get("drift_label", "")
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

st.title("⏰ Urgency Engine")
st.markdown(
    "How much time do you have left — and how much have you already lost?"
)
st.markdown("---")

urgency_info    = st.session_state.get("urgency_info", {})
focus_debt_info = st.session_state.get("focus_debt_info", {})
semester        = st.session_state.get("semester", 4)
best_track      = st.session_state.get("best_track", "your best matching track")

if not urgency_info:
    st.warning("⚠️ Urgency data not found. Please complete the quiz first.")
    st.stop()

urgency_level   = urgency_info.get("urgency_level", "Red")
urgency_color   = urgency_info.get("urgency_color", "#E74C3C")
urgency_message = urgency_info.get("urgency_message", "")
days_remaining  = urgency_info.get("days_remaining", 0)
weeks_remaining = urgency_info.get("weeks_remaining", 0)

# ── Urgency Banner ────────────────────────────────────────────
level_icon = {"Green": "🟢", "Yellow": "🟡", "Red": "🔴"}.get(urgency_level, "🔴")

st.markdown(f"""
<div style="background:{urgency_color}22; border:2px solid {urgency_color};
            border-radius:12px; padding:1.5rem; margin-bottom:1.5rem;">
    <div style="font-size:1.5rem; font-weight:900; color:{urgency_color};">
        {level_icon} Urgency Level: {urgency_level}
    </div>
    <div style="color:#FAFAFA; font-size:1.05rem; margin-top:0.5rem;">
        {urgency_message}
    </div>
</div>
""", unsafe_allow_html=True)

# ── Countdown Cards ───────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div style="background:#1A1D27; border:1px solid #2D3250;
                border-radius:10px; padding:1.5rem; text-align:center;">
        <div style="color:#7F8C8D; font-size:0.85rem;">YOUR SEMESTER</div>
        <div style="font-size:3rem; font-weight:900; color:#6C63FF;">
            {semester}
        </div>
        <div style="color:#BDC3C7; font-size:0.9rem;">of 8 semesters</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    countdown_color = urgency_color
    if semester >= 7:
        countdown_text = "Active Now"
        countdown_sub  = "Placement season is here"
    else:
        countdown_text = str(weeks_remaining)
        countdown_sub  = "weeks until Semester 7"

    st.markdown(f"""
    <div style="background:#1A1D27; border:1px solid #2D3250;
                border-radius:10px; padding:1.5rem; text-align:center;">
        <div style="color:#7F8C8D; font-size:0.85rem;">TIME REMAINING</div>
        <div style="font-size:3rem; font-weight:900; color:{countdown_color};">
            {countdown_text}
        </div>
        <div style="color:#BDC3C7; font-size:0.9rem;">{countdown_sub}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    debt_hours = focus_debt_info.get("focus_debt_hours", 0)
    debt_color = "#E74C3C" if debt_hours > 90 else "#F39C12" if debt_hours > 30 else "#2ECC71"

    st.markdown(f"""
    <div style="background:#1A1D27; border:1px solid #2D3250;
                border-radius:10px; padding:1.5rem; text-align:center;">
        <div style="color:#7F8C8D; font-size:0.85rem;">FOCUS DEBT</div>
        <div style="font-size:3rem; font-weight:900; color:{debt_color};">
            {debt_hours}
        </div>
        <div style="color:#BDC3C7; font-size:0.9rem;">hours of wasted learning time</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Focus Debt Explanation ────────────────────────────────────
st.subheader("💸 Your Focus Debt Explained")

daily_hours    = focus_debt_info.get("daily_hours", 2)
days_to_recover = focus_debt_info.get("days_to_recover", 0)
distraction_skills = focus_debt_info.get("distraction_skills", [])
on_track_skills    = focus_debt_info.get("on_track_skills", [])

st.markdown(f"""
Your **Focus Debt** is the total estimated hours you have spent learning skills
that do not contribute to your best matching career track: **{best_track}**.

Each off-track skill is estimated at **30 hours** of learning time
(based on average free course lengths on YouTube and NPTEL).

> 📌 Your focus debt is **{debt_hours} hours**.
> At {daily_hours} hours of focused study per day,
> that is **{days_to_recover} days** of learning time redirected away from your career goal.
""")

# ── Two column skill breakdown ────────────────────────────────
st.markdown("---")
col_a, col_b = st.columns(2)

with col_a:
    st.markdown(f"#### ✅ On-Track Skills for {best_track}")
    if on_track_skills:
        for skill in on_track_skills:
            st.markdown(
                f"<div style='background:#1A1D27; border:1px solid #2ECC71; "
                f"border-radius:6px; padding:0.4rem 0.8rem; margin:0.25rem 0; "
                f"color:#2ECC71;'>✅ {skill}</div>",
                unsafe_allow_html=True,
            )
    else:
        st.info("None of your verified skills match the required list for this track.")

with col_b:
    st.markdown("#### ⚠️ Distraction Skills (Off-Track)")
    if distraction_skills:
        for skill in distraction_skills:
            st.markdown(
                f"<div style='background:#1A1D27; border:1px solid #E74C3C; "
                f"border-radius:6px; padding:0.4rem 0.8rem; margin:0.25rem 0; "
                f"color:#E74C3C;'>⚠️ {skill} — 30 hrs estimated</div>",
                unsafe_allow_html=True,
            )
    else:
        st.success("All your verified skills are on-track. No focus debt detected.")

st.markdown("---")

# ── Focus Debt vs Available Time Bar Chart ────────────────────
st.subheader("📊 Focus Debt vs Available Study Time")

# Estimate total available study hours in remaining semesters
# Each semester ≈ 20 weeks. 5 days/week. 2 hrs/day focused study.
semesters_remaining = max(0, 8 - semester)
available_hours = semesters_remaining * 20 * 5 * daily_hours

fig_bar = go.Figure()

fig_bar.add_trace(go.Bar(
    name="Focus Debt (hours already lost to off-track skills)",
    x=["Your Situation"],
    y=[debt_hours],
    marker_color="#E74C3C",
    text=[f"{debt_hours} hrs"],
    textposition="outside",
))

fig_bar.add_trace(go.Bar(
    name="Available Focused Study Hours Remaining",
    x=["Your Situation"],
    y=[available_hours],
    marker_color="#2ECC71",
    text=[f"{available_hours} hrs"],
    textposition="outside",
))

fig_bar.update_layout(
    barmode="group",
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    font=dict(color="#BDC3C7"),
    legend=dict(
        bgcolor="#1A1D27",
        bordercolor="#2D3250",
        font=dict(color="#BDC3C7"),
    ),
    yaxis=dict(
        gridcolor="#2D3250",
        title="Hours",
    ),
    xaxis=dict(gridcolor="#2D3250"),
    margin=dict(t=40, b=40),
    height=380,
)

st.plotly_chart(fig_bar, use_container_width=True)

st.caption(
    f"Available hours estimate: {semesters_remaining} semesters remaining "
    f"× 20 weeks × 5 days × {daily_hours} hrs/day = {available_hours} hrs"
)

# ── Distraction Skills Table ──────────────────────────────────
if distraction_skills:
    st.markdown("---")
    st.subheader("📋 Distraction Skills Breakdown")

    dist_df = pd.DataFrame([
        {
            "Skill": skill,
            "Estimated Hours Spent": 30,
            "Relevant to Best Track?": "❌ No",
            "Recommendation": "Deprioritise — focus on your career track first",
        }
        for skill in distraction_skills
    ])

    st.dataframe(dist_df, use_container_width=True, hide_index=True)

st.markdown("---")

# ── Navigation ────────────────────────────────────────────────
col_prev, col_next = st.columns(2)
with col_prev:
    if st.button("← Back to Drift Score", use_container_width=True):
        st.switch_page("pages/03_drift_score.py")
with col_next:
    if st.button("Next → Career Track Match 🏆", type="primary", use_container_width=True):
        st.switch_page("pages/05_career_match.py")