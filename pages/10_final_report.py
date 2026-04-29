# pages/10_final_report.py

import streamlit as st
import pandas as pd
from datetime import datetime
from brain import generate_student_report_csv, CAREER_TRACKS
from _sidebar import APPLE_CSS, render_sidebar
from session_store import init_session, clear_session

st.set_page_config(
    page_title="SkillDrift — My Report Card",
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
    st.stop()

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
peer_info       = st.session_state.get("peer_info",       {})
verified_skills = st.session_state.get("verified_skills", {})
career_matches  = st.session_state.get("career_matches",  [])

next_skill    = next_skill_info.get("skill", "N/A")          if next_skill_info else "N/A"
urgency_level = urgency_info.get("urgency_level", "Unknown")  if urgency_info    else "Unknown"

URGENCY_COLOR_MAP = {"Green": "#15803d", "Yellow": "#d97706", "Red": "#ba1a1a"}
urgency_color = URGENCY_COLOR_MAP.get(urgency_level, "#002c98")
today_str     = datetime.now().strftime("%d %B %Y")

# ── Page Title ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:1.25rem;">
    <div style="font-size:1.5rem;font-weight:800;color:#171c1f;font-family:'Manrope',sans-serif;">
        My Report Card
    </div>
    <div style="font-size:0.875rem;color:#515f74;margin-top:5px;">
        Everything SkillDrift calculated about your career readiness — all in one place.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Student Identity Card ───────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:#FFFFFF;border:2px solid #002c98;border-radius:14px;
            padding:1rem 1.4rem;box-shadow:0 1px 10px rgba(0,44,152,0.07);
            margin-bottom:1.25rem;display:flex;align-items:center;gap:1rem;">
    <div style="width:44px;height:44px;border-radius:50%;background:#e8eeff;
                display:flex;align-items:center;justify-content:center;flex-shrink:0;">
        <svg width="26" height="26" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
            <circle cx="40" cy="28" r="18" fill="#002c98"/>
            <ellipse cx="40" cy="66" rx="26" ry="17" fill="#002c98"/>
        </svg>
    </div>
    <div>
        <div style="font-size:1.25rem;font-weight:800;color:#171c1f;
                    font-family:'Manrope',sans-serif;line-height:1.2;">
            {student_name}
        </div>
        <div style="color:#515f74;font-size:0.82rem;margin-top:3px;">
            Semester {semester} &nbsp;|&nbsp; Report generated on {today_str} &nbsp;|&nbsp;
            <span style="color:#002c98;font-weight:600;">SkillDrift</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Score Cards Row ─────────────────────────────────────────────────────────────
ds_color = "#15803d" if drift_score <= 20 else "#d97706" if drift_score <= 60 else "#ba1a1a"
rs_color = "#15803d" if readiness_score >= 70 else "#d97706" if readiness_score >= 40 else "#ba1a1a"
peer_rate = peer_info.get("student_placement_rate", "N/A") if peer_info else "N/A"
pr_color  = "#15803d" if isinstance(peer_rate, int) and peer_rate >= 60 else "#d97706" if isinstance(peer_rate, int) and peer_rate >= 40 else "#ba1a1a"

sc1, sc2, sc3, sc4 = st.columns(4, gap="small")

with sc1:
    st.markdown(f"""
    <div class="sd-metric">
        <div class="sd-metric-label">Drift Score</div>
        <div class="sd-metric-value" style="color:{ds_color};">{drift_score}</div>
        <div class="sd-metric-sub">{drift_label}</div>
    </div>
    """, unsafe_allow_html=True)

with sc2:
    st.markdown(f"""
    <div class="sd-metric">
        <div class="sd-metric-label">Job Readiness</div>
        <div class="sd-metric-value" style="color:{rs_color};">{readiness_score}%</div>
        <div class="sd-metric-sub">target is 70%</div>
    </div>
    """, unsafe_allow_html=True)

with sc3:
    st.markdown(f"""
    <div class="sd-metric">
        <div class="sd-metric-label">Placement Chance</div>
        <div class="sd-metric-value" style="color:{pr_color};">{peer_rate}%</div>
        <div class="sd-metric-sub">based on your drift score</div>
    </div>
    """, unsafe_allow_html=True)

with sc4:
    st.markdown(f"""
    <div class="sd-metric">
        <div class="sd-metric-label">Time Status</div>
        <div class="sd-metric-value" style="color:{urgency_color};font-size:1.4rem;">{urgency_level}</div>
        <div class="sd-metric-sub">Semester {semester} of 8</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

# ── Two Column Summary ──────────────────────────────────────────────────────────
def report_row(label, value, value_color="#171c1f"):
    return f"""
    <div style="background:#FFFFFF;border:1px solid #e2e8f0;border-radius:9px;
                padding:0.65rem 1rem;margin:0.2rem 0;
                display:flex;justify-content:space-between;align-items:center;">
        <div style="color:#515f74;font-size:0.84rem;">{label}</div>
        <div style="color:{value_color};font-weight:700;font-size:0.86rem;
                    text-align:right;max-width:55%;">{value}</div>
    </div>
    """

col_left, col_right = st.columns(2, gap="large")

with col_left:
    st.markdown("""
    <div style="font-size:0.72rem;font-weight:700;color:#515f74;
                text-transform:uppercase;letter-spacing:0.8px;margin-bottom:6px;">
        Skill Analysis
    </div>""", unsafe_allow_html=True)
    st.markdown(report_row("Drift Score", f"{drift_score} — {drift_label}", ds_color),
                unsafe_allow_html=True)
    st.markdown(report_row("Entropy Score", f"{entropy_score} bits — {entropy_label} (skill scatter measure)"),
                unsafe_allow_html=True)
    st.markdown(report_row("Verified Skills", f"{len(verified_skills)} skills confirmed"),
                unsafe_allow_html=True)

    st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.72rem;font-weight:700;color:#515f74;
                text-transform:uppercase;letter-spacing:0.8px;margin-bottom:6px;">
        Career Match
    </div>""", unsafe_allow_html=True)
    st.markdown(report_row("Best Career Track", best_track, "#002c98"),
                unsafe_allow_html=True)
    st.markdown(report_row("Match Percentage", f"{match_pct}%", "#002c98"),
                unsafe_allow_html=True)
    st.markdown(report_row("Job Readiness", f"{readiness_score}%", rs_color),
                unsafe_allow_html=True)

with col_right:
    st.markdown("""
    <div style="font-size:0.72rem;font-weight:700;color:#515f74;
                text-transform:uppercase;letter-spacing:0.8px;margin-bottom:6px;">
        Action Plan
    </div>""", unsafe_allow_html=True)
    st.markdown(report_row("Next Skill to Learn", next_skill, "#d97706"),
                unsafe_allow_html=True)
    st.markdown(report_row("Time Status", urgency_level, urgency_color),
                unsafe_allow_html=True)
    st.markdown(report_row("Placement Chance", f"{peer_rate}%", pr_color),
                unsafe_allow_html=True)

    st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.72rem;font-weight:700;color:#515f74;
                text-transform:uppercase;letter-spacing:0.8px;margin-bottom:6px;">
        Top Missing Skills
    </div>""", unsafe_allow_html=True)

    best_match_data = career_matches[0] if career_matches else {}
    missing_skills  = best_match_data.get("missing_skills", [])

    if missing_skills:
        for i, ms in enumerate(missing_skills[:5], start=1):
            st.markdown(
                report_row(f"#{i}", f"{ms['skill']} — {ms['frequency_pct']:.0f}% of jobs", "#ba1a1a"),
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            report_row("Missing Skills", "None — all required skills verified", "#15803d"),
            unsafe_allow_html=True,
        )

st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:1.5rem 0;'>",
            unsafe_allow_html=True)

# ── Verified Skills Table ───────────────────────────────────────────────────────
st.markdown("""
<div style="font-size:0.95rem;font-weight:700;color:#171c1f;margin-bottom:8px;">
    Your Verified Skills
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
            "Level":          level,
            "Quiz Result":    status,
        })
    st.dataframe(pd.DataFrame(skill_rows), use_container_width=True, hide_index=True)
else:
    st.warning("No verified skills found in this session.")

st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:1.5rem 0;'>",
            unsafe_allow_html=True)

# ── What to do next ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="font-size:0.95rem;font-weight:700;color:#171c1f;margin-bottom:10px;">
    What Should You Do Now?
</div>
""", unsafe_allow_html=True)

if readiness_score >= 70:
    st.success(
        f"You are close to placement ready for {best_track}. "
        f"Your {readiness_score}% readiness puts you ahead of most students. "
        f"Now go deep — build one strong project end-to-end and push each skill to Advanced level."
    )
elif readiness_score >= 40:
    st.warning(
        f"You have a foundation for {best_track} but gaps remain. "
        f"Start with {next_skill} — it appears in the most job postings. "
        f"Do not add more skills until your readiness crosses 70%."
    )
else:
    st.error(
        f"Your readiness of {readiness_score}% means you are not yet competitive for {best_track} placements. "
        f"Open a free course on {next_skill} today and commit to it for 30 days. "
        f"Share this report with your placement cell or mentor right now."
    )

st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

# ── Download ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="font-size:0.95rem;font-weight:700;color:#171c1f;margin-bottom:8px;">
    Download Your Report
</div>
""", unsafe_allow_html=True)

session_data = {
    "student_name":   student_name,
    "semester":       semester,
    "drift_score":    drift_score,
    "drift_label":    drift_label,
    "entropy_score":  entropy_score,
    "entropy_label":  entropy_label,
    "best_track":     best_track,
    "match_pct":      match_pct,
    "readiness_score": readiness_score,
    "next_skill":     next_skill,
    "urgency_level":  urgency_level,
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
        label="Download as CSV",
        data=csv_bytes,
        file_name=filename,
        mime="text/csv",
        use_container_width=True,
        type="primary",
    )
with col_info:
    st.markdown("""
    <div style="background:#FFFFFF;border:1px solid #e2e8f0;border-radius:10px;
                padding:0.6rem 1rem;font-size:0.84rem;color:#515f74;line-height:1.5;">
        <strong style="color:#171c1f;">What to do with this file</strong>
        &nbsp;&nbsp;·&nbsp;&nbsp;
        Email to placement cell
        &nbsp;&nbsp;·&nbsp;&nbsp;
        Upload to Faculty Dashboard
        &nbsp;&nbsp;·&nbsp;&nbsp;
        Share with your mentor
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:1.5rem 0;'>",
            unsafe_allow_html=True)

# ── Quick Share Text ────────────────────────────────────────────────────────────
st.markdown("""
<div style="font-size:0.88rem;font-weight:700;color:#171c1f;margin-bottom:4px;">
    Quick Share — Copy and Send Anywhere
</div>
<div style="font-size:0.82rem;color:#515f74;margin-bottom:8px;">
    Paste this into WhatsApp, email, or Telegram to share your results instantly.
</div>
""", unsafe_allow_html=True)

plain_summary = f"""SkillDrift Report — {student_name}
Generated: {today_str}

Student     : {student_name}
Semester    : {semester}

SKILL ANALYSIS
Drift Score : {drift_score} / 100 ({drift_label})
Entropy     : {entropy_score} bits ({entropy_label})
Skills      : {len(verified_skills)} verified

CAREER MATCH
Best Track  : {best_track}
Match       : {match_pct}%
Readiness   : {readiness_score}%

ACTION PLAN
Learn Next  : {next_skill}
Time Status : {urgency_level}
Placement % : {peer_rate}%

Generated by SkillDrift — Career Focus Analyzer for B.Tech CSE Students"""

st.code(plain_summary, language=None)

st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:1.5rem 0;'>",
            unsafe_allow_html=True)

col_prev, col_restart = st.columns(2)
with col_prev:
    if st.button("Back — Job Market", use_container_width=True):
        st.switch_page("pages/08_market_intel.py")
with col_restart:
    if st.button("Start a New Analysis", use_container_width=True):
        clear_session()
        st.switch_page("pages/02_skill_input.py")