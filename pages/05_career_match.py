# Window 5 - Career Match 
# =============================================================
# pages/05_career_match.py — Window 5: Career Track Match
# Shows match percentages for all 8 tracks and gap analysis.
# =============================================================

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from brain import CAREER_TRACKS

st.set_page_config(
    page_title="SkillDrift — Career Track Match",
    page_icon="🏆",
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

st.title("🏆 Career Track Match")
st.markdown(
    "Your verified skills are matched against the required skill lists "
    "for all 8 CSE career tracks, built from 794 real Indian job postings."
)
st.markdown("---")

career_matches = st.session_state.get("career_matches", [])
verified_skills = st.session_state.get("verified_skills", {})

if not career_matches:
    st.warning("⚠️ Career match data not found. Please complete the quiz first.")
    st.stop()

best_match      = career_matches[0]
best_track      = best_match.get("track", "Unknown")
best_match_pct  = best_match.get("match_pct", 0.0)
matched_skills  = best_match.get("matched_skills", [])
missing_skills  = best_match.get("missing_skills", [])

# Check for tie at rank 1
tied_matches = [m for m in career_matches if m["match_pct"] == best_match_pct]

# ── Best Match Hero Card ──────────────────────────────────────
if len(tied_matches) > 1:
    tied_names = " and ".join([m["track"] for m in tied_matches])
    st.markdown(f"""
    <div style="background:#1A1D27; border:2px solid #F39C12;
                border-radius:12px; padding:1.5rem; margin-bottom:1rem;">
        <div style="color:#F39C12; font-size:0.9rem; font-weight:700;">
            🤝 TIE — Two Tracks Equally Matched
        </div>
        <div style="font-size:2rem; font-weight:900; color:#FAFAFA; margin-top:0.5rem;">
            {tied_names}
        </div>
        <div style="color:#BDC3C7; margin-top:0.5rem;">
            Both tracks match at <strong>{best_match_pct}%</strong>.
            Review the gap analysis for each and pick the one whose
            missing skills you are more interested in learning.
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    pct_color = (
        "#2ECC71" if best_match_pct >= 60
        else "#F39C12" if best_match_pct >= 35
        else "#E74C3C"
    )
    st.markdown(f"""
    <div style="background:#1A1D27; border:2px solid {pct_color};
                border-radius:12px; padding:1.5rem; margin-bottom:1rem;">
        <div style="color:#7F8C8D; font-size:0.9rem;">
            🏆 YOUR BEST MATCHING CAREER TRACK
        </div>
        <div style="font-size:2.5rem; font-weight:900; color:#FAFAFA; margin-top:0.25rem;">
            {best_track}
        </div>
        <div style="font-size:3rem; font-weight:900; color:{pct_color};">
            {best_match_pct}% Match
        </div>
        <div style="color:#BDC3C7; font-size:0.9rem;">
            {len(matched_skills)} of the required skills for this track
            are already in your verified profile.
        </div>
    </div>
    """, unsafe_allow_html=True)

# Progress bar for best match
st.progress(int(best_match_pct) / 100)

st.markdown("<br>", unsafe_allow_html=True)

# ── All 8 Tracks Ranked ───────────────────────────────────────
st.subheader("📊 All 8 Career Tracks — Your Match Percentage")

tracks_sorted  = [m["track"]     for m in career_matches]
percents_sorted = [m["match_pct"] for m in career_matches]
bar_colors = [
    "#6C63FF" if m["track"] == best_track else "#2D3250"
    for m in career_matches
]

fig_tracks = go.Figure(go.Bar(
    x=percents_sorted,
    y=tracks_sorted,
    orientation="h",
    marker_color=bar_colors,
    text=[f"{p}%" for p in percents_sorted],
    textposition="outside",
    textfont=dict(color="#BDC3C7"),
))

fig_tracks.update_layout(
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    font=dict(color="#BDC3C7"),
    xaxis=dict(
        range=[0, 110],
        gridcolor="#2D3250",
        title="Match Percentage",
    ),
    yaxis=dict(gridcolor="#2D3250"),
    margin=dict(l=20, r=60, t=20, b=20),
    height=400,
)

st.plotly_chart(fig_tracks, use_container_width=True)

# ── Second and Third Best Matches ─────────────────────────────
if len(career_matches) >= 3:
    st.subheader("🥈 Second and Third Best Matches")
    col2, col3 = st.columns(2)

    second = career_matches[1]
    third  = career_matches[2]

    with col2:
        st.markdown(f"""
        <div style="background:#1A1D27; border:1px solid #2D3250;
                    border-radius:10px; padding:1rem;">
            <div style="color:#7F8C8D; font-size:0.8rem;">2nd BEST MATCH</div>
            <div style="font-size:1.4rem; font-weight:700; color:#FAFAFA;">
                {second['track']}
            </div>
            <div style="font-size:1.8rem; font-weight:900; color:#6C63FF;">
                {second['match_pct']}%
            </div>
            <div style="color:#BDC3C7; font-size:0.85rem;">
                {len(second['matched_skills'])} skills matched
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="background:#1A1D27; border:1px solid #2D3250;
                    border-radius:10px; padding:1rem;">
            <div style="color:#7F8C8D; font-size:0.8rem;">3rd BEST MATCH</div>
            <div style="font-size:1.4rem; font-weight:700; color:#FAFAFA;">
                {third['track']}
            </div>
            <div style="font-size:1.8rem; font-weight:900; color:#6C63FF;">
                {third['match_pct']}%
            </div>
            <div style="color:#BDC3C7; font-size:0.85rem;">
                {len(third['matched_skills'])} skills matched
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ── Gap Analysis Table for Best Track ────────────────────────
st.subheader(f"🔍 Gap Analysis — {best_track}")
st.markdown(
    f"Every required skill for **{best_track}** is listed below. "
    "Green means you have it. Red means it is missing from your verified profile."
)

# Build full required skill list for best track
from brain import load_required_skills, TRACK_TO_ROLE
required_df = load_required_skills()
role_name   = TRACK_TO_ROLE.get(best_track, best_track)
track_req_df = required_df[required_df["track"] == role_name].copy()
track_req_df = track_req_df.sort_values("frequency_pct", ascending=False)

verified_lower = [s.lower() for s in verified_skills.keys()]

gap_rows = []
for _, row in track_req_df.iterrows():
    skill_name = row["skill"]
    freq_pct   = row["frequency_pct"]
    have_it    = skill_name.lower() in verified_lower

    gap_rows.append({
        "Status":         "✅ Have It" if have_it else "❌ Missing",
        "Skill":          skill_name,
        "Appears In JDs": f"{freq_pct:.1f}%",
        "Priority":       "High" if freq_pct >= 30 else "Medium" if freq_pct >= 15 else "Low",
    })

gap_df = pd.DataFrame(gap_rows)

# Color rows using dataframe styling
def color_status(val):
    if "✅" in str(val):
        return "color: #2ECC71; font-weight: 700"
    elif "❌" in str(val):
        return "color: #E74C3C; font-weight: 700"
    return ""

styled_df = gap_df.style.applymap(color_status, subset=["Status"])
st.dataframe(styled_df, use_container_width=True, hide_index=True)

# ── Gap Analysis for Tied Tracks ─────────────────────────────
if len(tied_matches) > 1:
    st.markdown("---")
    st.subheader("🤝 Gap Analysis for All Tied Tracks")
    st.markdown("Compare the missing skills for each tied track to decide which to pursue.")

    tied_tabs = st.tabs([m["track"] for m in tied_matches])
    for tab, match in zip(tied_tabs, tied_matches):
        with tab:
            role_n   = TRACK_TO_ROLE.get(match["track"], match["track"])
            req_df_t = required_df[required_df["track"] == role_n].copy()
            req_df_t = req_df_t.sort_values("frequency_pct", ascending=False)

            rows_t = []
            for _, row in req_df_t.iterrows():
                sn   = row["skill"]
                fp   = row["frequency_pct"]
                have = sn.lower() in verified_lower
                rows_t.append({
                    "Status":         "✅ Have It" if have else "❌ Missing",
                    "Skill":          sn,
                    "Appears In JDs": f"{fp:.1f}%",
                })
            st.dataframe(pd.DataFrame(rows_t), use_container_width=True, hide_index=True)

st.markdown("---")

# ── Navigation ────────────────────────────────────────────────
col_prev, col_next = st.columns(2)
with col_prev:
    if st.button("← Back to Urgency Engine", use_container_width=True):
        st.switch_page("pages/04_urgency.py")
with col_next:
    if st.button("Next → Next Skill & Readiness 📚", type="primary", use_container_width=True):
        st.switch_page("pages/06_next_skill.py")