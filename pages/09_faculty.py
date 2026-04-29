# pages/09_faculty.py — Faculty Dashboard (Login + Upload)
# FIX 1: Login max-width constrained to 480px — no stretching
# FIX 4: Back to Upload sets faculty_active_view = "upload" before switch_page
# FIX 5: Sign Out uses st.button + st.switch_page — no broken href routing

import streamlit as st
from session_store import init_session
import pandas as pd
import io
import zipfile
import os
from datetime import datetime
from brain import (
    verify_faculty_login,
    validate_and_process_batch,
)

# ── Layout: centered for login, wide after login ──────────────────────────────
_logged_in = st.session_state.get("faculty_logged_in", False)

st.set_page_config(
    page_title="SkillDrift — Faculty",
    page_icon="assets/logo.png",
    layout="wide" if _logged_in else "centered",
    initial_sidebar_state="collapsed",
)

init_session()

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL STYLES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800;900&family=Inter:wght@400;500;600;700&display=swap');

    [data-testid="stSidebarNav"]            { display: none !important; }
    [data-testid="collapsedControl"]        { display: none !important; }
    [data-testid="stExpandSidebar"]         { display: none !important; }
    [data-testid="stSidebarCollapseButton"] { display: none !important; }
    section[data-testid="stSidebar"]        { display: none !important; }
    header[data-testid="stHeader"]          { display: none !important; }
    .stDeployButton                         { display: none !important; }
    #MainMenu                               { display: none !important; }
    footer                                  { display: none !important; }

    :root {
        --blue:    #002c98;
        --text:    #171c1f;
        --muted:   #515f74;
        --surface: #f6fafe;
        --card:    #ffffff;
        --border:  #e2e8f0;
        --green:   #15803d;
        --red:     #ba1a1a;
        --amber:   #d97706;
    }

    html, body, .stApp {
        background-color: var(--surface) !important;
        font-family: 'Inter', sans-serif;
        color: var(--text);
    }

    /* Login layout uses centered (Streamlit default ~680px) but we further
       constrain with a wrapper div to 480px */
    .login-wrapper {
        max-width:    480px;
        margin:       0 auto;
        padding:      0 1rem;
    }

    /* Dashboard layout — max 1000px */
    .block-container {
        padding-top:    0         !important;
        padding-bottom: 3rem      !important;
        max-width:      1000px    !important;
        margin-left:    auto      !important;
        margin-right:   auto      !important;
        padding-left:   2rem      !important;
        padding-right:  2rem      !important;
    }

    h1, h2, h3, h4 {
        font-family: 'Manrope', sans-serif !important;
        color: var(--text) !important;
    }

    .stButton > button {
        border-radius:  8px;
        border:         1.5px solid var(--border);
        background:     var(--card);
        color:          var(--text);
        font-weight:    600;
        font-size:      0.9rem;
        font-family:    'Inter', sans-serif;
        padding:        0.5rem 1.25rem;
        transition:     all 0.12s ease;
    }
    .stButton > button:hover { background: #f0f4f8; border-color: #c2cad4; }
    .stButton > button[kind="primary"] {
        background:   var(--blue);
        color:        #ffffff;
        border-color: var(--blue);
        font-weight:  700;
    }
    .stButton > button[kind="primary"]:hover {
        background:   #0038bf;
        border-color: #0038bf;
    }

    .stTextInput label {
        font-family: 'Inter', sans-serif !important;
        font-size:   0.88rem !important;
        font-weight: 600 !important;
        color:       var(--text) !important;
    }
    .stTextInput input {
        font-family:   'Inter', sans-serif !important;
        font-size:     0.95rem !important;
        border-radius: 8px !important;
        border:        1.5px solid var(--border) !important;
        padding:       0.6rem 0.85rem !important;
    }
    .stTextInput input:focus {
        border-color: var(--blue) !important;
        box-shadow:   0 0 0 3px rgba(0,44,152,0.1) !important;
    }

    .stAlert { border-radius: 10px; font-family: 'Inter', sans-serif; }

    [data-testid="stFileUploader"] {
        border:        2px dashed var(--border);
        border-radius: 12px;
        background:    var(--card);
        padding:       0.5rem;
    }

    [data-testid="stExpander"] {
        background:    var(--card) !important;
        border:        1px solid var(--border) !important;
        border-radius: 10px !important;
    }
    [data-testid="stExpander"] summary {
        font-family: 'Inter', sans-serif !important;
        font-size:   0.88rem !important;
        font-weight: 600 !important;
        color:       var(--text) !important;
    }

    .stDownloadButton > button {
        border-radius:  8px;
        border:         1.5px solid var(--blue);
        background:     var(--blue);
        color:          #ffffff;
        font-weight:    700;
        font-size:      0.9rem;
        font-family:    'Inter', sans-serif;
        padding:        0.55rem 1.25rem;
    }
    .stDownloadButton > button:hover {
        background:   #0038bf;
        border-color: #0038bf;
    }

    .stDataFrame thead tr th {
        background-color: #f8fafc !important;
        color:            var(--muted) !important;
        font-size:        0.72rem !important;
        font-weight:      700 !important;
        letter-spacing:   0.06em !important;
        text-transform:   uppercase !important;
        font-family:      'Inter', sans-serif !important;
    }

    .sd-kpi {
        background:    var(--card);
        border:        1px solid var(--border);
        border-radius: 12px;
        padding:       20px 16px 18px;
        height:        100%;
        box-sizing:    border-box;
    }
    .sd-kpi-label {
        font-size:      0.65rem;
        font-weight:    700;
        color:          var(--muted);
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-family:    'Inter', sans-serif;
        margin-bottom:  8px;
        white-space:    nowrap;
    }
    .sd-kpi-value {
        font-size:   1.75rem;
        font-weight: 800;
        font-family: 'Manrope', sans-serif;
        color:       var(--text);
        line-height: 1;
        white-space: nowrap;
    }
    .sd-kpi-sub {
        font-size:   0.75rem;
        color:       var(--muted);
        margin-top:  6px;
        font-family: 'Inter', sans-serif;
        white-space: nowrap;
    }

    .sd-card-accent-blue {
        background:    var(--card);
        border:        1px solid var(--border);
        border-left:   4px solid var(--blue);
        border-radius: 12px;
        padding:       18px 16px;
    }
    .sd-card-accent-green {
        background:    var(--card);
        border:        1px solid var(--border);
        border-left:   4px solid var(--green);
        border-radius: 12px;
        padding:       18px 16px;
    }

    .sd-section-label {
        font-size:      0.7rem;
        font-weight:    700;
        color:          var(--muted);
        letter-spacing: 0.1em;
        text-transform: uppercase;
        font-family:    'Inter', sans-serif;
        margin-bottom:  14px;
        padding-bottom: 10px;
        border-bottom:  1px solid var(--border);
    }

    .sd-divider {
        border:     none;
        border-top: 1px solid var(--border);
        margin:     1.75rem 0;
    }

    .fac-topbar {
        display:         flex;
        justify-content: space-between;
        align-items:     center;
        padding:         16px 0;
        border-bottom:   1px solid var(--border);
        margin-bottom:   24px;
    }
    .fac-logo {
        font-family:    'Manrope', sans-serif;
        font-size:      1.15rem;
        font-weight:    800;
        color:          var(--blue);
        letter-spacing: -0.02em;
    }
    .fac-subtitle {
        font-family: 'Inter', sans-serif;
        font-size:   0.8rem;
        color:       var(--muted);
        margin-top:  2px;
    }

    /* ── Login page specific ── */
    .login-logo-text {
        font-family:    'Manrope', sans-serif;
        font-size:      1.25rem;
        font-weight:    800;
        color:          var(--blue);
        letter-spacing: -0.02em;
        text-align:     center;
        display:        block;
        margin-bottom:  8px;
    }
    .login-heading {
        font-family:   'Manrope', sans-serif;
        font-size:     1.75rem;
        font-weight:   800;
        color:         var(--text);
        text-align:    center;
        margin-bottom: 4px;
        line-height:   1.2;
    }
    .login-sub {
        font-size:     0.88rem;
        color:         var(--muted);
        text-align:    center;
        margin-bottom: 32px;
        font-family:   'Inter', sans-serif;
    }

    /* ── Tab switcher ── */
    .sd-tabs {
        display:       flex;
        margin-bottom: 24px;
        border-radius: 10px;
        overflow:      hidden;
        border:        1.5px solid var(--border);
    }
    .sd-tab-active {
        flex:            1;
        padding:         0.6rem 0;
        text-align:      center;
        font-size:       0.88rem;
        font-weight:     700;
        background:      var(--blue);
        color:           #ffffff;
        font-family:     'Inter', sans-serif;
        text-decoration: none;
        display:         block;
    }
    .sd-tab-inactive {
        flex:            1;
        padding:         0.6rem 0;
        text-align:      center;
        font-size:       0.88rem;
        font-weight:     600;
        background:      var(--card);
        color:           var(--muted);
        font-family:     'Inter', sans-serif;
        text-decoration: none;
        display:         block;
        transition:      background 0.12s;
    }
    .sd-tab-inactive:hover { background: #f0f4f8; color: var(--text); }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def extract_csvs_from_zip(zip_file_obj) -> list:
    extracted = []
    try:
        with zipfile.ZipFile(zip_file_obj, "r") as zf:
            for name in zf.namelist():
                if name.lower().endswith(".csv") and not name.startswith("__MACOSX"):
                    data = zf.read(name)
                    buf  = io.BytesIO(data)
                    buf.name = os.path.basename(name)
                    extracted.append(buf)
    except zipfile.BadZipFile:
        pass
    return extracted


def do_signout():
    """Clear all faculty session state and rerun to show login."""
    keys_to_clear = [k for k in st.session_state.keys() if k.startswith("faculty")]
    for k in keys_to_clear:
        del st.session_state[k]
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# LOGIN SCREEN
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.get("faculty_logged_in"):

    # FIX 1: constrain login to 480px via wrapper — not stretched
    st.markdown("""
    <style>
        /* On centered layout the block-container is already ~680px.
           We wrap inputs in a narrower div so the form looks compact. */
        .login-outer {
            max-width:  480px;
            margin:     0 auto;
            padding:    0;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:2.5rem;'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div style='max-width:480px;margin:0 auto;'>
        <div style='text-align:center;margin-bottom:6px;'>
            <span class='login-logo-text'>SkillDrift</span>
        </div>
        <div class='login-heading'>Faculty Login</div>
        <div class='login-sub'>Sign in to access the Faculty Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    # Constrain input width via columns trick: spacer | form | spacer
    _, col_form, _ = st.columns([1, 4, 1])

    with col_form:
        lockout_time   = st.session_state.get("faculty_lockout_time")
        login_attempts = st.session_state.get("faculty_login_attempts", 0)

        if lockout_time is not None and login_attempts >= 3:
            st.error("Account temporarily locked. Refresh the page to try again.")
            st.stop()

        email_input    = st.text_input("Email Address", placeholder="faculty@college.edu", key="login_email")
        password_input = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pwd")

        st.markdown("<div style='height:0.35rem;'></div>", unsafe_allow_html=True)

        col_login, col_home = st.columns(2)
        with col_login:
            login_btn = st.button("Sign In", type="primary", use_container_width=True, key="login_btn")
        with col_home:
            if st.button("Back to Home", use_container_width=True, key="home_btn"):
                st.switch_page("pages/01_home.py")

        if login_btn:
            if not email_input.strip() or not password_input.strip():
                st.error("Please enter both email address and password.")
            else:
                success, faculty_name_val, error_msg = verify_faculty_login(
                    email_input.strip(), password_input.strip()
                )
                if success:
                    st.session_state["faculty_logged_in"]      = True
                    st.session_state["faculty_name"]           = faculty_name_val
                    st.session_state["faculty_login_attempts"] = 0
                    st.session_state["faculty_lockout_time"]   = None
                    st.session_state["faculty_active_view"]    = "upload"
                    st.rerun()
                else:
                    attempts = st.session_state.get("faculty_login_attempts", 0) + 1
                    st.session_state["faculty_login_attempts"] = attempts
                    if attempts >= 3:
                        st.session_state["faculty_lockout_time"] = datetime.now().isoformat()
                        st.error("Account locked — too many failed attempts. Refresh the page.")
                    else:
                        st.error(f"Incorrect credentials. {3 - attempts} attempt(s) remaining.")

    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# POST-LOGIN DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
faculty_name = st.session_state.get("faculty_name", "Faculty")

if "faculty_active_view" not in st.session_state:
    st.session_state["faculty_active_view"] = "upload"

# ── Handle query param: tab switching from batch results page ─────────────────
_qp = st.query_params.to_dict()
if _qp.get("tab") == "upload":
    st.session_state["faculty_active_view"] = "upload"
    st.query_params.clear()
    st.rerun()
if _qp.get("tab") == "results":
    st.session_state["faculty_active_view"] = "results"
    st.query_params.clear()
    st.rerun()

# ── TOP NAV BAR — uses Streamlit buttons (no href) ────────────────────────────
col_logo, col_nav = st.columns([7, 3])
with col_logo:
    st.markdown(
        "<div class='fac-topbar' style='border-bottom:none;margin-bottom:0;padding-bottom:0;'>"
        "<div>"
        "<div class='fac-logo'>SkillDrift</div>"
        "<div class='fac-subtitle'>Faculty Dashboard &mdash; " + faculty_name + "</div>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )
with col_nav:
    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    nav_c1, nav_c2 = st.columns(2)
    with nav_c1:
        if st.button("Home", use_container_width=True, key="topnav_home"):
            st.switch_page("pages/01_home.py")
    with nav_c2:
        # FIX 5: pure Streamlit button — never causes "Page not found"
        if st.button("Sign Out", use_container_width=True, key="topnav_signout"):
            do_signout()

st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:0 0 22px 0;'>",
            unsafe_allow_html=True)

# ── TAB SWITCHER ──────────────────────────────────────────────────────────────
active_view = st.session_state.get("faculty_active_view", "upload")
has_results = bool(st.session_state.get("faculty_batch_results"))

if has_results:
    upload_cls  = "sd-tab-active"   if active_view == "upload"  else "sd-tab-inactive"
    results_cls = "sd-tab-active"   if active_view == "results" else "sd-tab-inactive"
    st.markdown(
        "<div class='sd-tabs'>"
        "<a href='?tab=upload'  class='" + upload_cls  + "'>Upload Files</a>"
        "<a href='?tab=results' class='" + results_cls + "'>Analysis Results</a>"
        "</div>",
        unsafe_allow_html=True,
    )


# =============================================================================
# VIEW A — UPLOAD
# =============================================================================
if active_view == "upload":

    st.markdown('<div class="sd-section-label">Upload Student Reports</div>', unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#515f74;font-size:0.87rem;margin-top:-8px;margin-bottom:18px;"
        "font-family:Inter,sans-serif;'>"
        "Upload student CSV files or a ZIP folder. Scores are recalculated from raw skill data."
        "</p>",
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns(2, gap="medium")
    with col_a:
        st.markdown("""
        <div class="sd-card-accent-blue">
            <div style="font-family:Manrope,sans-serif;font-weight:700;font-size:0.9rem;
                        color:#171c1f;margin-bottom:6px;">Option A — CSV Files</div>
            <div style="font-size:0.83rem;color:#515f74;line-height:1.55;">
                Upload one or more <code style="background:#f6fafe;padding:1px 5px;
                border-radius:4px;">.csv</code> files from the student Final Report page.
                Supports up to 100 files at once.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown("""
        <div class="sd-card-accent-green">
            <div style="font-family:Manrope,sans-serif;font-weight:700;font-size:0.9rem;
                        color:#171c1f;margin-bottom:6px;">Option B — ZIP Folder</div>
            <div style="font-size:0.83rem;color:#515f74;line-height:1.55;">
                Compress all CSVs into one <code style="background:#f6fafe;padding:1px 5px;
                border-radius:4px;">.zip</code> and upload here.
                All CSV files inside are extracted automatically.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.75rem;'></div>", unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Drop files here or click to browse",
        type=["csv", "zip"],
        accept_multiple_files=True,
        help="Accepts .csv files and .zip archives.",
        key="file_uploader",
    )

    with st.expander("Expected CSV format"):
        st.markdown(
            "<div style='color:#171c1f;font-size:0.85rem;line-height:1.6;font-family:Inter,sans-serif;'>"
            "Required columns: <strong>student_name</strong>, <strong>semester</strong>, "
            "<strong>verified_skills</strong>. All other columns are ignored and recalculated."
            "</div>",
            unsafe_allow_html=True,
        )
        sample = pd.DataFrame([
            {"student_name": "Priya Sharma", "semester": 4,
             "verified_skills": "Python:Intermediate,SQL:Beginner"},
            {"student_name": "Rahul Verma",  "semester": 6,
             "verified_skills": "Java:Advanced,SQL:Intermediate,Docker:Beginner"},
        ])
        st.dataframe(sample, use_container_width=True, hide_index=True)

    if not uploaded_files:
        st.markdown("<div style='height:0.75rem;'></div>", unsafe_allow_html=True)
        st.info("Upload student CSV files or a ZIP folder above to get started.")
        st.stop()

    direct_csvs, zip_extracted_csvs, zip_names = [], [], []
    for f in uploaded_files:
        if f.name.lower().endswith(".zip"):
            extracted = extract_csvs_from_zip(f)
            zip_extracted_csvs.extend(extracted)
            zip_names.append(f.name)
        else:
            direct_csvs.append(f)

    all_csv_files = direct_csvs + zip_extracted_csvs

    st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        st.markdown(f"""
        <div class="sd-kpi">
            <div class="sd-kpi-label">Total Files Ready</div>
            <div class="sd-kpi-value">{len(all_csv_files)}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="sd-kpi">
            <div class="sd-kpi-label">Direct CSVs</div>
            <div class="sd-kpi-value" style="color:#002c98;">{len(direct_csvs)}</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        zip_sub = ("<div class='sd-kpi-sub'>" + ", ".join(zip_names) + "</div>") if zip_names else ""
        st.markdown(f"""
        <div class="sd-kpi">
            <div class="sd-kpi-label">From ZIP</div>
            <div class="sd-kpi-value" style="color:#15803d;">{len(zip_extracted_csvs)}</div>
            {zip_sub}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    if st.button(
        f"Run Batch Analysis  ({len(all_csv_files)} file{'s' if len(all_csv_files) != 1 else ''})",
        type="primary",
        use_container_width=True,
        key="process_btn",
    ):
        with st.spinner("Validating files and recalculating all scores..."):
            results = validate_and_process_batch(all_csv_files)
            st.session_state["faculty_batch_results"] = results
            st.session_state["faculty_active_view"]   = "results"
        st.switch_page("pages/09c_batch_results.py")


# =============================================================================
# VIEW B — redirect to dedicated results page
# =============================================================================
elif active_view == "results":
    if not st.session_state.get("faculty_batch_results"):
        st.warning("No results found. Upload files and run batch analysis first.")
        if st.button("Go to Upload", key="goto_upload"):
            st.session_state["faculty_active_view"] = "upload"
            st.rerun()
        st.stop()
    st.switch_page("pages/09c_batch_results.py")
