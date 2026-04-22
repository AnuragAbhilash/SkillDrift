# pages/05_career_match.py

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from brain import CAREER_TRACKS, load_required_skills, TRACK_TO_ROLE
from _sidebar import APPLE_CSS, render_sidebar

st.set_page_config(
    page_title="SkillDrift — Career Track Match",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(APPLE_CSS, unsafe_allow_html=True)

if not st.session_state.get("student_name"):
    st.warning("Session not found. Please start from the beginning.")
    st.switch_page("pages/02_skill_input.py")

render_sidebar()

career_matches  = st.session_state.get("career_matches", [])
verified_skills = st.session_state.get("verified_skills", {})

if not career_matches:
    st.warning("Career match data not found. Please complete the quiz first.")
    st.stop()

best_match     = career_matches[0]
best_track     = best_match.get("track", "Unknown")
best_match_pct = best_match.get("match_pct", 0.0)
matched_skills = best_match.get("matched_skills", [])
missing_skills = best_match.get("missing_skills", [])
tied_matches   = [m for m in career_matches if m["match_pct"] == best_match_pct]

st.markdown("""
<div style="margin-bottom:1.25rem;">
    <div style="font-size:1.6rem; font-weight:700; color:#1D1D1F;">Career Track Match</div>
    <div style="font-size:0.88rem; color:#86868B; margin-top:0.2rem;">
        Your verified skills matched against 8 CSE career tracks — built from 794 real Indian job postings.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Best Match Card ───────────────────────────────────────────
if len(tied_matches) > 1:
    tied_names = " and ".join([m["track"] for m in tied_matches])
    st.markdown(f"""
    <div style="background:#FFFFFF; border:2px solid #FF9500; border-radius:14px;
                padding:1.5rem; margin-bottom:1rem; box-shadow:0 1px 8px rgba(0,0,0,0.05);">
        <div style="color:#FF9500; font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.8px;">
            Tie — Two Tracks Equally Matched
        </div>
        <div style="font-size:1.8rem; font-weight:700; color:#1D1D1F; margin-top:0.35rem;">{tied_names}</div>
        <div style="color:#86868B; font-size:0.88rem; margin-top:0.35rem;">
            Both match at <strong style="color:#1D1D1F;">{best_match_pct}%</strong>.
            Review the gap analysis for each and pick the one whose missing skills you want to learn.
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    pct_color = "#34C759" if best_match_pct >= 60 else "#FF9500" if best_match_pct >= 35 else "#FF3B30"
    st.markdown(f"""
    <div style="background:#FFFFFF; border:2px solid {pct_color}; border-radius:14px;
                padding:1.5rem; margin-bottom:1rem; box-shadow:0 1px 8px rgba(0,0,0,0.05);">
        <div style="color:#86868B; font-size:0.7rem; font-weight:600; text-transform:uppercase; letter-spacing:0.8px;">
            Your Best Matching Career Track
        </div>
        <div style="font-size:1.9rem; font-weight:700; color:#1D1D1F; margin-top:0.25rem;">{best_track}</div>
        <div style="font-size:2.5rem; font-weight:700; color:{pct_color}; line-height:1.1;">{best_match_pct}% Match</div>
        <div style="color:#86868B; font-size:0.85rem; margin-top:0.35rem;">
            {len(matched_skills)} of the required skills for this track are in your verified profile.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.progress(int(best_match_pct) / 100)
st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

# ── All 8 Tracks Chart ────────────────────────────────────────
st.markdown("""
<div style="font-size:0.88rem; font-weight:600; color:#1D1D1F; margin-bottom:0.75rem;">
    All 8 Career Tracks — Your Match Percentage
</div>
""", unsafe_allow_html=True)

tracks_sorted   = [m["track"]     for m in career_matches]
percents_sorted = [m["match_pct"] for m in career_matches]
bar_colors = ["#6C63FF" if m["track"] == best_track else "#D2D2D7" for m in career_matches]

fig_tracks = go.Figure(go.Bar(
    x=percents_sorted, y=tracks_sorted, orientation="h",
    marker_color=bar_colors,
    text=[f"{p}%" for p in percents_sorted],
    textposition="outside",
    textfont=dict(color="#1D1D1F", size=11),
))
fig_tracks.update_layout(
    paper_bgcolor="#FFFFFF", plot_bgcolor="#F5F5F7",
    font=dict(color="#1D1D1F", size=11),
    xaxis=dict(range=[0, 115], gridcolor="#D2D2D7", title="Match %", color="#86868B"),
    yaxis=dict(gridcolor="#D2D2D7", color="#1D1D1F"),
    margin=dict(l=10, r=50, t=15, b=15),
    height=340,
)
st.plotly_chart(fig_tracks, use_container_width=True)

# ── 2nd & 3rd Best ────────────────────────────────────────────
if len(career_matches) >= 3:
    st.markdown("""
    <div style="font-size:0.88rem; font-weight:600; color:#1D1D1F; margin-bottom:0.6rem;">
        Second and Third Best Matches
    </div>
    """, unsafe_allow_html=True)
    col2, col3 = st.columns(2, gap="medium")
    for col, rank_label, match in [
        (col2, "2nd Best", career_matches[1]),
        (col3, "3rd Best", career_matches[2]),
    ]:
        with col:
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #D2D2D7; border-radius:12px;
                        padding:1.1rem; box-shadow:0 1px 6px rgba(0,0,0,0.04);">
                <div style="color:#86868B; font-size:0.68rem; font-weight:600; text-transform:uppercase;">{rank_label}</div>
                <div style="font-size:1.2rem; font-weight:700; color:#1D1D1F; margin-top:0.2rem;">{match['track']}</div>
                <div style="font-size:1.7rem; font-weight:700; color:#6C63FF;">{match['match_pct']}%</div>
                <div style="color:#86868B; font-size:0.82rem;">{len(match['matched_skills'])} skills matched</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<hr style='border:none; border-top:1px solid #D2D2D7; margin:1.5rem 0;'>",
            unsafe_allow_html=True)

# ── Gap Analysis ──────────────────────────────────────────────
st.markdown(f"""
<div style="font-size:0.88rem; font-weight:600; color:#1D1D1F; margin-bottom:0.3rem;">
    Gap Analysis — {best_track}
</div>
<div style="font-size:0.82rem; color:#86868B; margin-bottom:0.75rem;">
    Every required skill for {best_track} is listed below.
    Red = missing from your verified profile.
</div>
""", unsafe_allow_html=True)

required_df  = load_required_skills()
role_name    = TRACK_TO_ROLE.get(best_track, best_track)
track_req_df = required_df[required_df["track"] == role_name].copy()
track_req_df = track_req_df.sort_values("frequency_pct", ascending=False)

verified_lower = [s.lower() for s in verified_skills.keys()]

gap_rows = []
for _, row in track_req_df.iterrows():
    skill_name = row["skill"]
    freq_pct   = row["frequency_pct"]
    have_it    = skill_name.lower() in verified_lower
    gap_rows.append({
        "Status":         "Have It" if have_it else "Missing",
        "Skill":          skill_name,
        "Appears In JDs": f"{freq_pct:.1f}%",
        "Priority":       "High" if freq_pct >= 30 else "Medium" if freq_pct >= 15 else "Low",
    })

gap_df = pd.DataFrame(gap_rows)

def color_status(val):
    if val == "Have It":
        return "color: #34C759; font-weight: 700"
    elif val == "Missing":
        return "color: #FF3B30; font-weight: 700"
    return ""

styled_df = gap_df.style.map(color_status, subset=["Status"])
st.dataframe(styled_df, use_container_width=True, hide_index=True)

# ── Tied Tracks ───────────────────────────────────────────────
if len(tied_matches) > 1:
    st.markdown("<hr style='border:none; border-top:1px solid #D2D2D7; margin:1.25rem 0;'>",
                unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.88rem; font-weight:600; color:#1D1D1F; margin-bottom:0.75rem;">
        Gap Analysis for All Tied Tracks
    </div>
    """, unsafe_allow_html=True)
    tied_tabs = st.tabs([m["track"] for m in tied_matches])
    for tab, match in zip(tied_tabs, tied_matches):
        with tab:
            role_n   = TRACK_TO_ROLE.get(match["track"], match["track"])
            req_df_t = required_df[required_df["track"] == role_n].copy()
            req_df_t = req_df_t.sort_values("frequency_pct", ascending=False)
            rows_t = []
            for _, row in req_df_t.iterrows():
                have = row["skill"].lower() in verified_lower
                rows_t.append({
                    "Status":         "Have It" if have else "Missing",
                    "Skill":          row["skill"],
                    "Appears In JDs": f"{row['frequency_pct']:.1f}%",
                })
            styled_t = pd.DataFrame(rows_t).style.map(color_status, subset=["Status"])
            st.dataframe(styled_t, use_container_width=True, hide_index=True)

st.markdown("<hr style='border:none; border-top:1px solid #D2D2D7; margin:1.5rem 0;'>",
            unsafe_allow_html=True)

col_prev, col_next = st.columns(2)
with col_prev:
    if st.button("Back — Urgency Engine", use_container_width=True):
        st.switch_page("pages/04_urgency.py")
with col_next:
    if st.button("Next — Next Skill & Readiness", type="primary", use_container_width=True):
        st.switch_page("pages/06_next_skill.py")
