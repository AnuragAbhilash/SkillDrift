# Window 7 - Peer Mirror 
# =============================================================
# pages/07_peer_mirror.py — Window 7: Peer Mirror & Survival Rate
# Shows estimated placement rates and survival rates by track.
# =============================================================

import streamlit as st
import plotly.graph_objects as go
from brain import CAREER_TRACKS, FOCUSED_PLACEMENT_RATES, TRACK_SURVIVAL_RATES

st.set_page_config(
    page_title="SkillDrift — Peer Mirror",
    page_icon="👥",
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

st.title("👥 Peer Mirror & Survival Rate")
st.markdown(
    "What typically happens to students with a skill profile like yours "
    "when placement season arrives?"
)

st.info(
    "📊 **Data Disclaimer:** All placement rates and survival rates shown "
    "on this page are **estimates** based on general industry skill-depth research "
    "from NASSCOM annual reports and AICTE published outcome data. "
    "They are not exact figures for specific drift score ranges. "
    "The Drift Score is the mathematically defensible output. "
    "These rates provide contextual support.",
    icon="ℹ️",
)

st.markdown("---")

peer_info      = st.session_state.get("peer_info", {})
drift_score    = st.session_state.get("drift_score", 0)
drift_label    = st.session_state.get("drift_label", "")
best_track     = st.session_state.get("best_track", "Unknown")
student_name   = st.session_state.get("student_name", "You")

if not peer_info:
    st.warning("⚠️ Peer data not found. Please complete the quiz first.")
    st.stop()

student_rate  = peer_info.get("student_placement_rate", 0)
focused_rate  = peer_info.get("focused_placement_rate", 0)
survival_rates = peer_info.get("survival_rates", TRACK_SURVIVAL_RATES)
disclaimer    = peer_info.get("disclaimer", "")

# ── Two Hero Metric Cards ─────────────────────────────────────
col_you, col_focused = st.columns(2)

rate_color = (
    "#2ECC71" if student_rate >= 60
    else "#F39C12" if student_rate >= 40
    else "#E74C3C"
)

with col_you:
    st.markdown(f"""
    <div style="background:#1A1D27; border:2px solid {rate_color};
                border-radius:12px; padding:2rem; text-align:center;">
        <div style="color:#7F8C8D; font-size:0.85rem; letter-spacing:1px;">
            YOUR ESTIMATED PLACEMENT RATE
        </div>
        <div style="font-size:4rem; font-weight:900; color:{rate_color}; margin:0.5rem 0;">
            {student_rate}%
        </div>
        <div style="color:#BDC3C7; font-size:0.9rem;">
            Students with Drift Score {drift_score} ({drift_label})
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_focused:
    st.markdown(f"""
    <div style="background:#1A1D27; border:2px solid #2ECC71;
                border-radius:12px; padding:2rem; text-align:center;">
        <div style="color:#7F8C8D; font-size:0.85rem; letter-spacing:1px;">
            FOCUSED {best_track.upper()} STUDENT RATE
        </div>
        <div style="font-size:4rem; font-weight:900; color:#2ECC71; margin:0.5rem 0;">
            {focused_rate}%
        </div>
        <div style="color:#BDC3C7; font-size:0.9rem;">
            Students focused on {best_track} from early semesters
        </div>
    </div>
    """, unsafe_allow_html=True)

# Gap callout
gap = focused_rate - student_rate
if gap > 0:
    st.markdown(f"""
    <div style="background:#E74C3C22; border:1px solid #E74C3C;
                border-radius:8px; padding:1rem; text-align:center;
                margin-top:1rem;">
        <span style="color:#E74C3C; font-size:1.2rem; font-weight:700;">
            ⚠️ The focus gap costs you {gap} percentage points
            in estimated placement probability.
        </span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Side-by-Side Bar Charts ───────────────────────────────────
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("📊 Placement Rate Comparison")

    fig_placement = go.Figure()
    fig_placement.add_trace(go.Bar(
        name="Your Estimated Rate",
        x=["Your Profile"],
        y=[student_rate],
        marker_color=rate_color,
        text=[f"{student_rate}%"],
        textposition="outside",
        textfont=dict(color="#FAFAFA"),
    ))
    fig_placement.add_trace(go.Bar(
        name=f"Focused {best_track} Students",
        x=[f"Focused {best_track}"],
        y=[focused_rate],
        marker_color="#2ECC71",
        text=[f"{focused_rate}%"],
        textposition="outside",
        textfont=dict(color="#FAFAFA"),
    ))
    fig_placement.update_layout(
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font=dict(color="#BDC3C7"),
        yaxis=dict(range=[0, 110], gridcolor="#2D3250", title="Placement Rate (%)"),
        xaxis=dict(gridcolor="#2D3250"),
        legend=dict(bgcolor="#1A1D27", bordercolor="#2D3250"),
        margin=dict(t=20, b=20),
        height=360,
        showlegend=False,
    )
    st.plotly_chart(fig_placement, use_container_width=True)

with col_chart2:
    st.subheader("🏁 Survival Rate by Career Track")
    st.caption(
        "% of students who commit to a track and reach "
        "placement readiness by Semester 8"
    )

    tracks_s  = list(survival_rates.keys())
    rates_s   = list(survival_rates.values())
    bar_colors_s = [
        "#6C63FF" if t == best_track else "#2D3250"
        for t in tracks_s
    ]

    fig_survival = go.Figure(go.Bar(
        x=rates_s,
        y=tracks_s,
        orientation="h",
        marker_color=bar_colors_s,
        text=[f"{r}%" for r in rates_s],
        textposition="outside",
        textfont=dict(color="#BDC3C7"),
    ))
    fig_survival.update_layout(
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font=dict(color="#BDC3C7"),
        xaxis=dict(range=[0, 110], gridcolor="#2D3250", title="Survival Rate (%)"),
        yaxis=dict(gridcolor="#2D3250"),
        margin=dict(t=20, b=20, l=10, r=50),
        height=360,
    )
    st.plotly_chart(fig_survival, use_container_width=True)

st.markdown("---")

# ── Plain English Paragraph ───────────────────────────────────
st.subheader("📝 What These Numbers Mean for You")

track_survival = survival_rates.get(best_track, 60)

if student_rate >= 60:
    overall_tone = (
        f"Your current profile puts you in a relatively strong position. "
        f"Students with a Drift Score of {drift_score} have an estimated "
        f"placement rate of {student_rate}% — above the average for Indian CSE graduates."
    )
elif student_rate >= 40:
    overall_tone = (
        f"Your current profile shows moderate placement risk. "
        f"Students with a Drift Score of {drift_score} have an estimated "
        f"placement rate of {student_rate}% — this is below what focused students achieve "
        f"and leaves significant room for improvement."
    )
else:
    overall_tone = (
        f"Your current profile carries high placement risk. "
        f"Students with a Drift Score of {drift_score} have an estimated "
        f"placement rate of only {student_rate}% — nearly half the rate of "
        f"focused students in your recommended track."
    )

track_tone = (
    f"**{best_track}** has a survival rate of **{track_survival}%**, "
    f"meaning {track_survival} out of every 100 students who commit to this track "
    f"early enough reach placement readiness by Semester 8. "
)

if track_survival >= 70:
    track_tone += (
        "This is one of the more achievable tracks — strong demand and learnable skills."
    )
elif track_survival >= 55:
    track_tone += (
        "This track is achievable with consistent effort but requires focus "
        "from this semester onwards."
    )
else:
    track_tone += (
        "This track requires deep mathematical and technical foundations. "
        "Starting late significantly reduces your probability of reaching readiness. "
        "Consider whether an adjacent track with a higher survival rate "
        "might be more strategic."
    )

action_tone = (
    f"\n\nThe difference between your estimated {student_rate}% and the "
    f"focused student rate of {focused_rate}% is not talent — it is "
    f"time and deliberate focus. Every additional semester of drift "
    f"reduces that gap's recoverability."
)

st.markdown(overall_tone + "\n\n" + track_tone + action_tone)

st.markdown("---")

# ── Placement Rate Lookup Table ───────────────────────────────
with st.expander("📖 View Full Placement Rate Lookup Table (All Drift Score Ranges)"):
    st.markdown(
        "These estimates are based on general industry skill-depth research. "
        "They are labeled as estimates throughout this platform."
    )
    import pandas as pd
    lookup_data = [
        {"Drift Score Range": "80 – 100", "Label": "Highly Focused",
         "Est. Placement Rate": "78%"},
        {"Drift Score Range": "60 – 80",  "Label": "Moderately Focused",
         "Est. Placement Rate": "62%"},
        {"Drift Score Range": "40 – 60",  "Label": "Drifting",
         "Est. Placement Rate": "44%"},
        {"Drift Score Range": "20 – 40",  "Label": "Highly Scattered",
         "Est. Placement Rate": "29%"},
        {"Drift Score Range": "0 – 20",   "Label": "Extremely Scattered",
         "Est. Placement Rate": "18%"},
    ]
    st.dataframe(pd.DataFrame(lookup_data), use_container_width=True, hide_index=True)

st.markdown("---")

# ── Navigation ────────────────────────────────────────────────
col_prev, col_next = st.columns(2)
with col_prev:
    if st.button("← Back to Next Skill", use_container_width=True):
        st.switch_page("pages/06_next_skill.py")
with col_next:
    if st.button("Next → Market Intelligence 🗺️", type="primary", use_container_width=True):
        st.switch_page("pages/08_market_intel.py")