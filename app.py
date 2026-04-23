# app.py
# =============================================================
# app.py — SkillDrift Main Entry Point
# This is the first file Streamlit runs.
# It sets up global page config and session state defaults.
# All navigation happens through the pages/ folder.
# =============================================================

import streamlit as st

# Page config — must be the very first Streamlit call
st.set_page_config(
    page_title="SkillDrift — Career Focus Analyzer",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Initialize session state defaults if not already set
# This runs every time the app loads
defaults = {
    "student_name":       None,
    "semester":           None,
    "selected_skills":    {},
    "verified_skills":    {},
    "quiz_results":       [],
    "quiz_complete":      False,
    "drift_score":        None,
    "drift_label":        None,
    "track_counts":       None,
    "entropy_score":      None,
    "entropy_label":      None,
    "career_matches":     None,
    "best_track":         None,
    "match_pct":          None,
    "readiness_score":    None,
    "next_skill_info":    None,
    "urgency_info":       None,
    "focus_debt_info":    None,
    "peer_info":          None,
    "session_start":      None,
    "faculty_logged_in":  False,
    "faculty_name":       None,
    "faculty_login_attempts": 0,
    "faculty_lockout_time":   None,
    "gemini_client":      None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Route to home page content directly
st.switch_page("pages/01_home.py")


