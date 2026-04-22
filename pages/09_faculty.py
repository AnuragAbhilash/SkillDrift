# pages/09_faculty.py — Window 9: Faculty Dashboard

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
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    [data-testid="stSidebarNav"] { display: none; }
    .stApp { background-color: #F5F5F7; }
    .block-container { padding-top: 2rem; padding-bottom: 3rem; }
    h1, h2, h3 { color: #1D1D1F !important; }
    .stButton > button {
        border-radius: 8px;
        border: 1px solid #D2D2D7;
        background: #F5F5F7;
        color: #1D1D1F;
        font-weight: 500;
        transition: all 0.15s ease;
    }
    .stButton > button:hover { background: #E8E8ED; }
    .stButton > button[kind="primary"] {
        background: #6C63FF;
        color: #FFFFFF;
        border-color: #6C63FF;
    }
    .stButton > button[kind="primary"]:hover { background: #5A52E0; }
    section[data-testid="stSidebar"] > div {
        background-color: #FFFFFF;
        border-right: 1px solid #D2D2D7;
    }
    .stTextInput > div > div input { border-radius: 8px; }
    .stAlert { border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# =============================================================
# SECTION A — LOGIN SCREEN
# =============================================================

if not st.session_state.get("faculty_logged_in"):

    st.markdown("""
    <div style="text-align:center; padding:2.5rem 0 1rem 0;">
        <div style="font-size:2.2rem; font-weight:700; color:#1D1D1F;">
            Faculty / HOD Login
        </div>
        <div style="color:#86868B; margin-top:0.5rem; font-size:1rem;">
            This dashboard is for faculty and HODs only.
            Students please use the main student flow.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_spacer1, col_form, col_spacer2 = st.columns([2, 3, 2])

    with col_form:
        st.markdown("---")

        lockout_time   = st.session_state.get("faculty_lockout_time")
        login_attempts = st.session_state.get("faculty_login_attempts", 0)

        if lockout_time is not None and login_attempts >= 3:
            st.error("Too many failed attempts. Please refresh the page to try again.")
            st.stop()

        email_input    = st.text_input(
            "Faculty Email Address", placeholder="faculty@college.edu"
        )
        password_input = st.text_input(
            "Password", type="password", placeholder="Enter your password"
        )

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
                    email_input.strip(),
                    password_input.strip(),
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

# =============================================================
# SECTION B — FACULTY DASHBOARD (post-login)
# =============================================================

faculty_name = st.session_state.get("faculty_name", "Faculty")

with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding:1.5rem 0 1rem 0;">
        <div style="width:60px; height:60px; border-radius:50%; background:#F0EFFF;
                    display:flex; align-items:center; justify-content:center;
                    margin:0 auto; font-size:1.5rem; color:#6C63FF; font-weight:700;">
            F
        </div>
        <div style="font-weight:700; color:#1D1D1F; font-size:1rem; margin-top:0.75rem;">
            {faculty_name}
        </div>
        <div style="color:#86868B; font-size:0.8rem;">Faculty Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("Back to Home", use_container_width=True):
        st.switch_page("pages/01_home.py")

    st.markdown("---")
    if st.button("Sign Out", use_container_width=True):
        st.session_state["faculty_logged_in"]      = False
        st.session_state["faculty_name"]           = None
        st.session_state["faculty_login_attempts"] = 0
        st.session_state["faculty_lockout_time"]   = None
        st.rerun()

# ── Header ────────────────────────────────────────────────────
st.title(f"Faculty Dashboard — Welcome, {faculty_name}")
st.markdown(
    "Upload student report CSV files here. The system validates each file, "
    "removes duplicates, and **recalculates all scores fresh from raw skill data** — "
    "so no student can manipulate their CSV to appear more ready than they are."
)
st.markdown("---")

# =============================================================
# SECTION C — FILE UPLOAD
# =============================================================

st.subheader("Upload Student Report CSVs")
st.markdown(
    "Upload individual student CSV files downloaded from the Final Report page. "
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
        "Upload student CSV files above to begin batch analysis. "
        "Students download these files from the Final Report page of their dashboard."
    )
    st.markdown("---")

    with st.expander("Expected CSV Format"):
        st.markdown(
            "The system reads only the `student_name`, `semester`, "
            "and `verified_skills` columns. All score columns are ignored "
            "and recalculated fresh to prevent tampering."
        )
        sample = pd.DataFrame([
            {
                "student_name":   "Priya Sharma",
                "semester":       4,
                "verified_skills": "Python:Intermediate,SQL:Beginner,Excel:Beginner",
            },
            {
                "student_name":   "Rahul Verma",
                "semester":       6,
                "verified_skills": "Java:Advanced,SQL:Intermediate,Docker:Beginner",
            },
        ])
        st.dataframe(sample, use_container_width=True, hide_index=True)
    st.stop()

# =============================================================
# SECTION D — PROCESS FILES
# =============================================================

process_btn = st.button(
    f"Process {len(uploaded_files)} File(s) and Generate Batch Analysis",
    type="primary",
    use_container_width=True,
)

if process_btn:
    with st.spinner("Validating files, removing duplicates, recalculating all scores..."):
        results = validate_and_process_batch(uploaded_files)
        st.session_state["faculty_batch_results"] = results

results = st.session_state.get("faculty_batch_results")
if not results:
    st.stop()

merged_df       = results.get("merged_df", pd.DataFrame())
valid_count     = results.get("valid_count", 0)
skipped_files   = results.get("skipped_files", [])
duplicate_count = results.get("duplicate_count", 0)
summary         = results.get("summary", {})

# ── Validation Summary ────────────────────────────────────────
st.markdown("---")
st.subheader("Upload Validation Summary")

col_v1, col_v2, col_v3, col_v4 = st.columns(4)
with col_v1:
    st.metric("Files Uploaded",    len(uploaded_files))
with col_v2:
    st.metric("Files Valid",       valid_count)
with col_v3:
    st.metric("Files Skipped",     len(uploaded_files) - valid_count)
with col_v4:
    st.metric("Duplicates Removed", duplicate_count)

if skipped_files:
    with st.expander(f"{len(skipped_files)} issue(s) during validation — click to expand"):
        for msg in skipped_files:
            st.warning(msg)

if merged_df.empty:
    st.error(
        "No valid student data could be processed. "
        "Please check that files follow the expected format."
    )
    st.stop()

total_students = summary.get("total_students", len(merged_df))
st.success(f"Successfully processed **{total_students} students** from {valid_count} valid file(s).")
st.markdown("---")

# =============================================================
# SECTION E — BATCH SUMMARY METRICS
# =============================================================

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
        paper_bgcolor="#FFFFFF",
        font=dict(color="#1D1D1F"),
        legend=dict(bgcolor="#FFFFFF", bordercolor="#D2D2D7", borderwidth=1),
        margin=dict(t=20, b=20, l=20, r=20),
        height=260,
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
            textfont=dict(color="#1D1D1F"),
        ))
        fig_track_dist.update_layout(
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#F5F5F7",
            font=dict(color="#1D1D1F"),
            xaxis=dict(gridcolor="#D2D2D7", color="#1D1D1F"),
            yaxis=dict(gridcolor="#D2D2D7", color="#1D1D1F"),
            margin=dict(t=20, b=20, l=10, r=40),
            height=260,
        )
        st.plotly_chart(fig_track_dist, use_container_width=True)

st.markdown("---")

# ── Top Missing Skills ────────────────────────────────────────
st.subheader("Top 5 Skills Most Commonly Missing Across the Batch")

top_missing = summary.get("top_missing_skills", [])
if top_missing:
    for rank, (skill, count) in enumerate(top_missing, start=1):
        pct_missing = round((count / total_students) * 100, 1)
        bar_color   = "#FF3B30" if rank == 1 else "#FF9500" if rank <= 3 else "#6C63FF"
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

    if top_missing:
        top_skill_name = top_missing[0][0]
        top_skill_pct  = round((top_missing[0][1] / total_students) * 100, 1)
        st.markdown(f"""
        <div style="background:#F0EFFF; border:1px solid #6C63FF;
                    border-radius:10px; padding:1rem; margin-top:1rem;">
            <strong style="color:#6C63FF;">Faculty Recommendation:</strong>
            <span style="color:#1D1D1F;">
                {top_skill_pct}% of students in this batch are missing
                <strong>{top_skill_name}</strong>.
                A focused {top_skill_name} workshop before placement season
                is strongly recommended.
            </span>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# =============================================================
# SECTION F — HEATMAP
# =============================================================

st.subheader("Batch Skill Heatmap")
st.markdown(
    "Each row is a student. Each column is a skill. "
    "Green = verified at a good level. Yellow = Beginner. Red = missing."
)

all_skills_set = set()
for _, row in merged_df.iterrows():
    from brain import parse_skills_string
    skills_dict = parse_skills_string(str(row.get("verified_skills", "")))
    all_skills_set.update(skills_dict.keys())

all_skills_list = sorted(list(all_skills_set))

heatmap_data   = []
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
        heatmap_matrix,
        ax=ax,
        cmap=cmap,
        norm=norm,
        linewidths=0.3,
        linecolor="#F5F5F7",
        cbar=True,
        cbar_kws={"ticks": [0, 1, 2], "label": "Skill Level"},
    )

    cbar = ax.collections[0].colorbar
    cbar.set_ticklabels(["Missing", "Beginner", "Intermediate/Advanced"])
    cbar.ax.yaxis.label.set_color("#1D1D1F")
    cbar.ax.tick_params(colors="#1D1D1F")
    cbar.ax.set_facecolor("#FFFFFF")

    ax.set_xlabel("Skills", color="#1D1D1F", fontsize=9)
    ax.set_ylabel("Students", color="#1D1D1F", fontsize=9)
    ax.tick_params(colors="#1D1D1F", labelsize=7)
    ax.set_title(
        f"Batch Skill Heatmap — {n_students} Students x {n_skills} Skills",
        color="#1D1D1F", fontsize=11, pad=10,
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

st.subheader("Full Student Analysis Table")
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
# SECTION H — DOWNLOAD
# =============================================================

st.subheader("Download Full Batch Report")

csv_buffer = io.StringIO()
merged_df.to_csv(csv_buffer, index=False)
csv_bytes  = csv_buffer.getvalue().encode("utf-8")

today_str = datetime.now().strftime("%Y_%m_%d")
filename  = f"SkillDrift_Batch_Report_{today_str}.csv"

st.download_button(
    label="Download Full Batch Report as CSV",
    data=csv_bytes,
    file_name=filename,
    mime="text/csv",
    use_container_width=True,
    type="primary",
)

st.caption(
    "This CSV contains all student names, verified skill lists, "
    "and freshly recalculated scores. Share it with your placement cell "
    "or use it for curriculum planning."
)
