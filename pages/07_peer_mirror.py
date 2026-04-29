# pages/07_peer_mirror.py

import streamlit as st
from session_store import init_session
import plotly.graph_objects as go
import pandas as pd
from brain import CAREER_TRACKS, FOCUSED_PLACEMENT_RATES, TRACK_SURVIVAL_RATES
from _sidebar import APPLE_CSS, render_sidebar

st.set_page_config(
    page_title="SkillDrift — Placement Odds",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session()
st.session_state["_current_page"] = "peer"
st.markdown(APPLE_CSS, unsafe_allow_html=True)
render_sidebar()

if not st.session_state.get("student_name"):
    st.warning("Session not found. Please start from the beginning.")
    st.switch_page("pages/02_skill_input.py")
    st.stop()

peer_info    = st.session_state.get("peer_info", {})
drift_score  = st.session_state.get("drift_score") or 0
drift_label  = st.session_state.get("drift_label", "")
best_track   = st.session_state.get("best_track", "Unknown")
student_name = st.session_state.get("student_name", "You")

if not peer_info:
    st.warning("Placement data not found. Please complete the quiz first.")
    st.stop()

student_rate   = peer_info.get("student_placement_rate", 0)
student_range  = peer_info.get("student_placement_range", "")
focused_rate   = peer_info.get("focused_placement_rate", 0)
survival_rates = peer_info.get("survival_rates", TRACK_SURVIVAL_RATES)
gap            = focused_rate - student_rate
rate_color     = "#15803d" if student_rate >= 60 else "#d97706" if student_rate >= 40 else "#ba1a1a"

# ── Page Title ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:1.25rem;">
    <div style="font-size:1.5rem;font-weight:800;color:#171c1f;font-family:'Manrope',sans-serif;">
        Placement Odds
    </div>
    <div style="font-size:0.875rem;color:#515f74;margin-top:5px;">
        Based on your current skill profile, what are your chances of getting placed?
    </div>
</div>
""", unsafe_allow_html=True)

# ── Two Big Rate Cards ──────────────────────────────────────────────────────────
col_you, col_focused = st.columns(2, gap="medium")

with col_you:
    st.markdown(f"""
    <div style="background:#FFFFFF;border:2px solid {rate_color};border-radius:16px;
                padding:1.75rem;text-align:center;box-shadow:0 1px 8px rgba(0,0,0,0.05);">
        <div style="color:#515f74;font-size:0.68rem;font-weight:700;
                    letter-spacing:0.9px;text-transform:uppercase;margin-bottom:4px;">
            Your Placement Chance
        </div>
        <div style="font-size:3.8rem;font-weight:800;color:{rate_color};
                    margin:0.3rem 0;font-family:'Manrope',sans-serif;">
            ~{student_rate}%
        </div>
        <div style="font-size:0.88rem;color:{rate_color};font-weight:600;margin-bottom:4px;">
            Estimated range: {student_range}
        </div>
        <div style="color:#515f74;font-size:0.82rem;">
            Based on students with a similar Drift Score ({drift_score})
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_focused:
    st.markdown(f"""
    <div style="background:#FFFFFF;border:2px solid #15803d;border-radius:16px;
                padding:1.75rem;text-align:center;box-shadow:0 1px 8px rgba(0,0,0,0.05);">
        <div style="color:#515f74;font-size:0.68rem;font-weight:700;
                    letter-spacing:0.9px;text-transform:uppercase;margin-bottom:4px;">
            What Focused {best_track} Students Get
        </div>
        <div style="font-size:3.8rem;font-weight:800;color:#15803d;
                    margin:0.3rem 0;font-family:'Manrope',sans-serif;">
            {focused_rate}%
        </div>
        <div style="color:#515f74;font-size:0.82rem;">
            Students who stayed focused on {best_track} from early on
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Gap alert ───────────────────────────────────────────────────────────────────
if gap > 0:
    st.markdown(f"""
    <div style="background:#fff5f5;border:1.5px solid #ba1a1a;border-radius:10px;
                padding:14px 18px;text-align:center;margin-top:14px;">
        <span style="color:#ba1a1a;font-size:0.95rem;font-weight:700;">
            You are {gap}% below what a focused {best_track} student gets.
            That gap closes when you stop spreading across too many skills.
        </span>
    </div>
    """, unsafe_allow_html=True)
elif gap <= 0:
    st.markdown(f"""
    <div style="background:#f0fdf4;border:1.5px solid #15803d;border-radius:10px;
                padding:14px 18px;text-align:center;margin-top:14px;">
        <span style="color:#15803d;font-size:0.95rem;font-weight:700;">
            You are matching or beating the placement rate of a focused {best_track} student. Keep going.
        </span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:1.25rem;'></div>", unsafe_allow_html=True)

# ── Placement Rate Bar Chart — full width, clean ────────────────────────────────
st.markdown("""
<div style="font-size:0.95rem;font-weight:700;color:#171c1f;margin-bottom:4px;">
    Your Odds vs a Focused Student
</div>
<div style="font-size:0.82rem;color:#515f74;margin-bottom:12px;">
    The green bar is what you could reach if you focus on one track now.
</div>
""", unsafe_allow_html=True)

fig_p = go.Figure()
fig_p.add_trace(go.Bar(
    x=["Your Current Profile"],
    y=[student_rate],
    marker_color=rate_color,
    text=[f"{student_rate}%"],
    textposition="outside",
    textfont=dict(color="#171c1f", size=14, family="Manrope"),
    width=0.35,
))
fig_p.add_trace(go.Bar(
    x=[f"Focused {best_track} Student"],
    y=[focused_rate],
    marker_color="#15803d",
    text=[f"{focused_rate}%"],
    textposition="outside",
    textfont=dict(color="#171c1f", size=14, family="Manrope"),
    width=0.35,
))
fig_p.update_layout(
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#f8fafc",
    font=dict(color="#171c1f", size=12, family="Inter"),
    yaxis=dict(
        range=[0, 110],
        gridcolor="#e2e8f0",
        title="Placement Chance (%)",
        color="#515f74",
    ),
    xaxis=dict(gridcolor="#e2e8f0", color="#171c1f"),
    showlegend=False,
    margin=dict(t=20, b=20, l=20, r=20),
    height=320,
    bargap=0.5,
)
st.plotly_chart(fig_p, use_container_width=True)

st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:1.25rem 0;'>",
            unsafe_allow_html=True)

# ── What this means — 3 action cards ───────────────────────────────────────────
st.markdown("""
<div style="font-size:0.95rem;font-weight:700;color:#171c1f;margin-bottom:12px;">
    What This Means for You
</div>
""", unsafe_allow_html=True)

if student_rate >= 60:
    msg_bg    = "#f0fdf4"
    msg_bdr   = "#15803d"
    msg_color = "#14532d"
    msg_text  = f"You are in a strong position. Your current skill profile gives you a {student_rate}% placement chance — above the average Indian CSE student. Keep building depth in {best_track} to push it even higher."
elif student_rate >= 40:
    msg_bg    = "#fffbeb"
    msg_bdr   = "#d97706"
    msg_color = "#78350f"
    msg_text  = f"You are getting closer, but not there yet. At {student_rate}%, you have a real chance if you focus now. Stop adding random skills and go deep on {best_track} — that is what companies want."
else:
    msg_bg    = "#fff5f5"
    msg_bdr   = "#ba1a1a"
    msg_color = "#7f1d1d"
    msg_text  = f"Your current profile gives you a {student_rate}% placement chance, which is low. The good news is this is fixable. Start with the Next Skill to Learn page and commit to {best_track} for the next 2 semesters."

st.markdown(f"""
<div style="background:{msg_bg};border:1.5px solid {msg_bdr};border-radius:12px;
            padding:18px 22px;font-size:0.9rem;color:{msg_color};line-height:1.75;">
    {msg_text}
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

# ── Disclaimer — always visible ───────────────────────────────────────────────
st.markdown("""
<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;
            padding:10px 16px;margin-top:8px;">
    <div style="font-size:0.78rem;color:#515f74;line-height:1.6;">
        <strong style="color:#171c1f;">Note:</strong>
        These are estimates based on NASSCOM and AICTE outcome data — not guarantees.
        Actual placement depends on interview performance, college, and market conditions.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Lookup table (collapsed) ────────────────────────────────────────────────────
with st.expander("See how Drift Score connects to placement chance"):
    lookup_data = [
        {"Drift Score": "0 to 20",   "Profile Type": "Highly Focused",     "Estimated Range": "65–85%", "Midpoint": "~78%"},
        {"Drift Score": "20 to 40",  "Profile Type": "Mostly Focused",     "Estimated Range": "50–70%", "Midpoint": "~62%"},
        {"Drift Score": "40 to 60",  "Profile Type": "Drifting",           "Estimated Range": "35–55%", "Midpoint": "~44%"},
        {"Drift Score": "60 to 80",  "Profile Type": "Too Scattered",      "Estimated Range": "20–38%", "Midpoint": "~29%"},
        {"Drift Score": "80 to 100", "Profile Type": "Extremely Scattered","Estimated Range": "10–25%", "Midpoint": "~18%"},
    ]
    st.dataframe(pd.DataFrame(lookup_data), use_container_width=True, hide_index=True)

st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:1.5rem 0;'>",
            unsafe_allow_html=True)

col_prev, col_next = st.columns(2)
with col_prev:
    if st.button("Back — Next Skill to Learn", use_container_width=True):
        st.switch_page("pages/06_next_skill.py")
with col_next:
    if st.button("Next — Job Market", type="primary", use_container_width=True):
        st.switch_page("pages/08_market_intel.py")