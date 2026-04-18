# Window 10 - Final Report 
# =============================================================
# pages/10_final_report.py — Window 10: Final Summary & Download
# Brings together all analysis into one downloadable report.
# =============================================================

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
from brain import generate_student_report_csv, CAREER_TRACKS

st.set_page_config(
    page_title="SkillDrift — Final Report",
    page_icon="📄",
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
# MAIN CONTENT — Pull everything from session_state
# =============================================================

semester        = st.session_state.get("semester", "?")
drift_score     = st.session_state.get("drift_score", 0)
drift_label     = st.session_state.get("drift_label", "")
entropy_score   = st.session_state.get("entropy_score", 0)
entropy_label   = st.session_state.get("entropy_label", "")
best_track      = st.session_state.get("best_track", "Unknown")
match_pct       = st.session_state.get("match_pct", 0)
readiness_score = st.session_state.get("readiness_score", 0)
next_skill_info = st.session_state.get("next_skill_info", {})
urgency_info    = st.session_state.get("urgency_info", {})
focus_debt_info = st.session_state.get("focus_debt_info", {})
peer_info       = st.session_state.get("peer_info", {})
verified_skills = st.session_state.get("verified_skills", {})
career_matches  = st.session_state.get("career_matches", [])

next_skill       = next_skill_info.get("skill", "N/A") if next_skill_info else "N/A"
urgency_level    = urgency_info.get("urgency_level", "Unknown") if urgency_info else "Unknown"
urgency_color    = urgency_info.get("urgency_color", "#6C63FF") if urgency_info else "#6C63FF"
focus_debt_hours = focus_debt_info.get("focus_debt_hours", 0) if focus_debt_info else 0
days_to_recover  = focus_debt_info.get("days_to_recover", 0) if focus_debt_info else 0

today_str = datetime.now().strftime("%Y-%m-%d")

# ── Page Title ────────────────────────────────────────────────
st.title("📄 Your SkillDrift Report Card")
st.markdown(
    "Everything SkillDrift calculated about your career readiness — "
    "in one place. Download it and share it with your placement cell."
)
st.markdown("---")

# ── Student Identity Card ─────────────────────────────────────
st.markdown(f"""
<div style="background:#1A1D27; border:2px solid #6C63FF;
            border-radius:14px; padding:1.5rem; margin-bottom:1.5rem;">
    <div style="display:flex; align-items:center; gap:1.5rem;">
        <svg width="72" height="72" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
            <circle cx="40" cy="40" r="40" fill="#2D3250"/>
            <circle cx="40" cy="30" r="15" fill="#6C63FF"/>
            <ellipse cx="40" cy="65" rx="22" ry="15" fill="#6C63FF"/>
        </svg>
        <div>
            <div style="font-size:1.8rem; font-weight:900; color:#FAFAFA;">
                {student_name}
            </div>
            <div style="color:#BDC3C7; font-size:1rem;">
                Semester {semester} &nbsp;|&nbsp; Report generated {today_str}
            </div>
            <div style="color:#6C63FF; font-size:0.9rem; margin-top:0.25rem;">
                SkillDrift Career Focus Analyzer
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Two Column Report Summary ─────────────────────────────────
st.subheader("📊 Complete Analysis Summary")

col_left, col_right = st.columns(2)

def make_report_row(label, value, value_color="#FAFAFA"):
    return f"""
    <div style="background:#1A1D27; border:1px solid #2D3250;
                border-radius:8px; padding:0.85rem 1rem; margin:0.3rem 0;
                display:flex; justify-content:space-between; align-items:center;">
        <div style="color:#7F8C8D; font-size:0.9rem;">{label}</div>
        <div style="color:{value_color}; font-weight:700; font-size:0.95rem;
                    text-align:right; max-width:55%;">{value}</div>
    </div>
    """

# Determine colors
ds_color = (
    "#2ECC71" if drift_score >= 60
    else "#F39C12" if drift_score >= 40
    else "#E74C3C"
)
es_color = (
    "#2ECC71" if entropy_score < 1.2
    else "#F39C12" if entropy_score < 2.0
    else "#E74C3C"
)
rs_color = (
    "#2ECC71" if readiness_score >= 70
    else "#F39C12" if readiness_score >= 40
    else "#E74C3C"
)

with col_left:
    st.markdown("**📐 Skill Analysis**")
    st.markdown(
        make_report_row("Drift Score", f"{drift_score} — {drift_label}", ds_color),
        unsafe_allow_html=True,
    )
    st.markdown(
        make_report_row("Entropy Score", f"{entropy_score} bits — {entropy_label}", es_color),
        unsafe_allow_html=True,
    )
    st.markdown(
        make_report_row("Verified Skills", f"{len(verified_skills)} skills confirmed"),
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**🏆 Career Match**")
    st.markdown(
        make_report_row("Best Career Track", best_track, "#6C63FF"),
        unsafe_allow_html=True,
    )
    st.markdown(
        make_report_row("Match Percentage", f"{match_pct}%", "#6C63FF"),
        unsafe_allow_html=True,
    )
    st.markdown(
        make_report_row("Readiness Score", f"{readiness_score}%", rs_color),
        unsafe_allow_html=True,
    )

with col_right:
    st.markdown("**⚡ Action Plan**")
    st.markdown(
        make_report_row("Next Skill to Learn", next_skill, "#F39C12"),
        unsafe_allow_html=True,
    )
    st.markdown(
        make_report_row("Urgency Level", urgency_level, urgency_color),
        unsafe_allow_html=True,
    )
    st.markdown(
        make_report_row(
            "Focus Debt",
            f"{focus_debt_hours} hrs ({days_to_recover} days at 2 hrs/day)",
            "#E74C3C" if focus_debt_hours > 60 else "#F39C12",
        ),
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**🔍 Top Missing Skills**")

    best_match_data = career_matches[0] if career_matches else {}
    missing_skills  = best_match_data.get("missing_skills", [])

    if missing_skills:
        for i, ms in enumerate(missing_skills[:5], start=1):
            st.markdown(
                make_report_row(
                    f"#{i} Missing Skill",
                    f"{ms['skill']} ({ms['frequency_pct']:.1f}% of JDs)",
                    "#E74C3C",
                ),
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            make_report_row("Missing Skills", "None — All required skills verified ✅", "#2ECC71"),
            unsafe_allow_html=True,
        )

st.markdown("---")

# ── Verified Skills Full List ─────────────────────────────────
st.subheader("✅ Your Verified Skill Profile")

if verified_skills:
    import pandas as pd

    quiz_results = st.session_state.get("quiz_results", [])
    status_map = {
        r["skill"]: r["status"]
        for r in quiz_results
    } if quiz_results else {}

    skill_rows = []
    for skill, level in verified_skills.items():
        status = status_map.get(skill, "Confirmed")
        status_icon = {
            "Confirmed":  "✅",
            "Downgraded": "⚠️",
            "Unverified": "🔶",
        }.get(status, "✅")

        skill_rows.append({
            "Skill":          skill,
            "Verified Level": level,
            "Quiz Status":    f"{status_icon} {status}",
        })

    skill_df = pd.DataFrame(skill_rows)
    st.dataframe(skill_df, use_container_width=True, hide_index=True)
else:
    st.warning("No verified skills found in this session.")

st.markdown("---")

# =============================================================
# DOWNLOAD SECTION
# =============================================================

st.subheader("⬇️ Download Your Report")

session_data = {
    "student_name":    student_name,
    "semester":        semester,
    "drift_score":     drift_score,
    "drift_label":     drift_label,
    "entropy_score":   entropy_score,
    "entropy_label":   entropy_label,
    "best_track":      best_track,
    "match_pct":       match_pct,
    "readiness_score": readiness_score,
    "next_skill":      next_skill,
    "urgency_level":   urgency_level,
    "focus_debt_hours": focus_debt_hours,
    "verified_skills": verified_skills,
}

csv_string = generate_student_report_csv(session_data)
csv_bytes  = csv_string.encode("utf-8")

name_for_file = student_name.strip().replace(" ", "_")
date_for_file = datetime.now().strftime("%Y_%m_%d")
filename      = f"SkillDrift_Report_{name_for_file}_{date_for_file}.csv"

col_dl, col_info = st.columns([2, 3])

with col_dl:
    st.download_button(
        label="⬇️ Download My Report as CSV",
        data=csv_bytes,
        file_name=filename,
        mime="text/csv",
        use_container_width=True,
        type="primary",
    )

with col_info:
    st.markdown("""
    <div style="background:#1A1D27; border:1px solid #2D3250;
                border-radius:8px; padding:1rem; font-size:0.9rem;
                color:#BDC3C7;">
        <strong style="color:#FAFAFA;">What to do with this file:</strong><br><br>
        📧 Email it to your college placement cell<br>
        🏫 Upload it to the Faculty Dashboard when your HOD requests it<br>
        👨‍🏫 Share it with your mentor or career advisor<br>
        💾 Keep a copy for your own reference
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── Plain Text Copy Block ─────────────────────────────────────
st.subheader("📋 Quick Share Summary")
st.markdown(
    "Copy this text and paste it anywhere — WhatsApp, email, or Telegram."
)

peer_rate = peer_info.get("student_placement_rate", "N/A") if peer_info else "N/A"

plain_text_summary = f"""SkillDrift Career Report — {student_name}
Generated: {today_str}

Student Name  : {student_name}
Semester      : {semester}

SKILL ANALYSIS
Drift Score   : {drift_score} / 100 ({drift_label})
Entropy Score : {entropy_score} bits ({entropy_label})
Verified Skills: {len(verified_skills)}

CAREER MATCH
Best Track    : {best_track}
Match %       : {match_pct}%
Readiness     : {readiness_score}%

ACTION PLAN
Next Skill    : {next_skill}
Urgency       : {urgency_level}
Focus Debt    : {focus_debt_hours} hours

Est. Placement Rate (current profile): {peer_rate}%

Generated by SkillDrift — Career Focus Analyzer for B.Tech CSE Students"""

st.code(plain_text_summary, language=None)

st.markdown("---")

# ── What Happens Next ─────────────────────────────────────────
st.subheader("🗺️ What Should You Do Next?")

readiness_tier = (
    "high" if readiness_score >= 70
    else "medium" if readiness_score >= 40
    else "low"
)

if readiness_tier == "high":
    st.success(
        f"✅ **You are approaching placement readiness for {best_track}.** "
        f"Your readiness score of {readiness_score}% puts you ahead of most peers. "
        f"Focus on deepening your top skills to Advanced level and building one "
        f"complete project that demonstrates end-to-end capability in {best_track}."
    )
elif readiness_tier == "medium":
    st.warning(
        f"⚠️ **You are partially ready for {best_track} roles.** "
        f"Your readiness score of {readiness_score}% means you have a foundation "
        f"but significant gaps remain. "
        f"Start with **{next_skill}** today — it appears in the highest percentage "
        f"of job postings for your target track. "
        f"Stop learning new technologies until your readiness score crosses 70%."
    )
else:
    st.error(
        f"🚨 **Your readiness score of {readiness_score}% requires urgent action.** "
        f"You are not yet competitive for {best_track} placements at your current trajectory. "
        f"Your most important step today: open a free course on **{next_skill}** "
        f"and commit to studying it for the next 30 days exclusively. "
        f"Share this report with your mentor and placement cell immediately."
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Navigation ────────────────────────────────────────────────
col_prev, col_restart = st.columns(2)
with col_prev:
    if st.button("← Back to Market Intelligence", use_container_width=True):
        st.switch_page("pages/08_market_intel.py")
with col_restart:
    if st.button("🔄 Start a New Analysis", use_container_width=True):
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