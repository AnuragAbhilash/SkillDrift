# pages/09_faculty.py

import streamlit as st
import pandas as pd
import io
import zipfile
import os
from datetime import datetime
from brain import verify_faculty_login, validate_and_process_batch

_logged_in = st.session_state.get("faculty_logged_in", False)

st.set_page_config(
    page_title="SkillDrift — Faculty",
    page_icon="assets/logo.png",
    layout="wide" if _logged_in else "centered",
    initial_sidebar_state="collapsed",
)

try:
    from session_store import init_session
    init_session()
except ImportError:
    pass

SHARED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800;900&family=Inter:wght@400;500;600;700&display=swap');

[data-testid="stSidebarNav"],[data-testid="collapsedControl"],
[data-testid="stExpandSidebar"],[data-testid="stSidebarCollapseButton"],
section[data-testid="stSidebar"],header[data-testid="stHeader"],
.stDeployButton,#MainMenu,footer{display:none!important}

:root{
    --blue:#002c98;--text:#171c1f;--muted:#515f74;
    --surface:#f6fafe;--card:#ffffff;--border:#e2e8f0;
    --green:#15803d;--red:#ba1a1a;--amber:#d97706;
}

html,body,.stApp{background:var(--surface)!important;font-family:'Inter',sans-serif;color:var(--text)}

.block-container{
    padding-top:0!important;padding-bottom:3rem!important;
    max-width:1000px!important;margin:0 auto!important;
    padding-left:2rem!important;padding-right:2rem!important;
}

/* Buttons */
.stButton>button{
    border-radius:8px;border:1.5px solid var(--border);
    background:var(--card);color:var(--text);
    font-weight:600;font-size:0.87rem;font-family:'Inter',sans-serif;
    padding:0.45rem 1rem;transition:all 0.12s ease;white-space:nowrap;
}
.stButton>button:hover{background:#f0f4f8;border-color:#c2cad4}
.stButton>button[kind="primary"]{background:var(--blue);color:#fff;border-color:var(--blue);font-weight:700}
.stButton>button[kind="primary"]:hover{background:#0038bf;border-color:#0038bf}

/* Inputs */
.stTextInput label{font-family:'Inter',sans-serif!important;font-size:0.84rem!important;font-weight:600!important;color:var(--muted)!important}
.stTextInput input{font-family:'Inter',sans-serif!important;font-size:0.92rem!important;border-radius:8px!important;border:1.5px solid var(--border)!important;padding:0.55rem 0.85rem!important;background:var(--card)!important;color:var(--text)!important}
.stTextInput input:focus{border-color:var(--blue)!important;box-shadow:0 0 0 3px rgba(0,44,152,0.1)!important;outline:none!important}

.stAlert{border-radius:10px;font-family:'Inter',sans-serif}

[data-testid="stFileUploader"]{border:2px dashed var(--border);border-radius:12px;background:var(--card);padding:0.5rem}

[data-testid="stExpander"]{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:10px!important}
[data-testid="stExpander"] summary{font-family:'Inter',sans-serif!important;font-size:0.87rem!important;font-weight:600!important;color:var(--text)!important}

/* Topbar */
.fac-logo{font-family:'Manrope',sans-serif;font-size:1.1rem;font-weight:800;color:var(--blue);letter-spacing:-0.02em}
.fac-subtitle{font-size:0.78rem;color:var(--muted);margin-top:1px;font-family:'Inter',sans-serif}

/* Section label */
.sd-section-label{font-size:0.68rem;font-weight:700;color:var(--muted);letter-spacing:0.1em;text-transform:uppercase;font-family:'Inter',sans-serif;margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid var(--border)}

/* KPI */
.sd-kpi{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:16px 14px 14px;height:100%;box-sizing:border-box;overflow:hidden}
.sd-kpi-label{font-size:0.62rem;font-weight:700;color:var(--muted);letter-spacing:0.08em;text-transform:uppercase;font-family:'Inter',sans-serif;margin-bottom:6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sd-kpi-value{font-size:1.65rem;font-weight:800;font-family:'Manrope',sans-serif;color:var(--text);line-height:1;white-space:nowrap}
.sd-kpi-sub{font-size:0.72rem;color:var(--muted);margin-top:5px;font-family:'Inter',sans-serif;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

.sd-card-accent-blue{background:var(--card);border:1px solid var(--border);border-left:4px solid var(--blue);border-radius:10px;padding:16px 14px}
.sd-card-accent-green{background:var(--card);border:1px solid var(--border);border-left:4px solid var(--green);border-radius:10px;padding:16px 14px}
.sd-divider{border:none;border-top:1px solid var(--border);margin:1.5rem 0}

/* FIX 1: sign out wrapper */
.signout-wrap .stButton>button{border-color:#fca5a5!important;color:#ba1a1a!important;background:#fff5f5!important}
.signout-wrap .stButton>button:hover{background:#fef2f2!important;border-color:#f87171!important}

/* FIX 5: tab switcher */
.sd-tabs{display:flex;border:1.5px solid var(--border);border-radius:10px;overflow:hidden;margin-bottom:20px}
.sd-tab-active{flex:1;padding:0.55rem 0;text-align:center;font-size:0.87rem;font-weight:700;font-family:'Inter',sans-serif;background:var(--blue);color:#fff;text-decoration:none;cursor:pointer;display:block}
.sd-tab-inactive{flex:1;padding:0.55rem 0;text-align:center;font-size:0.87rem;font-weight:600;font-family:'Inter',sans-serif;background:var(--card);color:var(--muted);text-decoration:none;cursor:pointer;display:block}
.sd-tab-inactive:hover{background:#f0f4f8;color:var(--text)}

/* FIX 6: login card — 380px, narrow, professional */
.login-card{max-width:380px;margin:3.5rem auto 0;background:var(--card);border:1px solid var(--border);border-radius:16px;padding:2.25rem 2rem 2rem;box-shadow:0 4px 24px rgba(23,28,31,0.07)}
.login-logo{font-family:'Manrope',sans-serif;font-size:1.1rem;font-weight:800;color:var(--blue);letter-spacing:-0.02em;text-align:center;margin-bottom:10px;display:block}
.login-title{font-family:'Manrope',sans-serif;font-size:1.45rem;font-weight:800;color:var(--text);text-align:center;margin-bottom:4px;line-height:1.2}
.login-sub{font-size:0.82rem;color:var(--muted);text-align:center;margin-bottom:1.5rem;font-family:'Inter',sans-serif;line-height:1.5}
.login-divider{border:none;border-top:1px solid var(--border);margin:0 0 1.5rem}
</style>
"""
st.markdown(SHARED_CSS, unsafe_allow_html=True)


def extract_csvs_from_zip(zip_file_obj):
    extracted = []
    try:
        with zipfile.ZipFile(zip_file_obj, "r") as zf:
            for name in zf.namelist():
                if name.lower().endswith(".csv") and not name.startswith("__MACOSX"):
                    buf = io.BytesIO(zf.read(name))
                    buf.name = os.path.basename(name)
                    extracted.append(buf)
    except zipfile.BadZipFile:
        pass
    return extracted


def do_signout():
    for k in [k for k in st.session_state if k.startswith("faculty")]:
        del st.session_state[k]
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.get("faculty_logged_in"):

    # FIX 6: narrow card rendered via HTML, inputs constrained with column trick
    st.markdown("""
    <div class="login-card">
        <span class="login-logo">SkillDrift</span>
        <div class="login-title">Faculty Login</div>
        <div class="login-sub">Sign in to access the Faculty &amp; HOD Dashboard</div>
        <hr class="login-divider">
    </div>
    """, unsafe_allow_html=True)

    # Columns ratio 1:2:1 keeps the form ~380px wide on centered layout
    _, col_form, _ = st.columns([1, 2, 1])

    with col_form:
        lockout_time   = st.session_state.get("faculty_lockout_time")
        login_attempts = st.session_state.get("faculty_login_attempts", 0)

        if lockout_time is not None and login_attempts >= 3:
            st.error("Account temporarily locked. Refresh the page to try again.")
            st.stop()

        email_input    = st.text_input("Email Address", placeholder="faculty@college.edu", key="login_email")
        password_input = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pwd")

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        c_signin, c_home = st.columns(2)
        with c_signin:
            login_btn = st.button("Sign In", type="primary", use_container_width=True, key="login_btn")
        with c_home:
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
                    st.session_state.update({
                        "faculty_logged_in": True,
                        "faculty_name": faculty_name_val,
                        "faculty_login_attempts": 0,
                        "faculty_lockout_time": None,
                        "faculty_active_view": "upload",
                    })
                    st.rerun()
                else:
                    attempts = login_attempts + 1
                    st.session_state["faculty_login_attempts"] = attempts
                    if attempts >= 3:
                        st.session_state["faculty_lockout_time"] = datetime.now().isoformat()
                        st.error("Account locked after 3 failed attempts. Refresh the page.")
                    else:
                        st.error(f"Incorrect credentials. {3 - attempts} attempt(s) remaining.")
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# POST-LOGIN
# ─────────────────────────────────────────────────────────────────────────────
faculty_name = st.session_state.get("faculty_name", "Faculty")

if "faculty_active_view" not in st.session_state:
    st.session_state["faculty_active_view"] = "upload"

_qp = st.query_params.to_dict()
if _qp.get("tab") in ("upload", "results"):
    st.session_state["faculty_active_view"] = _qp["tab"]
    st.query_params.clear()
    st.rerun()

# FIX 1: topnav — [8,2] ratio, sign-out inside .signout-wrap
col_logo, col_nav = st.columns([8, 2])
with col_logo:
    st.markdown(
        "<div style='padding:14px 0 8px'>"
        "<div class='fac-logo'>SkillDrift</div>"
        "<div class='fac-subtitle'>Faculty Dashboard &mdash; " + faculty_name + "</div>"
        "</div>",
        unsafe_allow_html=True,
    )
with col_nav:
    st.markdown("<div style='padding-top:14px'>", unsafe_allow_html=True)
    nc1, nc2 = st.columns(2)
    with nc1:
        if st.button("Home", use_container_width=True, key="topnav_home"):
            st.switch_page("pages/01_home.py")
    with nc2:
        st.markdown("<div class='signout-wrap'>", unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True, key="topnav_signout"):
            do_signout()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:0 0 20px'>", unsafe_allow_html=True)

# FIX 5: tab switcher
active_view = st.session_state.get("faculty_active_view", "upload")
has_results = bool(st.session_state.get("faculty_batch_results"))

if has_results:
    uc = "sd-tab-active" if active_view == "upload"  else "sd-tab-inactive"
    rc = "sd-tab-active" if active_view == "results" else "sd-tab-inactive"
    st.markdown(
        f"<div class='sd-tabs'>"
        f"<a href='?tab=upload'  class='{uc}'>Upload Files</a>"
        f"<a href='?tab=results' class='{rc}'>Analysis Results</a>"
        f"</div>",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# VIEW A — UPLOAD
# ─────────────────────────────────────────────────────────────────────────────
if active_view == "upload":

    st.markdown('<div class="sd-section-label">Upload Student Reports</div>', unsafe_allow_html=True)
    st.markdown(
        "<p style='color:var(--muted);font-size:0.84rem;margin-top:-6px;margin-bottom:16px;"
        "font-family:Inter,sans-serif;line-height:1.55'>Upload student CSV files or a ZIP folder. "
        "All scores are recalculated from raw skill data.</p>",
        unsafe_allow_html=True,
    )

    ca, cb = st.columns(2, gap="medium")
    with ca:
        st.markdown("""
        <div class="sd-card-accent-blue">
            <div style="font-family:Manrope,sans-serif;font-weight:700;font-size:0.88rem;color:var(--text);margin-bottom:5px">Option A — CSV Files</div>
            <div style="font-size:0.81rem;color:var(--muted);line-height:1.55">Upload one or more <code style="background:#f0f4ff;padding:1px 5px;border-radius:3px;color:var(--blue)">.csv</code> files from the student Final Report page. Supports up to 100 files at once.</div>
        </div>
        """, unsafe_allow_html=True)
    with cb:
        st.markdown("""
        <div class="sd-card-accent-green">
            <div style="font-family:Manrope,sans-serif;font-weight:700;font-size:0.88rem;color:var(--text);margin-bottom:5px">Option B — ZIP Folder</div>
            <div style="font-size:0.81rem;color:var(--muted);line-height:1.55">Compress all CSVs into one <code style="background:#f0fff4;padding:1px 5px;border-radius:3px;color:var(--green)">.zip</code> and upload here. All CSV files inside are extracted automatically.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Drop files here or click to browse",
        type=["csv", "zip"], accept_multiple_files=True,
        key="file_uploader", label_visibility="collapsed",
    )

    with st.expander("Expected CSV format"):
        st.markdown(
            "<div style='font-size:0.83rem;color:var(--text);line-height:1.6;font-family:Inter,sans-serif'>"
            "Required columns: <strong>student_name</strong>, <strong>semester</strong>, "
            "<strong>verified_skills</strong>. All pre-calculated scores are ignored.</div>",
            unsafe_allow_html=True,
        )
        st.dataframe(pd.DataFrame([
            {"student_name":"Priya Sharma","semester":4,"verified_skills":"Python:Intermediate,SQL:Beginner"},
            {"student_name":"Rahul Verma", "semester":6,"verified_skills":"Java:Advanced,Docker:Beginner"},
        ]), use_container_width=True, hide_index=True)

    if not uploaded_files:
        st.info("Upload student CSV files or a ZIP folder above to get started.")
        st.stop()

    direct_csvs, zip_extracted_csvs, zip_names = [], [], []
    for f in uploaded_files:
        if f.name.lower().endswith(".zip"):
            ex = extract_csvs_from_zip(f); zip_extracted_csvs.extend(ex); zip_names.append(f.name)
        else:
            direct_csvs.append(f)
    all_csv_files = direct_csvs + zip_extracted_csvs

    if zip_names:
        st.success(f"Extracted from ZIP: {', '.join(zip_names)} — {len(zip_extracted_csvs)} CSV file(s) found.")

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3, gap="medium")
    with c1: st.markdown(f'<div class="sd-kpi"><div class="sd-kpi-label">Total Files Ready</div><div class="sd-kpi-value">{len(all_csv_files)}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="sd-kpi"><div class="sd-kpi-label">Direct CSVs</div><div class="sd-kpi-value" style="color:var(--blue)">{len(direct_csvs)}</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="sd-kpi"><div class="sd-kpi-label">From ZIP</div><div class="sd-kpi-value" style="color:var(--green)">{len(zip_extracted_csvs)}</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    if st.button(
        f"Run Batch Analysis  ({len(all_csv_files)} file{'s' if len(all_csv_files)!=1 else ''})",
        type="primary", use_container_width=True, key="process_btn",
    ):
        with st.spinner("Validating files and recalculating all scores..."):
            results = validate_and_process_batch(all_csv_files)
            st.session_state["faculty_batch_results"] = results
            st.session_state["faculty_active_view"]   = "results"
        st.switch_page("pages/09c_batch_results.py")

elif active_view == "results":
    if not st.session_state.get("faculty_batch_results"):
        st.warning("No results found. Upload files and run batch analysis first.")
        if st.button("Go to Upload", key="goto_upload"):
            st.session_state["faculty_active_view"] = "upload"; st.rerun()
        st.stop()
    st.switch_page("pages/09c_batch_results.py")