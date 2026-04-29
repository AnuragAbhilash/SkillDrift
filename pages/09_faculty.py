# pages/09_faculty.py — Window 9: Faculty Dashboard
# Updated with:
#   • ZIP folder upload support (extracts CSVs automatically)
#   • Per-student "View Dashboard" button
#   • Student dashboard stored in session, viewed in 09b_student_view.py

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import io
import zipfile
import tempfile
import os
from datetime import datetime
from brain import (
    verify_faculty_login,
    validate_and_process_batch,
    CAREER_TRACKS,
    parse_skills_string,
)

st.set_page_config(
    page_title="SkillDrift — Faculty Dashboard",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    [data-testid="stSidebarNav"]            { display: none !important; }
    [data-testid="collapsedControl"]        { display: none !important; }
    [data-testid="stExpandSidebar"]         { display: none !important; }
    [data-testid="stSidebarCollapseButton"] { display: none !important; }
    section[data-testid="stSidebar"]        { display: none !important; }
    header[data-testid="stHeader"]          { display: none !important; }
    .stDeployButton                         { display: none !important; }
    #MainMenu                               { display: none !important; }
    footer                                  { display: none !important; }

    .stApp { background-color: #F5F5F7; }
    .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1080px; }
    h1, h2, h3 { color: #1D1D1F !important; }
    .stButton > button {
        border-radius: 8px; border: 1px solid #D2D2D7;
        background: #F5F5F7; color: #1D1D1F;
        font-weight: 500; transition: all 0.15s ease;
    }
    .stButton > button:hover { background: #E8E8ED; }
    .stButton > button[kind="primary"] {
        background: #6C63FF; color: #FFFFFF; border-color: #6C63FF;
    }
    .stButton > button[kind="primary"]:hover { background: #5A52E0; }
    .stTextInput > div > div input { border-radius: 8px; }
    .stAlert { border-radius: 12px; }

    /* student table row hover */
    .student-row {
        background: #FFFFFF; border: 1px solid #D2D2D7; border-radius: 10px;
        padding: 0.8rem 1rem; margin: 0.3rem 0;
        display: flex; align-items: center; gap: 1rem;
    }
    .urgency-badge {
        border-radius: 6px; padding: 2px 10px; font-size: 0.78rem;
        font-weight: 700; white-space: nowrap;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HELPER: extract CSVs from a ZIP file into in-memory file-like objects
# ─────────────────────────────────────────────────────────────────────────────

def extract_csvs_from_zip(zip_file_obj) -> list:
    """
    Opens a ZIP and returns a list of (filename, BytesIO) pairs for every
    .csv file found at any depth inside the archive.
    """
    extracted = []
    try:
        with zipfile.ZipFile(zip_file_obj, "r") as zf:
            for name in zf.namelist():
                if name.lower().endswith(".csv") and not name.startswith("__MACOSX"):
                    data = zf.read(name)
                    buf = io.BytesIO(data)
                    buf.name = os.path.basename(name)   # mimic UploadedFile.name
                    extracted.append(buf)
    except zipfile.BadZipFile:
        pass
    return extracted


# ─────────────────────────────────────────────────────────────────────────────
# LOGIN SCREEN
# ─────────────────────────────────────────────────────────────────────────────

if not st.session_state.get("faculty_logged_in"):

    st.markdown("""
    <div style="text-align:center; padding:2.5rem 0 1rem 0;">
        <div style="font-size:2.2rem; font-weight:700; color:#1D1D1F;">
            Faculty / HOD Login
        </div>
        <div style="color:#86868B; margin-top:0.5rem; font-size:1rem;">
            This dashboard is for faculty and HODs only.
        </div>
    </div>
    """, unsafe_allow_html=True)

    _, col_form, _ = st.columns([2, 3, 2])

    with col_form:
        st.markdown("---")

        lockout_time   = st.session_state.get("faculty_lockout_time")
        login_attempts = st.session_state.get("faculty_login_attempts", 0)

        if lockout_time is not None and login_attempts >= 3:
            st.error("Too many failed attempts. Please refresh the page to try again.")
            st.stop()

        email_input    = st.text_input("Faculty Email Address", placeholder="faculty@college.edu")
        password_input = st.text_input("Password", type="password", placeholder="Enter your password")

        col_login, col_home = st.columns(2)
        with col_login:
            login_btn = st.button("Login", type="primary", use_container_width=True)
        with col_home:
            if st.button("Back to Home", use_container_width=True):
                st.switch_page("pages/01_home.py")

        if login_btn:
            if not email_input.strip() or not password_input.strip():
                st.error("Please enter both email and password.")
            else:
                success, faculty_name, error_msg = verify_faculty_login(
                    email_input.strip(), password_input.strip()
                )
                if success:
                    st.session_state["faculty_logged_in"]      = True
                    st.session_state["faculty_name"]           = faculty_name
                    st.session_state["faculty_login_attempts"] = 0
                    st.session_state["faculty_lockout_time"]   = None
                    st.success(f"Welcome, {faculty_name}. Redirecting...")
                    st.rerun()
                else:
                    attempts = st.session_state.get("faculty_login_attempts", 0) + 1
                    st.session_state["faculty_login_attempts"] = attempts
                    if attempts >= 3:
                        st.session_state["faculty_lockout_time"] = datetime.now().isoformat()
                        st.error("Too many failed attempts. Please refresh the page to try again.")
                    else:
                        remaining = 3 - attempts
                        st.error(f"{error_msg} — {remaining} attempt(s) remaining.")

    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# FACULTY DASHBOARD (post-login)
# ─────────────────────────────────────────────────────────────────────────────

faculty_name = st.session_state.get("faculty_name", "Faculty")

_fac_l, _fac_r = st.columns([7, 3])
with _fac_r:
    _btn1, _btn2 = st.columns(2)
    with _btn1:
        if st.button("← Home", use_container_width=True):
            st.switch_page("pages/01_home.py")
    with _btn2:
        if st.button("Sign Out", use_container_width=True):
            for k in ["faculty_logged_in", "faculty_name", "faculty_login_attempts",
                      "faculty_lockout_time", "faculty_batch_results"]:
                st.session_state[k] = False if k == "faculty_logged_in" else None if "name" in k or "time" in k else 0
            st.rerun()

st.title(f"Faculty Dashboard — Welcome, {faculty_name}")
st.markdown(
    "Upload individual student CSV reports **or a ZIP folder** containing multiple CSVs. "
    "All scores are recalculated fresh from raw skill data — tamper-proof."
)
st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# FILE UPLOAD SECTION
# Accepts: individual CSVs + ZIP files (both in the same upload widget)
# ─────────────────────────────────────────────────────────────────────────────

st.subheader("📁 Upload Student Reports")

col_info1, col_info2 = st.columns(2)
with col_info1:
    st.markdown("""
    <div style="background:#FFFFFF; border:1px solid #D2D2D7; border-radius:10px; padding:1rem;">
        <strong style="color:#1D1D1F;">Option A — Individual CSVs</strong><br>
        <span style="color:#86868B; font-size:0.88rem;">
        Upload one or more <code>.csv</code> report files downloaded by students
        from their Final Report page. Up to 100 files at once.
        </span>
    </div>
    """, unsafe_allow_html=True)
with col_info2:
    st.markdown("""
    <div style="background:#FFFFFF; border:1px solid #D2D2D7; border-radius:10px; padding:1rem;">
        <strong style="color:#1D1D1F;">Option B — ZIP Folder</strong><br>
        <span style="color:#86868B; font-size:0.88rem;">
        Ask students to submit their CSVs, compress the folder into a
        <code>.zip</code> file, and upload it here. All CSVs inside are extracted automatically.
        </span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "Upload student report CSVs or a ZIP file",
    type=["csv", "zip"],
    accept_multiple_files=True,
    help="Accepts .csv files and .zip archives containing .csv files. Max 100 student reports.",
)

if not uploaded_files:
    st.info("Upload student CSV files or a ZIP folder above to begin batch analysis.")
    with st.expander("Expected CSV format (what students download from Final Report page)"):
        st.markdown(
            "The system reads `student_name`, `semester`, and `verified_skills`. "
            "All score columns are ignored and recalculated fresh."
        )
        sample = pd.DataFrame([
            {"student_name": "Priya Sharma", "semester": 4,
             "verified_skills": "Python:Intermediate,SQL:Beginner,Excel:Beginner"},
            {"student_name": "Rahul Verma", "semester": 6,
             "verified_skills": "Java:Advanced,SQL:Intermediate,Docker:Beginner"},
        ])
        st.dataframe(sample, use_container_width=True, hide_index=True)
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# SEPARATE ZIP FILES FROM DIRECT CSVs
# ─────────────────────────────────────────────────────────────────────────────

direct_csvs = []
zip_extracted_csvs = []
zip_names = []

for f in uploaded_files:
    if f.name.lower().endswith(".zip"):
        extracted = extract_csvs_from_zip(f)
        zip_extracted_csvs.extend(extracted)
        zip_names.append(f.name)
    else:
        direct_csvs.append(f)

all_csv_files = direct_csvs + zip_extracted_csvs

if zip_names:
    st.success(
        f"📦 Extracted CSVs from ZIP: **{', '.join(zip_names)}** — "
        f"found **{len(zip_extracted_csvs)} CSV file(s)** inside."
    )

st.markdown(
    f"**Total files ready to process:** {len(all_csv_files)} "
    f"({len(direct_csvs)} direct CSVs + {len(zip_extracted_csvs)} from ZIP)"
)

process_btn = st.button(
    f"⚡ Process {len(all_csv_files)} File(s) and Generate Batch Analysis",
    type="primary",
    use_container_width=True,
)

if process_btn:
    with st.spinner("Validating files, removing duplicates, recalculating all scores..."):
        results = validate_and_process_batch(all_csv_files)
        st.session_state["faculty_batch_results"] = results
    # Auto-redirect to the combined results + placement dashboard
    st.switch_page("pages/09c_batch_results.py")

# If a previous batch exists, show a button to go back to it
results = st.session_state.get("faculty_batch_results")
if results and results.get("all_student_analyses"):
    total_prev = results.get("summary", {}).get("total_students", 0)
    st.info(f"📊 Previous batch loaded: **{total_prev} students** already processed.")
    if st.button("View Previous Batch Results →", use_container_width=True):
        st.switch_page("pages/09c_batch_results.py")
    st.stop()

if not results:
    st.stop()