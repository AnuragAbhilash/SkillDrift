# pages/03_drift_score.py

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from brain import CAREER_TRACKS
from _sidebar import APPLE_CSS, render_sidebar

st.set_page_config(
    page_title="SkillDrift — Drift Score",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(APPLE_CSS, unsafe_allow_html=True)

if not st.session_state.get("student_name"):
    st.warning("Session not found. Please start from the beginning.")
    st.switch_page("pages/02_skill_input.py")

render_sidebar()

drift_score   = st.session_state.get("drift_score")   or 0
drift_label   = st.session_state.get("drift_label")   or ""
entropy_score = st.session_state.get("entropy_score") or 0
entropy_label = st.session_state.get("entropy_label") or ""
track_counts  = st.session_state.get("track_counts")  or {}
verified_skills = st.session_state.get("verified_skills", {})

if not verified_skills:
    st.warning("No verified skills found. Please go back and complete the quiz honestly.")
    st.stop()

st.markdown("""
<div style="margin-bottom:1.25rem;">
    <div style="font-size:1.6rem; font-weight:700; color:#1D1D1F;">Drift Score & Entropy Score</div>
    <div style="font-size:0.88rem; color:#86868B; margin-top:0.2rem;">
        Calculated from your verified skills only. Skills you failed the quiz for are excluded.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Score Cards ───────────────────────────────────────────────
drift_color = (
    "#34C759" if drift_score <= 20
    else "#FF9500" if drift_score <= 60
    else "#FF3B30"
)
entropy_color = (
    "#34C759" if entropy_score < 1.2
    else "#FF9500" if entropy_score < 2.0
    else "#FF3B30"
)

c1, c2, c3 = st.columns(3, gap="medium")

with c1:
    st.markdown(f"""
    <div style="background:#FFFFFF; border:2px solid {drift_color};
                border-radius:16px; padding:1.75rem; text-align:center;
                box-shadow:0 1px 8px rgba(0,0,0,0.05);">
        <div style="color:#86868B; font-size:0.65rem; font-weight:600;
                    letter-spacing:0.9px; text-transform:uppercase; margin-bottom:0.4rem;">
            Drift Score
        </div>
        <div style="font-size:3.5rem; font-weight:700; color:{drift_color}; line-height:1;">
            {drift_score}
        </div>
        <div style="color:#1D1D1F; font-size:0.9rem; font-weight:600; margin-top:0.35rem;">
            {drift_label}
        </div>
        <div style="color:#86868B; font-size:0.78rem; margin-top:0.3rem;">
            0 = Focused &nbsp;|&nbsp; 100 = Scattered
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div style="background:#FFFFFF; border:2px solid {entropy_color};
                border-radius:16px; padding:1.75rem; text-align:center;
                box-shadow:0 1px 8px rgba(0,0,0,0.05);">
        <div style="color:#86868B; font-size:0.65rem; font-weight:600;
                    letter-spacing:0.9px; text-transform:uppercase; margin-bottom:0.4rem;">
            Entropy Score
        </div>
        <div style="font-size:3.5rem; font-weight:700; color:{entropy_color}; line-height:1;">
            {entropy_score}
        </div>
        <div style="color:#1D1D1F; font-size:0.9rem; font-weight:600; margin-top:0.35rem;">
            {entropy_label}
        </div>
        <div style="color:#86868B; font-size:0.78rem; margin-top:0.3rem;">
            0 bits = Focused &nbsp;|&nbsp; 3 bits = Max Scatter
        </div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    skill_count = len(verified_skills)
    st.markdown(f"""
    <div style="background:#FFFFFF; border:2px solid #6C63FF;
                border-radius:16px; padding:1.75rem; text-align:center;
                box-shadow:0 1px 8px rgba(0,0,0,0.05);">
        <div style="color:#86868B; font-size:0.65rem; font-weight:600;
                    letter-spacing:0.9px; text-transform:uppercase; margin-bottom:0.4rem;">
            Verified Skills
        </div>
        <div style="font-size:3.5rem; font-weight:700; color:#6C63FF; line-height:1;">
            {skill_count}
        </div>
        <div style="color:#1D1D1F; font-size:0.9rem; font-weight:600; margin-top:0.35rem;">
            Skills Confirmed
        </div>
        <div style="color:#86868B; font-size:0.78rem; margin-top:0.3rem;">
            after Gemini verification
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:1.25rem;'></div>", unsafe_allow_html=True)

# ── What do these mean ────────────────────────────────────────
if drift_score <= 20:
    drift_interpretation = "Your skills are concentrated in very few tracks. This is the ideal pattern — not drifting."
elif drift_score <= 40:
    drift_interpretation = "Mostly concentrated with some spread. Mild drift — manageable if you stay focused."
elif drift_score <= 60:
    drift_interpretation = "Visible spread across multiple tracks. You are drifting — needs correction before placement season."
else:
    drift_interpretation = "Broadly scattered across many unrelated tracks. Strong drift — this is a placement risk."

ca, cb = st.columns(2, gap="large")

with ca:
    st.markdown("""
    <div style="font-size:0.88rem; font-weight:600; color:#1D1D1F; margin-bottom:0.5rem;">
        What is the Drift Score?
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#FFFFFF; border:1px solid #D2D2D7; border-radius:12px;
                padding:1.25rem; color:#1D1D1F; line-height:1.65; font-size:0.88rem;">
        Your score of <strong>{drift_score}</strong> measures how scattered your {skill_count} verified
        skills are across 8 CSE career tracks.<br><br>
        <strong>0</strong> = All skills in one track — fully focused.<br>
        <strong>100</strong> = Skills spread equally across all 8 tracks — maximum drift.<br><br>
        <div style="background:#F5F5F7; border-radius:8px; padding:0.6rem 0.85rem;
                    border-left:3px solid {drift_color}; font-size:0.85rem;">
            {drift_interpretation}
        </div>
    </div>
    """, unsafe_allow_html=True)

with cb:
    st.markdown("""
    <div style="font-size:0.88rem; font-weight:600; color:#1D1D1F; margin-bottom:0.5rem;">
        What is the Entropy Score?
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#FFFFFF; border:1px solid #D2D2D7; border-radius:12px;
                padding:1.25rem; color:#1D1D1F; line-height:1.65; font-size:0.88rem;">
        Based on Shannon's Information Entropy — a mathematical measure of disorder.<br><br>
        <strong>0 bits</strong> = All skills in one track — perfect focus.<br>
        <strong>~3 bits</strong> = Skills spread equally — maximum disorder.<br><br>
        Your <strong>{entropy_score} bits</strong> puts you in the
        <strong>{entropy_label}</strong> category.<br><br>
        <div style="background:#F5F5F7; border-radius:8px; padding:0.6rem 0.85rem;
                    border-left:3px solid {entropy_color}; font-size:0.85rem;">
            Drift Score measures magnitude of spread. Entropy measures how many tracks
            you have spread into. Both together give a complete picture.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border:none; border-top:1px solid #D2D2D7; margin:1.5rem 0;'>",
            unsafe_allow_html=True)

# ── Track Breakdown ───────────────────────────────────────────
st.markdown("""
<div style="font-size:0.88rem; font-weight:600; color:#1D1D1F; margin-bottom:0.4rem;">
    Your Skills Across All 8 Career Tracks
</div>
<div style="font-size:0.82rem; color:#86868B; margin-bottom:0.75rem;">
    More skills in ONE track = less drift = better placement readiness.
</div>
""", unsafe_allow_html=True)

total_skill_count = max(len(verified_skills), 1)

if track_counts:
    track_df = pd.DataFrame([
        {
            "Career Track":     track,
            "Skills You Have":  count,
            "Share of Profile": f"{round(count / total_skill_count * 100, 1)}%",
            "Focus Signal":     (
                "Primary Track" if count == max(track_counts.values()) and count > 0
                else "Secondary" if count > 0
                else "None"
            ),
        }
        for track, count in track_counts.items()
    ])

    if not track_df.empty:
        track_df = track_df.sort_values("Skills You Have", ascending=False).reset_index(drop=True)

    def color_focus(val):
        if val == "Primary Track":
            return "color: #6C63FF; font-weight: 700"
        elif val == "Secondary":
            return "color: #FF9500"
        return "color: #86868B"

    styled = track_df.style.map(color_focus, subset=["Focus Signal"])
    st.dataframe(styled, use_container_width=True, hide_index=True)
else:
    st.info("No track data available. Please complete the quiz first.")

st.markdown("<hr style='border:none; border-top:1px solid #D2D2D7; margin:1.5rem 0;'>",
            unsafe_allow_html=True)

col_nav1, col_nav2 = st.columns(2)
with col_nav2:
    if st.button("Next — Urgency Engine", type="primary", use_container_width=True):
        st.switch_page("pages/04_urgency.py")
