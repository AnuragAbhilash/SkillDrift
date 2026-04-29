# pages/09_faculty.py — Faculty Dashboard
# Fully redesigned: professional, industry-level UI/UX
# - Separate "Analysis Results" section (no scroll-after-button)
# - Clean cards, proper spacing, no emojis, easy English labels
# - Matches student dashboard color palette and design language
# FIX 1: Home + Sign Out moved into top nav bar (top-right)
# FIX 2: Metric cards use custom HTML so labels never get cut off
# FIX 3: Student table uses st.dataframe — perfect alignment, no View button

import streamlit as st
from session_store import init_session
import plotly.graph_objects as go
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import io
import zipfile
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

init_session()

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL STYLES
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    /* Hide streamlit chrome */
    [data-testid="stSidebarNav"]            { display: none !important; }
    [data-testid="collapsedControl"]        { display: none !important; }
    [data-testid="stExpandSidebar"]         { display: none !important; }
    [data-testid="stSidebarCollapseButton"] { display: none !important; }
    section[data-testid="stSidebar"]        { display: none !important; }
    header[data-testid="stHeader"]          { display: none !important; }
    .stDeployButton                         { display: none !important; }
    #MainMenu                               { display: none !important; }
    footer                                  { display: none !important; }

    /* Base layout */
    .stApp { background-color: #F5F5F7; }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 1100px;
    }

    /* Typography */
    h1, h2, h3, h4 { color: #1D1D1F !important; font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif; }
    p, span, div { font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif; }

    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        border: 1px solid #D2D2D7;
        background: #FFFFFF;
        color: #1D1D1F;
        font-weight: 500;
        font-size: 0.88rem;
        padding: 0.45rem 1rem;
        transition: all 0.15s ease;
    }
    .stButton > button:hover {
        background: #F0F0F5;
        border-color: #B0B0BB;
    }
    .stButton > button[kind="primary"] {
        background: #6C63FF;
        color: #FFFFFF;
        border-color: #6C63FF;
        font-weight: 600;
    }
    .stButton > button[kind="primary"]:hover {
        background: #5A52E0;
        border-color: #5A52E0;
    }

    /* Inputs */
    .stTextInput > div > div input {
        border-radius: 8px;
        border: 1px solid #D2D2D7;
        font-size: 0.9rem;
    }
    .stTextInput > div > div input:focus {
        border-color: #6C63FF;
        box-shadow: 0 0 0 3px rgba(108, 99, 255, 0.12);
    }

    /* Alerts */
    .stAlert { border-radius: 10px; }

    /* File uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed #D2D2D7;
        border-radius: 12px;
        background: #FAFAFA;
        padding: 0.5rem;
    }

    /* Cards */
    .sd-card {
        background: #FFFFFF;
        border: 1px solid #E5E5EA;
        border-radius: 14px;
        padding: 1.25rem 1.4rem;
        margin-bottom: 0.75rem;
    }
    .sd-card-accent {
        background: #FFFFFF;
        border: 1px solid #E5E5EA;
        border-left: 4px solid #6C63FF;
        border-radius: 14px;
        padding: 1.25rem 1.4rem;
        margin-bottom: 0.75rem;
    }

    /* FIX 2: Custom metric cards — never truncate */
    .sd-metric-card {
        background: #FFFFFF;
        border: 1px solid #E5E5EA;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        min-height: 80px;
    }
    .sd-metric-label {
        font-size: 0.72rem;
        font-weight: 600;
        color: #86868B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.3rem;
        white-space: normal;
        word-break: break-word;
        line-height: 1.3;
    }
    .sd-metric-value {
        font-size: 1.55rem;
        font-weight: 700;
        color: #1D1D1F;
        line-height: 1.2;
    }

    /* Section header */
    .section-header {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1D1D1F;
        margin-bottom: 0.75rem;
        margin-top: 0.25rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #E5E5EA;
    }

    /* Divider */
    .sd-divider {
        border: none;
        border-top: 1px solid #E5E5EA;
        margin: 1.75rem 0;
    }

    /* FIX 3: Student table styles */
    .sd-table-header {
        display: grid;
        grid-template-columns: 1.6fr 1.1fr 1.4fr 0.9fr 0.9fr 1.1fr;
        gap: 0;
        padding: 0.5rem 1.2rem;
        margin-bottom: 0.25rem;
        background: #F5F5F7;
        border-radius: 8px;
        border: 1px solid #E5E5EA;
    }
    .sd-table-header-cell {
        font-size: 0.72rem;
        font-weight: 700;
        color: #86868B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0.25rem 0.4rem;
    }
    .sd-table-row {
        display: grid;
        grid-template-columns: 1.6fr 1.1fr 1.4fr 0.9fr 0.9fr 1.1fr;
        gap: 0;
        padding: 0.85rem 1.2rem;
        background: #FFFFFF;
        border: 1px solid #E5E5EA;
        border-radius: 12px;
        margin-bottom: 0.5rem;
        align-items: center;
    }
    .sd-table-cell {
        padding: 0 0.4rem;
    }

    /* Scrollable analysis container */
    .results-page {
        background: #F5F5F7;
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid #E5E5EA;
    }

    /* FIX 1: Nav bar button group styles */
    .nav-btn-group {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }
    .nav-btn {
        padding: 0.35rem 0.9rem;
        border-radius: 8px;
        border: 1px solid #D2D2D7;
        background: #FFFFFF;
        color: #1D1D1F;
        font-size: 0.85rem;
        font-weight: 500;
        cursor: pointer;
        text-decoration: none;
        white-space: nowrap;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HELPER: extract CSVs from ZIP
# ─────────────────────────────────────────────────────────────────────────────

def extract_csvs_from_zip(zip_file_obj) -> list:
    extracted = []
    try:
        with zipfile.ZipFile(zip_file_obj, "r") as zf:
            for name in zf.namelist():
                if name.lower().endswith(".csv") and not name.startswith("__MACOSX"):
                    data = zf.read(name)
                    buf = io.BytesIO(data)
                    buf.name = os.path.basename(name)
                    extracted.append(buf)
    except zipfile.BadZipFile:
        pass
    return extracted


# ─────────────────────────────────────────────────────────────────────────────
# FIX 2 HELPER: Custom metric card (never truncates)
# ─────────────────────────────────────────────────────────────────────────────

def metric_card(label: str, value: str, value_color: str = "#1D1D1F"):
    st.markdown(f"""
    <div class="sd-metric-card">
        <div class="sd-metric-label">{label}</div>
        <div class="sd-metric-value" style="color:{value_color};">{value}</div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# LOGIN SCREEN
# ─────────────────────────────────────────────────────────────────────────────

if not st.session_state.get("faculty_logged_in"):

    # Centered login card
    _, col_form, _ = st.columns([1.5, 3, 1.5])

    with col_form:
        st.markdown("""
        <div style="text-align:center; padding: 2.5rem 0 1.5rem 0;">
            <div style="
                width: 56px; height: 56px; border-radius: 14px;
                background: linear-gradient(135deg, #6C63FF, #9B94FF);
                margin: 0 auto 1rem auto;
                display: flex; align-items: center; justify-content: center;">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2C9.24 2 7 4.24 7 7s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5z" fill="white"/>
                    <path d="M12 14c-5.33 0-8 2.67-8 4v2h16v-2c0-1.33-2.67-4-8-4z" fill="white"/>
                </svg>
            </div>
            <div style="font-size: 1.75rem; font-weight: 700; color: #1D1D1F; letter-spacing: -0.02em;">
                Faculty Login
            </div>
            <div style="color: #86868B; margin-top: 0.4rem; font-size: 0.9rem;">
                Access the Faculty and HOD Dashboard
            </div>
        </div>
        """, unsafe_allow_html=True)

        lockout_time   = st.session_state.get("faculty_lockout_time")
        login_attempts = st.session_state.get("faculty_login_attempts", 0)

        if lockout_time is not None and login_attempts >= 3:
            st.error("Account temporarily locked due to too many failed attempts. Please refresh the page.")
            st.stop()

        email_input    = st.text_input("Email Address", placeholder="faculty@college.edu")
        password_input = st.text_input("Password", type="password", placeholder="Enter your password")

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        col_login, col_home = st.columns(2)
        with col_login:
            login_btn = st.button("Sign In", type="primary", use_container_width=True)
        with col_home:
            if st.button("Back to Home", use_container_width=True):
                st.switch_page("pages/01_home.py")

        if login_btn:
            if not email_input.strip() or not password_input.strip():
                st.error("Please enter both your email address and password.")
            else:
                success, faculty_name, error_msg = verify_faculty_login(
                    email_input.strip(), password_input.strip()
                )
                if success:
                    st.session_state["faculty_logged_in"]      = True
                    st.session_state["faculty_name"]           = faculty_name
                    st.session_state["faculty_login_attempts"] = 0
                    st.session_state["faculty_lockout_time"]   = None
                    st.session_state["faculty_active_view"]    = "upload"
                    st.success(f"Welcome back, {faculty_name}. Loading your dashboard...")
                    st.rerun()
                else:
                    attempts = st.session_state.get("faculty_login_attempts", 0) + 1
                    st.session_state["faculty_login_attempts"] = attempts
                    if attempts >= 3:
                        st.session_state["faculty_lockout_time"] = datetime.now().isoformat()
                        st.error("Account locked — too many failed attempts. Please refresh the page.")
                    else:
                        remaining = 3 - attempts
                        st.error(f"Incorrect credentials. {remaining} attempt(s) remaining.")

    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# FACULTY DASHBOARD (post-login)
# ─────────────────────────────────────────────────────────────────────────────

faculty_name = st.session_state.get("faculty_name", "Faculty")

if "faculty_active_view" not in st.session_state:
    st.session_state["faculty_active_view"] = "upload"

# ── HANDLE QUERY PARAMS (sign-out + tab switching via HTML links) ─────────────

_qp = st.query_params.to_dict()

if _qp.get("signout") == "1":
    for k in ["faculty_logged_in", "faculty_name", "faculty_login_attempts",
              "faculty_lockout_time", "faculty_batch_results", "faculty_active_view"]:
        st.session_state[k] = (
            False if k == "faculty_logged_in"
            else None if "name" in k or "time" in k or "results" in k
            else 0
        )
    st.query_params.clear()
    st.rerun()

if _qp.get("tab") == "upload":
    st.session_state["faculty_active_view"] = "upload"
    st.query_params.clear()
    st.rerun()

if _qp.get("tab") == "results":
    st.session_state["faculty_active_view"] = "results"
    st.query_params.clear()
    st.rerun()

# ── TOP NAVIGATION BAR — 100% pure HTML, Home & Sign Out inside the bar ───────

st.markdown(
    "<div style='"
    "background:#FFFFFF; border:1px solid #E5E5EA; border-radius:14px;"
    "padding:0.85rem 1.25rem; display:flex; align-items:center;"
    "justify-content:space-between; margin-bottom:1.25rem;'>"

    # Left: logo + title
    "<div style='display:flex; align-items:center; gap:0.75rem;'>"
    "<div style='width:38px; height:38px; border-radius:10px;"
    "background:linear-gradient(135deg,#6C63FF,#9B94FF);"
    "display:flex; align-items:center; justify-content:center; flex-shrink:0;'>"
    "<svg width='20' height='20' viewBox='0 0 24 24' fill='none'>"
    "<path d='M12 2C9.24 2 7 4.24 7 7s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5z' fill='white'/>"
    "<path d='M12 14c-5.33 0-8 2.67-8 4v2h16v-2c0-1.33-2.67-4-8-4z' fill='white'/>"
    "</svg></div>"
    "<div>"
    "<div style='font-weight:700; font-size:0.95rem; color:#1D1D1F; line-height:1.2;'>Faculty Dashboard</div>"
    "<div style='font-size:0.78rem; color:#86868B;'>Welcome, " + faculty_name + " \u2014 SkillDrift Batch Analysis Tool</div>"
    "</div></div>"

    # Right: Home + Sign Out as pure <a> links styled as buttons
    "<div style='display:flex; gap:0.5rem; align-items:center;'>"
    "<a href='/01_home' target='_self' style='"
    "display:inline-block; padding:0.38rem 1.1rem; border-radius:8px;"
    "border:1px solid #D2D2D7; background:#FFFFFF; color:#1D1D1F;"
    "font-size:0.85rem; font-weight:500; text-decoration:none;"
    "font-family:-apple-system,BlinkMacSystemFont,sans-serif; line-height:1.5;'>"
    "Home</a>"
    "<a href='?signout=1' target='_self' style='"
    "display:inline-block; padding:0.38rem 1.1rem; border-radius:8px;"
    "border:1px solid #D2D2D7; background:#FFFFFF; color:#1D1D1F;"
    "font-size:0.85rem; font-weight:500; text-decoration:none;"
    "font-family:-apple-system,BlinkMacSystemFont,sans-serif; line-height:1.5;'>"
    "Sign Out</a>"
    "</div>"

    "</div>",
    unsafe_allow_html=True,
)

# ── VIEW SWITCHER — full width, split 50/50, proper tab bar ───────────────────

active_view = st.session_state.get("faculty_active_view", "upload")
has_results = bool(st.session_state.get("faculty_batch_results"))

if has_results:
    # Active tab: purple fill. Inactive: white with border. Both span full width 50/50.
    upload_bg    = "#6C63FF" if active_view == "upload"  else "#FFFFFF"
    upload_color = "#FFFFFF" if active_view == "upload"  else "#1D1D1F"
    upload_bord  = "#6C63FF" if active_view == "upload"  else "#D2D2D7"
    results_bg   = "#6C63FF" if active_view == "results" else "#FFFFFF"
    results_color= "#FFFFFF" if active_view == "results" else "#1D1D1F"
    results_bord = "#6C63FF" if active_view == "results" else "#D2D2D7"

    st.markdown(
        "<div style='display:flex; width:100%; gap:0; margin-bottom:1.25rem;'>"

        "<a href='?tab=upload' target='_self' style='"
        "flex:1; display:block; text-align:center;"
        "padding:0.7rem 0; font-size:0.92rem; font-weight:600;"
        "background:" + upload_bg + "; color:" + upload_color + ";"
        "border:1.5px solid " + upload_bord + ";"
        "border-radius:10px 0 0 10px; text-decoration:none;"
        "font-family:-apple-system,BlinkMacSystemFont,sans-serif;"
        "transition:all 0.15s;'>Upload Files</a>"

        "<a href='?tab=results' target='_self' style='"
        "flex:1; display:block; text-align:center;"
        "padding:0.7rem 0; font-size:0.92rem; font-weight:600;"
        "background:" + results_bg + "; color:" + results_color + ";"
        "border:1.5px solid " + results_bord + ";"
        "border-left:none;"
        "border-radius:0 10px 10px 0; text-decoration:none;"
        "font-family:-apple-system,BlinkMacSystemFont,sans-serif;"
        "transition:all 0.15s;'>View Analysis</a>"

        "</div>",
        unsafe_allow_html=True,
    )


# =============================================================================
# VIEW A — UPLOAD & CONFIGURE
# =============================================================================

if active_view == "upload":

    st.markdown("""
    <div class="section-header">Upload Student Reports</div>
    <p style="color:#86868B; font-size:0.9rem; margin-top:-0.4rem; margin-bottom:1.25rem;">
        Upload individual student CSV reports or a ZIP folder containing multiple CSVs.
        All scores are recalculated from raw skill data — tamper-proof and consistent.
    </p>
    """, unsafe_allow_html=True)

    col_info1, col_info2 = st.columns(2, gap="medium")
    with col_info1:
        st.markdown("""
        <div class="sd-card-accent">
            <div style="font-weight: 700; color: #1D1D1F; font-size: 0.92rem; margin-bottom: 0.4rem;">
                Option A — Individual CSV Files
            </div>
            <div style="color: #86868B; font-size: 0.85rem; line-height: 1.5;">
                Upload one or more <code style="background:#F5F5F7; padding:1px 5px; border-radius:4px;">.csv</code>
                report files downloaded by students from their Final Report page.
                Supports up to 100 files at once.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_info2:
        st.markdown("""
        <div class="sd-card" style="border-left: 4px solid #34C759;">
            <div style="font-weight: 700; color: #1D1D1F; font-size: 0.92rem; margin-bottom: 0.4rem;">
                Option B — ZIP Folder
            </div>
            <div style="color: #86868B; font-size: 0.85rem; line-height: 1.5;">
                Collect all student CSVs into one folder, compress it as a
                <code style="background:#F5F5F7; padding:1px 5px; border-radius:4px;">.zip</code>
                file, and upload here. All CSV files inside are extracted automatically.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Drop files here or click to browse",
        type=["csv", "zip"],
        accept_multiple_files=True,
        help="Accepts .csv files and .zip archives. Maximum 100 student reports.",
    )

    with st.expander("View expected CSV format"):
        st.markdown("""
        <div style="color: #1D1D1F; font-size: 0.88rem; line-height: 1.6;">
            The system reads three columns: <strong>student_name</strong>,
            <strong>semester</strong>, and <strong>verified_skills</strong>.
            All score columns are ignored and recalculated fresh from raw data.
        </div>
        """, unsafe_allow_html=True)
        sample = pd.DataFrame([
            {"student_name": "Priya Sharma",  "semester": 4,
             "verified_skills": "Python:Intermediate,SQL:Beginner,Excel:Beginner"},
            {"student_name": "Rahul Verma",   "semester": 6,
             "verified_skills": "Java:Advanced,SQL:Intermediate,Docker:Beginner"},
        ])
        st.dataframe(sample, use_container_width=True, hide_index=True)

    if not uploaded_files:
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.info("Upload student CSV files or a ZIP folder above to start batch analysis.")
        st.stop()

    direct_csvs        = []
    zip_extracted_csvs = []
    zip_names          = []

    for f in uploaded_files:
        if f.name.lower().endswith(".zip"):
            extracted = extract_csvs_from_zip(f)
            zip_extracted_csvs.extend(extracted)
            zip_names.append(f.name)
        else:
            direct_csvs.append(f)

    all_csv_files = direct_csvs + zip_extracted_csvs

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="sd-card" style="display:flex; align-items:center; gap:2rem; flex-wrap:wrap;">
        <div>
            <div style="font-size:0.75rem; color:#86868B; text-transform:uppercase; letter-spacing:0.04em;">
                Total Files Ready
            </div>
            <div style="font-size:1.6rem; font-weight:700; color:#1D1D1F;">
                {len(all_csv_files)}
            </div>
        </div>
        <div>
            <div style="font-size:0.75rem; color:#86868B; text-transform:uppercase; letter-spacing:0.04em;">
                Direct CSVs
            </div>
            <div style="font-size:1.6rem; font-weight:700; color:#6C63FF;">
                {len(direct_csvs)}
            </div>
        </div>
        <div>
            <div style="font-size:0.75rem; color:#86868B; text-transform:uppercase; letter-spacing:0.04em;">
                Extracted from ZIP
            </div>
            <div style="font-size:1.6rem; font-weight:700; color:#34C759;">
                {len(zip_extracted_csvs)}
            </div>
        </div>
        {"<div style='color:#86868B; font-size:0.85rem;'>ZIP: " + ", ".join(zip_names) + "</div>" if zip_names else ""}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    process_btn = st.button(
        f"Run Batch Analysis  ({len(all_csv_files)} file{'s' if len(all_csv_files) != 1 else ''})",
        type="primary",
        use_container_width=True,
    )

    if process_btn:
        with st.spinner("Validating files, removing duplicates, and recalculating all scores..."):
            results = validate_and_process_batch(all_csv_files)
            st.session_state["faculty_batch_results"]  = results
            st.session_state["faculty_active_view"]    = "results"
        st.rerun()


# =============================================================================
# VIEW B — ANALYSIS RESULTS
# =============================================================================

elif active_view == "results":

    results = st.session_state.get("faculty_batch_results")
    if not results:
        st.warning("No analysis results found. Please upload files and run batch analysis first.")
        if st.button("Go to Upload"):
            st.session_state["faculty_active_view"] = "upload"
            st.rerun()
        st.stop()

    merged_df            = results.get("merged_df", pd.DataFrame())
    all_student_analyses = results.get("all_student_analyses", [])
    valid_count          = results.get("valid_count", 0)
    skipped_files        = results.get("skipped_files", [])
    duplicate_count      = results.get("duplicate_count", 0)
    summary              = results.get("summary", {})
    total_students       = summary.get("total_students", len(merged_df))

    # ── SECTION HEADER ───────────────────────────────────────────────────────

    st.markdown("""
    <div class="section-header">Batch Analysis Results</div>
    """, unsafe_allow_html=True)

    # ── VALIDATION SUMMARY ROW ────────────────────────────────────────────────
    # FIX 2: Use metric_card() helper — labels never truncate

    col_v1, col_v2, col_v3, col_v4 = st.columns(4, gap="medium")
    files_uploaded = valid_count + len(skipped_files)
    with col_v1:
        metric_card("Files Uploaded", str(files_uploaded))
    with col_v2:
        metric_card("Files Processed", str(valid_count))
    with col_v3:
        metric_card("Files Skipped", str(len(skipped_files)))
    with col_v4:
        metric_card("Duplicates Removed", str(duplicate_count))

    if skipped_files:
        with st.expander(f"View {len(skipped_files)} validation issue(s)"):
            for msg in skipped_files:
                st.warning(msg)

    if merged_df.empty:
        st.error("No valid student data could be processed. Please check that files follow the expected format.")
        st.stop()

    st.markdown(f"""
    <div style="
        background: #F0FFF4;
        border: 1px solid #34C759;
        border-radius: 10px;
        padding: 0.75rem 1.1rem;
        margin: 1rem 0;
        color: #1D4731;
        font-size: 0.88rem;
        font-weight: 500;
    ">
        Analysis complete — <strong>{total_students} students</strong> processed
        from <strong>{valid_count} valid file(s)</strong>.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # ── BATCH SUMMARY METRICS ─────────────────────────────────────────────────
    # FIX 2: All 6 metrics use metric_card() — no truncation ever

    st.markdown('<div class="section-header">Batch Summary</div>', unsafe_allow_html=True)

    avg_drift     = summary.get("avg_drift_score", 0)
    avg_readiness = summary.get("avg_readiness_score", 0)
    avg_entropy   = summary.get("avg_entropy_score", 0)
    red_count     = summary.get("red_count", 0)
    yellow_count  = summary.get("yellow_count", 0)
    green_count   = summary.get("green_count", 0)

    col_m1, col_m2, col_m3, col_m4, col_m5, col_m6 = st.columns(6, gap="small")
    with col_m1:
        metric_card("Avg Drift Score", str(avg_drift))
    with col_m2:
        metric_card("Avg Readiness", f"{avg_readiness}%")
    with col_m3:
        metric_card("Avg Entropy", f"{avg_entropy} bits")
    with col_m4:
        metric_card("High Urgency", str(red_count), value_color="#FF3B30")
    with col_m5:
        metric_card("Medium Urgency", str(yellow_count), value_color="#FF9500")
    with col_m6:
        metric_card("Low Urgency", str(green_count), value_color="#34C759")

    st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

    # ── CHARTS ROW ────────────────────────────────────────────────────────────

    col_pie, col_track = st.columns(2, gap="large")

    with col_pie:
        st.markdown("""
        <div style="font-weight:600; color:#1D1D1F; font-size:0.92rem; margin-bottom:0.5rem;">
            Urgency Level Distribution
        </div>
        <div style="font-size:0.8rem; color:#86868B; margin-bottom:0.75rem;">
            Breakdown of students by placement urgency
        </div>
        """, unsafe_allow_html=True)

        fig_pie = go.Figure(go.Pie(
            labels=["High Urgency", "Medium Urgency", "Low Urgency"],
            values=[red_count, yellow_count, green_count],
            marker_colors=["#FF3B30", "#FF9500", "#34C759"],
            hole=0.52,
            textfont=dict(color="#1D1D1F", size=12),
            hovertemplate="%{label}<br>%{value} students (%{percent})<extra></extra>",
        ))
        fig_pie.update_layout(
            paper_bgcolor="#FFFFFF",
            font=dict(color="#1D1D1F", family="-apple-system, BlinkMacSystemFont, sans-serif"),
            legend=dict(
                bgcolor="#FFFFFF", bordercolor="#E5E5EA", borderwidth=1,
                font=dict(size=11, color="#1D1D1F"),
                orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5,
            ),
            margin=dict(t=10, b=40, l=10, r=10),
            height=280,
        )
        fig_pie.add_annotation(
            text=f"<b>{total_students}</b><br><span style='font-size:10px'>students</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#1D1D1F"),
            align="center",
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

    with col_track:
        st.markdown("""
        <div style="font-weight:600; color:#1D1D1F; font-size:0.92rem; margin-bottom:0.5rem;">
            Career Track Distribution
        </div>
        <div style="font-size:0.8rem; color:#86868B; margin-bottom:0.75rem;">
            How many students best match each career track
        </div>
        """, unsafe_allow_html=True)

        track_dist = summary.get("track_distribution", {})
        if track_dist:
            sorted_tracks = dict(sorted(track_dist.items(), key=lambda x: x[1], reverse=True))
            track_colors = ["#6C63FF", "#5A9EFF", "#34C759", "#FF9500", "#FF3B30",
                            "#AF52DE", "#00C7BE", "#FF6B6B"]

            fig_track = go.Figure(go.Bar(
                x=list(sorted_tracks.values()),
                y=list(sorted_tracks.keys()),
                orientation="h",
                marker=dict(
                    color=track_colors[:len(sorted_tracks)],
                    line=dict(width=0),
                ),
                text=list(sorted_tracks.values()),
                textposition="outside",
                textfont=dict(color="#1D1D1F", size=11),
                hovertemplate="%{y}<br>%{x} students<extra></extra>",
            ))
            fig_track.update_layout(
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FAFAFA",
                font=dict(color="#1D1D1F", family="-apple-system, BlinkMacSystemFont, sans-serif"),
                xaxis=dict(
                    gridcolor="#F0F0F5", showgrid=True,
                    color="#86868B", tickfont=dict(size=10),
                    zeroline=False,
                ),
                yaxis=dict(
                    gridcolor="rgba(0,0,0,0)", showgrid=False,
                    color="#1D1D1F", tickfont=dict(size=10),
                    automargin=True,
                ),
                margin=dict(t=10, b=20, l=10, r=50),
                height=280,
                bargap=0.3,
            )
            st.plotly_chart(fig_track, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # ── TOP MISSING SKILLS ────────────────────────────────────────────────────

    st.markdown('<div class="section-header">Top Skills Missing Across the Batch</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.85rem; color:#86868B; margin-top:-0.4rem; margin-bottom:1rem;">
        Skills that the highest number of students are missing, ranked by frequency.
    </div>
    """, unsafe_allow_html=True)

    top_missing = summary.get("top_missing_skills", [])
    if top_missing:
        RANK_COLORS = ["#FF3B30", "#FF6B35", "#FF9500", "#6C63FF", "#6C63FF"]

        skill_names  = [s[0] for s in top_missing]
        skill_counts = [s[1] for s in top_missing]
        skill_pcts   = [round((c / total_students) * 100, 1) for c in skill_counts]

        fig_miss = go.Figure(go.Bar(
            x=skill_counts,
            y=skill_names,
            orientation="h",
            marker=dict(
                color=RANK_COLORS[:len(skill_names)],
                line=dict(width=0),
            ),
            text=[f"{c} students ({p}%)" for c, p in zip(skill_counts, skill_pcts)],
            textposition="outside",
            textfont=dict(color="#1D1D1F", size=11),
            hovertemplate="%{y}<br>Missing in %{x} students<extra></extra>",
        ))
        fig_miss.update_layout(
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FAFAFA",
            font=dict(color="#1D1D1F", family="-apple-system, BlinkMacSystemFont, sans-serif"),
            xaxis=dict(
                gridcolor="#F0F0F5", showgrid=True,
                color="#86868B", tickfont=dict(size=10),
                zeroline=False, title=dict(text="Number of Students", font=dict(size=11)),
            ),
            yaxis=dict(
                gridcolor="rgba(0,0,0,0)", showgrid=False,
                color="#1D1D1F", tickfont=dict(size=11),
                automargin=True,
            ),
            margin=dict(t=15, b=20, l=10, r=80),
            height=220,
            bargap=0.35,
        )
        st.plotly_chart(fig_miss, use_container_width=True, config={"displayModeBar": False})

        top_skill_name = top_missing[0][0]
        top_skill_pct  = round((top_missing[0][1] / total_students) * 100, 1)
        st.markdown(f"""
        <div style="
            background: #F0EFFF;
            border: 1px solid #6C63FF;
            border-radius: 10px;
            padding: 1rem 1.25rem;
            margin-top: 0.5rem;
        ">
            <div style="font-weight: 700; color: #6C63FF; font-size: 0.85rem;
                        text-transform: uppercase; letter-spacing: 0.04em; margin-bottom:0.35rem;">
                Recommendation
            </div>
            <div style="color: #1D1D1F; font-size: 0.9rem; line-height: 1.5;">
                <strong>{top_skill_pct}% of students</strong> are missing
                <strong>{top_skill_name}</strong>. A focused workshop or module on this
                skill is recommended before the placement season begins.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # ── SKILL HEATMAP ─────────────────────────────────────────────────────────

    st.markdown('<div class="section-header">Batch Skill Heatmap</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.85rem; color:#86868B; margin-top:-0.4rem; margin-bottom:1rem;">
        Each cell shows one student's skill level.
        <span style="color:#34C759; font-weight:600;">Green</span> = Intermediate / Advanced &nbsp;|&nbsp;
        <span style="color:#FF9500; font-weight:600;">Yellow</span> = Beginner &nbsp;|&nbsp;
        <span style="color:#FF3B30; font-weight:600;">Red</span> = Missing
    </div>
    """, unsafe_allow_html=True)

    all_skills_set = set()
    for analysis in all_student_analyses:
        all_skills_set.update(analysis["verified_skills"].keys())
    all_skills_list = sorted(list(all_skills_set))

    heatmap_data   = []
    student_labels = []

    for analysis in all_student_analyses:
        student_labels.append(analysis["student_name"][:22])
        row_vals = []
        for skill in all_skills_list:
            level = analysis["verified_skills"].get(skill, None)
            if level in ("Advanced", "Intermediate"):
                row_vals.append(2)
            elif level == "Beginner":
                row_vals.append(1)
            else:
                row_vals.append(0)
        heatmap_data.append(row_vals)

    heatmap_matrix = pd.DataFrame(heatmap_data, index=student_labels, columns=all_skills_list)

    if not heatmap_matrix.empty:
        n_students = len(heatmap_matrix)
        n_skills   = len(all_skills_list)
        fig_h      = max(5, min(n_students * 0.42, 22))
        fig_w      = max(10, min(n_skills  * 0.38, 30))

        fig_heat, ax = plt.subplots(figsize=(fig_w, fig_h))
        fig_heat.patch.set_facecolor("#FFFFFF")
        ax.set_facecolor("#FFFFFF")

        cmap   = mcolors.ListedColormap(["#FF3B30", "#FF9500", "#34C759"])
        bounds = [-0.5, 0.5, 1.5, 2.5]
        norm   = mcolors.BoundaryNorm(bounds, cmap.N)

        sns.heatmap(
            heatmap_matrix, ax=ax, cmap=cmap, norm=norm,
            linewidths=0.25, linecolor="#F5F5F7",
            cbar=True,
            cbar_kws={"ticks": [0, 1, 2], "label": "Skill Level", "shrink": 0.7},
        )
        cbar = ax.collections[0].colorbar
        cbar.set_ticklabels(["Missing", "Beginner", "Intermediate / Advanced"])
        cbar.ax.yaxis.label.set_color("#1D1D1F")
        cbar.ax.tick_params(colors="#1D1D1F", labelsize=8)

        ax.set_xlabel("Skills", color="#86868B", fontsize=9, labelpad=8)
        ax.set_ylabel("Students", color="#86868B", fontsize=9, labelpad=8)
        ax.tick_params(colors="#1D1D1F", labelsize=7.5)
        ax.set_title(
            f"{n_students} Students  x  {n_skills} Skills",
            color="#1D1D1F", fontsize=10, pad=12, fontweight="600",
        )
        plt.xticks(rotation=45, ha="right", fontsize=7.5)
        plt.yticks(fontsize=7.5)
        plt.tight_layout(pad=1.5)

        st.pyplot(fig_heat, use_container_width=True)
        plt.close(fig_heat)

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # ── FIX 3: STUDENT TABLE — perfect alignment, no View button ──────────────
    # Build a plain DataFrame and render with st.dataframe for pixel-perfect
    # column alignment. No custom HTML grid needed, no View button.

    st.markdown('<div class="section-header">Student Analysis Table</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.85rem; color:#86868B; margin-top:-0.4rem; margin-bottom:1rem;">
        Full batch overview — student name, drift score, best career track, readiness, urgency level, and next recommended skill.
    </div>
    """, unsafe_allow_html=True)

    URGENCY_COLORS = {"Red": "#FF3B30", "Yellow": "#FF9500", "Green": "#34C759"}

    # Build display rows
    table_rows = []
    for analysis in all_student_analyses:
        name      = analysis["student_name"]
        sem       = analysis["semester"]
        drift     = analysis["drift_score"]
        drift_lbl = analysis["drift_label"]
        track     = analysis["best_track"]
        match     = analysis["match_pct"]
        readiness = analysis["readiness_score"]
        urgency   = analysis["urgency_level"]
        next_sk   = analysis.get("next_skill") or "—"

        table_rows.append({
            "Student": name,
            "Semester": f"Sem {sem}",
            "Drift Score": drift,
            "Drift Label": drift_lbl,
            "Best Track": track,
            "Match %": f"{match}%",
            "Readiness": f"{readiness}%",
            "Urgency": urgency,
            "Next Skill": next_sk,
        })

    table_df = pd.DataFrame(table_rows)

    # Use HTML table for full control — pixel-aligned columns, colored values, no view button
    def urgency_badge(u):
        color_map = {"Red": "#FF3B30", "Yellow": "#FF9500", "Green": "#34C759"}
        bg_map    = {"Red": "#FFF0EE", "Yellow": "#FFF8EE", "Green": "#EDFFF4"}
        c = color_map.get(u, "#6C63FF")
        b = bg_map.get(u, "#F0EFFF")
        return f'<span style="background:{b}; color:{c}; border-radius:6px; padding:3px 10px; font-size:0.75rem; font-weight:700; white-space:nowrap;">{u}</span>'

    def drift_color(score):
        if score <= 20:   return "#34C759"
        if score <= 60:   return "#FF9500"
        return "#FF3B30"

    def readiness_color(score_str):
        try:
            v = float(score_str.replace("%",""))
        except:
            return "#1D1D1F"
        if v >= 70:  return "#34C759"
        if v >= 40:  return "#FF9500"
        return "#FF3B30"

    # Build HTML table rows as plain string — NOT as f-string outer wrapper.
    # Reason: embedding an f-string (rows_html) inside another f-string causes
    # Streamlit to detect curly-brace remnants and render the entire block as
    # a raw code block instead of HTML. We concatenate the wrapper as plain strings.

    rows_html = ""
    for row in table_rows:
        d_col   = drift_color(row["Drift Score"])
        r_col   = readiness_color(row["Readiness"])
        u_badge = urgency_badge(row["Urgency"])

        rows_html += (
            "<tr>"
            "<td style='padding:12px 14px; background:#FFFFFF; border-top:1px solid #E5E5EA;"
            " border-bottom:1px solid #E5E5EA; border-left:1px solid #E5E5EA;"
            " border-radius:12px 0 0 12px; vertical-align:middle;'>"
            "<div style='font-weight:700; color:#1D1D1F; font-size:0.88rem;'>" + row["Student"] + "</div>"
            "<div style='color:#86868B; font-size:0.75rem;'>" + row["Semester"] + "</div>"
            "</td>"

            "<td style='padding:12px 14px; background:#FFFFFF; border-top:1px solid #E5E5EA;"
            " border-bottom:1px solid #E5E5EA; vertical-align:middle;'>"
            "<div style='font-weight:700; color:" + d_col + "; font-size:0.9rem;'>" + str(row["Drift Score"]) + "</div>"
            "<div style='color:#86868B; font-size:0.75rem;'>" + row["Drift Label"] + "</div>"
            "</td>"

            "<td style='padding:12px 14px; background:#FFFFFF; border-top:1px solid #E5E5EA;"
            " border-bottom:1px solid #E5E5EA; vertical-align:middle;'>"
            "<div style='font-weight:600; color:#6C63FF; font-size:0.85rem;'>" + row["Best Track"] + "</div>"
            "<div style='color:#86868B; font-size:0.75rem;'>" + row["Match %"] + " match</div>"
            "</td>"

            "<td style='padding:12px 14px; background:#FFFFFF; border-top:1px solid #E5E5EA;"
            " border-bottom:1px solid #E5E5EA; vertical-align:middle;'>"
            "<div style='font-weight:700; color:" + r_col + "; font-size:0.9rem;'>" + row["Readiness"] + "</div>"
            "</td>"

            "<td style='padding:12px 14px; background:#FFFFFF; border-top:1px solid #E5E5EA;"
            " border-bottom:1px solid #E5E5EA; vertical-align:middle;'>"
            + u_badge +
            "</td>"

            "<td style='padding:12px 14px; background:#FFFFFF; border-top:1px solid #E5E5EA;"
            " border-bottom:1px solid #E5E5EA; border-right:1px solid #E5E5EA;"
            " border-radius:0 12px 12px 0; vertical-align:middle;'>"
            "<div style='font-weight:600; color:#FF9500; font-size:0.85rem;'>" + row["Next Skill"] + "</div>"
            "</td>"
            "</tr>"
        )

    # Build the full table using plain string concatenation — no outer f-string
    table_header = (
        "<div style='width:100%; overflow-x:auto;'>"
        "<table style='width:100%; border-collapse:separate; border-spacing:0 6px;"
        " font-family:-apple-system, BlinkMacSystemFont, sans-serif;'>"
        "<thead>"
        "<tr style='background:#F5F5F7;'>"
        "<th style='padding:10px 14px; text-align:left; font-size:0.72rem; font-weight:700;"
        " color:#86868B; text-transform:uppercase; letter-spacing:0.05em;"
        " border-bottom:2px solid #E5E5EA; width:22%;'>Student</th>"
        "<th style='padding:10px 14px; text-align:left; font-size:0.72rem; font-weight:700;"
        " color:#86868B; text-transform:uppercase; letter-spacing:0.05em;"
        " border-bottom:2px solid #E5E5EA; width:16%;'>Drift Score</th>"
        "<th style='padding:10px 14px; text-align:left; font-size:0.72rem; font-weight:700;"
        " color:#86868B; text-transform:uppercase; letter-spacing:0.05em;"
        " border-bottom:2px solid #E5E5EA; width:20%;'>Best Track</th>"
        "<th style='padding:10px 14px; text-align:left; font-size:0.72rem; font-weight:700;"
        " color:#86868B; text-transform:uppercase; letter-spacing:0.05em;"
        " border-bottom:2px solid #E5E5EA; width:13%;'>Readiness</th>"
        "<th style='padding:10px 14px; text-align:left; font-size:0.72rem; font-weight:700;"
        " color:#86868B; text-transform:uppercase; letter-spacing:0.05em;"
        " border-bottom:2px solid #E5E5EA; width:13%;'>Urgency</th>"
        "<th style='padding:10px 14px; text-align:left; font-size:0.72rem; font-weight:700;"
        " color:#86868B; text-transform:uppercase; letter-spacing:0.05em;"
        " border-bottom:2px solid #E5E5EA; width:16%;'>Next Skill</th>"
        "</tr>"
        "</thead>"
        "<tbody>"
    )
    table_footer = "</tbody></table></div>"

    full_table_html = table_header + rows_html + table_footer

    st.markdown(full_table_html, unsafe_allow_html=True)

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # ── DOWNLOAD SECTION ──────────────────────────────────────────────────────

    st.markdown('<div class="section-header">Download Report</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.85rem; color:#86868B; margin-top:-0.4rem; margin-bottom:1rem;">
        Download the complete batch report as a CSV file. This file contains all student
        names, verified skill lists, and freshly recalculated scores. Share it with your
        placement cell or department.
    </div>
    """, unsafe_allow_html=True)

    csv_buffer = io.StringIO()
    merged_df.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode("utf-8")
    today_str = datetime.now().strftime("%Y_%m_%d")
    filename  = f"SkillDrift_Batch_Report_{today_str}.csv"

    col_dl, col_info = st.columns([2, 4], gap="medium")
    with col_dl:
        st.download_button(
            label="Download Batch Report (CSV)",
            data=csv_bytes,
            file_name=filename,
            mime="text/csv",
            use_container_width=True,
            type="primary",
        )
    with col_info:
        st.markdown(f"""
        <div style="
            background: #F5F5F7;
            border: 1px solid #E5E5EA;
            border-radius: 10px;
            padding: 0.75rem 1rem;
            font-size: 0.83rem;
            color: #86868B;
            line-height: 1.5;
        ">
            <strong style="color:#1D1D1F;">File:</strong> {filename}<br>
            <strong style="color:#1D1D1F;">Rows:</strong> {total_students} students<br>
            <strong style="color:#1D1D1F;">Generated:</strong> {datetime.now().strftime("%d %B %Y, %I:%M %p")}
        </div>
        """, unsafe_allow_html=True)