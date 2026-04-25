# pages/10_final_report.py

import streamlit as st
from session_store import init_session
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from brain import generate_student_report_csv, CAREER_TRACKS
from _sidebar import APPLE_CSS, render_sidebar

st.set_page_config(
    page_title="SkillDrift — Final Report",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session()
st.session_state["_current_page"] = "report"
st.markdown(APPLE_CSS, unsafe_allow_html=True)
render_sidebar()

if not st.session_state.get("student_name"):
    st.warning("Session not found. Please start from the beginning.")
    st.switch_page("pages/02_skill_input.py")


student_name    = st.session_state.get("student_name", "")
semester        = st.session_state.get("semester", "?")
drift_score     = st.session_state.get("drift_score")     or 0
drift_label     = st.session_state.get("drift_label")     or ""
entropy_score   = st.session_state.get("entropy_score")   or 0
entropy_label   = st.session_state.get("entropy_label")   or ""
best_track      = st.session_state.get("best_track",      "Unknown")
match_pct       = st.session_state.get("match_pct",       0)
readiness_score = st.session_state.get("readiness_score") or 0
next_skill_info = st.session_state.get("next_skill_info", {})
urgency_info    = st.session_state.get("urgency_info",    {})
focus_debt_info = st.session_state.get("focus_debt_info", {})
peer_info       = st.session_state.get("peer_info",       {})
verified_skills = st.session_state.get("verified_skills", {})
career_matches  = st.session_state.get("career_matches",  [])

next_skill       = next_skill_info.get("skill", "N/A")          if next_skill_info else "N/A"
urgency_level    = urgency_info.get("urgency_level", "Unknown")  if urgency_info    else "Unknown"
focus_debt_hours = focus_debt_info.get("focus_debt_hours", 0)   if focus_debt_info else 0
days_to_recover  = focus_debt_info.get("days_to_recover", 0)    if focus_debt_info else 0

URGENCY_COLOR_MAP = {"Green": "#34C759", "Yellow": "#FF9500", "Red": "#FF3B30"}
urgency_color = URGENCY_COLOR_MAP.get(urgency_level, "#6C63FF")
today_str     = datetime.now().strftime("%Y-%m-%d")

st.markdown("""
<div style="margin-bottom:1.25rem;">
    <div style="font-size:1.6rem; font-weight:700; color:#1D1D1F;">Your SkillDrift Report Card</div>
    <div style="font-size:0.88rem; color:#86868B; margin-top:0.2rem;">
        Everything SkillDrift calculated about your career readiness — in one place.
        Download and share with your placement cell.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Identity Card — compact ───────────────────────────────────
st.markdown(f"""
<div style="background:#FFFFFF; border:2px solid #6C63FF; border-radius:14px;
            padding:1.1rem 1.4rem; box-shadow:0 1px 10px rgba(108,99,255,0.08);
            margin-bottom:1.25rem; display:flex; align-items:center; gap:1rem;">
    <div style="width:44px; height:44px; border-radius:50%; background:#F0EFFF;
                display:flex; align-items:center; justify-content:center; flex-shrink:0;">
        <svg width="26" height="26" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
            <circle cx="40" cy="28" r="18" fill="#6C63FF"/>
            <ellipse cx="40" cy="66" rx="26" ry="17" fill="#6C63FF"/>
        </svg>
    </div>
    <div>
        <div style="font-size:1.25rem; font-weight:700; color:#1D1D1F; line-height:1.2;">
            {student_name}
        </div>
        <div style="color:#86868B; font-size:0.82rem; margin-top:0.15rem;">
            Semester {semester} &nbsp;|&nbsp; Report generated {today_str} &nbsp;|&nbsp;
            <span style="color:#6C63FF;">SkillDrift Career Focus Analyzer</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Summary ───────────────────────────────────────────────────
st.markdown("""
<div style="font-size:0.88rem; font-weight:600; color:#1D1D1F; margin-bottom:0.75rem;">
    Complete Analysis Summary
</div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns(2, gap="large")

def report_row(label: str, value: str, value_color: str = "#1D1D1F") -> str:
    return f"""
    <div style="background:#FFFFFF; border:1px solid #D2D2D7; border-radius:9px;
                padding:0.7rem 1rem; margin:0.25rem 0;
                display:flex; justify-content:space-between; align-items:center;">
        <div style="color:#86868B; font-size:0.85rem;">{label}</div>
        <div style="color:{value_color}; font-weight:600; font-size:0.88rem;
                    text-align:right; max-width:55%;">{value}</div>
    </div>
    """

ds_color = "#34C759" if drift_score <= 20 else "#FF9500" if drift_score <= 60 else "#FF3B30"
es_color = "#34C759" if entropy_score < 1.2 else "#FF9500" if entropy_score < 2.0 else "#FF3B30"
rs_color = "#34C759" if readiness_score >= 70 else "#FF9500" if readiness_score >= 40 else "#FF3B30"

with col_left:
    st.markdown("""<div style="font-size:0.78rem; font-weight:600; color:#86868B;
                    text-transform:uppercase; letter-spacing:0.8px; margin-bottom:0.4rem;">
                    Skill Analysis</div>""", unsafe_allow_html=True)
    st.markdown(
        report_row("Drift Score", f"{drift_score} — {drift_label}", ds_color),
        unsafe_allow_html=True,
    )
    st.markdown(
        report_row("Entropy Score", f"{entropy_score} bits — {entropy_label}", es_color),
        unsafe_allow_html=True,
    )
    st.markdown(
        report_row("Verified Skills", f"{len(verified_skills)} skills confirmed"),
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:0.6rem;'></div>", unsafe_allow_html=True)
    st.markdown("""<div style="font-size:0.78rem; font-weight:600; color:#86868B;
                    text-transform:uppercase; letter-spacing:0.8px; margin-bottom:0.4rem;">
                    Career Match</div>""", unsafe_allow_html=True)
    st.markdown(
        report_row("Best Career Track", best_track, "#6C63FF"),
        unsafe_allow_html=True,
    )
    st.markdown(
        report_row("Match Percentage", f"{match_pct}%", "#6C63FF"),
        unsafe_allow_html=True,
    )
    st.markdown(
        report_row("Readiness Score", f"{readiness_score}%", rs_color),
        unsafe_allow_html=True,
    )

with col_right:
    st.markdown("""<div style="font-size:0.78rem; font-weight:600; color:#86868B;
                    text-transform:uppercase; letter-spacing:0.8px; margin-bottom:0.4rem;">
                    Action Plan</div>""", unsafe_allow_html=True)
    st.markdown(
        report_row("Next Skill to Learn", next_skill, "#FF9500"),
        unsafe_allow_html=True,
    )
    st.markdown(
        report_row("Urgency Level", urgency_level, urgency_color),
        unsafe_allow_html=True,
    )
    st.markdown(
        report_row(
            "Focus Debt",
            f"{focus_debt_hours} hrs ({days_to_recover} days at 2 hrs/day)",
            "#FF3B30" if focus_debt_hours > 60 else "#FF9500",
        ),
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:0.6rem;'></div>", unsafe_allow_html=True)
    st.markdown("""<div style="font-size:0.78rem; font-weight:600; color:#86868B;
                    text-transform:uppercase; letter-spacing:0.8px; margin-bottom:0.4rem;">
                    Top Missing Skills</div>""", unsafe_allow_html=True)

    best_match_data = career_matches[0] if career_matches else {}
    missing_skills  = best_match_data.get("missing_skills", [])

    if missing_skills:
        for i, ms in enumerate(missing_skills[:5], start=1):
            st.markdown(
                report_row(f"#{i} Missing", f"{ms['skill']} ({ms['frequency_pct']:.1f}% of JDs)", "#FF3B30"),
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            report_row("Missing Skills", "None — All required skills verified", "#34C759"),
            unsafe_allow_html=True,
        )

st.markdown("<hr style='border:none; border-top:1px solid #D2D2D7; margin:1.5rem 0;'>",
            unsafe_allow_html=True)

# ── Verified Skill Profile ────────────────────────────────────
st.markdown("""
<div style="font-size:0.88rem; font-weight:600; color:#1D1D1F; margin-bottom:0.5rem;">
    Your Verified Skill Profile
</div>
""", unsafe_allow_html=True)

if verified_skills:
    quiz_results = st.session_state.get("quiz_results", [])
    status_map   = {r["skill"]: r["status"] for r in quiz_results} if quiz_results else {}

    skill_rows = []
    for skill, level in verified_skills.items():
        status = status_map.get(skill, "Confirmed")
        skill_rows.append({
            "Skill":          skill,
            "Verified Level": level,
            "Quiz Status":    {"Confirmed": "Confirmed", "Downgraded": "Downgraded",
                               "Unverified": "Unverified"}.get(status, "Confirmed"),
        })
    st.dataframe(pd.DataFrame(skill_rows), use_container_width=True, hide_index=True)
else:
    st.warning("No verified skills found in this session.")

st.markdown("<hr style='border:none; border-top:1px solid #D2D2D7; margin:1.5rem 0;'>",
            unsafe_allow_html=True)

# ── Download ──────────────────────────────────────────────────
st.markdown("""
<div style="font-size:0.88rem; font-weight:600; color:#1D1D1F; margin-bottom:0.5rem;">
    Download Your Report
</div>
""", unsafe_allow_html=True)

session_data = {
    "student_name": student_name, "semester": semester,
    "drift_score": drift_score, "drift_label": drift_label,
    "entropy_score": entropy_score, "entropy_label": entropy_label,
    "best_track": best_track, "match_pct": match_pct,
    "readiness_score": readiness_score, "next_skill": next_skill,
    "urgency_level": urgency_level, "focus_debt_hours": focus_debt_hours,
    "verified_skills": verified_skills,
}

csv_string    = generate_student_report_csv(session_data)
csv_bytes     = csv_string.encode("utf-8")
name_for_file = student_name.strip().replace(" ", "_")
date_for_file = datetime.now().strftime("%Y_%m_%d")
filename      = f"SkillDrift_Report_{name_for_file}_{date_for_file}.csv"

col_dl, col_info = st.columns([2, 3])
with col_dl:
    st.download_button(
        label="Download Report as CSV",
        data=csv_bytes,
        file_name=filename,
        mime="text/csv",
        use_container_width=True,
        type="primary",
    )
with col_info:
    st.markdown("""
    <div style="background:#FFFFFF; border:1px solid #D2D2D7; border-radius:10px;
                padding:0.9rem 1rem; font-size:0.85rem; color:#86868B; line-height:1.7;">
        <strong style="color:#1D1D1F;">What to do with this file</strong><br>
        Email it to your college placement cell &nbsp;|&nbsp;
        Upload to the Faculty Dashboard when requested &nbsp;|&nbsp;
        Share with your mentor or career advisor
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border:none; border-top:1px solid #D2D2D7; margin:1.5rem 0;'>",
            unsafe_allow_html=True)

# ── Quick Share ───────────────────────────────────────────────
st.markdown("""
<div style="font-size:0.88rem; font-weight:600; color:#1D1D1F; margin-bottom:0.3rem;">
    Quick Share Summary
</div>
<div style="font-size:0.82rem; color:#86868B; margin-bottom:0.5rem;">
    Copy and paste this anywhere — email, WhatsApp, or Telegram.
</div>
""", unsafe_allow_html=True)

peer_rate    = peer_info.get("student_placement_rate", "N/A") if peer_info else "N/A"
plain_summary = f"""SkillDrift Career Report — {student_name}
Generated: {today_str}

Student Name   : {student_name}
Semester       : {semester}

SKILL ANALYSIS
Drift Score    : {drift_score} / 100 ({drift_label})
Entropy Score  : {entropy_score} bits ({entropy_label})
Verified Skills: {len(verified_skills)}

CAREER MATCH
Best Track     : {best_track}
Match %        : {match_pct}%
Readiness      : {readiness_score}%

ACTION PLAN
Next Skill     : {next_skill}
Urgency        : {urgency_level}
Focus Debt     : {focus_debt_hours} hours

Est. Placement Rate (current profile): {peer_rate}%

Generated by SkillDrift — Career Focus Analyzer for B.Tech CSE Students"""

st.code(plain_summary, language=None)

st.markdown("<hr style='border:none; border-top:1px solid #D2D2D7; margin:1.5rem 0;'>",
            unsafe_allow_html=True)

# ── What to Do Next ───────────────────────────────────────────
st.markdown("""
<div style="font-size:0.88rem; font-weight:600; color:#1D1D1F; margin-bottom:0.6rem;">
    What Should You Do Next?
</div>
""", unsafe_allow_html=True)

if readiness_score >= 70:
    st.success(
        f"You are approaching placement readiness for {best_track}. "
        f"Your {readiness_score}% readiness puts you ahead of most peers. "
        f"Deepen your top skills to Advanced level and build one complete end-to-end project."
    )
elif readiness_score >= 40:
    st.warning(
        f"You are partially ready for {best_track}. "
        f"At {readiness_score}%, you have a foundation but gaps remain. "
        f"Start with {next_skill} today — it has the highest impact on your track. "
        f"Stop adding new technologies until your readiness crosses 70%."
    )
else:
    st.error(
        f"Your {readiness_score}% readiness requires urgent action. "
        f"You are not yet competitive for {best_track} placements at this trajectory. "
        f"Open a free course on {next_skill} and commit to it for 30 days exclusively. "
        f"Share this report with your mentor and placement cell immediately."
    )

st.markdown("<div style='height:0.75rem;'></div>", unsafe_allow_html=True)

col_prev, col_restart = st.columns(2)
with col_prev:
    if st.button("Back — Market Intelligence", use_container_width=True):
        st.switch_page("pages/08_market_intel.py")
with col_restart:
    if st.button("Start a New Analysis", use_container_width=True):
        keys_to_clear = [
            "student_name", "semester", "selected_skills", "verified_skills",
            "quiz_results", "quiz_complete", "drift_score", "drift_label",
            "track_counts", "entropy_score", "entropy_label", "career_matches",
            "best_track", "match_pct", "readiness_score", "next_skill_info",
            "urgency_info", "focus_debt_info", "peer_info", "session_start",
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.switch_page("pages/02_skill_input.py")
