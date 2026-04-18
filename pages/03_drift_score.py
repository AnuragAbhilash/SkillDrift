# Window 3 - Drift Score 
# =============================================================
# pages/03_drift_score.py — Window 3: Drift Score Dashboard
# This page sets up the permanent sidebar shown on all pages.
# It is also the landing page after quiz completion.
# =============================================================

import streamlit as st
import plotly.graph_objects as go
from brain import CAREER_TRACKS

st.set_page_config(
    page_title="SkillDrift — Your Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Session guard — redirect to skill input if no session
if not st.session_state.get("student_name"):
    st.warning("⚠️ Session not found. Please start from the beginning.")
    st.switch_page("pages/02_skill_input.py")

# =============================================================
# SIDEBAR — Permanent across all dashboard windows
# =============================================================

with st.sidebar:
    # Avatar + Name
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

    # Score cards
    drift_score = st.session_state.get("drift_score")
    drift_label = st.session_state.get("drift_label", "")
    entropy_score = st.session_state.get("entropy_score")
    entropy_label = st.session_state.get("entropy_label", "")

    if drift_score is not None:
        # Color based on score
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
                {entropy_score} <span style="font-size:1rem;">bits</span>
            </div>
            <div style="color:#BDC3C7; font-size:0.85rem;">{entropy_label}</div>
        </div>
        """, unsafe_allow_html=True)

        # Radar chart
        track_counts = st.session_state.get("track_counts", {})
        if track_counts:
            tracks = list(track_counts.keys())
            counts = list(track_counts.values())
            counts_closed = counts + [counts[0]]
            tracks_closed = tracks + [tracks[0]]

            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=counts_closed,
                theta=tracks_closed,
                fill="toself",
                fillcolor="rgba(108, 99, 255, 0.3)",
                line=dict(color="#6C63FF", width=2),
                name="Your Skills",
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        showticklabels=False,
                        gridcolor="#2D3250",
                    ),
                    angularaxis=dict(
                        tickfont=dict(size=9, color="#BDC3C7"),
                        gridcolor="#2D3250",
                    ),
                    bgcolor="#0E1117",
                ),
                paper_bgcolor="#0E1117",
                plot_bgcolor="#0E1117",
                showlegend=False,
                margin=dict(l=20, r=20, t=20, b=20),
                height=280,
            )
            st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.info("Complete the skill quiz to see your scores here.")

    st.markdown("---")

    # Navigation
    st.markdown("**📊 Your Dashboard**")
    nav_pages = [
        ("🎯 Drift & Entropy Scores", "pages/03_drift_score.py"),
        ("⏰ Urgency Engine",          "pages/04_urgency.py"),
        ("🏆 Career Track Match",      "pages/05_career_match.py"),
        ("📚 Next Skill & Readiness",  "pages/06_next_skill.py"),
        ("👥 Peer Mirror",             "pages/07_peer_mirror.py"),
        ("🗺️ Market Intelligence",    "pages/08_market_intel.py"),
        ("📄 Final Report",            "pages/10_final_report.py"),
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
# MAIN CONTENT — Window 3
# =============================================================

st.title("🎯 Your Drift Score & Entropy Score")
st.markdown(
    "These two scores are calculated from your **verified** skill profile only. "
    "Skills you failed the quiz for are excluded."
)
st.markdown("---")

verified_skills = st.session_state.get("verified_skills", {})

if not verified_skills:
    st.warning(
        "⚠️ No verified skills found. "
        "This usually means all skills were marked Not Verified in the quiz. "
        "Please go back and re-enter your skills honestly."
    )
    st.stop()

drift_score  = st.session_state.get("drift_score")
drift_label  = st.session_state.get("drift_label")
entropy_score = st.session_state.get("entropy_score")
entropy_label = st.session_state.get("entropy_label")
track_counts  = st.session_state.get("track_counts", {})

# ── Score Display ─────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    drift_color = (
        "#2ECC71" if drift_score >= 60
        else "#F39C12" if drift_score >= 40
        else "#E74C3C"
    )
    st.markdown(f"""
    <div style="background:#1A1D27; border:2px solid {drift_color};
                border-radius:12px; padding:2rem; text-align:center;">
        <div style="color:#7F8C8D; font-size:0.9rem; margin-bottom:0.5rem;">
            DRIFT SCORE
        </div>
        <div style="font-size:4rem; font-weight:900; color:{drift_color};">
            {drift_score}
        </div>
        <div style="color:#FAFAFA; font-size:1.1rem; font-weight:600;">
            {drift_label}
        </div>
        <div style="color:#7F8C8D; font-size:0.8rem; margin-top:0.5rem;">
            out of 100
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    entropy_color = (
        "#2ECC71" if entropy_score < 1.2
        else "#F39C12" if entropy_score < 2.0
        else "#E74C3C"
    )
    st.markdown(f"""
    <div style="background:#1A1D27; border:2px solid {entropy_color};
                border-radius:12px; padding:2rem; text-align:center;">
        <div style="color:#7F8C8D; font-size:0.9rem; margin-bottom:0.5rem;">
            ENTROPY SCORE
        </div>
        <div style="font-size:4rem; font-weight:900; color:{entropy_color};">
            {entropy_score}
        </div>
        <div style="color:#FAFAFA; font-size:1.1rem; font-weight:600;">
            {entropy_label}
        </div>
        <div style="color:#7F8C8D; font-size:0.8rem; margin-top:0.5rem;">
            bits (Shannon Entropy)
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    skill_count = len(verified_skills)
    st.markdown(f"""
    <div style="background:#1A1D27; border:2px solid #6C63FF;
                border-radius:12px; padding:2rem; text-align:center;">
        <div style="color:#7F8C8D; font-size:0.9rem; margin-bottom:0.5rem;">
            VERIFIED SKILLS
        </div>
        <div style="font-size:4rem; font-weight:900; color:#6C63FF;">
            {skill_count}
        </div>
        <div style="color:#FAFAFA; font-size:1.1rem; font-weight:600;">
            Skills Confirmed
        </div>
        <div style="color:#7F8C8D; font-size:0.8rem; margin-top:0.5rem;">
            after Gemini verification
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── What Your Scores Mean ─────────────────────────────────────
st.subheader("📖 What These Numbers Mean For You")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("**Drift Score Explained**")
    st.markdown(f"""
    Your Drift Score of **{drift_score}** is calculated using the
    **standard deviation** of how your {skill_count} verified skills
    are distributed across 8 career tracks.

    A score of **100** means all your skills are in exactly one track —
    perfectly focused. A score of **0** means skills are perfectly spread
    across all 8 tracks — completely scattered.

    **{drift_label}** means {"your skills show meaningful concentration in fewer tracks." if drift_score >= 60 else "your skills are spread across too many tracks without sufficient depth in any one."}
    """)

with col_b:
    st.markdown("**Entropy Score Explained**")
    st.markdown(f"""
    Your Entropy Score of **{entropy_score} bits** is calculated using
    **Shannon's Information Entropy formula**: H = -Σ p × log₂(p)

    A score of **0 bits** means all skills in one track — perfect order.
    A score of **3 bits** means skills equally spread across all 8 tracks —
    maximum disorder.

    A hireable Data Analyst profile typically scores **below 1.2 bits**.
    Your score of {entropy_score} bits puts you in the
    **{entropy_label}** category.
    """)

st.markdown("---")

# ── Track Breakdown Table ─────────────────────────────────────
st.subheader("📊 Your Skill Distribution Across All 8 Tracks")

import pandas as pd

track_df = pd.DataFrame([
    {
        "Career Track": track,
        "Skills You Have": count,
        "Signal": "🟢 Strong" if count >= 3 else "🟡 Weak" if count >= 1 else "🔴 None",
    }
    for track, count in track_counts.items()
]).sort_values("Skills You Have", ascending=False)

st.dataframe(track_df, use_container_width=True, hide_index=True)

st.markdown("---")

# ── Navigation to next window ─────────────────────────────────
col_nav1, col_nav2 = st.columns(2)
with col_nav2:
    if st.button("Next → Urgency Engine ⏰", type="primary", use_container_width=True):
        st.switch_page("pages/04_urgency.py")