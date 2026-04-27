# app.py
# =============================================================
# SkillDrift main entry point.
# Sets global page config, initializes persistent session,
# then routes to the home page.
# =============================================================

import streamlit as st

st.set_page_config(
    page_title="SkillDrift - Career Focus Analyzer",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from session_store import init_session, save_session

init_session()
save_session()

st.switch_page("pages/01_home.py")
