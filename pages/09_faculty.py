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
    f"Process {len(all_csv_files)} File(s) and Generate Batch Analysis",
    type="primary",
    use_container_width=True,
)

if process_btn:
    with st.spinner("Validating files, removing duplicates, recalculating all scores..."):
        results = validate_and_process_batch(all_csv_files)
        st.session_state["faculty_batch_results"] = results

results = st.session_state.get("faculty_batch_results")
if not results:
    st.stop()

merged_df             = results.get("merged_df", pd.DataFrame())
all_student_analyses  = results.get("all_student_analyses", [])
valid_count           = results.get("valid_count", 0)
skipped_files         = results.get("skipped_files", [])
duplicate_count       = results.get("duplicate_count", 0)
summary               = results.get("summary", {})

# ─────────────────────────────────────────────────────────────────────────────
# VALIDATION SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("---")
st.subheader("Upload Validation Summary")

col_v1, col_v2, col_v3, col_v4 = st.columns(4)
with col_v1: st.metric("Files Uploaded",     len(all_csv_files))
with col_v2: st.metric("Files Valid",        valid_count)
with col_v3: st.metric("Files Skipped",      len(all_csv_files) - valid_count)
with col_v4: st.metric("Duplicates Removed", duplicate_count)

if skipped_files:
    with st.expander(f"{len(skipped_files)} issue(s) during validation"):
        for msg in skipped_files:
            st.warning(msg)

if merged_df.empty:
    st.error("No valid student data could be processed. Check that files follow the expected format.")
    st.stop()

total_students = summary.get("total_students", len(merged_df))
st.success(f"Successfully processed **{total_students} students** from {valid_count} valid file(s).")
st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# BATCH SUMMARY METRICS
# ─────────────────────────────────────────────────────────────────────────────

st.subheader("Batch Summary Statistics")

avg_drift     = summary.get("avg_drift_score", 0)
avg_readiness = summary.get("avg_readiness_score", 0)
avg_entropy   = summary.get("avg_entropy_score", 0)
red_count     = summary.get("red_count", 0)
yellow_count  = summary.get("yellow_count", 0)
green_count   = summary.get("green_count", 0)

col_m1, col_m2, col_m3, col_m4, col_m5, col_m6 = st.columns(6)
with col_m1: st.metric("Avg Drift Score",  avg_drift)
with col_m2: st.metric("Avg Readiness",    f"{avg_readiness}%")
with col_m3: st.metric("Avg Entropy",      f"{avg_entropy} bits")
with col_m4: st.metric("High Urgency",     red_count)
with col_m5: st.metric("Medium Urgency",   yellow_count)
with col_m6: st.metric("Low Urgency",      green_count)

col_pie, col_track = st.columns(2, gap="medium")

with col_pie:
    st.markdown("#### Urgency Level Distribution")
    fig_pie = go.Figure(go.Pie(
        labels=["High (Red)", "Medium (Yellow)", "Low (Green)"],
        values=[red_count, yellow_count, green_count],
        marker_colors=["#FF3B30", "#FF9500", "#34C759"],
        hole=0.45,
        textfont=dict(color="#1D1D1F"),
    ))
    fig_pie.update_layout(
        paper_bgcolor="#FFFFFF", font=dict(color="#1D1D1F"),
        legend=dict(bgcolor="#FFFFFF", bordercolor="#D2D2D7", borderwidth=1),
        margin=dict(t=20, b=20, l=20, r=20), height=260,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_track:
    st.markdown("#### Best Track Distribution")
    track_dist = summary.get("track_distribution", {})
    if track_dist:
        fig_track_dist = go.Figure(go.Bar(
            x=list(track_dist.values()), y=list(track_dist.keys()),
            orientation="h", marker_color="#6C63FF",
            text=list(track_dist.values()), textposition="outside",
            textfont=dict(color="#1D1D1F"),
        ))
        fig_track_dist.update_layout(
            paper_bgcolor="#FFFFFF", plot_bgcolor="#F5F5F7",
            font=dict(color="#1D1D1F"),
            xaxis=dict(gridcolor="#D2D2D7", color="#1D1D1F"),
            yaxis=dict(gridcolor="#D2D2D7", color="#1D1D1F"),
            margin=dict(t=20, b=20, l=10, r=40), height=260,
        )
        st.plotly_chart(fig_track_dist, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# TOP MISSING SKILLS
# ─────────────────────────────────────────────────────────────────────────────

st.subheader("Top 5 Skills Most Commonly Missing")

top_missing = summary.get("top_missing_skills", [])
if top_missing:
    for rank, (skill, count) in enumerate(top_missing, start=1):
        pct_missing = round((count / total_students) * 100, 1)
        bar_color = "#FF3B30" if rank == 1 else "#FF9500" if rank <= 3 else "#6C63FF"
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #D2D2D7;
                    border-left:4px solid {bar_color};
                    border-radius:10px; padding:0.75rem 1rem; margin:0.3rem 0;">
            <span style="color:{bar_color}; font-weight:700;">#{rank}</span>
            <span style="color:#1D1D1F; font-weight:600; margin-left:0.75rem;">{skill}</span>
            <span style="color:#86868B; font-size:0.9rem; margin-left:0.75rem;">
                — missing in {count} students ({pct_missing}% of batch)
            </span>
        </div>
        """, unsafe_allow_html=True)

    top_skill_name = top_missing[0][0]
    top_skill_pct  = round((top_missing[0][1] / total_students) * 100, 1)
    st.markdown(f"""
    <div style="background:#F0EFFF; border:1px solid #6C63FF;
                border-radius:10px; padding:1rem; margin-top:1rem;">
        <strong style="color:#6C63FF;">Faculty Recommendation:</strong>
        <span style="color:#1D1D1F;">
            {top_skill_pct}% of students are missing <strong>{top_skill_name}</strong>.
            A focused workshop is strongly recommended before placement season.
        </span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# HEATMAP
# ─────────────────────────────────────────────────────────────────────────────

st.subheader("Batch Skill Heatmap")
st.markdown("Green = verified at a good level · Yellow = Beginner · Red = missing")

all_skills_set = set()
for analysis in all_student_analyses:
    all_skills_set.update(analysis["verified_skills"].keys())
all_skills_list = sorted(list(all_skills_set))

heatmap_data   = []
student_labels = []

for analysis in all_student_analyses:
    student_labels.append(analysis["student_name"][:20])
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
    fig_height = max(5, min(n_students * 0.4, 20))
    fig_width  = max(10, min(n_skills * 0.35, 28))

    fig_heat, ax = plt.subplots(figsize=(fig_width, fig_height))
    fig_heat.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    cmap   = mcolors.ListedColormap(["#FF3B30", "#FF9500", "#34C759"])
    bounds = [-0.5, 0.5, 1.5, 2.5]
    norm   = mcolors.BoundaryNorm(bounds, cmap.N)

    sns.heatmap(
        heatmap_matrix, ax=ax, cmap=cmap, norm=norm,
        linewidths=0.3, linecolor="#F5F5F7", cbar=True,
        cbar_kws={"ticks": [0, 1, 2], "label": "Skill Level"},
    )
    cbar = ax.collections[0].colorbar
    cbar.set_ticklabels(["Missing", "Beginner", "Intermediate/Advanced"])
    cbar.ax.yaxis.label.set_color("#1D1D1F")
    cbar.ax.tick_params(colors="#1D1D1F")
    ax.set_xlabel("Skills", color="#1D1D1F", fontsize=9)
    ax.set_ylabel("Students", color="#1D1D1F", fontsize=9)
    ax.tick_params(colors="#1D1D1F", labelsize=7)
    ax.set_title(
        f"Batch Skill Heatmap — {n_students} Students × {n_skills} Skills",
        color="#1D1D1F", fontsize=11, pad=10,
    )
    plt.xticks(rotation=45, ha="right", fontsize=7)
    plt.yticks(fontsize=7)
    plt.tight_layout()
    st.pyplot(fig_heat, use_container_width=True)
    plt.close(fig_heat)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# PER-STUDENT TABLE WITH "VIEW DASHBOARD" BUTTON
# This is the new section. Each row shows the student summary and a button
# that stores that student's full analysis in session_state and navigates
# to the student view page.
# ─────────────────────────────────────────────────────────────────────────────

st.subheader("📋 Full Student Analysis Table")
st.markdown(
    "Click **View Dashboard** on any student to see their complete 8-window analysis — "
    "built from the data they submitted."
)

URGENCY_COLORS = {"Red": "#FF3B30", "Yellow": "#FF9500", "Green": "#34C759"}

# Store the lookup dict by student name for navigation
student_lookup = {a["student_name"]: a for a in all_student_analyses}
st.session_state["faculty_student_lookup"] = student_lookup

for analysis in all_student_analyses:
    name         = analysis["student_name"]
    sem          = analysis["semester"]
    drift        = analysis["drift_score"]
    drift_lbl    = analysis["drift_label"]
    track        = analysis["best_track"]
    match        = analysis["match_pct"]
    readiness    = analysis["readiness_score"]
    urgency      = analysis["urgency_level"]
    urgency_col  = URGENCY_COLORS.get(urgency, "#6C63FF")
    next_sk      = analysis["next_skill"]

    col_info, col_btn = st.columns([8, 2])

    with col_info:
        st.markdown(f"""
        <div style="background:#FFFFFF; border:1px solid #D2D2D7; border-radius:10px;
                    padding:0.75rem 1rem; display:flex; align-items:center;
                    flex-wrap:wrap; gap:1rem;">
            <div style="min-width:140px;">
                <div style="font-weight:700; color:#1D1D1F; font-size:0.95rem;">{name}</div>
                <div style="color:#86868B; font-size:0.8rem;">Semester {sem}</div>
            </div>
            <div style="min-width:110px;">
                <div style="font-size:0.75rem; color:#86868B;">Drift Score</div>
                <div style="font-weight:600; color:#1D1D1F;">{drift} — {drift_lbl}</div>
            </div>
            <div style="min-width:110px;">
                <div style="font-size:0.75rem; color:#86868B;">Best Track</div>
                <div style="font-weight:600; color:#6C63FF;">{track} ({match}%)</div>
            </div>
            <div style="min-width:90px;">
                <div style="font-size:0.75rem; color:#86868B;">Readiness</div>
                <div style="font-weight:600; color:#1D1D1F;">{readiness}%</div>
            </div>
            <div>
                <span style="background:{urgency_col}22; color:{urgency_col};
                             border-radius:6px; padding:2px 10px; font-size:0.78rem;
                             font-weight:700;">{urgency} Urgency</span>
            </div>
            <div style="min-width:120px;">
                <div style="font-size:0.75rem; color:#86868B;">Next Skill</div>
                <div style="font-weight:600; color:#FF9500;">{next_sk or "—"}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_btn:
        # The key must be unique per student
        if st.button("View Dashboard", key=f"view_dash_{name}", use_container_width=True):
            # Store the selected student analysis for the view page
            st.session_state["faculty_viewing_student"] = name
            st.switch_page("pages/09b_student_view.py")

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# DOWNLOAD FULL BATCH REPORT
# ─────────────────────────────────────────────────────────────────────────────

st.subheader("Download Full Batch Report")

csv_buffer = io.StringIO()
merged_df.to_csv(csv_buffer, index=False)
csv_bytes = csv_buffer.getvalue().encode("utf-8")
today_str = datetime.now().strftime("%Y_%m_%d")
filename  = f"SkillDrift_Batch_Report_{today_str}.csv"

st.download_button(
    label="⬇️ Download Full Batch Report as CSV",
    data=csv_bytes,
    file_name=filename,
    mime="text/csv",
    use_container_width=True,
    type="primary",
)
st.caption(
    "This CSV contains all student names, verified skill lists, "
    "and freshly recalculated scores. Share it with your placement cell."
)