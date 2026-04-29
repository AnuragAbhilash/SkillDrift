# pages/05_career_match.py

import streamlit as st
from session_store import init_session
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

init_session()
st.session_state["_current_page"] = "career"
st.markdown(APPLE_CSS, unsafe_allow_html=True)
render_sidebar()

if not st.session_state.get("student_name"):
    st.warning("Session not found. Please start from the beginning.")
    st.switch_page("pages/02_skill_input.py")
    st.stop()

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

# ── Page Title ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:1.25rem;">
    <div style="font-size:1.5rem;font-weight:800;color:#171c1f;font-family:'Manrope',sans-serif;">
        Career Track Match
    </div>
    <div style="font-size:0.875rem;color:#515f74;margin-top:5px;">
        Your skills matched against 8 real CSE careers — based on 1600 actual Indian job postings.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Best Match Card ────────────────────────────────────────────────────────────
if len(tied_matches) > 1:
    tied_names = " and ".join([m["track"] for m in tied_matches])
    st.markdown(f"""
    <div style="background:#FFFFFF;border:2px solid #d97706;border-radius:14px;
                padding:1.5rem;margin-bottom:1rem;box-shadow:0 1px 8px rgba(0,0,0,0.05);">
        <div style="color:#d97706;font-size:0.72rem;font-weight:700;
                    text-transform:uppercase;letter-spacing:0.8px;">
            Two tracks tied at the same score
        </div>
        <div style="font-size:1.8rem;font-weight:700;color:#171c1f;margin-top:0.35rem;">
            {tied_names}
        </div>
        <div style="color:#515f74;font-size:0.88rem;margin-top:0.35rem;">
            Both match at <strong style="color:#171c1f;">{best_match_pct}%</strong>.
            Look at the gap table below and pick whichever track's missing skills
            you actually want to learn.
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    pct_color = "#15803d" if best_match_pct >= 60 else "#d97706" if best_match_pct >= 35 else "#ba1a1a"
    st.markdown(f"""
    <div style="background:#FFFFFF;border:2px solid {pct_color};border-radius:14px;
                padding:1.5rem;margin-bottom:1rem;box-shadow:0 1px 8px rgba(0,0,0,0.05);">
        <div style="color:#515f74;font-size:0.72rem;font-weight:600;
                    text-transform:uppercase;letter-spacing:0.8px;">
            Your Best Matching Career
        </div>
        <div style="font-size:2rem;font-weight:800;color:#171c1f;margin-top:0.25rem;">
            {best_track}
        </div>
        <div style="font-size:2.5rem;font-weight:800;color:{pct_color};line-height:1.15;">
            {best_match_pct}% Match
        </div>
        <div style="color:#515f74;font-size:0.85rem;margin-top:0.35rem;">
            {len(matched_skills)} of the required skills for this role are already in your profile.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.progress(int(best_match_pct) / 100)
st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

# ── All 8 Tracks Chart ─────────────────────────────────────────────────────────
st.markdown("""
<div style="font-size:0.95rem;font-weight:700;color:#171c1f;margin-bottom:4px;">
    How You Compare Across All 8 Tracks
</div>
<div style="font-size:0.82rem;color:#515f74;margin-bottom:12px;">
    Purple bar is your best match. The longer the bar, the more of that career's skills you already have.
</div>
""", unsafe_allow_html=True)

tracks_sorted   = [m["track"]     for m in career_matches]
percents_sorted = [m["match_pct"] for m in career_matches]
bar_colors      = ["#002c98" if m["track"] == best_track else "#94a3b8" for m in career_matches]

fig_tracks = go.Figure(go.Bar(
    x=percents_sorted, y=tracks_sorted, orientation="h",
    marker_color=bar_colors,
    text=[f"{p}%" for p in percents_sorted],
    textposition="outside",
    textfont=dict(color="#171c1f", size=11),
))
fig_tracks.update_layout(
    paper_bgcolor="#FFFFFF", plot_bgcolor="#f8fafc",
    font=dict(color="#171c1f", size=11, family="Inter"),
    xaxis=dict(range=[0, 118], gridcolor="#e2e8f0", title="Match %", color="#515f74"),
    yaxis=dict(gridcolor="#e2e8f0", color="#171c1f"),
    margin=dict(l=10, r=50, t=10, b=10),
    height=330,
    showlegend=False,
)
st.plotly_chart(fig_tracks, use_container_width=True)

# ── 2nd and 3rd Best ───────────────────────────────────────────────────────────
if len(career_matches) >= 3:
    st.markdown("""
    <div style="font-size:0.95rem;font-weight:700;color:#171c1f;margin-bottom:10px;">
        Your Next Best Options
    </div>
    """, unsafe_allow_html=True)
    col2, col3 = st.columns(2, gap="medium")
    for col, rank_label, match in [
        (col2, "2nd Best Match", career_matches[1]),
        (col3, "3rd Best Match", career_matches[2]),
    ]:
        with col:
            st.markdown(f"""
            <div style="background:#FFFFFF;border:1px solid #e2e8f0;border-radius:12px;
                        padding:1.1rem;box-shadow:0 1px 6px rgba(0,0,0,0.04);">
                <div style="color:#515f74;font-size:0.68rem;font-weight:600;
                            text-transform:uppercase;">{rank_label}</div>
                <div style="font-size:1.2rem;font-weight:700;color:#171c1f;
                            margin-top:0.2rem;">{match['track']}</div>
                <div style="font-size:1.7rem;font-weight:700;color:#002c98;">
                    {match['match_pct']}%
                </div>
                <div style="color:#515f74;font-size:0.82rem;">
                    {len(match['matched_skills'])} skills already matched
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:1.5rem 0;'>",
            unsafe_allow_html=True)

# ── Gap Table ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="font-size:0.95rem;font-weight:700;color:#171c1f;margin-bottom:4px;">
    Skills Gap for {best_track}
</div>
<div style="font-size:0.82rem;color:#515f74;margin-bottom:12px;">
    Every skill this career needs. Green means you have it. Red means you are missing it.
    The % shows how often companies ask for each skill.
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
        "Status":                "Have It" if have_it else "Missing",
        "Skill":                 skill_name,
        "Companies Asking For":  f"{freq_pct:.1f}%",
        "Priority":              "High" if freq_pct >= 30 else "Medium" if freq_pct >= 15 else "Low",
    })

gap_df = pd.DataFrame(gap_rows)

def color_status(val):
    if val == "Have It":
        return "color: #15803d; font-weight: 700"
    elif val == "Missing":
        return "color: #ba1a1a; font-weight: 700"
    return ""

styled_df = gap_df.style.map(color_status, subset=["Status"])
st.dataframe(styled_df, use_container_width=True, hide_index=True)

# ── Tied Tracks ────────────────────────────────────────────────────────────────
if len(tied_matches) > 1:
    st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:1.25rem 0;'>",
                unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.95rem;font-weight:700;color:#171c1f;margin-bottom:10px;">
        Gap Tables for All Tied Tracks
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
                    "Status":                "Have It" if have else "Missing",
                    "Skill":                 row["skill"],
                    "Companies Asking For":  f"{row['frequency_pct']:.1f}%",
                })
            styled_t = pd.DataFrame(rows_t).style.map(color_status, subset=["Status"])
            st.dataframe(styled_t, use_container_width=True, hide_index=True)

st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:1.5rem 0;'>",
            unsafe_allow_html=True)

col_prev, col_next = st.columns(2)
with col_prev:
    if st.button("Back — Time Left", use_container_width=True):
        st.switch_page("pages/04_urgency.py")
with col_next:
    if st.button("Next — Next Skill to Learn", type="primary", use_container_width=True):
        st.switch_page("pages/06_next_skill.py")
