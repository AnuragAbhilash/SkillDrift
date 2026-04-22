# pages/07_peer_mirror.py

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from brain import CAREER_TRACKS, FOCUSED_PLACEMENT_RATES, TRACK_SURVIVAL_RATES
from _sidebar import APPLE_CSS, render_sidebar

st.set_page_config(
    page_title="SkillDrift — Peer Mirror",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(APPLE_CSS, unsafe_allow_html=True)

if not st.session_state.get("student_name"):
    st.warning("Session not found. Please start from the beginning.")
    st.switch_page("pages/02_skill_input.py")

render_sidebar()

peer_info    = st.session_state.get("peer_info", {})
drift_score  = st.session_state.get("drift_score") or 0
drift_label  = st.session_state.get("drift_label", "")
best_track   = st.session_state.get("best_track", "Unknown")
student_name = st.session_state.get("student_name", "You")

if not peer_info:
    st.warning("Peer data not found. Please complete the quiz first.")
    st.stop()

student_rate   = peer_info.get("student_placement_rate", 0)
focused_rate   = peer_info.get("focused_placement_rate", 0)
survival_rates = peer_info.get("survival_rates", TRACK_SURVIVAL_RATES)

st.markdown("""
<div style="margin-bottom:0.75rem;">
    <div style="font-size:1.6rem; font-weight:700; color:#1D1D1F;">Peer Mirror & Survival Rate</div>
    <div style="font-size:0.88rem; color:#86868B; margin-top:0.2rem;">
        What typically happens to students with a skill profile like yours when placement season arrives.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#F5F5F7; border:1px solid #D2D2D7; border-radius:10px;
            padding:0.75rem 1rem; font-size:0.8rem; color:#86868B; margin-bottom:1.25rem;">
    Disclaimer: Placement and survival rates are estimates based on NASSCOM annual reports and AICTE outcome data.
    The Drift Score is the mathematically verified output. These rates provide contextual support.
</div>
""", unsafe_allow_html=True)

# ── Hero Metrics ──────────────────────────────────────────────
rate_color = "#34C759" if student_rate >= 60 else "#FF9500" if student_rate >= 40 else "#FF3B30"
gap        = focused_rate - student_rate

col_you, col_focused = st.columns(2, gap="medium")

with col_you:
    st.markdown(f"""
    <div style="background:#FFFFFF; border:2px solid {rate_color}; border-radius:16px;
                padding:1.75rem; text-align:center; box-shadow:0 1px 8px rgba(0,0,0,0.05);">
        <div style="color:#86868B; font-size:0.65rem; font-weight:600;
                    letter-spacing:0.9px; text-transform:uppercase;">Your Estimated Placement Rate</div>
        <div style="font-size:3.5rem; font-weight:700; color:{rate_color}; margin:0.4rem 0;">
            {student_rate}%
        </div>
        <div style="color:#86868B; font-size:0.82rem;">
            Students with Drift Score {drift_score} ({drift_label})
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_focused:
    st.markdown(f"""
    <div style="background:#FFFFFF; border:2px solid #34C759; border-radius:16px;
                padding:1.75rem; text-align:center; box-shadow:0 1px 8px rgba(0,0,0,0.05);">
        <div style="color:#86868B; font-size:0.65rem; font-weight:600;
                    letter-spacing:0.9px; text-transform:uppercase;">Focused {best_track} Student Rate</div>
        <div style="font-size:3.5rem; font-weight:700; color:#34C759; margin:0.4rem 0;">
            {focused_rate}%
        </div>
        <div style="color:#86868B; font-size:0.82rem;">
            Students focused on {best_track} from early semesters
        </div>
    </div>
    """, unsafe_allow_html=True)

if gap > 0:
    st.markdown(f"""
    <div style="background:#FF3B3010; border:1px solid #FF3B30; border-radius:9px;
                padding:0.85rem 1rem; text-align:center; margin-top:0.85rem;">
        <span style="color:#FF3B30; font-size:1rem; font-weight:600;">
            The focus gap costs you {gap} percentage points in estimated placement probability.
        </span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

# ── Charts ────────────────────────────────────────────────────
col_chart1, col_chart2 = st.columns(2, gap="medium")

with col_chart1:
    st.markdown("""
    <div style="font-size:0.85rem; font-weight:600; color:#1D1D1F; margin-bottom:0.5rem;">
        Placement Rate Comparison
    </div>
    """, unsafe_allow_html=True)
    fig_p = go.Figure()
    fig_p.add_trace(go.Bar(
        x=["Your Profile"], y=[student_rate],
        marker_color=rate_color,
        text=[f"{student_rate}%"], textposition="outside", textfont=dict(color="#1D1D1F"),
    ))
    fig_p.add_trace(go.Bar(
        x=[f"Focused {best_track}"], y=[focused_rate],
        marker_color="#34C759",
        text=[f"{focused_rate}%"], textposition="outside", textfont=dict(color="#1D1D1F"),
    ))
    fig_p.update_layout(
        paper_bgcolor="#FFFFFF", plot_bgcolor="#F5F5F7",
        font=dict(color="#1D1D1F", size=11),
        yaxis=dict(range=[0, 115], gridcolor="#D2D2D7", title="Placement Rate (%)", color="#86868B"),
        xaxis=dict(gridcolor="#D2D2D7", color="#1D1D1F"),
        showlegend=False, margin=dict(t=15, b=15), height=300,
    )
    st.plotly_chart(fig_p, use_container_width=True)

with col_chart2:
    st.markdown("""
    <div style="font-size:0.85rem; font-weight:600; color:#1D1D1F; margin-bottom:0.25rem;">
        Survival Rate by Career Track
    </div>
    <div style="font-size:0.78rem; color:#86868B; margin-bottom:0.5rem;">
        % of students who commit to a track and reach readiness by Semester 8
    </div>
    """, unsafe_allow_html=True)

    tracks_s = list(survival_rates.keys())
    rates_s  = list(survival_rates.values())
    colors_s = ["#6C63FF" if t == best_track else "#D2D2D7" for t in tracks_s]

    fig_s = go.Figure(go.Bar(
        x=rates_s, y=tracks_s, orientation="h",
        marker_color=colors_s,
        text=[f"{r}%" for r in rates_s], textposition="outside", textfont=dict(color="#1D1D1F"),
    ))
    fig_s.update_layout(
        paper_bgcolor="#FFFFFF", plot_bgcolor="#F5F5F7",
        font=dict(color="#1D1D1F", size=11),
        xaxis=dict(range=[0, 115], gridcolor="#D2D2D7", title="Survival Rate (%)", color="#86868B"),
        yaxis=dict(gridcolor="#D2D2D7", color="#1D1D1F"),
        margin=dict(t=15, b=15, l=5, r=40), height=300,
    )
    st.plotly_chart(fig_s, use_container_width=True)

st.markdown("<hr style='border:none; border-top:1px solid #D2D2D7; margin:1.25rem 0;'>",
            unsafe_allow_html=True)

# ── Summary ───────────────────────────────────────────────────
st.markdown("""
<div style="font-size:0.88rem; font-weight:600; color:#1D1D1F; margin-bottom:0.6rem;">
    What This Means for You
</div>
""", unsafe_allow_html=True)

track_survival = survival_rates.get(best_track, 60)

if student_rate >= 60:
    rate_msg = f"Your profile puts you in a relatively strong position. Students with a Drift Score of {drift_score} have an estimated placement rate of {student_rate}% — above the Indian CSE average."
elif student_rate >= 40:
    rate_msg = f"Your profile shows moderate placement risk. At {student_rate}%, you are below what focused students achieve. There is meaningful room to improve by narrowing your focus."
else:
    rate_msg = f"Your profile carries high placement risk. At only {student_rate}%, you are nearly half the rate of focused students. Start with the Next Skill page and commit to one track immediately."

if track_survival >= 70:
    survival_msg = f"{best_track} has a survival rate of {track_survival}%. Strong demand and learnable skills — very achievable with consistent effort."
elif track_survival >= 55:
    survival_msg = f"{best_track} has a survival rate of {track_survival}%. Achievable with consistent effort starting this semester."
else:
    survival_msg = f"{best_track} has a survival rate of {track_survival}%. This track requires deep foundations. Starting late reduces your probability significantly — consider whether an adjacent track might be more strategic."

st.markdown(f"""
<div style="background:#FFFFFF; border:1px solid #D2D2D7; border-radius:12px;
            padding:1.25rem; font-size:0.88rem; color:#1D1D1F; line-height:1.7;">
    {rate_msg}<br><br>
    {survival_msg}<br><br>
    <span style="color:#86868B;">
        The difference between your {student_rate}% and the focused rate of {focused_rate}%
        is not talent — it is time and deliberate focus. Every semester of drift makes the
        gap harder to close.
    </span>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:0.75rem;'></div>", unsafe_allow_html=True)

# ── Lookup Table ──────────────────────────────────────────────
with st.expander("View Full Placement Rate Lookup Table"):
    lookup_data = [
        {"Drift Score Range": "0 – 20",   "Label": "Highly Focused",      "Est. Placement Rate": "78%"},
        {"Drift Score Range": "20 – 40",  "Label": "Moderately Focused",  "Est. Placement Rate": "62%"},
        {"Drift Score Range": "40 – 60",  "Label": "Drifting",            "Est. Placement Rate": "44%"},
        {"Drift Score Range": "60 – 80",  "Label": "Highly Scattered",    "Est. Placement Rate": "29%"},
        {"Drift Score Range": "80 – 100", "Label": "Extremely Scattered", "Est. Placement Rate": "18%"},
    ]
    st.dataframe(pd.DataFrame(lookup_data), use_container_width=True, hide_index=True)

st.markdown("<hr style='border:none; border-top:1px solid #D2D2D7; margin:1.5rem 0;'>",
            unsafe_allow_html=True)

col_prev, col_next = st.columns(2)
with col_prev:
    if st.button("Back — Next Skill", use_container_width=True):
        st.switch_page("pages/06_next_skill.py")
with col_next:
    if st.button("Next — Market Intelligence", type="primary", use_container_width=True):
        st.switch_page("pages/08_market_intel.py")
