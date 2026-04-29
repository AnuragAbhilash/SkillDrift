# pages/09c_batch_results.py
# Batch Results + Placement Visualization Dashboard
# Two tabs: Batch Analysis | Placement Intelligence

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import io
from datetime import datetime

st.set_page_config(
    page_title="SkillDrift — Batch Results",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500&family=Lato:wght@300;400;700&display=swap');

[data-testid="stSidebarNav"],
[data-testid="collapsedControl"],
[data-testid="stExpandSidebar"],
[data-testid="stSidebarCollapseButton"],
section[data-testid="stSidebar"],
header[data-testid="stHeader"],
.stDeployButton, #MainMenu, footer { display: none !important; }

:root {
    --bg:        #0C0F1A;
    --surface:   #131726;
    --surface2:  #1A1F30;
    --border:    #252A3E;
    --border2:   #2E3450;
    --text:      #E8ECF4;
    --muted:     #6B7699;
    --muted2:    #8892B0;
    --amber:     #F5A623;
    --amber-dim: rgba(245,166,35,0.12);
    --teal:      #00C2A8;
    --teal-dim:  rgba(0,194,168,0.10);
    --red:       #FF4D6A;
    --red-dim:   rgba(255,77,106,0.10);
    --blue:      #4B8EF0;
    --blue-dim:  rgba(75,142,240,0.10);
    --green:     #2DD4A0;
    --green-dim: rgba(45,212,160,0.10);
}

html, body, .stApp {
    background: var(--bg) !important;
    font-family: 'Lato', sans-serif !important;
    color: var(--text) !important;
}
.block-container {
    padding-top: 0 !important;
    padding-bottom: 4rem !important;
    max-width: 1280px !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* Header */
.sd-header {
    background: linear-gradient(180deg, #0F1322 0%, #131726 100%);
    border-bottom: 1px solid var(--border);
    padding: 1.5rem 0 1.25rem 0;
    margin-bottom: 2rem;
}
.sd-wordmark {
    font-family: 'Syne', sans-serif;
    font-size: 0.85rem;
    font-weight: 800;
    color: var(--muted);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.35rem;
}
.sd-page-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: -0.03em;
    line-height: 1.2;
}
.sd-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: var(--muted);
    letter-spacing: 0.06em;
    margin-top: 0.3rem;
}

/* Section labels */
.sd-section {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    font-weight: 500;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.85rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
}

/* KPI cards */
.kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.1rem 1.2rem 1rem;
    position: relative;
    overflow: hidden;
    height: 100%;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.kpi-card.amber::before { background: var(--amber); }
.kpi-card.teal::before  { background: var(--teal);  }
.kpi-card.red::before   { background: var(--red);   }
.kpi-card.blue::before  { background: var(--blue);  }
.kpi-card.green::before { background: var(--green); }
.kpi-card.muted::before { background: var(--border2); }
.kpi-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.5rem;
}
.kpi-value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    line-height: 1;
    color: #FFFFFF;
}
.kpi-sub {
    font-size: 0.73rem;
    color: var(--muted2);
    margin-top: 0.35rem;
    line-height: 1.4;
}

/* Student row */
.s-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.4rem;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.75rem;
}
.s-name { font-family:'Syne',sans-serif; font-weight:700; font-size:0.9rem; color:#FFFFFF; }
.s-sem  { font-family:'JetBrains Mono',monospace; font-size:0.68rem; color:var(--muted); }
.s-stat { font-family:'JetBrains Mono',monospace; font-size:0.78rem; font-weight:500; }
.s-lbl  { font-family:'JetBrains Mono',monospace; font-size:0.58rem; color:var(--muted); text-transform:uppercase; letter-spacing:0.1em; }
.badge {
    display: inline-block;
    border-radius: 4px;
    padding: 2px 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    font-weight: 500;
    letter-spacing: 0.06em;
}
.badge-red   { background:var(--red-dim);   color:var(--red);   border:1px solid rgba(255,77,106,0.3);  }
.badge-amber { background:var(--amber-dim); color:var(--amber); border:1px solid rgba(245,166,35,0.3);  }
.badge-green { background:var(--green-dim); color:var(--green); border:1px solid rgba(45,212,160,0.3); }

/* Missing skill bars */
.skill-bar-wrap {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.65rem 0.9rem;
    margin-bottom: 0.3rem;
}
.skill-bar-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.3rem;
}
.skill-bar-name { font-weight:700; font-size:0.85rem; color:#FFFFFF; }
.skill-bar-pct  { font-family:'JetBrains Mono',monospace; font-size:0.72rem; color:var(--muted2); }
.skill-bar-track { height:3px; border-radius:2px; background:var(--border2); overflow:hidden; }
.skill-bar-fill  { height:100%; border-radius:2px; }

/* Info box */
.info-box {
    background: var(--blue-dim);
    border: 1px solid rgba(75,142,240,0.25);
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    font-size:0.85rem;
    color:var(--muted2);
    line-height:1.65;
}
.info-box strong { color:#FFFFFF; }

/* Divider */
.sd-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.75rem 0;
}

/* Matrix description card */
.mx-desc-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    height: 100%;
}
.mx-number {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem;
    color: var(--muted);
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}
.mx-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 0.6rem;
}
.mx-body {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: var(--muted);
    line-height: 1.7;
}

/* Expander */
[data-testid="stExpander"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary {
    font-family: 'Lato', sans-serif !important;
    font-size: 0.85rem !important;
    color: var(--text) !important;
}

/* Buttons */
.stButton > button {
    font-family: 'Lato', sans-serif !important;
    font-size: 0.83rem !important;
    font-weight: 700 !important;
    border-radius: 7px !important;
    border: 1px solid var(--border2) !important;
    background: var(--surface2) !important;
    color: var(--text) !important;
    padding: 0.42rem 1rem !important;
    letter-spacing: 0.02em !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover {
    background: var(--border) !important;
    border-color: var(--muted) !important;
    color: #FFFFFF !important;
}
.stButton > button[kind="primary"] {
    background: var(--amber) !important;
    border-color: var(--amber) !important;
    color: #0C0F1A !important;
    font-weight: 700 !important;
}
.stButton > button[kind="primary"]:hover {
    background: #e8961a !important;
}

/* Tabs */
[data-testid="stTabs"] [role="tablist"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 2px !important;
    margin-bottom: 1.5rem !important;
}
[data-testid="stTabs"] button[role="tab"] {
    font-family: 'Lato', sans-serif !important;
    font-size: 0.83rem !important;
    font-weight: 700 !important;
    color: var(--muted) !important;
    border-radius: 7px !important;
    padding: 0.45rem 1.25rem !important;
    letter-spacing: 0.04em !important;
    transition: all 0.15s !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    background: var(--amber) !important;
    color: #0C0F1A !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# GUARD
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.get("faculty_logged_in"):
    st.error("Access denied. Please log in via the Faculty Dashboard.")
    if st.button("Go to Faculty Login"):
        st.switch_page("pages/09_faculty.py")
    st.stop()

results = st.session_state.get("faculty_batch_results")
if not results or not results.get("all_student_analyses"):
    st.warning("No batch data found. Please upload and process student reports first.")
    if st.button("Back to Faculty Dashboard"):
        st.switch_page("pages/09_faculty.py")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# UNPACK
# ─────────────────────────────────────────────────────────────────────────────
all_student_analyses = results["all_student_analyses"]
merged_df            = results.get("merged_df", pd.DataFrame())
valid_count          = results.get("valid_count", 0)
skipped_files        = results.get("skipped_files", [])
duplicate_count      = results.get("duplicate_count", 0)
summary              = results.get("summary", {})
total_students       = summary.get("total_students", len(merged_df))
faculty_name         = st.session_state.get("faculty_name", "Faculty")
today_str            = datetime.now().strftime("%d %b %Y")
files_uploaded       = valid_count + len([s for s in skipped_files if not s.startswith("WARNING")])

student_lookup = {a["student_name"]: a for a in all_student_analyses}
st.session_state["faculty_student_lookup"] = student_lookup

# Classify
def classify_drift(s):
    return "fully_focused" if s <= 30 else "moderately_focused" if s <= 60 else "not_focused"
def classify_readiness(s):
    return "high" if s >= 70 else "moderate" if s >= 40 else "poor"
def classify_entropy(s):
    return "highly_ordered" if s < 1.2 else "moderate" if s < 2.2 else "high_disorder"

groups = {
    "drift":     {"fully_focused":[], "moderately_focused":[], "not_focused":[]},
    "readiness": {"high":[], "moderate":[], "poor":[]},
    "entropy":   {"highly_ordered":[], "moderate":[], "high_disorder":[]},
}
for a in all_student_analyses:
    groups["drift"][classify_drift(a["drift_score"])].append(a)
    groups["readiness"][classify_readiness(a["readiness_score"])].append(a)
    groups["entropy"][classify_entropy(a["entropy_score"])].append(a)

# Plotly dark base
PD = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#6B7699", family="JetBrains Mono"),
)

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="sd-header">
    <div class="sd-wordmark">SkillDrift</div>
    <div class="sd-page-title">Batch Analysis Results</div>
    <div class="sd-meta">{faculty_name} &nbsp;&nbsp;/&nbsp;&nbsp; {total_students} students &nbsp;&nbsp;/&nbsp;&nbsp; {today_str}</div>
</div>
""", unsafe_allow_html=True)

nav_l, nav_r = st.columns([11, 1])
with nav_r:
    if st.button("Back", use_container_width=True):
        st.switch_page("pages/09_faculty.py")

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab_batch, tab_placement = st.tabs(["BATCH ANALYSIS", "PLACEMENT INTELLIGENCE"])


# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — BATCH ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
with tab_batch:

    # Validation
    st.markdown('<div class="sd-section">Upload Validation</div>', unsafe_allow_html=True)
    v1,v2,v3,v4 = st.columns(4)
    for col, lbl, val, sub, acc in [
        (v1, "FILES UPLOADED",     files_uploaded,                      "submitted by faculty",          "muted"),
        (v2, "RECORDS VALID",      valid_count,                         "passed validation",             "green"),
        (v3, "SKIPPED",            max(0, files_uploaded - valid_count),"format or parse errors",        "red"),
        (v4, "DUPLICATES REMOVED", duplicate_count,                     "same student, multiple files",  "amber"),
    ]:
        with col:
            st.markdown(f'<div class="kpi-card {acc}"><div class="kpi-label">{lbl}</div><div class="kpi-value">{val}</div><div class="kpi-sub">{sub}</div></div>', unsafe_allow_html=True)

    if skipped_files:
        with st.expander(f"Validation issues — {len(skipped_files)} item(s)"):
            for msg in skipped_files:
                st.markdown(f"<span style='font-family:JetBrains Mono,monospace;font-size:0.78rem;color:#FF4D6A;'>{msg}</span>", unsafe_allow_html=True)

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # Stats
    avg_drift     = summary.get("avg_drift_score", 0)
    avg_readiness = summary.get("avg_readiness_score", 0)
    avg_entropy   = summary.get("avg_entropy_score", 0)
    red_count     = summary.get("red_count", 0)
    yellow_count  = summary.get("yellow_count", 0)
    green_count   = summary.get("green_count", 0)

    st.markdown('<div class="sd-section">Batch Statistics</div>', unsafe_allow_html=True)
    m1,m2,m3,m4,m5,m6 = st.columns(6)
    for col, lbl, val, sub, acc in [
        (m1,"AVG DRIFT",     avg_drift,            "lower = more focused",    "blue"),
        (m2,"AVG READINESS", f"{avg_readiness}%",  "toward best career track","green"),
        (m3,"AVG ENTROPY",   f"{avg_entropy} bits","lower = more focused",    "teal"),
        (m4,"HIGH URGENCY",  red_count,            "semester 5 and above",    "red"),
        (m5,"MED URGENCY",   yellow_count,          "semester 3 to 4",        "amber"),
        (m6,"LOW URGENCY",   green_count,           "semester 1 to 2",        "muted"),
    ]:
        with col:
            st.markdown(f'<div class="kpi-card {acc}"><div class="kpi-label">{lbl}</div><div class="kpi-value">{val}</div><div class="kpi-sub">{sub}</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

    # Charts
    chart_l, chart_r = st.columns(2, gap="large")
    with chart_l:
        st.markdown('<div class="sd-section">Urgency Distribution</div>', unsafe_allow_html=True)
        fig_pie = go.Figure(go.Pie(
            labels=["High Urgency","Medium Urgency","Low Urgency"],
            values=[red_count, yellow_count, green_count],
            marker=dict(colors=["#FF4D6A","#F5A623","#2DD4A0"], line=dict(color="#131726",width=2)),
            hole=0.6, textfont=dict(color="#E8ECF4",size=10,family="JetBrains Mono"),
            hovertemplate="<b>%{label}</b><br>%{value} students<br>%{percent}<extra></extra>",
        ))
        fig_pie.update_layout(**PD, showlegend=True,
            legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color="#6B7699",size=10),orientation="h",yanchor="bottom",y=-0.2),
            margin=dict(t=10,b=50,l=10,r=10), height=280)
        st.plotly_chart(fig_pie, use_container_width=True)

    with chart_r:
        st.markdown('<div class="sd-section">Career Track Distribution</div>', unsafe_allow_html=True)
        track_dist = summary.get("track_distribution", {})
        if track_dist:
            sorted_td = sorted(track_dist.items(), key=lambda x: x[1])
            fig_track = go.Figure(go.Bar(
                x=[v for _,v in sorted_td], y=[k for k,_ in sorted_td],
                orientation="h",
                marker=dict(color=[v for _,v in sorted_td],
                    colorscale=[[0,"#252A3E"],[0.5,"#00C2A8"],[1,"#F5A623"]],
                    showscale=False, line=dict(color="rgba(0,0,0,0)")),
                text=[str(v) for _,v in sorted_td], textposition="outside",
                textfont=dict(color="#6B7699",size=10,family="JetBrains Mono"),
            ))
            fig_track.update_layout(**PD,
                xaxis=dict(gridcolor="#1A1F30",color="#6B7699",zeroline=False),
                yaxis=dict(gridcolor="#1A1F30",color="#8892B0",showgrid=False),
                margin=dict(t=10,b=10,l=10,r=60), height=280)
            st.plotly_chart(fig_track, use_container_width=True)

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # Missing skills
    st.markdown('<div class="sd-section">Top Skills Missing Across Batch</div>', unsafe_allow_html=True)
    top_missing = summary.get("top_missing_skills", [])
    if top_missing:
        max_c = top_missing[0][1] if top_missing else 1
        for rank, (skill, count) in enumerate(top_missing, start=1):
            pct  = round((count / total_students) * 100, 1)
            fill = round((count / max_c) * 100)
            bar_color = "#FF4D6A" if rank == 1 else "#F5A623" if rank <= 3 else "#4B8EF0"
            st.markdown(f"""
            <div class="skill-bar-wrap">
                <div class="skill-bar-top">
                    <span class="skill-bar-name">#{rank} &nbsp; {skill}</span>
                    <span class="skill-bar-pct">{count} students &nbsp;/&nbsp; {pct}%</span>
                </div>
                <div class="skill-bar-track">
                    <div class="skill-bar-fill" style="width:{fill}%;background:{bar_color};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        top_name = top_missing[0][0]
        top_pct  = round((top_missing[0][1] / total_students) * 100, 1)
        st.markdown(f"""
        <div class="info-box" style="margin-top:0.75rem;">
            <strong>Faculty Recommendation —</strong>
            {top_pct}% of this batch are missing <strong>{top_name}</strong>.
            A focused workshop before placement season is strongly recommended.
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # Heatmap
    st.markdown('<div class="sd-section">Batch Skill Coverage Heatmap</div>', unsafe_allow_html=True)
    st.markdown("<span style='font-size:0.72rem;color:#6B7699;font-family:JetBrains Mono,monospace;'>DARK GREEN = Proficient &nbsp; AMBER = Beginner &nbsp; DARK RED = Missing</span>", unsafe_allow_html=True)
    st.markdown("<div style='height:0.4rem;'></div>", unsafe_allow_html=True)

    all_skills_set = set()
    for a in all_student_analyses:
        all_skills_set.update(a["verified_skills"].keys())
    all_skills_list = sorted(list(all_skills_set))

    hmap_data, hmap_labels = [], []
    for a in all_student_analyses:
        hmap_labels.append(a["student_name"][:22])
        row = []
        for sk in all_skills_list:
            lv = a["verified_skills"].get(sk, None)
            row.append(2 if lv in ("Advanced","Intermediate") else 1 if lv == "Beginner" else 0)
        hmap_data.append(row)

    hmap_matrix = pd.DataFrame(hmap_data, index=hmap_labels, columns=all_skills_list)
    if not hmap_matrix.empty:
        n_s = len(hmap_matrix); n_k = len(all_skills_list)
        fw = max(10, min(n_k * 0.55, 32))
        fh = max(4,  min(n_s * 0.5,  18))
        fig_h, ax = plt.subplots(figsize=(fw, fh))
        fig_h.patch.set_facecolor("#131726")
        ax.set_facecolor("#131726")
        cmap = mcolors.ListedColormap(["#3D1520","#5C3B00","#0D3D2E"])
        norm = mcolors.BoundaryNorm([-0.5,0.5,1.5,2.5], cmap.N)
        sns.heatmap(hmap_matrix, ax=ax, cmap=cmap, norm=norm,
                    linewidths=0.4, linecolor="#0C0F1A", cbar=True,
                    cbar_kws={"ticks":[0,1,2],"label":"Skill Level"})
        cbar = ax.collections[0].colorbar
        cbar.set_ticklabels(["Missing","Beginner","Proficient"])
        cbar.ax.yaxis.label.set_color("#6B7699")
        cbar.ax.tick_params(colors="#6B7699", labelsize=8)
        cbar.outline.set_edgecolor("#252A3E")
        cbar.ax.set_facecolor("#131726")
        ax.set_xlabel("Skills", color="#6B7699", fontsize=9, labelpad=8, fontfamily="monospace")
        ax.set_ylabel("Students", color="#6B7699", fontsize=9, labelpad=8, fontfamily="monospace")
        ax.tick_params(colors="#8892B0", labelsize=7.5)
        ax.set_title(f"Skill Coverage Matrix  —  {n_s} Students  x  {n_k} Skills",
                     color="#E8ECF4", fontsize=11, pad=14, fontfamily="monospace", fontweight="bold")
        for spine in ax.spines.values(): spine.set_edgecolor("#252A3E")
        plt.xticks(rotation=45, ha="right", fontsize=7.5, color="#8892B0")
        plt.yticks(fontsize=8, color="#8892B0")
        plt.tight_layout()
        st.pyplot(fig_h, use_container_width=True)
        plt.close(fig_h)

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # Student cards
    st.markdown('<div class="sd-section">Individual Student Records</div>', unsafe_allow_html=True)
    BADGE_CLS = {"Red":"badge-red","Yellow":"badge-amber","Green":"badge-green"}
    for a in all_student_analyses:
        name = a["student_name"]
        bc   = BADGE_CLS.get(a["urgency_level"], "badge-amber")
        rc   = "#2DD4A0" if a["readiness_score"] >= 70 else "#F5A623" if a["readiness_score"] >= 40 else "#FF4D6A"
        dc   = "#2DD4A0" if a["drift_score"] <= 30 else "#F5A623" if a["drift_score"] <= 60 else "#FF4D6A"
        col_card, col_btn = st.columns([11, 1])
        with col_card:
            st.markdown(f"""
            <div class="s-card">
                <div style="min-width:155px;">
                    <div class="s-name">{name}</div>
                    <div class="s-sem">SEM {a['semester']}</div>
                </div>
                <div style="min-width:130px;">
                    <div class="s-lbl">Drift Score</div>
                    <div class="s-stat" style="color:{dc};">{a['drift_score']} &mdash; {a['drift_label']}</div>
                </div>
                <div style="min-width:140px;">
                    <div class="s-lbl">Best Track</div>
                    <div class="s-stat" style="color:#4B8EF0;">{a['best_track']} ({a['match_pct']}%)</div>
                </div>
                <div style="min-width:100px;">
                    <div class="s-lbl">Readiness</div>
                    <div class="s-stat" style="color:{rc};">{a['readiness_score']}%</div>
                </div>
                <div style="min-width:90px;">
                    <div class="s-lbl">Entropy</div>
                    <div class="s-stat" style="color:#00C2A8;">{a['entropy_score']} bits</div>
                </div>
                <div><span class="badge {bc}">{a['urgency_level'].upper()} URGENCY</span></div>
                <div style="min-width:110px;">
                    <div class="s-lbl">Next Skill</div>
                    <div class="s-stat" style="color:#F5A623;">{a['next_skill'] or 'N/A'}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_btn:
            if st.button("View", key=f"b_view_{name}", use_container_width=True):
                st.session_state["faculty_viewing_student"] = name
                st.switch_page("pages/09b_student_view.py")

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # Download
    st.markdown('<div class="sd-section">Export</div>', unsafe_allow_html=True)
    csv_buf = io.StringIO()
    merged_df.to_csv(csv_buf, index=False)
    st.download_button(
        label="Download Full Batch Report  (CSV)",
        data=csv_buf.getvalue().encode("utf-8"),
        file_name=f"SkillDrift_Batch_{datetime.now().strftime('%Y_%m_%d')}.csv",
        mime="text/csv", type="primary", use_container_width=False,
    )
    st.markdown("<span style='font-size:0.75rem;color:#6B7699;font-family:JetBrains Mono,monospace;'>All student records with freshly recalculated scores. Share with placement cell or HOD.</span>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — PLACEMENT INTELLIGENCE
# ═════════════════════════════════════════════════════════════════════════════
with tab_placement:

    st.markdown(f"""
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;
                padding:1.25rem 1.5rem;margin-bottom:1.75rem;">
        <div style="font-family:'Syne',sans-serif;font-size:1.15rem;font-weight:700;color:#FFFFFF;margin-bottom:4px;">
            Placement Intelligence Dashboard
        </div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:var(--muted);">
            {total_students} students classified across three independent readiness dimensions.
            Expand any group to inspect individual student profiles.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # KPIs
    placement_ready = len(groups["readiness"]["high"])
    fully_focused   = len(groups["drift"]["fully_focused"])
    high_disorder   = len(groups["entropy"]["high_disorder"])
    high_urgency    = sum(1 for a in all_student_analyses if a["urgency_level"] == "Red")

    pk1,pk2,pk3,pk4 = st.columns(4)
    for col, lbl, val, sub, acc in [
        (pk1,"PLACEMENT READY",  placement_ready, f"{round(placement_ready/total_students*100) if total_students else 0}% — readiness 70% or above", "green"),
        (pk2,"FULLY FOCUSED",    fully_focused,   f"{round(fully_focused/total_students*100) if total_students else 0}% — drift score 0 to 30",     "teal"),
        (pk3,"SKILL DISORDER",   high_disorder,   f"{round(high_disorder/total_students*100) if total_students else 0}% — entropy above 2.2 bits",  "red"),
        (pk4,"URGENT ATTENTION", high_urgency,    "semester 5 and above — immediate action needed",                                                  "amber"),
    ]:
        with col:
            st.markdown(f'<div class="kpi-card {acc}"><div class="kpi-label">{lbl}</div><div class="kpi-value">{val}</div><div class="kpi-sub">{sub}</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

    # Stacked bar overview
    st.markdown('<div class="sd-section">Three-Dimension Overview</div>', unsafe_allow_html=True)

    drift_v     = [len(groups["drift"]["fully_focused"]),    len(groups["drift"]["moderately_focused"]),    len(groups["drift"]["not_focused"])]
    readiness_v = [len(groups["readiness"]["high"]),         len(groups["readiness"]["moderate"]),          len(groups["readiness"]["poor"])]
    entropy_v   = [len(groups["entropy"]["highly_ordered"]), len(groups["entropy"]["moderate"]),            len(groups["entropy"]["high_disorder"])]

    dims = [
        ("Skill Drift",  drift_v,     ["Fully Focused","Moderately Focused","Not Focused"]),
        ("Readiness",    readiness_v, ["High","Moderate","Poor"]),
        ("Entropy",      entropy_v,   ["Highly Ordered","Moderate","High Disorder"]),
    ]
    grp_colors = ["#2DD4A0","#F5A623","#FF4D6A"]
    fig_ov = go.Figure()
    for dim_name, vals, labels in dims:
        total_dim = sum(vals) or 1
        for i,(val,lbl) in enumerate(zip(vals,labels)):
            pct = round(val/total_dim*100,1)
            fig_ov.add_trace(go.Bar(
                name=lbl, x=[val], y=[dim_name], orientation="h",
                marker=dict(color=grp_colors[i], line=dict(color="#0C0F1A",width=1)),
                text=f"  {val}  ({pct}%)" if val > 0 else "",
                textposition="inside",
                textfont=dict(color="#0C0F1A",size=10,family="JetBrains Mono"),
                hovertemplate=f"<b>{lbl}</b><br>{val} students ({pct}%)<extra>{dim_name}</extra>",
                showlegend=(dim_name == "Skill Drift"),
                legendgroup=lbl,
            ))
    fig_ov.update_layout(barmode="stack", **PD,
        xaxis=dict(title="Number of Students", gridcolor="#1A1F30",color="#6B7699",
                   title_font=dict(size=10,family="JetBrains Mono")),
        yaxis=dict(color="#E8ECF4", tickfont=dict(size=12,family="Syne",color="#E8ECF4"),
                   categoryorder="array",categoryarray=["Entropy","Readiness","Skill Drift"]),
        legend=dict(orientation="h",yanchor="bottom",y=-0.3,bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#8892B0",size=10,family="JetBrains Mono")),
        margin=dict(t=20,b=70,l=20,r=20), height=280)
    st.plotly_chart(fig_ov, use_container_width=True)

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # Scatter: Drift vs Readiness
    st.markdown('<div class="sd-section">Drift vs Readiness — Student Map</div>', unsafe_allow_html=True)
    st.markdown("<span style='font-size:0.72rem;color:#6B7699;font-family:JetBrains Mono,monospace;'>Each point is one student. Ideal students cluster bottom-left (low drift, high readiness). Point size = semester.</span>", unsafe_allow_html=True)
    st.markdown("<div style='height:0.4rem;'></div>", unsafe_allow_html=True)

    if all_student_analyses:
        scatter_df = pd.DataFrame([{
            "name": a["student_name"], "drift": a["drift_score"],
            "readiness": a["readiness_score"], "urgency": a["urgency_level"],
            "track": a["best_track"], "semester": a["semester"],
        } for a in all_student_analyses])

        urg_colors = {"Red":"#FF4D6A","Yellow":"#F5A623","Green":"#2DD4A0"}
        fig_sc = go.Figure()
        for uv, uc in urg_colors.items():
            sub = scatter_df[scatter_df["urgency"] == uv]
            if sub.empty: continue
            fig_sc.add_trace(go.Scatter(
                x=sub["drift"], y=sub["readiness"],
                mode="markers+text",
                name=f"{uv} Urgency",
                marker=dict(color=uc, size=sub["semester"]*3+6,
                            opacity=0.85, line=dict(color="#0C0F1A",width=1.5)),
                text=sub["name"],
                textposition="top center",
                textfont=dict(size=8,color="#8892B0",family="JetBrains Mono"),
                hovertemplate="<b>%{text}</b><br>Drift: %{x}<br>Readiness: %{y}%<extra></extra>",
            ))
        fig_sc.add_shape(type="rect", x0=0, y0=70, x1=30, y1=100,
            fillcolor="rgba(45,212,160,0.06)",
            line=dict(color="rgba(45,212,160,0.2)",width=1,dash="dot"))
        fig_sc.add_annotation(x=15, y=85, text="Ideal Zone", showarrow=False,
            font=dict(color="rgba(45,212,160,0.45)",size=9,family="JetBrains Mono"))
        fig_sc.update_layout(**PD,
            xaxis=dict(title="Drift Score  (lower = more focused)", gridcolor="#1A1F30",color="#6B7699",
                       range=[-5,105], zeroline=False, title_font=dict(size=10,family="JetBrains Mono")),
            yaxis=dict(title="Readiness  (%)", gridcolor="#1A1F30",color="#6B7699",
                       range=[-5,105], zeroline=False, title_font=dict(size=10,family="JetBrains Mono")),
            legend=dict(bgcolor="rgba(19,23,38,0.9)",bordercolor="#252A3E",borderwidth=1,
                        font=dict(color="#8892B0",size=10,family="JetBrains Mono")),
            margin=dict(t=20,b=40,l=40,r=20), height=400)
        st.plotly_chart(fig_sc, use_container_width=True)

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # Entropy histogram
    st.markdown('<div class="sd-section">Entropy Distribution</div>', unsafe_allow_html=True)
    if all_student_analyses:
        ent_vals = [a["entropy_score"] for a in all_student_analyses]
        fig_ent = go.Figure()
        fig_ent.add_trace(go.Histogram(
            x=ent_vals, nbinsx=min(15, max(5, total_students//2)),
            marker=dict(color=ent_vals,
                colorscale=[[0,"#2DD4A0"],[0.45,"#F5A623"],[1,"#FF4D6A"]],
                line=dict(color="#0C0F1A",width=0.8), cmin=0, cmax=3),
            hovertemplate="Entropy %{x:.2f} bits<br>Count: %{y}<extra></extra>",
        ))
        for thresh, label, color in [(1.2,"Focused Threshold","#2DD4A0"),(2.2,"Disorder Threshold","#FF4D6A")]:
            fig_ent.add_vline(x=thresh, line_dash="dash", line_color=color, line_width=1.5,
                annotation=dict(text=label, font=dict(color=color,size=9,family="JetBrains Mono"),yanchor="top"))
        fig_ent.update_layout(**PD, showlegend=False,
            xaxis=dict(title="Shannon Entropy (bits)",gridcolor="#1A1F30",color="#6B7699",
                       title_font=dict(size=10,family="JetBrains Mono")),
            yaxis=dict(title="Number of Students",gridcolor="#1A1F30",color="#6B7699",
                       title_font=dict(size=10,family="JetBrains Mono")),
            margin=dict(t=20,b=40,l=40,r=20), height=280)
        st.plotly_chart(fig_ent, use_container_width=True)

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # Group expanders helper
    def render_group(matrix_key, group_key, label, color, range_desc, total):
        student_list = groups[matrix_key][group_key]
        count = len(student_list)
        pct   = round((count/total)*100) if total > 0 else 0
        with st.expander(f"{label}  —  {count} student{'s' if count!=1 else ''}  ({pct}%)  ·  {range_desc}", expanded=False):
            if not student_list:
                st.markdown("<span style='color:#6B7699;font-size:0.82rem;font-family:JetBrains Mono,monospace;'>No students in this group.</span>", unsafe_allow_html=True)
                return

            # Mini readiness bar chart
            if len(student_list) >= 2:
                mini_v = [a["readiness_score"] for a in student_list]
                mini_n = [a["student_name"] for a in student_list]
                mini_c = ["#2DD4A0" if v >= 70 else "#F5A623" if v >= 40 else "#FF4D6A" for v in mini_v]
                fig_m = go.Figure(go.Bar(x=mini_n, y=mini_v,
                    marker=dict(color=mini_c, line=dict(color="#0C0F1A",width=0.5)),
                    text=[f"{v}%" for v in mini_v], textposition="outside",
                    textfont=dict(color="#8892B0",size=9,family="JetBrains Mono"),
                    hovertemplate="%{x}<br>Readiness: %{y}%<extra></extra>"))
                fig_m.update_layout(**PD,
                    xaxis=dict(gridcolor="#1A1F30",color="#6B7699",tickfont=dict(size=8,family="JetBrains Mono")),
                    yaxis=dict(gridcolor="#1A1F30",color="#6B7699",range=[0,115],
                               title="Readiness %",title_font=dict(size=9,family="JetBrains Mono")),
                    showlegend=False, margin=dict(t=10,b=10,l=40,r=10), height=150)
                st.plotly_chart(fig_m, use_container_width=True)

            # Header row
            h1,h2,h3,h4,h5,h6 = st.columns([3,1,2,2,2,2])
            for hc, ht in zip([h1,h2,h3,h4,h5,h6], ["NAME","SEM","DRIFT","READINESS","TRACK","NEXT SKILL"]):
                hc.markdown(f"<span style='font-family:JetBrains Mono,monospace;font-size:0.58rem;color:#6B7699;letter-spacing:0.12em;'>{ht}</span>", unsafe_allow_html=True)

            st.markdown("<hr style='border:none;border-top:1px solid #252A3E;margin:0.3rem 0 0.6rem;'>", unsafe_allow_html=True)

            for s in student_list:
                rc2 = "#2DD4A0" if s["readiness_score"]>=70 else "#F5A623" if s["readiness_score"]>=40 else "#FF4D6A"
                dc2 = "#2DD4A0" if s["drift_score"]<=30 else "#F5A623" if s["drift_score"]<=60 else "#FF4D6A"
                c1,c2,c3,c4,c5,c6 = st.columns([3,1,2,2,2,2])
                c1.markdown(f"<span style='font-family:Syne,sans-serif;font-weight:700;font-size:0.87rem;color:#FFFFFF;'>{s['student_name']}</span>", unsafe_allow_html=True)
                c2.markdown(f"<span style='font-family:JetBrains Mono,monospace;font-size:0.76rem;color:#6B7699;'>{s['semester']}</span>", unsafe_allow_html=True)
                c3.markdown(f"<span style='font-family:JetBrains Mono,monospace;font-size:0.78rem;color:{dc2};font-weight:500;'>{s['drift_score']}</span>", unsafe_allow_html=True)
                c4.markdown(f"<span style='font-family:JetBrains Mono,monospace;font-size:0.78rem;color:{rc2};font-weight:500;'>{s['readiness_score']}%</span>", unsafe_allow_html=True)
                c5.markdown(f"<span style='font-family:JetBrains Mono,monospace;font-size:0.73rem;color:#4B8EF0;'>{s['best_track']}</span>", unsafe_allow_html=True)
                c6.markdown(f"<span style='font-family:JetBrains Mono,monospace;font-size:0.73rem;color:#F5A623;'>{s['next_skill'] or 'N/A'}</span>", unsafe_allow_html=True)

                if st.button("View Dashboard", key=f"pl_{matrix_key}_{group_key}_{s['student_name']}", use_container_width=False):
                    st.session_state["faculty_viewing_student"] = s["student_name"]
                    st.switch_page("pages/09b_student_view.py")
                st.markdown("<div style='border-top:1px solid #1A1F30;margin:0.25rem 0;'></div>", unsafe_allow_html=True)

    # Matrix 1 — Drift
    mx1_l, mx1_r = st.columns([3, 5])
    with mx1_l:
        st.markdown("""
        <div class="mx-desc-card">
            <div class="mx-number">Matrix 01</div>
            <div class="mx-title">Skill Drift</div>
            <div class="mx-body">
                Measures how scattered student skills are across the 8 career tracks.<br><br>
                <span style="color:#2DD4A0;">Fully Focused</span> — drift 0 to 30<br>
                <span style="color:#F5A623;">Moderately Focused</span> — drift 31 to 60<br>
                <span style="color:#FF4D6A;">Not Focused</span> — drift 61 to 100
            </div>
        </div>
        """, unsafe_allow_html=True)
        dv = [len(groups["drift"]["fully_focused"]),len(groups["drift"]["moderately_focused"]),len(groups["drift"]["not_focused"])]
        fig_d = go.Figure(go.Pie(labels=["Fully Focused","Moderately Focused","Not Focused"], values=dv,
            marker=dict(colors=["#2DD4A0","#F5A623","#FF4D6A"],line=dict(color="#0C0F1A",width=2)),
            hole=0.65, textinfo="none", hovertemplate="%{label}<br>%{value}<extra></extra>"))
        fig_d.update_layout(**PD, showlegend=False, margin=dict(t=10,b=10,l=10,r=10), height=150)
        st.plotly_chart(fig_d, use_container_width=True)

    with mx1_r:
        st.markdown('<div class="sd-section">Groups — click to expand</div>', unsafe_allow_html=True)
        render_group("drift","fully_focused",      "Fully Focused",       "green","Drift 0 to 30",    total_students)
        render_group("drift","moderately_focused", "Moderately Focused",  "amber","Drift 31 to 60",   total_students)
        render_group("drift","not_focused",        "Not Focused",         "red",  "Drift 61 to 100",  total_students)

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # Matrix 2 — Readiness
    mx2_l, mx2_r = st.columns([3, 5])
    with mx2_l:
        st.markdown("""
        <div class="mx-desc-card">
            <div class="mx-number">Matrix 02</div>
            <div class="mx-title">Placement Readiness</div>
            <div class="mx-body">
                Weighted score: verified skills against job posting frequency in Indian market data.<br><br>
                <span style="color:#2DD4A0;">High</span> — readiness 70% or above<br>
                <span style="color:#F5A623;">Moderate</span> — readiness 40 to 69%<br>
                <span style="color:#FF4D6A;">Poor</span> — readiness below 40%
            </div>
        </div>
        """, unsafe_allow_html=True)
        rv = [len(groups["readiness"]["high"]),len(groups["readiness"]["moderate"]),len(groups["readiness"]["poor"])]
        fig_r = go.Figure(go.Pie(labels=["High","Moderate","Poor"], values=rv,
            marker=dict(colors=["#2DD4A0","#F5A623","#FF4D6A"],line=dict(color="#0C0F1A",width=2)),
            hole=0.65, textinfo="none", hovertemplate="%{label}<br>%{value}<extra></extra>"))
        fig_r.update_layout(**PD, showlegend=False, margin=dict(t=10,b=10,l=10,r=10), height=150)
        st.plotly_chart(fig_r, use_container_width=True)

    with mx2_r:
        st.markdown('<div class="sd-section">Groups — click to expand</div>', unsafe_allow_html=True)
        render_group("readiness","high",     "High Readiness",     "green","Readiness 70% or above", total_students)
        render_group("readiness","moderate", "Moderate Readiness", "amber","Readiness 40 to 69%",    total_students)
        render_group("readiness","poor",     "Poor Readiness",     "red",  "Readiness below 40%",    total_students)

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # Matrix 3 — Entropy
    mx3_l, mx3_r = st.columns([3, 5])
    with mx3_l:
        st.markdown("""
        <div class="mx-desc-card">
            <div class="mx-number">Matrix 03</div>
            <div class="mx-title">Skill Entropy</div>
            <div class="mx-body">
                Shannon Entropy measures disorder in the skill distribution.
                Lower bits means more focused and more ordered.<br><br>
                <span style="color:#2DD4A0;">Highly Ordered</span> — below 1.2 bits<br>
                <span style="color:#F5A623;">Moderate</span> — 1.2 to 2.2 bits<br>
                <span style="color:#FF4D6A;">High Disorder</span> — above 2.2 bits
            </div>
        </div>
        """, unsafe_allow_html=True)
        ev = [len(groups["entropy"]["highly_ordered"]),len(groups["entropy"]["moderate"]),len(groups["entropy"]["high_disorder"])]
        fig_e = go.Figure(go.Pie(labels=["Highly Ordered","Moderate","High Disorder"], values=ev,
            marker=dict(colors=["#2DD4A0","#F5A623","#FF4D6A"],line=dict(color="#0C0F1A",width=2)),
            hole=0.65, textinfo="none", hovertemplate="%{label}<br>%{value}<extra></extra>"))
        fig_e.update_layout(**PD, showlegend=False, margin=dict(t=10,b=10,l=10,r=10), height=150)
        st.plotly_chart(fig_e, use_container_width=True)

    with mx3_r:
        st.markdown('<div class="sd-section">Groups — click to expand</div>', unsafe_allow_html=True)
        render_group("entropy","highly_ordered","Highly Ordered","green","Entropy below 1.2 bits",   total_students)
        render_group("entropy","moderate",      "Moderate",      "amber","Entropy 1.2 to 2.2 bits",  total_students)
        render_group("entropy","high_disorder", "High Disorder", "red",  "Entropy above 2.2 bits",   total_students)

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # Full table
    st.markdown('<div class="sd-section">Complete Classification Table</div>', unsafe_allow_html=True)
    DRIFT_LBL     = {"fully_focused":"Fully Focused","moderately_focused":"Moderately Focused","not_focused":"Not Focused"}
    READINESS_LBL = {"high":"High","moderate":"Moderate","poor":"Poor"}
    ENTROPY_LBL   = {"highly_ordered":"Highly Ordered","moderate":"Moderate","high_disorder":"High Disorder"}
    rows = []
    for a in all_student_analyses:
        rows.append({
            "Student":          a["student_name"],
            "Sem":              a["semester"],
            "Drift Score":      a["drift_score"],
            "Drift Group":      DRIFT_LBL[classify_drift(a["drift_score"])],
            "Readiness %":      a["readiness_score"],
            "Readiness Group":  READINESS_LBL[classify_readiness(a["readiness_score"])],
            "Entropy (bits)":   a["entropy_score"],
            "Entropy Group":    ENTROPY_LBL[classify_entropy(a["entropy_score"])],
            "Best Track":       a["best_track"],
            "Urgency":          a["urgency_level"],
            "Next Skill":       a["next_skill"],
        })
    summary_df = pd.DataFrame(rows)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    st.markdown("<div style='height:0.75rem;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="sd-section">Export for Placement Cell</div>', unsafe_allow_html=True)
    pl_buf = io.StringIO()
    summary_df.to_csv(pl_buf, index=False)
    st.download_button(
        label="Download Placement Classification Report  (CSV)",
        data=pl_buf.getvalue().encode("utf-8"),
        file_name=f"SkillDrift_Placement_{datetime.now().strftime('%Y_%m_%d')}.csv",
        mime="text/csv", type="primary", use_container_width=False,
    )
    st.markdown("<span style='font-size:0.75rem;color:#6B7699;font-family:JetBrains Mono,monospace;'>Drift group, readiness group, entropy group, best track, urgency, and next skill for every student.</span>", unsafe_allow_html=True)