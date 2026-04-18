# Window 9 - Faculty Dashboard 
# =============================================================
# pages/09_faculty.py — Window 9: Faculty Dashboard
# Faculty login, multi-CSV upload, batch analysis, heatmap.
# Students cannot access this page.
# =============================================================

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import io
from datetime import datetime
from brain import (
    verify_faculty_login,
    validate_and_process_batch,
    CAREER_TRACKS,
)

st.set_page_config(
    page_title="SkillDrift — Faculty Dashboard",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide default nav
st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)

# =============================================================
# SECTION A — LOGIN SCREEN
# Shown when faculty is not yet logged in.
# =============================================================

if not st.session_state.get("faculty_logged_in"):

    st.markdown("""
    <div style="text-align:center; padding: 2rem 0 1rem 0;">
        <div style="font-size:2.5rem; font-weight:900; color:#FAFAFA;">
            🔐 Faculty / HOD Login
        </div>
        <div style="color:#BDC3C7; margin-top:0.5rem;">
            This dashboard is for faculty and HODs only.
            Students please use the main student flow.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_spacer1, col_form, col_spacer2 = st.columns([2, 3, 2])

    with col_form:
        st.markdown("---")

        # Lockout check
        lockout_time    = st.session_state.get("faculty_lockout_time")
        login_attempts  = st.session_state.get("faculty_login_attempts", 0)

        if lockout_time is not None and login_attempts >= 3:
            st.error(
                "🔒 Too many failed attempts. "
                "Please refresh the page to try again."
            )
            st.stop()

        email_input    = st.text_input("Faculty Gmail Address", placeholder="faculty@college.edu")
        password_input = st.text_input("Password", type="password", placeholder="Enter your password")

        col_login, col_home = st.columns(2)
        with col_login:
            login_btn = st.button("🔐 Login", type="primary", use_container_width=True)
        with col_home:
            if st.button("← Back to Home", use_container_width=True):
                st.switch_page("pages/01_home.py")

        if login_btn:
            if not email_input.strip() or not password_input.strip():
                st.error("Please enter both email and password.")
            else:
                success, faculty_name, error_msg = verify_faculty_login(
                    email_input.strip(),
                    password_input.strip(),
                )

                if success:
                    st.session_state["faculty_logged_in"] = True
                    st.session_state["faculty_name"]       = faculty_name
                    st.session_state["faculty_login_attempts"] = 0
                    st.session_state["faculty_lockout_time"]   = None
                    st.success(f"✅ Welcome, {faculty_name}! Redirecting...")
                    st.rerun()
                else:
                    attempts = st.session_state.get("faculty_login_attempts", 0) + 1
                    st.session_state["faculty_login_attempts"] = attempts

                    if attempts >= 3:
                        st.session_state["faculty_lockout_time"] = datetime.now().isoformat()
                        st.error(
                            "🔒 Too many failed attempts. "
                            "Please refresh the page to try again."
                        )
                    else:
                        remaining = 3 - attempts
                        st.error(f"❌ {error_msg} — {remaining} attempt(s) remaining.")

    st.stop()  # Nothing below this renders until login succeeds

# =============================================================
# SECTION B — FACULTY DASHBOARD (post-login)
# =============================================================

faculty_name = st.session_state.get("faculty_name", "Faculty")

# ── Faculty Sidebar ───────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding:1rem 0;">
        <div style="font-size:2rem;">🏫</div>
        <div style="font-weight:700; color:#FAFAFA; font-size:1rem;">
            {faculty_name}
        </div>
        <div style="color:#7F8C8D; font-size:0.8rem;">Faculty Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("← Back to Home", use_container_width=True):
        st.switch_page("pages/01_home.py")

    st.markdown("---")
    if st.button("🚪 Logout Faculty", use_container_width=True):
        st.session_state["faculty_logged_in"] = False
        st.session_state["faculty_name"]       = None
        st.session_state["faculty_login_attempts"] = 0
        st.session_state["faculty_lockout_time"]   = None
        st.rerun()

# ── Dashboard Header ──────────────────────────────────────────
st.title(f"🏫 Faculty Dashboard — Welcome, {faculty_name}")
st.markdown(
    "Upload student report CSV files here. The system validates each file, "
    "removes duplicates, and **recalculates all scores fresh from raw skill data** — "
    "so no student can cheat by editing their CSV."
)
st.markdown("---")

# =============================================================
# SECTION C — FILE UPLOAD
# =============================================================

st.subheader("📁 Upload Student Report CSVs")
st.markdown(
    "Upload individual student CSV files downloaded from Window 10. "
    "You can upload up to **100 files at once**."
)

uploaded_files = st.file_uploader(
    "Upload student report CSVs",
    type=["csv"],
    accept_multiple_files=True,
    help="Each file must be a SkillDrift student report CSV. Max 100 files.",
)

if not uploaded_files:
    st.info(
        "👆 Upload student CSV files above to begin batch analysis. "
        "Students download these files from Window 10 of their dashboard."
    )
    st.markdown("---")

    # Show expected CSV format
    with st.expander("📋 Expected CSV Format"):
        st.markdown(
            "The system reads only the `student_name`, `semester`, "
            "and `verified_skills` columns. All score columns are ignored "
            "and recalculated fresh to prevent tampering."
        )
        sample = pd.DataFrame([
            {
                "student_name": "Priya Sharma",
                "semester": 4,
                "verified_skills": "Python:Intermediate,SQL:Beginner,Excel:Beginner",
            },
            {
                "student_name": "Rahul Verma",
                "semester": 6,
                "verified_skills": "Java:Advanced,SQL:Intermediate,Docker:Beginner",
            },
        ])
        st.dataframe(sample, use_container_width=True, hide_index=True)
    st.stop()

# =============================================================
# SECTION D — PROCESS UPLOADED FILES
# =============================================================

process_btn = st.button(
    f"⚙️ Process {len(uploaded_files)} File(s) and Generate Batch Analysis",
    type="primary",
    use_container_width=True,
)

if process_btn:
    with st.spinner("Validating files, removing duplicates, recalculating all scores..."):
        results = validate_and_process_batch(uploaded_files)
        st.session_state["faculty_batch_results"] = results

# Pull from session so results persist without re-uploading
results = st.session_state.get("faculty_batch_results")

if not results:
    st.stop()

merged_df      = results.get("merged_df", pd.DataFrame())
valid_count    = results.get("valid_count", 0)
skipped_files  = results.get("skipped_files", [])
duplicate_count = results.get("duplicate_count", 0)
summary        = results.get("summary", {})

# ── Validation Summary ────────────────────────────────────────
st.markdown("---")
st.subheader("📋 Upload Validation Summary")

col_v1, col_v2, col_v3, col_v4 = st.columns(4)
with col_v1:
    st.metric("Files Uploaded",  len(uploaded_files))
with col_v2:
    st.metric("Files Valid",     valid_count)
with col_v3:
    st.metric("Files Skipped",   len(uploaded_files) - valid_count)
with col_v4:
    st.metric("Duplicates Removed", duplicate_count)

if skipped_files:
    with st.expander(f"⚠️ {len(skipped_files)} issue(s) during validation — click to expand"):
        for msg in skipped_files:
            st.warning(msg)

if merged_df.empty:
    st.error(
        "❌ No valid student data could be processed. "
        "Please check that files follow the expected format."
    )
    st.stop()

total_students = summary.get("total_students", len(merged_df))
st.success(
    f"✅ Successfully processed **{total_students} students** from {valid_count} valid file(s)."
)

st.markdown("---")

# =============================================================
# SECTION E — BATCH SUMMARY METRICS
# =============================================================

st.subheader("📊 Batch Summary Statistics")

avg_drift      = summary.get("avg_drift_score", 0)
avg_readiness  = summary.get("avg_readiness_score", 0)
avg_entropy    = summary.get("avg_entropy_score", 0)
red_count      = summary.get("red_count", 0)
yellow_count   = summary.get("yellow_count", 0)
green_count    = summary.get("green_count", 0)

col_m1, col_m2, col_m3, col_m4, col_m5, col_m6 = st.columns(6)
with col_m1:
    st.metric("Avg Drift Score",    avg_drift)
with col_m2:
    st.metric("Avg Readiness",      f"{avg_readiness}%")
with col_m3:
    st.metric("Avg Entropy",        f"{avg_entropy} bits")
with col_m4:
    st.metric("🔴 High Urgency",    red_count)
with col_m5:
    st.metric("🟡 Medium Urgency",  yellow_count)
with col_m6:
    st.metric("🟢 Low Urgency",     green_count)

# Urgency distribution pie
col_pie, col_track = st.columns(2)

with col_pie:
    st.markdown("#### Urgency Level Distribution")
    fig_pie = go.Figure(go.Pie(
        labels=["🔴 Red (High)", "🟡 Yellow (Medium)", "🟢 Green (Low)"],
        values=[red_count, yellow_count, green_count],
        marker_colors=["#E74C3C", "#F39C12", "#2ECC71"],
        hole=0.45,
        textfont=dict(color="#FAFAFA"),
    ))
    fig_pie.update_layout(
        paper_bgcolor="#0E1117",
        font=dict(color="#BDC3C7"),
        legend=dict(bgcolor="#1A1D27", bordercolor="#2D3250"),
        margin=dict(t=20, b=20, l=20, r=20),
        height=280,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_track:
    st.markdown("#### Best Track Distribution")
    track_dist = summary.get("track_distribution", {})
    if track_dist:
        fig_track_dist = go.Figure(go.Bar(
            x=list(track_dist.values()),
            y=list(track_dist.keys()),
            orientation="h",
            marker_color="#6C63FF",
            text=list(track_dist.values()),
            textposition="outside",
            textfont=dict(color="#BDC3C7"),
        ))
        fig_track_dist.update_layout(
            paper_bgcolor="#0E1117",
            plot_bgcolor="#0E1117",
            font=dict(color="#BDC3C7"),
            xaxis=dict(gridcolor="#2D3250"),
            yaxis=dict(gridcolor="#2D3250"),
            margin=dict(t=20, b=20, l=10, r=40),
            height=280,
        )
        st.plotly_chart(fig_track_dist, use_container_width=True)

st.markdown("---")

# ── Top Missing Skills ────────────────────────────────────────
st.subheader("🔍 Top 5 Skills Most Commonly Missing Across the Batch")

top_missing = summary.get("top_missing_skills", [])
if top_missing:
    for rank, (skill, count) in enumerate(top_missing, start=1):
        pct_missing = round((count / total_students) * 100, 1)
        bar_color = "#E74C3C" if rank == 1 else "#F39C12" if rank <= 3 else "#6C63FF"
        st.markdown(f"""
        <div style="background:#1A1D27; border:1px solid #2D3250;
                    border-radius:8px; padding:0.75rem 1rem; margin:0.3rem 0;
                    border-left:4px solid {bar_color};">
            <span style="color:{bar_color}; font-weight:900;">#{rank}</span>
            <span style="color:#FAFAFA; font-weight:700; margin-left:0.75rem;">
                {skill}
            </span>
            <span style="color:#BDC3C7; font-size:0.9rem; margin-left:0.75rem;">
                — missing in {count} students ({pct_missing}% of batch)
            </span>
        </div>
        """, unsafe_allow_html=True)

    # Faculty recommendation
    if top_missing:
        top_skill_name = top_missing[0][0]
        top_skill_pct  = round((top_missing[0][1] / total_students) * 100, 1)
        st.markdown(f"""
        <div style="background:#6C63FF22; border:1px solid #6C63FF;
                    border-radius:8px; padding:1rem; margin-top:1rem;">
            <strong style="color:#6C63FF;">📌 Faculty Recommendation:</strong>
            <span style="color:#FAFAFA;">
                {top_skill_pct}% of students in this batch are missing
                <strong>{top_skill_name}</strong>.
                A focused {top_skill_name} workshop before placement season
                is strongly recommended.
            </span>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# =============================================================
# SECTION F — STUDENT HEATMAP
# =============================================================

st.subheader("🗃️ Batch Skill Heatmap")
st.markdown(
    "Each row is a student. Each column is a skill. "
    "**Green** = verified at a good level. "
    "**Yellow** = Beginner. "
    "**Red** = missing."
)

# Build heatmap matrix
# Get all unique skills from all students
all_skills_set = set()
for _, row in merged_df.iterrows():
    from brain import parse_skills_string
    skills_dict = parse_skills_string(str(row.get("verified_skills", "")))
    all_skills_set.update(skills_dict.keys())

all_skills_list = sorted(list(all_skills_set))

# Build numeric matrix: 2 = Advanced/Intermediate, 1 = Beginner, 0 = Missing
heatmap_data = []
student_labels = []

for _, row in merged_df.iterrows():
    from brain import parse_skills_string
    skills_dict = parse_skills_string(str(row.get("verified_skills", "")))
    student_labels.append(row.get("student_name", "Unknown")[:20])

    row_vals = []
    for skill in all_skills_list:
        level = skills_dict.get(skill, None)
        if level in ("Advanced", "Intermediate"):
            row_vals.append(2)
        elif level == "Beginner":
            row_vals.append(1)
        else:
            row_vals.append(0)
    heatmap_data.append(row_vals)

heatmap_matrix = pd.DataFrame(
    heatmap_data,
    index=student_labels,
    columns=all_skills_list,
)

if not heatmap_matrix.empty:
    n_students = len(heatmap_matrix)
    fig_height = max(6, min(n_students * 0.4, 20))
    n_skills   = len(all_skills_list)
    fig_width  = max(10, min(n_skills * 0.35, 28))

    fig_heat, ax = plt.subplots(figsize=(fig_width, fig_height))
    fig_heat.patch.set_facecolor("#0E1117")
    ax.set_facecolor("#0E1117")

    cmap = mcolors.ListedColormap(["#E74C3C", "#F39C12", "#2ECC71"])
    bounds = [-0.5, 0.5, 1.5, 2.5]
    norm   = mcolors.BoundaryNorm(bounds, cmap.N)

    sns.heatmap(
        heatmap_matrix,
        ax=ax,
        cmap=cmap,
        norm=norm,
        linewidths=0.3,
        linecolor="#1A1D27",
        cbar=True,
        cbar_kws={
            "ticks": [0, 1, 2],
            "label": "Skill Level",
        },
    )

    cbar = ax.collections[0].colorbar
    cbar.set_ticklabels(["Missing", "Beginner", "Intermediate/Advanced"])
    cbar.ax.yaxis.label.set_color("#BDC3C7")
    cbar.ax.tick_params(colors="#BDC3C7")
    cbar.ax.set_facecolor("#1A1D27")

    ax.set_xlabel("Skills", color="#BDC3C7", fontsize=9)
    ax.set_ylabel("Students", color="#BDC3C7", fontsize=9)
    ax.tick_params(colors="#BDC3C7", labelsize=7)
    ax.set_title(
        f"Batch Skill Heatmap — {n_students} Students × {n_skills} Skills",
        color="#FAFAFA", fontsize=11, pad=10,
    )
    plt.xticks(rotation=45, ha="right", fontsize=7)
    plt.yticks(fontsize=7)
    plt.tight_layout()

    st.pyplot(fig_heat, use_container_width=True)
    plt.close(fig_heat)

st.markdown("---")

# =============================================================
# SECTION G — FULL STUDENT TABLE
# =============================================================

st.subheader("👥 Full Student Analysis Table")
st.markdown("All scores freshly recalculated from raw skill data.")

display_df = merged_df[[
    "student_name", "semester", "drift_score", "drift_label",
    "entropy_score", "best_track", "match_pct",
    "readiness_score", "urgency_level", "focus_debt_hours",
    "next_skill", "skill_count",
]].copy()

display_df.columns = [
    "Student Name", "Semester", "Drift Score", "Drift Label",
    "Entropy (bits)", "Best Track", "Match %",
    "Readiness %", "Urgency", "Focus Debt (hrs)",
    "Next Skill", "Verified Skills Count",
]

st.dataframe(display_df, use_container_width=True, hide_index=True)

st.markdown("---")

# =============================================================
# SECTION H — DOWNLOAD BUTTON
# =============================================================

st.subheader("⬇️ Download Full Batch Report")

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
)

st.caption(
    "This CSV contains all student names, verified skill lists, "
    "and freshly recalculated scores. Share it with your placement cell "
    "or use it for curriculum planning."
)