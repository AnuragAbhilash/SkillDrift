# pages/09c_batch_results.py

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

# ─────────────────────────────────────────────────────────────────────────────
# CSS — FIX 2: KPI card font matches student dashboard (Manrope + Inter)
#      FIX 5: tab pills styled correctly
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
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
.block-container{padding-top:0!important;padding-bottom:3rem!important;max-width:1000px!important;margin:0 auto!important;padding-left:2rem!important;padding-right:2rem!important}

/* Buttons */
.stButton>button{border-radius:8px;border:1.5px solid var(--border);background:var(--card);color:var(--text);font-weight:600;font-size:0.87rem;font-family:'Inter',sans-serif;padding:0.45rem 1rem;transition:all 0.12s ease;white-space:nowrap}
.stButton>button:hover{background:#f0f4f8;border-color:#c2cad4}
.stButton>button[kind="primary"]{background:var(--blue);color:#fff;border-color:var(--blue);font-weight:700}
.stButton>button[kind="primary"]:hover{background:#0038bf;border-color:#0038bf}

.stDownloadButton>button{border-radius:8px;border:1.5px solid var(--blue);background:var(--blue);color:#fff;font-weight:700;font-size:0.88rem;font-family:'Inter',sans-serif;padding:0.5rem 1.25rem}
.stDownloadButton>button:hover{background:#0038bf;border-color:#0038bf}

.stAlert{border-radius:10px;font-family:'Inter',sans-serif}

[data-testid="stExpander"]{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:10px!important}
[data-testid="stExpander"] summary{font-family:'Inter',sans-serif!important;font-size:0.87rem!important;font-weight:600!important;color:var(--text)!important}

/* Dataframe */
.stDataFrame thead tr th{background:#f8fafc!important;color:var(--muted)!important;font-size:0.7rem!important;font-weight:700!important;letter-spacing:0.06em!important;text-transform:uppercase!important;font-family:'Inter',sans-serif!important}
.stDataFrame tbody tr td{font-family:'Inter',sans-serif!important;font-size:0.85rem!important}

/* FIX 5: Streamlit native tabs override */
div[data-baseweb="tab-list"]{background:var(--card)!important;border:1.5px solid var(--border)!important;border-radius:10px!important;padding:4px!important;gap:3px!important}
div[data-baseweb="tab"]{border-radius:7px!important;font-family:'Inter',sans-serif!important;font-size:0.87rem!important;font-weight:600!important;color:var(--muted)!important;padding:0.45rem 1.4rem!important}
div[data-baseweb="tab"][aria-selected="true"]{background:var(--blue)!important;color:#fff!important;font-weight:700!important}
div[data-baseweb="tab-highlight"]{display:none!important}
div[data-baseweb="tab-border"]{display:none!important}

/* Topbar */
.fac-logo{font-family:'Manrope',sans-serif;font-size:1.1rem;font-weight:800;color:var(--blue);letter-spacing:-0.02em}
.fac-subtitle{font-size:0.78rem;color:var(--muted);margin-top:1px;font-family:'Inter',sans-serif}

/* Section label */
.sd-section-label{font-size:0.68rem;font-weight:700;color:var(--muted);letter-spacing:0.1em;text-transform:uppercase;font-family:'Inter',sans-serif;margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid var(--border)}

/* FIX 2: KPI cards — font identical to student dashboard */
.sd-kpi{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:18px 14px 16px;height:100%;box-sizing:border-box;overflow:hidden}
.sd-kpi-label{font-size:0.62rem;font-weight:700;color:var(--muted);letter-spacing:0.08em;text-transform:uppercase;font-family:'Inter',sans-serif;margin-bottom:7px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sd-kpi-value{font-size:1.75rem;font-weight:800;font-family:'Manrope',sans-serif;color:var(--text);line-height:1;white-space:nowrap}
.sd-kpi-sub{font-size:0.74rem;color:var(--muted);margin-top:5px;font-family:'Inter',sans-serif;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

.sd-card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:22px 20px;box-shadow:0 2px 12px rgba(23,28,31,.04)}
.sd-divider{border:none;border-top:1px solid var(--border);margin:1.75rem 0}

/* Skill bar */
.skill-row{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:10px 14px;margin-bottom:5px;box-shadow:0 1px 4px rgba(23,28,31,.03)}
.skill-row-top{display:flex;justify-content:space-between;margin-bottom:6px}
.skill-name{font-weight:700;font-size:0.88rem;color:var(--text);font-family:'Inter',sans-serif}
.skill-pct{font-size:0.78rem;color:var(--muted);font-family:'Inter',sans-serif}
.skill-track{height:4px;background:var(--border);border-radius:2px;overflow:hidden}
.skill-fill{height:100%;border-radius:2px}

/* Matrix cards */
.mx-card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px;box-shadow:0 2px 12px rgba(23,28,31,.04);height:100%}
.mx-num{font-size:0.62rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:var(--muted);font-family:'Inter',sans-serif;margin-bottom:4px}
.mx-title{font-family:'Manrope',sans-serif;font-size:1rem;font-weight:700;color:var(--text);margin-bottom:8px}
.mx-body{font-size:0.82rem;color:var(--muted);line-height:1.7;font-family:'Inter',sans-serif}
.mx-body .g{color:var(--green);font-weight:600}
.mx-body .a{color:var(--amber);font-weight:600}
.mx-body .r{color:var(--red);font-weight:600}

/* Sign out */
.signout-wrap .stButton>button{border-color:#fca5a5!important;color:#ba1a1a!important;background:#fff5f5!important}
.signout-wrap .stButton>button:hover{background:#fef2f2!important;border-color:#f87171!important}

/* FIX 4: modal overlay for student view */
.modal-overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(23,28,31,0.45);z-index:9998;display:flex;align-items:center;justify-content:center}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# GUARD
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.get("faculty_logged_in"):
    st.error("Access denied. Please log in via the Faculty Dashboard.")
    if st.button("Go to Faculty Login", key="guard_login"):
        st.switch_page("pages/09_faculty.py")
    st.stop()

results = st.session_state.get("faculty_batch_results")
if not results or not results.get("all_student_analyses"):
    st.warning("No batch data found. Upload and process student reports first.")
    if st.button("Back to Faculty Dashboard", key="guard_back"):
        st.switch_page("pages/09_faculty.py")
    st.stop()


def do_signout():
    for k in [k for k in st.session_state if k.startswith("faculty")]:
        del st.session_state[k]
    st.switch_page("pages/09_faculty.py")


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
files_uploaded       = valid_count + len(skipped_files)

student_lookup = {a["student_name"]: a for a in all_student_analyses}
st.session_state["faculty_student_lookup"] = student_lookup

# Classifiers
def classify_drift(s):    return "fully_focused" if s<=30 else "moderately_focused" if s<=60 else "not_focused"
def classify_readiness(s):return "high" if s>=70 else "moderate" if s>=40 else "poor"
def classify_entropy(s):  return "highly_ordered" if s<1.2 else "moderate" if s<2.2 else "high_disorder"

groups = {
    "drift":     {"fully_focused":[],"moderately_focused":[],"not_focused":[]},
    "readiness": {"high":[],"moderate":[],"poor":[]},
    "entropy":   {"highly_ordered":[],"moderate":[],"high_disorder":[]},
}
for a in all_student_analyses:
    groups["drift"][classify_drift(a["drift_score"])].append(a)
    groups["readiness"][classify_readiness(a["readiness_score"])].append(a)
    groups["entropy"][classify_entropy(a["entropy_score"])].append(a)

PW   = dict(paper_bgcolor="#ffffff", plot_bgcolor="#f6fafe", font=dict(color="#515f74", family="Inter"))
GRID = "#e2e8f0"

# ─────────────────────────────────────────────────────────────────────────────
# TOP NAV BAR  (FIX 1 applied here too)
# ─────────────────────────────────────────────────────────────────────────────
col_logo, col_h, col_s = st.columns([8, 1.1, 1.1])
with col_logo:
    st.markdown(
        "<div style='padding:14px 0 8px'>"
        "<div class='fac-logo'>SkillDrift</div>"
        "<div class='fac-subtitle'>Batch Analysis &mdash; " + faculty_name +
        " &nbsp;/&nbsp; " + str(total_students) + " students &nbsp;/&nbsp; " + today_str +
        "</div></div>",
        unsafe_allow_html=True,
    )
with col_h:
    st.markdown("<div style='padding-top:14px'>", unsafe_allow_html=True)
    if st.button("Home", use_container_width=True, key="topnav_home"):
        st.switch_page("pages/01_home.py")
    st.markdown("</div>", unsafe_allow_html=True)
with col_s:
    st.markdown("<div style='padding-top:14px'><div class='signout-wrap'>", unsafe_allow_html=True)
    if st.button("Sign Out", use_container_width=True, key="topnav_signout"):
        do_signout()
    st.markdown("</div></div>", unsafe_allow_html=True)

st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:0 0 18px'>", unsafe_allow_html=True)

col_back, _ = st.columns([2, 10])
with col_back:
    if st.button("Back to Upload", key="back_to_upload"):
        st.session_state["faculty_active_view"] = "upload"
        st.switch_page("pages/09_faculty.py")

# ─────────────────────────────────────────────────────────────────────────────
# FIX 4: inline expanded student detail (replaces separate section + modal)
# Track which student is expanded
# ─────────────────────────────────────────────────────────────────────────────
if "batch_expanded_student" not in st.session_state:
    st.session_state["batch_expanded_student"] = None


# ─────────────────────────────────────────────────────────────────────────────
# TABS (FIX 5: native Streamlit tabs with CSS override above)
# ─────────────────────────────────────────────────────────────────────────────
tab_batch, tab_placement = st.tabs(["  Batch Analysis  ", "  Placement Intelligence  "])


# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — BATCH ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
with tab_batch:

    # Validation KPIs
    st.markdown('<div class="sd-section-label">Upload Validation</div>', unsafe_allow_html=True)
    v1,v2,v3,v4 = st.columns(4, gap="medium")
    for col,lbl,val,sub,color in [
        (v1,"Files Uploaded",    files_uploaded,               "submitted",         "#002c98"),
        (v2,"Records Valid",     valid_count,                  "passed validation", "#15803d"),
        (v3,"Skipped",           max(0,files_uploaded-valid_count),"parse errors",  "#ba1a1a"),
        (v4,"Duplicates Removed",duplicate_count,              "kept latest",       "#d97706"),
    ]:
        with col:
            st.markdown(f'<div class="sd-kpi"><div class="sd-kpi-label">{lbl}</div><div class="sd-kpi-value" style="color:{color}">{val}</div><div class="sd-kpi-sub">{sub}</div></div>', unsafe_allow_html=True)

    if skipped_files:
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        with st.expander(f"Validation issues — {len(skipped_files)} item(s)"):
            for msg in skipped_files:
                st.warning(msg)

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # FIX 2: Batch stats KPIs — Manrope font, same size as student dashboard
    avg_drift     = summary.get("avg_drift_score", 0)
    avg_readiness = summary.get("avg_readiness_score", 0)
    avg_entropy   = summary.get("avg_entropy_score", 0)
    red_count     = summary.get("red_count", 0)
    yellow_count  = summary.get("yellow_count", 0)
    green_count   = summary.get("green_count", 0)

    st.markdown('<div class="sd-section-label">Batch Statistics</div>', unsafe_allow_html=True)
    m1,m2,m3,m4,m5,m6 = st.columns(6, gap="small")
    for col,lbl,val,color in [
        (m1,"Avg Drift",     avg_drift,            "#002c98"),
        (m2,"Avg Readiness", f"{avg_readiness}%",  "#15803d"),
        (m3,"Avg Entropy",   f"{avg_entropy}b",    "#515f74"),
        (m4,"High Urgency",  red_count,            "#ba1a1a"),
        (m5,"Med Urgency",   yellow_count,         "#d97706"),
        (m6,"Low Urgency",   green_count,          "#15803d"),
    ]:
        with col:
            st.markdown(f'<div class="sd-kpi"><div class="sd-kpi-label">{lbl}</div><div class="sd-kpi-value" style="color:{color}">{val}</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

    # FIX 7: Keep only the two most informative batch charts
    # REMOVED: stacked bar (redundant with placement tab), entropy histogram (redundant with tab2)
    # KEPT: urgency donut + track distribution bar — both give unique batch-level info
    cl, cr = st.columns(2, gap="large")
    with cl:
        st.markdown("<div style='font-family:Manrope,sans-serif;font-weight:700;font-size:0.95rem;color:#171c1f;margin-bottom:3px'>Urgency Distribution</div><div style='font-size:0.8rem;color:#515f74;margin-bottom:12px'>Students by placement urgency level</div>", unsafe_allow_html=True)
        fig_pie = go.Figure(go.Pie(
            labels=["High Urgency","Medium Urgency","Low Urgency"],
            values=[red_count, yellow_count, green_count],
            marker=dict(colors=["#ba1a1a","#d97706","#15803d"], line=dict(color="#ffffff",width=2)),
            hole=0.56,
            textfont=dict(color="#ffffff", size=10, family="Inter"),
            hovertemplate="<b>%{label}</b><br>%{value} students (%{percent})<extra></extra>",
        ))
        fig_pie.update_layout(
            **PW, showlegend=True,
            legend=dict(bgcolor="#ffffff", font=dict(color="#515f74",size=10,family="Inter"),
                        orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
            margin=dict(t=10,b=55,l=10,r=10), height=270,
        )
        fig_pie.add_annotation(text=f"<b>{total_students}</b>", x=0.5, y=0.5,
            showarrow=False, font=dict(size=18,color="#171c1f",family="Manrope"))
        st.plotly_chart(fig_pie, use_container_width=True, key="batch_urgency_pie")

    with cr:
        st.markdown("<div style='font-family:Manrope,sans-serif;font-weight:700;font-size:0.95rem;color:#171c1f;margin-bottom:3px'>Career Track Distribution</div><div style='font-size:0.8rem;color:#515f74;margin-bottom:12px'>Students matched to each career track</div>", unsafe_allow_html=True)
        track_dist = summary.get("track_distribution", {})
        if track_dist:
            sorted_td = sorted(track_dist.items(), key=lambda x: x[1])
            fig_track = go.Figure(go.Bar(
                x=[v for _,v in sorted_td], y=[k for k,_ in sorted_td], orientation="h",
                marker=dict(color=[v for _,v in sorted_td],
                    colorscale=[[0,"#c7d5f5"],[0.5,"#4b72e0"],[1,"#002c98"]],
                    showscale=False, line=dict(color="rgba(0,0,0,0)")),
                text=[str(v) for _,v in sorted_td], textposition="outside",
                textfont=dict(color="#515f74",size=10,family="Inter"),
                hovertemplate="%{y}<br>%{x} students<extra></extra>",
            ))
            fig_track.update_layout(**PW,
                xaxis=dict(gridcolor=GRID,color="#515f74",zeroline=False,dtick=1),
                yaxis=dict(color="#171c1f",showgrid=False,automargin=True),
                margin=dict(t=10,b=10,l=10,r=50), height=270)
            st.plotly_chart(fig_track, use_container_width=True, key="batch_track_dist")

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # Missing skills
    st.markdown('<div class="sd-section-label">Skills Most Commonly Missing</div>', unsafe_allow_html=True)
    top_missing = summary.get("top_missing_skills", [])
    if top_missing:
        max_c = top_missing[0][1] or 1
        for rank,(skill,count) in enumerate(top_missing, start=1):
            pct  = round((count/total_students)*100, 1) if total_students else 0
            fill = round((count/max_c)*100)
            fc   = "#ba1a1a" if rank==1 else "#d97706" if rank<=3 else "#002c98"
            st.markdown(f"""
            <div class="skill-row">
                <div class="skill-row-top">
                    <span class="skill-name"><span style="color:{fc};font-size:0.7rem;font-weight:700">#{rank}</span>&nbsp;{skill}</span>
                    <span class="skill-pct">{count} students &nbsp;·&nbsp; {pct}%</span>
                </div>
                <div class="skill-track"><div class="skill-fill" style="width:{fill}%;background:{fc}"></div></div>
            </div>
            """, unsafe_allow_html=True)
        top_name = top_missing[0][0]
        top_pct  = round((top_missing[0][1]/total_students)*100, 1) if total_students else 0
        st.markdown(f"""
        <div style="background:#f0f4ff;border:1px solid #c7d5f5;border-radius:10px;padding:14px 18px;margin-top:8px">
            <div style="font-size:0.68rem;font-weight:700;color:#002c98;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;font-family:Inter,sans-serif">Recommendation</div>
            <div style="font-size:0.86rem;color:#171c1f;line-height:1.55;font-family:Inter,sans-serif">{top_pct}% of students are missing <strong>{top_name}</strong>. A focused workshop before placement season is recommended.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # Heatmap
    st.markdown('<div class="sd-section-label">Skill Coverage Heatmap</div>', unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.82rem;color:#515f74;margin-bottom:10px;font-family:Inter,sans-serif'>Green = Proficient &nbsp;&nbsp; Amber = Beginner &nbsp;&nbsp; Red = Missing</div>", unsafe_allow_html=True)

    all_skills_set = set()
    for a in all_student_analyses: all_skills_set.update(a["verified_skills"].keys())
    all_skills_list = sorted(all_skills_set)

    hmap_data,hmap_labels = [],[]
    for a in all_student_analyses:
        hmap_labels.append(a["student_name"][:20])
        hmap_data.append([
            2 if a["verified_skills"].get(sk) in ("Advanced","Intermediate")
            else 1 if a["verified_skills"].get(sk)=="Beginner" else 0
            for sk in all_skills_list
        ])

    hmap_matrix = pd.DataFrame(hmap_data, index=hmap_labels, columns=all_skills_list)
    if not hmap_matrix.empty:
        n_s,n_k = len(hmap_matrix),len(all_skills_list)
        fig_h,ax = plt.subplots(figsize=(max(10,min(n_k*0.55,32)), max(4,min(n_s*0.5,18))))
        fig_h.patch.set_facecolor("#ffffff"); ax.set_facecolor("#ffffff")
        cmap = mcolors.ListedColormap(["#ffdad6","#fef3c7","#dcfce7"])
        norm = mcolors.BoundaryNorm([-0.5,0.5,1.5,2.5], cmap.N)
        sns.heatmap(hmap_matrix, ax=ax, cmap=cmap, norm=norm,
                    linewidths=0.4, linecolor="#f6fafe", cbar=True,
                    cbar_kws={"ticks":[0,1,2],"label":"Skill Level"})
        cbar = ax.collections[0].colorbar
        cbar.set_ticklabels(["Missing","Beginner","Proficient"])
        cbar.ax.yaxis.label.set_color("#515f74"); cbar.ax.tick_params(colors="#515f74",labelsize=8)
        cbar.outline.set_edgecolor("#e2e8f0")
        ax.set_xlabel("Skills",color="#515f74",fontsize=9,labelpad=8)
        ax.set_ylabel("Students",color="#515f74",fontsize=9,labelpad=8)
        ax.tick_params(colors="#171c1f",labelsize=7.5)
        ax.set_title(f"Skill Coverage — {n_s} Students x {n_k} Skills",color="#171c1f",fontsize=11,pad=14,fontweight="bold")
        for sp in ax.spines.values(): sp.set_edgecolor("#e2e8f0")
        plt.xticks(rotation=45,ha="right",fontsize=7.5,color="#171c1f")
        plt.yticks(fontsize=8,color="#171c1f"); plt.tight_layout()
        st.pyplot(fig_h, use_container_width=True); plt.close(fig_h)

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # ── FIX 3 + FIX 4: Individual student records ─────────────────────────────
    # FIX 3: all numeric values cast to int before display (no decimals)
    # FIX 4: No separate "view" section below table.
    #         Table has NO "Next Skill" column.
    #         Each row has a "View" button — clicking expands an inline detail panel.
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown('<div class="sd-section-label">Individual Student Records</div>', unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.82rem;color:#515f74;margin-top:-6px;margin-bottom:14px;font-family:Inter,sans-serif'>Click View on any student to expand their full analysis below the table.</div>", unsafe_allow_html=True)

    # Build display table — FIX 3: int values, FIX 4: no Next Skill column
    table_rows = []
    for a in all_student_analyses:
        table_rows.append({
            "Student":    a["student_name"],
            "Sem":        int(a["semester"]),
            "Drift":      int(round(a["drift_score"])),        # FIX 3: integer
            "Status":     a["drift_label"],
            "Best Track": a["best_track"],
            "Match %":    int(round(a["match_pct"])),          # FIX 3: integer
            "Readiness":  int(round(a["readiness_score"])),    # FIX 3: integer
            "Urgency":    a["urgency_level"],
            # Next Skill REMOVED per FIX 4
        })

    table_df = pd.DataFrame(table_rows)

    def _sd(v): return "color:#15803d;font-weight:700" if v<=20 else "color:#d97706;font-weight:700" if v<=60 else "color:#ba1a1a;font-weight:700"
    def _sr(v): return "color:#15803d;font-weight:700" if v>=70 else "color:#d97706;font-weight:700" if v>=40 else "color:#ba1a1a;font-weight:700"
    def _su(v): return "color:#15803d;font-weight:700" if v=="Green" else "color:#d97706;font-weight:700" if v=="Yellow" else "color:#ba1a1a;font-weight:700" if v=="Red" else ""
    def _st(v): return "color:#002c98;font-weight:600"

    styled = (table_df.style
        .map(_sd, subset=["Drift"])
        .map(_sr, subset=["Readiness"])
        .map(_su, subset=["Urgency"])
        .map(_st, subset=["Best Track"]))

    st.dataframe(styled, use_container_width=True, hide_index=True,
                 height=min(420, 42+len(table_rows)*36))

    # FIX 4: View buttons grid (4 per row) — clicking sets expanded student
    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.81rem;color:#515f74;margin-bottom:10px;font-family:Inter,sans-serif'>Select a student to view their full analysis:</div>", unsafe_allow_html=True)

    n_cols = 4
    for chunk_start in range(0, len(all_student_analyses), n_cols):
        chunk = all_student_analyses[chunk_start:chunk_start+n_cols]
        btn_cols = st.columns(n_cols, gap="small")
        for idx, a in enumerate(chunk):
            name = a["student_name"]
            with btn_cols[idx]:
                is_expanded = (st.session_state["batch_expanded_student"] == name)
                btn_label   = f"  {name}" if not is_expanded else f"  {name} (close)"
                if st.button(btn_label, key=f"view_btn_{name}", use_container_width=True):
                    st.session_state["batch_expanded_student"] = None if is_expanded else name
                    st.rerun()

    # FIX 4: Inline expanded student detail panel
    expanded = st.session_state.get("batch_expanded_student")
    if expanded and expanded in student_lookup:
        a = student_lookup[expanded]

        ds_color = "#15803d" if a["drift_score"]<=20 else "#d97706" if a["drift_score"]<=60 else "#ba1a1a"
        rs_color = "#15803d" if a["readiness_score"]>=70 else "#d97706" if a["readiness_score"]>=40 else "#ba1a1a"
        es_color = "#15803d" if a["entropy_score"]<1.2 else "#d97706" if a["entropy_score"]<2.0 else "#ba1a1a"
        ur_color = {"Red":"#ba1a1a","Yellow":"#d97706","Green":"#15803d"}.get(a.get("urgency_info",{}).get("urgency_level",""),"#515f74")
        urgency_level = a.get("urgency_info",{}).get("urgency_level","—") if a.get("urgency_info") else "—"

        st.markdown(f"""
        <div style="background:#ffffff;border:2px solid #002c98;border-radius:14px;
                    padding:20px 22px;margin-top:14px;box-shadow:0 4px 20px rgba(0,44,152,0.1)">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">
                <div>
                    <div style="font-family:Manrope,sans-serif;font-size:1.1rem;font-weight:800;color:#171c1f">{expanded}</div>
                    <div style="font-size:0.78rem;color:#515f74;margin-top:2px">Semester {int(a['semester'])} &nbsp;·&nbsp; {len(a['verified_skills'])} verified skills</div>
                </div>
                <div style="text-align:right">
                    <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:#515f74;font-family:Inter,sans-serif">Urgency</div>
                    <div style="font-size:1rem;font-weight:800;color:{ur_color};font-family:Manrope,sans-serif">{urgency_level}</div>
                </div>
            </div>
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:16px">
                <div style="background:#f6fafe;border:1px solid #e2e8f0;border-radius:10px;padding:14px 12px">
                    <div style="font-size:0.6rem;font-weight:700;color:#515f74;text-transform:uppercase;letter-spacing:0.08em;font-family:Inter,sans-serif;margin-bottom:5px">Drift Score</div>
                    <div style="font-size:1.5rem;font-weight:800;font-family:Manrope,sans-serif;color:{ds_color};line-height:1">{int(round(a['drift_score']))}</div>
                    <div style="font-size:0.75rem;color:#515f74;margin-top:4px;font-family:Inter,sans-serif">{a['drift_label']}</div>
                </div>
                <div style="background:#f6fafe;border:1px solid #e2e8f0;border-radius:10px;padding:14px 12px">
                    <div style="font-size:0.6rem;font-weight:700;color:#515f74;text-transform:uppercase;letter-spacing:0.08em;font-family:Inter,sans-serif;margin-bottom:5px">Readiness</div>
                    <div style="font-size:1.5rem;font-weight:800;font-family:Manrope,sans-serif;color:{rs_color};line-height:1">{int(round(a['readiness_score']))}%</div>
                    <div style="font-size:0.75rem;color:#515f74;margin-top:4px;font-family:Inter,sans-serif">{a['best_track']}</div>
                </div>
                <div style="background:#f6fafe;border:1px solid #e2e8f0;border-radius:10px;padding:14px 12px">
                    <div style="font-size:0.6rem;font-weight:700;color:#515f74;text-transform:uppercase;letter-spacing:0.08em;font-family:Inter,sans-serif;margin-bottom:5px">Entropy</div>
                    <div style="font-size:1.5rem;font-weight:800;font-family:Manrope,sans-serif;color:{es_color};line-height:1">{a['entropy_score']}</div>
                    <div style="font-size:0.75rem;color:#515f74;margin-top:4px;font-family:Inter,sans-serif">{a['entropy_label']}</div>
                </div>
                <div style="background:#f6fafe;border:1px solid #e2e8f0;border-radius:10px;padding:14px 12px">
                    <div style="font-size:0.6rem;font-weight:700;color:#515f74;text-transform:uppercase;letter-spacing:0.08em;font-family:Inter,sans-serif;margin-bottom:5px">Next Skill</div>
                    <div style="font-size:1.1rem;font-weight:800;font-family:Manrope,sans-serif;color:#d97706;line-height:1.2">{a.get('next_skill') or 'N/A'}</div>
                    <div style="font-size:0.75rem;color:#515f74;margin-top:4px;font-family:Inter,sans-serif">highest impact</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Verified skills table inside the panel
        if a["verified_skills"]:
            on_track = (a.get("focus_debt_info") or {}).get("on_track_skills", [])
            skill_rows = [{"Skill":sk,"Level":lv,"On-Track":"Yes" if sk in on_track else "No"} for sk,lv in a["verified_skills"].items()]
            sk_df = pd.DataFrame(skill_rows)
            def _sl(v): return "color:#002c98;font-weight:700" if v=="Advanced" else "color:#15803d;font-weight:600" if v=="Intermediate" else "color:#515f74"
            def _so(v): return "color:#15803d;font-weight:700" if v=="Yes" else "color:#d97706"
            st.dataframe(sk_df.style.map(_sl,subset=["Level"]).map(_so,subset=["On-Track"]),
                         use_container_width=True, hide_index=True, key=f"sk_table_{expanded}")

        # Open full dashboard button
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        c_open, c_close, _ = st.columns([2,2,6])
        with c_open:
            if st.button("Open Full Dashboard", type="primary", key=f"open_full_{expanded}", use_container_width=True):
                st.session_state["faculty_viewing_student"] = expanded
                st.switch_page("pages/09b_student_view.py")
        with c_close:
            if st.button("Close", key=f"close_panel_{expanded}", use_container_width=True):
                st.session_state["batch_expanded_student"] = None
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # Export
    st.markdown('<div class="sd-section-label">Export</div>', unsafe_allow_html=True)
    csv_buf = io.StringIO(); merged_df.to_csv(csv_buf, index=False)
    col_dl, col_info = st.columns([3,5], gap="medium")
    with col_dl:
        st.download_button(
            label="Download Full Batch Report (CSV)",
            data=csv_buf.getvalue().encode("utf-8"),
            file_name=f"SkillDrift_Batch_{datetime.now().strftime('%Y_%m_%d')}.csv",
            mime="text/csv", type="primary", key="dl_batch",
        )
    with col_info:
        st.markdown(f"<div style='font-size:0.82rem;color:#515f74;font-family:Inter,sans-serif;padding-top:4px'>{total_students} students &nbsp;·&nbsp; Generated {datetime.now().strftime('%d %b %Y, %I:%M %p')}</div>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — PLACEMENT INTELLIGENCE
# FIX 7: Removed redundant charts (stacked bar from batch tab duplicate info,
#         urgency donut already in batch tab). Kept and enhanced:
#         - 4 KPI cards
#         - Drift vs Readiness scatter (unique — shows individual student positions)
#         - Entropy histogram (unique — distribution shape)
#         - 3 matrix expanders with mini bar charts
#         - Full classification table + export
# ═════════════════════════════════════════════════════════════════════════════
with tab_placement:

    st.markdown(f"""
    <div class="sd-card" style="margin-bottom:20px">
        <div style="font-family:Manrope,sans-serif;font-size:1.05rem;font-weight:700;color:#171c1f;margin-bottom:4px">Placement Intelligence</div>
        <div style="font-size:0.82rem;color:#515f74;font-family:Inter,sans-serif">{total_students} students classified across three readiness dimensions. Expand any group to inspect individual profiles.</div>
    </div>
    """, unsafe_allow_html=True)

    placement_ready = len(groups["readiness"]["high"])
    fully_focused   = len(groups["drift"]["fully_focused"])
    high_disorder   = len(groups["entropy"]["high_disorder"])
    high_urgency    = sum(1 for a in all_student_analyses if a["urgency_level"]=="Red")

    pk1,pk2,pk3,pk4 = st.columns(4, gap="medium")
    for col,lbl,val,sub,color in [
        (pk1,"Placement Ready",  placement_ready, f"{round(placement_ready/total_students*100) if total_students else 0}% readiness 70+", "#15803d"),
        (pk2,"Fully Focused",    fully_focused,   f"{round(fully_focused/total_students*100) if total_students else 0}% drift 0–30",      "#002c98"),
        (pk3,"Skill Disorder",   high_disorder,   f"{round(high_disorder/total_students*100) if total_students else 0}% entropy 2.2+",    "#ba1a1a"),
        (pk4,"Urgent Attention", high_urgency,    "semester 5 and above",                                                                  "#d97706"),
    ]:
        with col:
            st.markdown(f'<div class="sd-kpi"><div class="sd-kpi-label">{lbl}</div><div class="sd-kpi-value" style="color:{color}">{val}</div><div class="sd-kpi-sub">{sub}</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # FIX 7: Drift vs Readiness scatter — highest-value visualization, kept + enhanced
    st.markdown('<div class="sd-section-label">Drift vs Readiness — Student Map</div>', unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.82rem;color:#515f74;margin-bottom:10px;font-family:Inter,sans-serif'>Each point is one student. Ideal = bottom-left (low drift, high readiness). Point size = semester.</div>", unsafe_allow_html=True)

    if all_student_analyses:
        scatter_df = pd.DataFrame([{
            "name":a["student_name"],"drift":a["drift_score"],
            "readiness":a["readiness_score"],"urgency":a["urgency_level"],"semester":a["semester"],
        } for a in all_student_analyses])

        urg_colors = {"Red":"#ba1a1a","Yellow":"#d97706","Green":"#15803d"}
        fig_sc = go.Figure()
        for uv,uc in urg_colors.items():
            sub = scatter_df[scatter_df["urgency"]==uv]
            if sub.empty: continue
            fig_sc.add_trace(go.Scatter(
                x=sub["drift"], y=sub["readiness"], mode="markers+text",
                name=f"{uv} Urgency",
                marker=dict(color=uc, size=sub["semester"]*3+8, opacity=0.85, line=dict(color="#ffffff",width=1.5)),
                text=sub["name"], textposition="top center",
                textfont=dict(size=8,color="#515f74",family="Inter"),
                hovertemplate="<b>%{text}</b><br>Drift: %{x}<br>Readiness: %{y}%<extra></extra>",
            ))
        fig_sc.add_shape(type="rect",x0=0,y0=70,x1=30,y1=100,
            fillcolor="rgba(21,128,61,0.06)",line=dict(color="rgba(21,128,61,0.3)",width=1,dash="dot"))
        fig_sc.add_annotation(x=15,y=85,text="Ideal Zone",showarrow=False,
            font=dict(color="rgba(21,128,61,0.6)",size=9,family="Inter"))
        fig_sc.update_layout(**PW,
            xaxis=dict(title="Drift Score (lower = more focused)",gridcolor=GRID,color="#515f74",range=[-5,105],zeroline=False),
            yaxis=dict(title="Readiness (%)",gridcolor=GRID,color="#515f74",range=[-5,105],zeroline=False),
            legend=dict(bgcolor="#ffffff",bordercolor=GRID,borderwidth=1,font=dict(color="#515f74",size=10,family="Inter")),
            margin=dict(t=20,b=40,l=40,r=20), height=400)
        st.plotly_chart(fig_sc, use_container_width=True, key="pl_scatter")

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # FIX 7: Entropy histogram — kept, shows distribution shape not captured elsewhere
    st.markdown('<div class="sd-section-label">Entropy Distribution</div>', unsafe_allow_html=True)
    if all_student_analyses:
        ent_vals = [a["entropy_score"] for a in all_student_analyses]
        fig_ent = go.Figure()
        fig_ent.add_trace(go.Histogram(
            x=ent_vals, nbinsx=min(15,max(5,total_students//2)),
            marker=dict(color=ent_vals,
                colorscale=[[0,"#dcfce7"],[0.45,"#fef3c7"],[1,"#ffdad6"]],
                line=dict(color="#ffffff",width=0.8), cmin=0,cmax=3),
            hovertemplate="Entropy %{x:.2f} bits<br>Count: %{y}<extra></extra>",
        ))
        for thresh,label,color in [(1.2,"Focus Threshold","#15803d"),(2.2,"Disorder Threshold","#ba1a1a")]:
            fig_ent.add_vline(x=thresh,line_dash="dash",line_color=color,line_width=1.5,
                annotation=dict(text=label,font=dict(color=color,size=9,family="Inter"),yanchor="top"))
        fig_ent.update_layout(**PW, showlegend=False,
            xaxis=dict(title="Shannon Entropy (bits)",gridcolor=GRID,color="#515f74"),
            yaxis=dict(title="Number of Students",gridcolor=GRID,color="#515f74"),
            margin=dict(t=20,b=40,l=40,r=20), height=260)
        st.plotly_chart(fig_ent, use_container_width=True, key="pl_entropy_hist")

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # ── render_group — unique key fix inside ──────────────────────────────────
    def render_group(matrix_key, group_key, label, range_desc, total):
        student_list = groups[matrix_key][group_key]
        count = len(student_list)
        pct   = round((count/total)*100) if total>0 else 0

        with st.expander(f"{label}  —  {count} student{'s' if count!=1 else ''}  ({pct}%)  ·  {range_desc}", expanded=False):
            if not student_list:
                st.markdown("<span style='color:#515f74;font-size:0.82rem;font-family:Inter,sans-serif'>No students in this group.</span>", unsafe_allow_html=True)
                return

            if len(student_list) >= 2:
                mini_v = [int(round(a["readiness_score"])) for a in student_list]
                mini_n = [a["student_name"] for a in student_list]
                mini_c = ["#15803d" if v>=70 else "#d97706" if v>=40 else "#ba1a1a" for v in mini_v]
                fig_m = go.Figure(go.Bar(x=mini_n, y=mini_v,
                    marker=dict(color=mini_c,line=dict(color="#ffffff",width=0.5)),
                    text=[f"{v}%" for v in mini_v], textposition="outside",
                    textfont=dict(color="#515f74",size=9,family="Inter"),
                    hovertemplate="%{x}<br>Readiness: %{y}%<extra></extra>"))
                fig_m.update_layout(**PW,
                    xaxis=dict(gridcolor=GRID,color="#515f74",tickfont=dict(size=8,family="Inter")),
                    yaxis=dict(gridcolor=GRID,color="#515f74",range=[0,115],title="Readiness %"),
                    showlegend=False, margin=dict(t=10,b=10,l=40,r=10), height=150)
                # FIX: unique key = matrix_key + group_key
                st.plotly_chart(fig_m, use_container_width=True, key=f"grp_{matrix_key}_{group_key}")

            h1,h2,h3,h4,h5 = st.columns([3,1,2,2,2])
            for hc,ht in zip([h1,h2,h3,h4,h5],["Name","Sem","Drift","Readiness","Track"]):
                hc.markdown(f"<span style='font-size:0.62rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#515f74;font-family:Inter,sans-serif'>{ht}</span>", unsafe_allow_html=True)
            st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:6px 0 10px'>", unsafe_allow_html=True)

            for s in student_list:
                rc2 = "#15803d" if s["readiness_score"]>=70 else "#d97706" if s["readiness_score"]>=40 else "#ba1a1a"
                dc2 = "#15803d" if s["drift_score"]<=30 else "#d97706" if s["drift_score"]<=60 else "#ba1a1a"
                c1,c2,c3,c4,c5 = st.columns([3,1,2,2,2])
                c1.markdown(f"<span style='font-weight:700;font-size:0.87rem;color:#171c1f;font-family:Manrope,sans-serif'>{s['student_name']}</span>", unsafe_allow_html=True)
                c2.markdown(f"<span style='font-size:0.8rem;color:#515f74;font-family:Inter,sans-serif'>{int(s['semester'])}</span>", unsafe_allow_html=True)
                c3.markdown(f"<span style='font-size:0.82rem;color:{dc2};font-weight:600;font-family:Inter,sans-serif'>{int(round(s['drift_score']))}</span>", unsafe_allow_html=True)
                c4.markdown(f"<span style='font-size:0.82rem;color:{rc2};font-weight:600;font-family:Inter,sans-serif'>{int(round(s['readiness_score']))}%</span>", unsafe_allow_html=True)
                c5.markdown(f"<span style='font-size:0.78rem;color:#002c98;font-family:Inter,sans-serif'>{s['best_track']}</span>", unsafe_allow_html=True)
                if st.button("View", key=f"pl_btn_{matrix_key}_{group_key}_{s['student_name']}"):
                    st.session_state["faculty_viewing_student"] = s["student_name"]
                    st.switch_page("pages/09b_student_view.py")
                st.markdown("<div style='border-top:1px solid #f0f4f8;margin:4px 0'></div>", unsafe_allow_html=True)

    # Matrix 1 — Drift
    mx1l, mx1r = st.columns([3, 5])
    with mx1l:
        st.markdown("""<div class="mx-card"><div class="mx-num">Matrix 01</div><div class="mx-title">Skill Drift</div><div class="mx-body">How scattered skills are across 8 career tracks.<br><br><span class="g">Fully Focused</span> — drift 0 to 30<br><span class="a">Moderately Focused</span> — drift 31 to 60<br><span class="r">Not Focused</span> — drift 61 to 100</div></div>""", unsafe_allow_html=True)
        dv = [len(groups["drift"]["fully_focused"]),len(groups["drift"]["moderately_focused"]),len(groups["drift"]["not_focused"])]
        fig_d = go.Figure(go.Pie(labels=["Fully Focused","Moderately Focused","Not Focused"],values=dv,
            marker=dict(colors=["#15803d","#d97706","#ba1a1a"],line=dict(color="#ffffff",width=2)),
            hole=0.65,textinfo="none",hovertemplate="%{label}<br>%{value} students<extra></extra>"))
        fig_d.update_layout(**PW, showlegend=False, margin=dict(t=10,b=10,l=10,r=10), height=160)
        st.plotly_chart(fig_d, use_container_width=True, key="mx_donut_drift")
    with mx1r:
        st.markdown('<div class="sd-section-label">Groups</div>', unsafe_allow_html=True)
        render_group("drift","fully_focused",     "Fully Focused",     "Drift 0 to 30",   total_students)
        render_group("drift","moderately_focused","Moderately Focused","Drift 31 to 60",  total_students)
        render_group("drift","not_focused",       "Not Focused",       "Drift 61 to 100", total_students)

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # Matrix 2 — Readiness
    mx2l, mx2r = st.columns([3, 5])
    with mx2l:
        st.markdown("""<div class="mx-card"><div class="mx-num">Matrix 02</div><div class="mx-title">Placement Readiness</div><div class="mx-body">Verified skills matched against job posting frequency.<br><br><span class="g">High</span> — readiness 70% or above<br><span class="a">Moderate</span> — readiness 40 to 69%<br><span class="r">Poor</span> — readiness below 40%</div></div>""", unsafe_allow_html=True)
        rv = [len(groups["readiness"]["high"]),len(groups["readiness"]["moderate"]),len(groups["readiness"]["poor"])]
        fig_r = go.Figure(go.Pie(labels=["High","Moderate","Poor"],values=rv,
            marker=dict(colors=["#15803d","#d97706","#ba1a1a"],line=dict(color="#ffffff",width=2)),
            hole=0.65,textinfo="none",hovertemplate="%{label}<br>%{value} students<extra></extra>"))
        fig_r.update_layout(**PW, showlegend=False, margin=dict(t=10,b=10,l=10,r=10), height=160)
        st.plotly_chart(fig_r, use_container_width=True, key="mx_donut_readiness")
    with mx2r:
        st.markdown('<div class="sd-section-label">Groups</div>', unsafe_allow_html=True)
        render_group("readiness","high",    "High Readiness",    "Readiness 70% or above",total_students)
        render_group("readiness","moderate","Moderate Readiness","Readiness 40 to 69%",   total_students)
        render_group("readiness","poor",    "Poor Readiness",    "Readiness below 40%",   total_students)

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # Matrix 3 — Entropy
    mx3l, mx3r = st.columns([3, 5])
    with mx3l:
        st.markdown("""<div class="mx-card"><div class="mx-num">Matrix 03</div><div class="mx-title">Skill Entropy</div><div class="mx-body">Shannon Entropy measures disorder in the skill distribution.<br><br><span class="g">Highly Ordered</span> — below 1.2 bits<br><span class="a">Moderate</span> — 1.2 to 2.2 bits<br><span class="r">High Disorder</span> — above 2.2 bits</div></div>""", unsafe_allow_html=True)
        ev = [len(groups["entropy"]["highly_ordered"]),len(groups["entropy"]["moderate"]),len(groups["entropy"]["high_disorder"])]
        fig_e = go.Figure(go.Pie(labels=["Highly Ordered","Moderate","High Disorder"],values=ev,
            marker=dict(colors=["#15803d","#d97706","#ba1a1a"],line=dict(color="#ffffff",width=2)),
            hole=0.65,textinfo="none",hovertemplate="%{label}<br>%{value} students<extra></extra>"))
        fig_e.update_layout(**PW, showlegend=False, margin=dict(t=10,b=10,l=10,r=10), height=160)
        st.plotly_chart(fig_e, use_container_width=True, key="mx_donut_entropy")
    with mx3r:
        st.markdown('<div class="sd-section-label">Groups</div>', unsafe_allow_html=True)
        render_group("entropy","highly_ordered","Highly Ordered","Entropy below 1.2 bits", total_students)
        render_group("entropy","moderate",      "Moderate",      "Entropy 1.2 to 2.2 bits",total_students)
        render_group("entropy","high_disorder", "High Disorder", "Entropy above 2.2 bits",  total_students)

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # Full classification table
    st.markdown('<div class="sd-section-label">Complete Classification Table</div>', unsafe_allow_html=True)
    DRIFT_LBL    = {"fully_focused":"Fully Focused","moderately_focused":"Mod. Focused","not_focused":"Not Focused"}
    READINESS_LBL= {"high":"High","moderate":"Moderate","poor":"Poor"}
    ENTROPY_LBL  = {"highly_ordered":"Highly Ordered","moderate":"Moderate","high_disorder":"High Disorder"}

    rows = []
    for a in all_student_analyses:
        rows.append({
            "Student":         a["student_name"],
            "Sem":             int(a["semester"]),
            "Drift":           int(round(a["drift_score"])),      # FIX 3
            "Drift Group":     DRIFT_LBL[classify_drift(a["drift_score"])],
            "Readiness %":     int(round(a["readiness_score"])),  # FIX 3
            "Readiness Group": READINESS_LBL[classify_readiness(a["readiness_score"])],
            "Entropy":         a["entropy_score"],
            "Entropy Group":   ENTROPY_LBL[classify_entropy(a["entropy_score"])],
            "Best Track":      a["best_track"],
            "Urgency":         a["urgency_level"],
        })

    summary_df = pd.DataFrame(rows)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="sd-section-label">Export</div>', unsafe_allow_html=True)
    pl_buf = io.StringIO(); summary_df.to_csv(pl_buf, index=False)
    st.download_button(
        label="Download Placement Classification Report (CSV)",
        data=pl_buf.getvalue().encode("utf-8"),
        file_name=f"SkillDrift_Placement_{datetime.now().strftime('%Y_%m_%d')}.csv",
        mime="text/csv", type="primary", key="dl_placement",
    )
    st.markdown("<div style='font-size:0.8rem;color:#515f74;margin-top:6px;font-family:Inter,sans-serif'>Drift group, readiness group, entropy group, best track, and urgency for every student.</div>", unsafe_allow_html=True)
