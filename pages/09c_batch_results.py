# pages/09c_batch_results.py — Faculty Batch Results

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import io
import streamlit.components.v1 as components
from datetime import datetime

st.set_page_config(
    page_title="SkillDrift — Batch Results",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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
    .block-container {
        padding-top:    0         !important;
        padding-bottom: 3rem      !important;
        max-width:      1000px    !important;
        margin-left:    auto      !important;
        margin-right:   auto      !important;
        padding-left:   2rem      !important;
        padding-right:  2rem      !important;
    }
    h1, h2, h3, h4 { font-family: 'Manrope', sans-serif !important; color: var(--text) !important; }

    .stButton > button {
        border-radius: 8px; border: 1.5px solid var(--border);
        background: var(--card); color: var(--text);
        font-weight: 600; font-size: 0.88rem; font-family: 'Inter', sans-serif;
        padding: 0.45rem 1rem; transition: all 0.12s ease;
    }
    .stButton > button:hover { background: #f0f4f8; border-color: #c2cad4; }
    .stButton > button[kind="primary"] {
        background: var(--blue); color: #ffffff; border-color: var(--blue); font-weight: 700;
    }
    .stDownloadButton > button {
        border-radius: 8px; border: 1.5px solid var(--blue);
        background: var(--blue); color: #ffffff; font-weight: 700;
        font-size: 0.9rem; font-family: 'Inter', sans-serif; padding: 0.5rem 1.25rem;
    }
    .stAlert { border-radius: 10px; font-family: 'Inter', sans-serif; }
    [data-testid="stExpander"] {
        background: var(--card) !important; border: 1px solid var(--border) !important;
        border-radius: 10px !important;
    }
    [data-testid="stExpander"] summary {
        font-family: 'Inter', sans-serif !important; font-size: 0.88rem !important;
        font-weight: 600 !important; color: var(--text) !important;
    }
    div[data-baseweb="tab"] { color: var(--muted); font-size: 0.875rem; font-family: 'Inter', sans-serif; }
    div[data-baseweb="tab"][aria-selected="true"] { color: var(--text); font-weight: 700; }

    .sd-kpi {
        background: var(--card); border: 1px solid var(--border); border-radius: 12px;
        padding: 20px 16px 18px; height: 100%; box-sizing: border-box; overflow: hidden;
    }
    .sd-kpi-label {
        font-size: 0.65rem; font-weight: 700; color: var(--muted); letter-spacing: 0.08em;
        text-transform: uppercase; font-family: 'Inter', sans-serif;
        margin-bottom: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .sd-kpi-value {
        font-size: 1.75rem; font-weight: 800; font-family: 'Manrope', sans-serif;
        color: var(--text); line-height: 1; white-space: nowrap;
    }
    .sd-kpi-sub {
        font-size: 0.72rem; color: var(--muted); margin-top: 6px;
        font-family: 'Inter', sans-serif; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .sd-card {
        background: var(--card); border: 1px solid var(--border); border-radius: 12px;
        padding: 22px 20px; box-shadow: 0 2px 12px rgba(23,28,31,.04);
    }
    .sd-section-label {
        font-size: 0.7rem; font-weight: 700; color: var(--muted); letter-spacing: 0.1em;
        text-transform: uppercase; font-family: 'Inter', sans-serif;
        margin-bottom: 14px; padding-bottom: 10px; border-bottom: 1px solid var(--border);
    }
    .sd-divider { border: none; border-top: 1px solid var(--border); margin: 1.75rem 0; }

    .fac-logo {
        font-family: 'Manrope', sans-serif; font-size: 1.6rem; font-weight: 800;
        color: var(--blue); letter-spacing: -0.02em; line-height: 1.1;
    }
    .fac-subtitle {
        font-family: 'Inter', sans-serif; font-size: 0.95rem; font-weight: 600;
        color: var(--muted); margin-top: 4px;
    }
    .skill-row {
        background: var(--card); border: 1px solid var(--border); border-radius: 10px;
        padding: 10px 14px; margin-bottom: 5px; box-shadow: 0 1px 4px rgba(23,28,31,.03);
    }
    .skill-row-top { display: flex; justify-content: space-between; margin-bottom: 6px; }
    .skill-name { font-weight: 700; font-size: 0.88rem; color: var(--text); font-family: 'Inter', sans-serif; }
    .skill-pct  { font-size: 0.78rem; color: var(--muted); font-family: 'Inter', sans-serif; }
    .skill-track { height: 4px; background: var(--border); border-radius: 2px; overflow: hidden; }
    .skill-fill  { height: 100%; border-radius: 2px; }
    .mx-card {
        background: var(--card); border: 1px solid var(--border); border-radius: 12px;
        padding: 20px; box-shadow: 0 2px 12px rgba(23,28,31,.04); height: 100%;
    }
    .mx-num   { font-size: 0.62rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); font-family: 'Inter', sans-serif; margin-bottom: 4px; }
    .mx-title { font-family: 'Manrope', sans-serif; font-size: 1rem; font-weight: 700; color: var(--text); margin-bottom: 8px; }
    .mx-body  { font-size: 0.82rem; color: var(--muted); line-height: 1.7; font-family: 'Inter', sans-serif; }
    .mx-body .g { color: var(--green); font-weight: 600; }
    .mx-body .a { color: var(--amber); font-weight: 600; }
    .mx-body .r { color: var(--red);   font-weight: 600; }

    /* FIX 1: top bar layout — identical to 09_faculty.py upload page */
    .fac-topbar {
        display: flex; justify-content: space-between; align-items: center;
        padding: 16px 0; border-bottom: 1px solid var(--border); margin-bottom: 24px;
    }

    /* FIX 2 & 3: compact "View" buttons inside table rows.
       All st.button calls with type="primary" on this page are the in-table
       View buttons (st.download_button has its own selector .stDownloadButton).
       So we can safely compact every primary st.button.                        */
    .stButton > button[kind="primary"] {
        padding:        0px 10px !important;
        font-size:      0.72rem  !important;
        font-weight:    600      !important;
        min-height:     38px     !important;
        height:         38px     !important;
        border-radius:  6px      !important;
        line-height:    1        !important;
        width:          100%     !important;
        margin-top:     0px      !important;
    }
    div[data-testid="stButton"] {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
</style>
""", unsafe_allow_html=True)


# ── helpers ──────────────────────────────────────────────────────────────────
def do_signout():
    for k in [k for k in st.session_state if k.startswith("faculty")]:
        del st.session_state[k]
    st.switch_page("pages/09_faculty.py")

def _html_table(columns, col_widths, rows_html, height=None):
    """
    Render a fully self-contained HTML table via st.components.v1.html
    so Streamlit never escapes or mis-renders it.
    columns = list of header strings
    col_widths = list of pixel widths (strings like "180px") or None for auto
    rows_html = list of <tr>...</tr> HTML strings
    """
    thead_cells = ""
    for i, col in enumerate(columns):
        w = f'width="{col_widths[i]}"' if col_widths and col_widths[i] else ""
        thead_cells += f'<th {w}>{col}</th>'

    tbody = "\n".join(rows_html)
    table_html = f"""
    <!DOCTYPE html><html><head>
    <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@700;800&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
      * {{ box-sizing: border-box; margin: 0; padding: 0; }}
      body {{ background: transparent; font-family: 'Inter', sans-serif; }}
      table {{
        width: 100%; border-collapse: collapse;
        background: #ffffff; border: 1px solid #e2e8f0;
        border-radius: 10px; overflow: hidden; font-size: 13.5px;
      }}
      thead tr {{ background: #f8fafc; }}
      thead th {{
        padding: 10px 12px; text-align: left; font-size: 10.5px; font-weight: 700;
        color: #515f74; text-transform: uppercase; letter-spacing: 0.08em;
        border-bottom: 1.5px solid #e2e8f0; border-right: 1px solid #e2e8f0;
        white-space: nowrap; font-family: 'Inter', sans-serif;
      }}
      thead th:last-child {{ border-right: none; }}
      tbody tr {{ border-bottom: 1px solid #e2e8f0; }}
      tbody tr:last-child {{ border-bottom: none; }}
      tbody tr:hover {{ background: #f6fafe; }}
      tbody td {{
        padding: 10px 12px; vertical-align: middle;
        border-right: 1px solid #e2e8f0;
      }}
      tbody td:last-child {{ border-right: none; }}
      .n  {{ font-family: 'Manrope', sans-serif; font-weight: 700; font-size: 14px; color: #171c1f; }}
      .m  {{ color: #515f74; }}
      .b  {{ color: #002c98; font-weight: 600; }}
      .fw {{ font-weight: 700; }}
    </style>
    </head><body>
    <table><thead><tr>{thead_cells}</tr></thead>
    <tbody>{tbody}</tbody></table>
    </body></html>
    """
    h = height or (40 + len(rows_html) * 43 + 10)
    components.html(table_html, height=h, scrolling=False)


def _table_with_view_buttons(columns, col_widths, row_data, key_prefix):
    """
    Render a table where the LAST column is a real Streamlit "View" button.

    Each cell is a self-contained bordered mini-card. With gap="small" between
    st.columns, this gives a clean modern table look without iframe escaping
    issues — and the buttons are real Streamlit buttons that can switch pages.

    columns      : list of header strings (last = action column header, e.g. "View")
    col_widths   : list of relative column weights for st.columns
    row_data     : list of {"cells": [(text, css_class), ...],
                            "styles": [inline_style_str, ...] (optional),
                            "student_name": str}
    key_prefix   : unique prefix for button keys
    """
    last_idx = len(col_widths) - 1

    # Header row
    header_cols = st.columns(col_widths, gap="small")
    for i, c in enumerate(columns):
        with header_cols[i]:
            st.markdown(
                f'<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:6px;'
                f'padding:10px 10px 12px;font-size:10px;font-weight:700;color:#515f74;margin-bottom:8px;'
                f'text-transform:uppercase;letter-spacing:0.08em;font-family:Inter,sans-serif;'
                f'line-height:1.3;white-space:nowrap;overflow:hidden;'
                f'text-align:{"center" if i == last_idx else "left"};">{c}</div>',
                unsafe_allow_html=True,
            )

    # Data rows
    for ridx, rd in enumerate(row_data):
        row_cols = st.columns(col_widths, gap="small")
        cells    = rd["cells"]
        styles   = rd.get("styles", [""] * len(cells))

        for i, (text, klass) in enumerate(cells):
            with row_cols[i]:
                # Class → font / colour mapping (kept tight & consistent)
                font_family = "Manrope, sans-serif" if klass == "name" else "Inter, sans-serif"
                font_weight = "700" if klass in ("name", "bold") else "600" if klass == "blue" else "400"
                color_default = (
                    "#171c1f" if klass == "name"
                    else "#002c98" if klass == "blue"
                    else "#515f74" if klass == "muted"
                    else "#171c1f"
                )
                font_size = "13px" if klass == "name" else "12.5px"
                inline_style = styles[i] if i < len(styles) else ""
                st.markdown(
                    f'<div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:6px;'
                    f'padding:8px 10px;min-height:38px;display:flex;align-items:center;'
                    f'font-family:{font_family};font-size:{font_size};font-weight:{font_weight};'
                    f'color:{color_default};line-height:1.3;{inline_style}">{text}</div>',
                    unsafe_allow_html=True,
                )

        # Last column = real Streamlit button (type="primary" gets blue + compact via CSS)
        with row_cols[last_idx]:
            if st.button("View",
                         key=f"{key_prefix}_{ridx}_{rd['student_name']}",
                         type="primary",
                         use_container_width=True):
                st.session_state["faculty_viewing_student"] = rd["student_name"]
                st.switch_page("pages/09b_student_view.py")


# ── guards ───────────────────────────────────────────────────────────────────
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

# ── unpack ───────────────────────────────────────────────────────────────────
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

st.session_state["faculty_student_lookup"] = {a["student_name"]: a for a in all_student_analyses}

def classify_drift(s):     return "fully_focused" if s <= 30 else "moderately_focused" if s <= 60 else "not_focused"
def classify_readiness(s): return "high" if s >= 70 else "moderate" if s >= 40 else "poor"
def classify_entropy(s):   return "highly_ordered" if s < 1.2 else "moderate" if s < 2.2 else "high_disorder"

groups = {
    "drift":     {"fully_focused": [], "moderately_focused": [], "not_focused": []},
    "readiness": {"high": [], "moderate": [], "poor": []},
    "entropy":   {"highly_ordered": [], "moderate": [], "high_disorder": []},
}
for a in all_student_analyses:
    groups["drift"][classify_drift(a["drift_score"])].append(a)
    groups["readiness"][classify_readiness(a["readiness_score"])].append(a)
    groups["entropy"][classify_entropy(a["entropy_score"])].append(a)

PW   = dict(paper_bgcolor="#ffffff", plot_bgcolor="#f6fafe", font=dict(color="#515f74", family="Inter"))
GRID = "#e2e8f0"

# =============================================================================
# FIX 1: TOP NAV — identical structure to 09_faculty.py upload page.
# col_logo | col_nav  with col_nav containing nested nav_c1, nav_c2 columns.
# This gives the EXACT same alignment as the faculty upload page.
# =============================================================================
col_logo, col_nav = st.columns([7, 3])

with col_logo:
    st.markdown(
        "<div class='fac-topbar' style='border-bottom:none;margin-bottom:0;padding-bottom:0;'>"
        "<div>"
        f"<div class='fac-logo'>SkillDrift</div>"
        f"<div class='fac-subtitle'>Batch Analysis &mdash; {faculty_name}"
        f" &nbsp;/&nbsp; {total_students} students &nbsp;/&nbsp; {today_str}</div>"
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
        if st.button("Sign Out", use_container_width=True, key="topnav_signout"):
            do_signout()

st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:0 0 22px 0;'>",
            unsafe_allow_html=True)

col_back, _ = st.columns([2, 10])
with col_back:
    if st.button("Back to Upload", key="back_to_upload"):
        st.session_state["faculty_active_view"] = "upload"
        st.switch_page("pages/09_faculty.py")

# ── tabs ─────────────────────────────────────────────────────────────────────
tab_batch, tab_placement = st.tabs(["Batch Analysis", "Placement Intelligence"])


# =============================================================================
# TAB 1 — BATCH ANALYSIS
# =============================================================================
with tab_batch:

    # Upload Validation KPIs
    st.markdown('<div class="sd-section-label">Upload Validation</div>', unsafe_allow_html=True)
    v1, v2, v3, v4 = st.columns(4, gap="medium")
    for col, lbl, val, sub, color in [
        (v1, "Files Uploaded",     files_uploaded,                       "submitted",         "#002c98"),
        (v2, "Records Valid",      valid_count,                          "passed validation", "#15803d"),
        (v3, "Skipped",            max(0, files_uploaded - valid_count), "parse errors",      "#ba1a1a"),
        (v4, "Duplicates Removed", duplicate_count,                      "kept latest",       "#d97706"),
    ]:
        with col:
            st.markdown(f"""<div class="sd-kpi">
                <div class="sd-kpi-label">{lbl}</div>
                <div class="sd-kpi-value" style="color:{color};">{val}</div>
                <div class="sd-kpi-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    if skipped_files:
        st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
        with st.expander(f"Validation issues — {len(skipped_files)} item(s)"):
            for msg in skipped_files:
                st.warning(msg)

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # Batch Statistics KPIs
    avg_drift     = summary.get("avg_drift_score", 0)
    avg_readiness = summary.get("avg_readiness_score", 0)
    avg_entropy   = summary.get("avg_entropy_score", 0)
    red_count     = summary.get("red_count", 0)
    yellow_count  = summary.get("yellow_count", 0)
    green_count   = summary.get("green_count", 0)

    st.markdown('<div class="sd-section-label">Batch Statistics</div>', unsafe_allow_html=True)
    m1, m2, m3, m4, m5, m6 = st.columns(6, gap="small")
    for col, lbl, val, color in [
        (m1, "Avg Drift",     round(avg_drift),                 "#002c98"),
        (m2, "Avg Readiness", f"{round(avg_readiness)}%",       "#15803d"),
        (m3, "Avg Entropy",   f"{round(avg_entropy,2)}b",       "#515f74"),
        (m4, "High Urgency",  red_count,                        "#ba1a1a"),
        (m5, "Med Urgency",   yellow_count,                     "#d97706"),
        (m6, "Low Urgency",   green_count,                      "#15803d"),
    ]:
        with col:
            st.markdown(f"""<div class="sd-kpi">
                <div class="sd-kpi-label">{lbl}</div>
                <div class="sd-kpi-value" style="color:{color};">{val}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1.25rem;'></div>", unsafe_allow_html=True)

    # Charts row
    cl, cr = st.columns(2, gap="large")
    with cl:
        st.markdown("<div style='font-family:Manrope,sans-serif;font-weight:700;font-size:0.95rem;color:#171c1f;margin-bottom:3px;'>Urgency Distribution</div>"
                    "<div style='font-size:0.8rem;color:#515f74;margin-bottom:12px;'>Students by placement urgency level</div>",
                    unsafe_allow_html=True)
        fig_pie = go.Figure(go.Pie(
            labels=["High Urgency", "Medium Urgency", "Low Urgency"],
            values=[red_count, yellow_count, green_count],
            marker=dict(colors=["#ba1a1a", "#d97706", "#15803d"], line=dict(color="#ffffff", width=2)),
            hole=0.56, textfont=dict(color="#ffffff", size=10, family="Inter"),
            hovertemplate="<b>%{label}</b><br>%{value} students (%{percent})<extra></extra>",
        ))
        fig_pie.update_layout(**PW, showlegend=True,
            legend=dict(bgcolor="#ffffff", font=dict(color="#515f74", size=10, family="Inter"),
                        orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
            margin=dict(t=10, b=55, l=10, r=10), height=280)
        fig_pie.add_annotation(text=f"<b>{total_students}</b>", x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color="#171c1f", family="Manrope"))
        st.plotly_chart(fig_pie, use_container_width=True, key="batch_urgency_pie")

    with cr:
        st.markdown("<div style='font-family:Manrope,sans-serif;font-weight:700;font-size:0.95rem;color:#171c1f;margin-bottom:3px;'>Career Track Distribution</div>"
                    "<div style='font-size:0.8rem;color:#515f74;margin-bottom:12px;'>Students matched to each career track</div>",
                    unsafe_allow_html=True)
        track_dist = summary.get("track_distribution", {})
        if track_dist:
            sorted_td = sorted(track_dist.items(), key=lambda x: x[1])
            fig_track = go.Figure(go.Bar(
                x=[v for _, v in sorted_td], y=[k for k, _ in sorted_td], orientation="h",
                marker=dict(color=[v for _, v in sorted_td],
                            colorscale=[[0,"#c7d5f5"],[0.5,"#4b72e0"],[1,"#002c98"]],
                            showscale=False, line=dict(color="rgba(0,0,0,0)")),
                text=[str(v) for _, v in sorted_td], textposition="outside",
                textfont=dict(color="#515f74", size=10, family="Inter"),
                hovertemplate="%{y}<br>%{x} students<extra></extra>",
            ))
            fig_track.update_layout(**PW,
                xaxis=dict(gridcolor=GRID, color="#515f74", zeroline=False, dtick=1),
                yaxis=dict(color="#171c1f", showgrid=False, automargin=True),
                margin=dict(t=10, b=10, l=10, r=50), height=280)
            st.plotly_chart(fig_track, use_container_width=True, key="batch_track_dist")

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # Top missing skills
    st.markdown('<div class="sd-section-label">Skills Most Commonly Missing</div>', unsafe_allow_html=True)
    top_missing = summary.get("top_missing_skills", [])
    if top_missing:
        max_c = top_missing[0][1] if top_missing else 1
        for rank, (skill, count) in enumerate(top_missing, start=1):
            pct  = round((count / total_students) * 100) if total_students else 0
            fill = round((count / max_c) * 100)
            fc   = "#ba1a1a" if rank == 1 else "#d97706" if rank <= 3 else "#002c98"
            st.markdown(f"""<div class="skill-row">
                <div class="skill-row-top">
                    <span class="skill-name"><span style="color:{fc};font-size:0.7rem;font-weight:700;">#{rank}</span>&nbsp;{skill}</span>
                    <span class="skill-pct">{count} students &nbsp;·&nbsp; {pct}%</span>
                </div>
                <div class="skill-track"><div class="skill-fill" style="width:{fill}%;background:{fc};"></div></div>
            </div>""", unsafe_allow_html=True)

        top_name = top_missing[0][0]
        top_pct  = round((top_missing[0][1] / total_students) * 100) if total_students else 0
        st.markdown(f"""<div style="background:#f0f4ff;border:1px solid #c7d5f5;border-radius:10px;
                    padding:14px 18px;margin-top:8px;font-family:Inter,sans-serif;">
            <div style="font-size:0.7rem;font-weight:700;color:#002c98;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;">Recommendation</div>
            <div style="font-size:0.87rem;color:#171c1f;line-height:1.55;">{top_pct}% of students are missing <strong>{top_name}</strong>. A focused workshop before placement season is recommended.</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # Skill Coverage Heatmap
    st.markdown('<div class="sd-section-label">Skill Coverage Heatmap</div>', unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.82rem;color:#515f74;margin-bottom:10px;font-family:Inter,sans-serif;'>Green = Proficient &nbsp;&nbsp; Amber = Beginner &nbsp;&nbsp; Red = Missing</div>",
                unsafe_allow_html=True)

    all_skills_set = set()
    for a in all_student_analyses:
        all_skills_set.update(a["verified_skills"].keys())
    all_skills_list = sorted(list(all_skills_set))

    hmap_data, hmap_labels = [], []
    for a in all_student_analyses:
        hmap_labels.append(a["student_name"][:20])
        row = []
        for sk in all_skills_list:
            lv = a["verified_skills"].get(sk, None)
            row.append(2 if lv in ("Advanced", "Intermediate") else 1 if lv == "Beginner" else 0)
        hmap_data.append(row)

    hmap_matrix = pd.DataFrame(hmap_data, index=hmap_labels, columns=all_skills_list)
    if not hmap_matrix.empty:
        n_s = len(hmap_matrix); n_k = len(all_skills_list)
        fw = max(10, min(n_k * 0.55, 32)); fh = max(4, min(n_s * 0.5, 18))
        fig_h, ax = plt.subplots(figsize=(fw, fh))
        fig_h.patch.set_facecolor("#ffffff"); ax.set_facecolor("#ffffff")
        cmap = mcolors.ListedColormap(["#ffdad6", "#fef3c7", "#dcfce7"])
        norm = mcolors.BoundaryNorm([-0.5, 0.5, 1.5, 2.5], cmap.N)
        sns.heatmap(hmap_matrix, ax=ax, cmap=cmap, norm=norm, linewidths=0.4,
                    linecolor="#f6fafe", cbar=True, cbar_kws={"ticks":[0,1,2],"label":"Skill Level"})
        cbar = ax.collections[0].colorbar
        cbar.set_ticklabels(["Missing","Beginner","Proficient"])
        cbar.ax.yaxis.label.set_color("#515f74"); cbar.ax.tick_params(colors="#515f74", labelsize=8)
        cbar.outline.set_edgecolor("#e2e8f0")
        ax.set_xlabel("Skills", color="#515f74", fontsize=9, labelpad=8)
        ax.set_ylabel("Students", color="#515f74", fontsize=9, labelpad=8)
        ax.tick_params(colors="#171c1f", labelsize=7.5)
        ax.set_title(f"Skill Coverage — {n_s} Students × {n_k} Skills", color="#171c1f", fontsize=11, pad=14, fontweight="bold")
        for spine in ax.spines.values(): spine.set_edgecolor("#e2e8f0")
        plt.xticks(rotation=45, ha="right", fontsize=7.5, color="#171c1f")
        plt.yticks(fontsize=8, color="#171c1f")
        plt.tight_layout()
        st.pyplot(fig_h, use_container_width=True)
        plt.close(fig_h)

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # =========================================================================
    # FIX 2: INDIVIDUAL STUDENT RECORDS
    # View button is now in the LAST column of each row (no separate button row).
    # Uses _table_with_view_buttons → real Streamlit buttons inside a styled
    # column-based table, so st.switch_page works natively.
    # =========================================================================
    st.markdown('<div class="sd-section-label">Individual Student Records</div>', unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.82rem;color:#515f74;margin-top:-8px;margin-bottom:12px;font-family:Inter,sans-serif;'>"
                "Click <strong>View</strong> in any row to open that student's full analysis.</div>",
                unsafe_allow_html=True)

    # Build row data for the new table-with-buttons helper
    rec_rows = []
    for a in all_student_analyses:
        dv  = round(a["drift_score"])
        rv  = round(a["readiness_score"])
        urg = a["urgency_level"]
        dc  = "#15803d" if dv <= 30 else "#d97706" if dv <= 60 else "#ba1a1a"
        rc  = "#15803d" if rv >= 70  else "#d97706" if rv >= 40  else "#ba1a1a"
        uc  = "#15803d" if urg == "Green" else "#d97706" if urg == "Yellow" else "#ba1a1a"

        rec_rows.append({
            "cells": [
                (a["student_name"],                "name"),   # Student
                (str(a["semester"]),               "muted"),  # Sem
                (str(dv),                          "bold"),   # Drift
                (a["drift_label"],                 ""),       # Status
                (a["best_track"],                  "blue"),   # Best Track
                (f"{rv}%",                         "bold"),   # Readiness
                (urg,                              "bold"),   # Urgency
            ],
            "styles": [
                "",                              # name
                "",                              # sem
                f"color:{dc};",                  # drift coloured
                "",                              # status
                "",                              # track (already blue via class)
                f"color:{rc};",                  # readiness coloured
                f"color:{uc};",                  # urgency coloured
            ],
            "student_name": a["student_name"],
        })

    _table_with_view_buttons(
        columns    =["Student", "Sem", "Drift", "Status", "Best Track", "Readiness", "Urgency", "View"],
        col_widths =[2.6,        1,     1.2,     2.4,      2.4,         1.6,         1.5,       1.3],
        row_data   =rec_rows,
        key_prefix ="rec_view",
    )

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # Export
    st.markdown('<div class="sd-section-label">Export</div>', unsafe_allow_html=True)
    csv_buf = io.StringIO()
    merged_df.to_csv(csv_buf, index=False)
    col_dl, col_info = st.columns([3, 5], gap="medium")
    with col_dl:
        st.download_button(label="Download Full Batch Report (CSV)",
            data=csv_buf.getvalue().encode("utf-8"),
            file_name=f"SkillDrift_Batch_{datetime.now().strftime('%Y_%m_%d')}.csv",
            mime="text/csv", type="primary", key="dl_batch")
    with col_info:
        st.markdown(f"<div style='font-size:0.82rem;color:#515f74;font-family:Inter,sans-serif;padding-top:4px;'>"
                    f"{total_students} students &nbsp;·&nbsp; Generated {datetime.now().strftime('%d %b %Y, %I:%M %p')}</div>",
                    unsafe_allow_html=True)


# =============================================================================
# TAB 2 — PLACEMENT INTELLIGENCE
# =============================================================================
with tab_placement:

    st.markdown(f"""<div class="sd-card" style="margin-bottom:20px;">
        <div style="font-family:Manrope,sans-serif;font-size:1.05rem;font-weight:700;color:#171c1f;margin-bottom:4px;">Placement Intelligence</div>
        <div style="font-size:0.82rem;color:#515f74;font-family:Inter,sans-serif;">{total_students} students classified across three readiness dimensions. Expand any group to inspect individual profiles.</div>
    </div>""", unsafe_allow_html=True)

    placement_ready = len(groups["readiness"]["high"])
    fully_focused   = len(groups["drift"]["fully_focused"])
    high_disorder   = len(groups["entropy"]["high_disorder"])
    high_urgency    = sum(1 for a in all_student_analyses if a["urgency_level"] == "Red")

    pk1, pk2, pk3, pk4 = st.columns(4, gap="medium")
    for col, lbl, val, sub, color in [
        (pk1,"Placement Ready",  placement_ready, f"{round(placement_ready/total_students*100) if total_students else 0}% readiness 70+","#15803d"),
        (pk2,"Fully Focused",    fully_focused,   f"{round(fully_focused/total_students*100) if total_students else 0}% drift 0–30",     "#002c98"),
        (pk3,"Skill Disorder",   high_disorder,   f"{round(high_disorder/total_students*100) if total_students else 0}% entropy 2.2+",   "#ba1a1a"),
        (pk4,"Urgent Attention", high_urgency,    "semester 5 and above",                                                                "#d97706"),
    ]:
        with col:
            st.markdown(f"""<div class="sd-kpi">
                <div class="sd-kpi-label">{lbl}</div>
                <div class="sd-kpi-value" style="color:{color};">{val}</div>
                <div class="sd-kpi-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

    # Three-dimension grouped bar
    st.markdown('<div class="sd-section-label">Three-Dimension Overview</div>', unsafe_allow_html=True)
    drift_v     = [len(groups["drift"]["fully_focused"]),    len(groups["drift"]["moderately_focused"]),    len(groups["drift"]["not_focused"])]
    readiness_v = [len(groups["readiness"]["high"]),         len(groups["readiness"]["moderate"]),          len(groups["readiness"]["poor"])]
    entropy_v   = [len(groups["entropy"]["highly_ordered"]), len(groups["entropy"]["moderate"]),            len(groups["entropy"]["high_disorder"])]
    cats = ["Skill Drift", "Readiness", "Entropy"]
    fig_ov = go.Figure()
    for name, vals, color in [("Good",[drift_v[0],readiness_v[0],entropy_v[0]],"#15803d"),
                               ("Moderate",[drift_v[1],readiness_v[1],entropy_v[1]],"#d97706"),
                               ("Needs Attention",[drift_v[2],readiness_v[2],entropy_v[2]],"#ba1a1a")]:
        fig_ov.add_trace(go.Bar(name=name, x=cats, y=vals,
            marker=dict(color=color, line=dict(color="#ffffff", width=1)),
            text=vals, textposition="outside", textfont=dict(color="#515f74", size=10, family="Inter"),
            hovertemplate=f"<b>{name}</b><br>%{{y}} students<extra>%{{x}}</extra>"))
    fig_ov.update_layout(barmode="group", **PW,
        xaxis=dict(color="#171c1f", tickfont=dict(size=11, family="Manrope"), showgrid=False),
        yaxis=dict(title="Students", gridcolor=GRID, color="#515f74", zeroline=False, dtick=1),
        legend=dict(orientation="h", yanchor="bottom", y=-0.32, bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#515f74", size=10, family="Inter")),
        margin=dict(t=30, b=75, l=40, r=20), height=300)
    st.plotly_chart(fig_ov, use_container_width=True, key="pl_three_dim")

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # Drift vs Readiness scatter
    st.markdown('<div class="sd-section-label">Drift vs Readiness — Student Map</div>', unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.82rem;color:#515f74;margin-bottom:10px;font-family:Inter,sans-serif;'>Each dot is one student. Ideal zone = low drift + high readiness. Dot size = semester.</div>",
                unsafe_allow_html=True)
    if all_student_analyses:
        sdf = pd.DataFrame([{"name":a["student_name"],"drift":round(a["drift_score"]),
                              "readiness":round(a["readiness_score"]),"urgency":a["urgency_level"],
                              "semester":a["semester"]} for a in all_student_analyses])
        fig_sc = go.Figure()
        for uv, uc in {"Red":"#ba1a1a","Yellow":"#d97706","Green":"#15803d"}.items():
            sub = sdf[sdf["urgency"]==uv]
            if sub.empty: continue
            fig_sc.add_trace(go.Scatter(x=sub["drift"], y=sub["readiness"], mode="markers+text",
                name=f"{uv} Urgency",
                marker=dict(color=uc, size=sub["semester"]*3+8, opacity=0.85, line=dict(color="#ffffff",width=1.5)),
                text=sub["name"], textposition="top center", textfont=dict(size=8, color="#515f74", family="Inter"),
                hovertemplate="<b>%{text}</b><br>Drift: %{x}<br>Readiness: %{y}%<extra></extra>"))
        fig_sc.add_shape(type="rect",x0=0,y0=70,x1=30,y1=100, fillcolor="rgba(21,128,61,0.06)",
            line=dict(color="rgba(21,128,61,0.3)",width=1,dash="dot"))
        fig_sc.add_annotation(x=15,y=85,text="Ideal Zone",showarrow=False,
            font=dict(color="rgba(21,128,61,0.6)",size=9,family="Inter"))
        fig_sc.update_layout(**PW,
            xaxis=dict(title="Drift Score (lower = more focused)",gridcolor=GRID,color="#515f74",range=[-5,105],zeroline=False),
            yaxis=dict(title="Readiness (%)",gridcolor=GRID,color="#515f74",range=[-5,105],zeroline=False),
            legend=dict(bgcolor="#ffffff",bordercolor=GRID,borderwidth=1,font=dict(color="#515f74",size=10,family="Inter")),
            margin=dict(t=20,b=40,l=40,r=20), height=400)
        st.plotly_chart(fig_sc, use_container_width=True, key="pl_scatter")

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # Readiness per student
    st.markdown('<div class="sd-section-label">Readiness Score per Student</div>', unsafe_allow_html=True)
    if all_student_analyses:
        ss   = sorted(all_student_analyses, key=lambda a: a["readiness_score"])
        rn   = [a["student_name"] for a in ss]
        rv2  = [round(a["readiness_score"]) for a in ss]
        rc2  = ["#15803d" if v>=70 else "#d97706" if v>=40 else "#ba1a1a" for v in rv2]
        fig_rb = go.Figure(go.Bar(x=rv2, y=rn, orientation="h",
            marker=dict(color=rc2, line=dict(color="#ffffff",width=0.5)),
            text=[f"{v}%" for v in rv2], textposition="outside",
            textfont=dict(color="#515f74",size=9,family="Inter"),
            hovertemplate="%{y}<br>Readiness: %{x}%<extra></extra>"))
        fig_rb.add_vline(x=70, line_dash="dash", line_color="#15803d", line_width=1.5,
            annotation=dict(text="Target (70%)", font=dict(color="#15803d",size=9,family="Inter"),yanchor="top"))
        fig_rb.update_layout(**PW,
            xaxis=dict(title="Readiness %",gridcolor=GRID,color="#515f74",range=[0,120],zeroline=False),
            yaxis=dict(color="#171c1f",showgrid=False,automargin=True,tickfont=dict(size=9)),
            showlegend=False, margin=dict(t=20,b=40,l=10,r=60), height=max(250,len(rn)*28))
        st.plotly_chart(fig_rb, use_container_width=True, key="pl_readiness_bar")

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # =========================================================================
    # FIX 3: render_group — View button now lives in the LAST column of every
    # row (no separate button row below). Uses the same _table_with_view_buttons
    # helper as Fix 2, so styling, alignment and font sizes are perfectly
    # consistent across the page.
    # =========================================================================
    def render_group(matrix_key, group_key, label, range_desc, total):
        student_list = groups[matrix_key][group_key]
        count = len(student_list)
        pct   = round((count / total) * 100) if total > 0 else 0

        with st.expander(f"{label}  —  {count} student{'s' if count!=1 else ''}  ({pct}%)  ·  {range_desc}", expanded=False):
            if not student_list:
                st.markdown("<span style='color:#515f74;font-size:0.82rem;font-family:Inter,sans-serif;'>No students in this group.</span>", unsafe_allow_html=True)
                return

            # Build row data
            grp_rows = []
            for s in student_list:
                rc = "#15803d" if s["readiness_score"]>=70 else "#d97706" if s["readiness_score"]>=40 else "#ba1a1a"
                dc = "#15803d" if s["drift_score"]<=30     else "#d97706" if s["drift_score"]<=60     else "#ba1a1a"
                grp_rows.append({
                    "cells": [
                        (s["student_name"],                  "name"),
                        (str(s["semester"]),                 "muted"),
                        (str(round(s["drift_score"])),       "bold"),
                        (f"{round(s['readiness_score'])}%",  "bold"),
                        (s["best_track"],                    "blue"),
                    ],
                    "styles": [
                        "",
                        "",
                        f"color:{dc};",
                        f"color:{rc};",
                        "",
                    ],
                    "student_name": s["student_name"],
                })

            _table_with_view_buttons(
                columns    =["Name", "Sem", "Drift", "Readiness", "Track", "View"],
                col_widths =[2.2,    1.1,   1.2,     1.6,         2.5,     1.1],
                row_data   =grp_rows,
                key_prefix =f"pl_{matrix_key}_{group_key}",
            )

    # Matrix 1 — Drift
    mx1l, mx1r = st.columns([2.2, 5.8])
    with mx1l:
        st.markdown("""<div class="mx-card">
            <div class="mx-num">Matrix 01</div>
            <div class="mx-title">Skill Drift</div>
            <div class="mx-body">How scattered skills are across 8 career tracks.<br><br>
                <span class="g">Fully Focused</span> — drift 0 to 30<br>
                <span class="a">Moderately Focused</span> — drift 31 to 60<br>
                <span class="r">Not Focused</span> — drift 61 to 100
            </div></div>""", unsafe_allow_html=True)
        dv = [len(groups["drift"]["fully_focused"]), len(groups["drift"]["moderately_focused"]), len(groups["drift"]["not_focused"])]
        fig_d = go.Figure(go.Pie(labels=["Fully Focused","Moderately Focused","Not Focused"],values=dv,
            marker=dict(colors=["#15803d","#d97706","#ba1a1a"],line=dict(color="#ffffff",width=2)),
            hole=0.65,textinfo="none",hovertemplate="%{label}<br>%{value} students<extra></extra>"))
        fig_d.update_layout(**PW,showlegend=False,margin=dict(t=10,b=10,l=10,r=10),height=160)
        st.plotly_chart(fig_d, use_container_width=True, key="mx_donut_drift")
    with mx1r:
        st.markdown('<div class="sd-section-label">Groups</div>', unsafe_allow_html=True)
        render_group("drift","fully_focused",     "Fully Focused",     "Drift 0 to 30",   total_students)
        render_group("drift","moderately_focused","Moderately Focused","Drift 31 to 60",  total_students)
        render_group("drift","not_focused",       "Not Focused",       "Drift 61 to 100", total_students)

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # Matrix 2 — Readiness
    mx2l, mx2r = st.columns([2.2, 5.8])
    with mx2l:
        st.markdown("""<div class="mx-card">
            <div class="mx-num">Matrix 02</div>
            <div class="mx-title">Placement Readiness</div>
            <div class="mx-body">Verified skills matched against job posting frequency.<br><br>
                <span class="g">High</span> — readiness 70% or above<br>
                <span class="a">Moderate</span> — readiness 40 to 69%<br>
                <span class="r">Poor</span> — readiness below 40%
            </div></div>""", unsafe_allow_html=True)
        rv = [len(groups["readiness"]["high"]),len(groups["readiness"]["moderate"]),len(groups["readiness"]["poor"])]
        fig_r = go.Figure(go.Pie(labels=["High","Moderate","Poor"],values=rv,
            marker=dict(colors=["#15803d","#d97706","#ba1a1a"],line=dict(color="#ffffff",width=2)),
            hole=0.65,textinfo="none",hovertemplate="%{label}<br>%{value} students<extra></extra>"))
        fig_r.update_layout(**PW,showlegend=False,margin=dict(t=10,b=10,l=10,r=10),height=160)
        st.plotly_chart(fig_r, use_container_width=True, key="mx_donut_readiness")
    with mx2r:
        st.markdown('<div class="sd-section-label">Groups</div>', unsafe_allow_html=True)
        render_group("readiness","high",    "High Readiness",    "Readiness 70% or above",total_students)
        render_group("readiness","moderate","Moderate Readiness","Readiness 40 to 69%",   total_students)
        render_group("readiness","poor",    "Poor Readiness",    "Readiness below 40%",   total_students)

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # Matrix 3 — Entropy
    mx3l, mx3r = st.columns([2.2, 5.8])
    with mx3l:
        st.markdown("""<div class="mx-card">
            <div class="mx-num">Matrix 03</div>
            <div class="mx-title">Skill Entropy</div>
            <div class="mx-body">Shannon Entropy measures disorder in skill distribution.<br><br>
                <span class="g">Highly Ordered</span> — below 1.2 bits<br>
                <span class="a">Moderate</span> — 1.2 to 2.2 bits<br>
                <span class="r">High Disorder</span> — above 2.2 bits
            </div></div>""", unsafe_allow_html=True)
        ev = [len(groups["entropy"]["highly_ordered"]),len(groups["entropy"]["moderate"]),len(groups["entropy"]["high_disorder"])]
        fig_e = go.Figure(go.Pie(labels=["Highly Ordered","Moderate","High Disorder"],values=ev,
            marker=dict(colors=["#15803d","#d97706","#ba1a1a"],line=dict(color="#ffffff",width=2)),
            hole=0.65,textinfo="none",hovertemplate="%{label}<br>%{value} students<extra></extra>"))
        fig_e.update_layout(**PW,showlegend=False,margin=dict(t=10,b=10,l=10,r=10),height=160)
        st.plotly_chart(fig_e, use_container_width=True, key="mx_donut_entropy")
    with mx3r:
        st.markdown('<div class="sd-section-label">Groups</div>', unsafe_allow_html=True)
        render_group("entropy","highly_ordered","Highly Ordered","Entropy below 1.2 bits", total_students)
        render_group("entropy","moderate",      "Moderate",      "Entropy 1.2 to 2.2 bits",total_students)
        render_group("entropy","high_disorder", "High Disorder", "Entropy above 2.2 bits",  total_students)

    st.markdown('<hr class="sd-divider">', unsafe_allow_html=True)

    # Complete classification table
    st.markdown('<div class="sd-section-label">Complete Classification Table</div>', unsafe_allow_html=True)
    DL = {"fully_focused":"Fully Focused","moderately_focused":"Mod. Focused","not_focused":"Not Focused"}
    RL = {"high":"High","moderate":"Moderate","poor":"Poor"}
    EL = {"highly_ordered":"Highly Ordered","moderate":"Moderate","high_disorder":"High Disorder"}

    rows = []
    for a in all_student_analyses:
        rows.append({"Student":a["student_name"],"Sem":a["semester"],
            "Drift":round(a["drift_score"]),"Drift Group":DL[classify_drift(a["drift_score"])],
            "Readiness %":round(a["readiness_score"]),"Readiness Group":RL[classify_readiness(a["readiness_score"])],
            "Entropy":round(a["entropy_score"],2),"Entropy Group":EL[classify_entropy(a["entropy_score"])],
            "Best Track":a["best_track"],"Urgency":a["urgency_level"]})
    summary_df = pd.DataFrame(rows)

    # --- Colorful Classification Table ---
    def _drift_group_color(g):
        return {"Fully Focused":"#15803d","Mod. Focused":"#d97706","Not Focused":"#ba1a1a"}.get(g,"#515f74")
    def _readiness_group_color(g):
        return {"High":"#15803d","Moderate":"#d97706","Poor":"#ba1a1a"}.get(g,"#515f74")
    def _entropy_group_color(g):
        return {"Highly Ordered":"#15803d","Moderate":"#d97706","High Disorder":"#ba1a1a"}.get(g,"#515f74")
    def _readiness_pct_color(v):
        return "#15803d" if v >= 70 else "#d97706" if v >= 40 else "#ba1a1a"
    def _drift_val_color(v):
        return "#15803d" if v <= 30 else "#d97706" if v <= 60 else "#ba1a1a"
    def _urgency_color(u):
        return {"Green":"#15803d","Yellow":"#d97706","Red":"#ba1a1a"}.get(u,"#515f74")
    def _urgency_bg(u):
        return {"Green":"#f0fdf4","Yellow":"#fffbeb","Red":"#fff5f5"}.get(u,"#f8fafc")
    def _drift_group_bg(g):
        return {"Fully Focused":"#f0fdf4","Mod. Focused":"#fffbeb","Not Focused":"#fff5f5"}.get(g,"#f8fafc")
    def _readiness_group_bg(g):
        return {"High":"#f0fdf4","Moderate":"#fffbeb","Poor":"#fff5f5"}.get(g,"#f8fafc")
    def _entropy_group_bg(g):
        return {"Highly Ordered":"#f0fdf4","Moderate":"#fffbeb","High Disorder":"#fff5f5"}.get(g,"#f8fafc")

    tbl_rows_html = []
    for r in rows:
        dgc  = _drift_group_color(r["Drift Group"])
        dgb  = _drift_group_bg(r["Drift Group"])
        rgc  = _readiness_group_color(r["Readiness Group"])
        rgb_ = _readiness_group_bg(r["Readiness Group"])
        egc  = _entropy_group_color(r["Entropy Group"])
        egb  = _entropy_group_bg(r["Entropy Group"])
        rpc  = _readiness_pct_color(r["Readiness %"])
        dvc  = _drift_val_color(r["Drift"])
        uc   = _urgency_color(r["Urgency"])
        ub   = _urgency_bg(r["Urgency"])
        tbl_rows_html.append(f"""<tr>
            <td class="n">{r["Student"]}</td>
            <td class="m" style="text-align:center;">{r["Sem"]}</td>
            <td style="font-weight:700;color:{dvc};text-align:center;">{r["Drift"]}</td>
            <td style="background:{dgb};"><span style="color:{dgc};font-weight:700;font-size:11.5px;">{r["Drift Group"]}</span></td>
            <td style="font-weight:700;color:{rpc};text-align:center;">{r["Readiness %"]}%</td>
            <td style="background:{rgb_};"><span style="color:{rgc};font-weight:700;font-size:11.5px;">{r["Readiness Group"]}</span></td>
            <td class="m" style="text-align:center;">{r["Entropy"]}</td>
            <td style="background:{egb};"><span style="color:{egc};font-weight:700;font-size:11.5px;">{r["Entropy Group"]}</span></td>
            <td class="b">{r["Best Track"]}</td>
            <td style="background:{ub};text-align:center;"><span style="color:{uc};font-weight:700;font-size:11.5px;">{r["Urgency"]}</span></td>
        </tr>""")

    thead_html = """<tr>
        <th>Student</th><th>Sem</th><th>Drift</th><th>Drift Group</th>
        <th>Readiness %</th><th>Readiness Group</th><th>Entropy</th>
        <th>Entropy Group</th><th>Best Track</th><th>Urgency</th>
    </tr>"""

    full_table_html = f"""
    <!DOCTYPE html><html><head>
    <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@700;800&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
      * {{ box-sizing:border-box; margin:0; padding:0; }}
      html, body {{ background:transparent; font-family:'Inter',sans-serif; overflow-x:hidden; }}
      table {{
        width:100%; border-collapse:collapse;
        background:#ffffff; border:1px solid #e2e8f0;
        border-radius:12px; overflow:hidden; font-size:11.5px;
        table-layout:fixed;
      }}
      thead tr {{ background:#f8fafc; }}
      thead th {{
        padding:8px 7px; text-align:left; font-size:9.5px; font-weight:700;
        color:#515f74; text-transform:uppercase; letter-spacing:0.07em;
        border-bottom:1.5px solid #e2e8f0; border-right:1px solid #e2e8f0;
        white-space:nowrap; font-family:'Inter',sans-serif; overflow:hidden;
      }}
      thead th:last-child {{ border-right:none; }}
      tbody tr {{ border-bottom:1px solid #e2e8f0; transition:background 0.1s; }}
      tbody tr:last-child {{ border-bottom:none; }}
      tbody tr:hover {{ background:#f6fafe !important; }}
      tbody td {{
        padding:8px 7px; vertical-align:middle;
        border-right:1px solid #e2e8f0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
      }}
      tbody td:last-child {{ border-right:none; }}
      .n  {{ font-family:'Manrope',sans-serif; font-weight:700; font-size:12px; color:#171c1f; white-space:nowrap; }}
      .m  {{ color:#515f74; }}
      .b  {{ color:#002c98; font-weight:600; }}
      col.c-student  {{ width:16%; }}
      col.c-sem      {{ width:5%; }}
      col.c-drift    {{ width:6%; }}
      col.c-dgroup   {{ width:11%; }}
      col.c-rpct     {{ width:9%; }}
      col.c-rgroup   {{ width:11%; }}
      col.c-entropy  {{ width:7%; }}
      col.c-egroup   {{ width:13%; }}
      col.c-track    {{ width:13%; }}
      col.c-urgency  {{ width:9%; }}
    </style></head><body>
    <table>
      <colgroup>
        <col class="c-student"><col class="c-sem"><col class="c-drift"><col class="c-dgroup">
        <col class="c-rpct"><col class="c-rgroup"><col class="c-entropy"><col class="c-egroup">
        <col class="c-track"><col class="c-urgency">
      </colgroup>
      <thead>{thead_html}</thead>
    <tbody>{"".join(tbl_rows_html)}</tbody></table>
    </body></html>"""

    tbl_height = 44 + len(rows) * 44 + 10
    components.html(full_table_html, height=tbl_height, scrolling=True)

    st.markdown("<div style='height:0.75rem;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="sd-section-label">Export</div>', unsafe_allow_html=True)
    pl_buf = io.StringIO()
    summary_df.to_csv(pl_buf, index=False)
    st.download_button(label="Download Placement Classification Report (CSV)",
        data=pl_buf.getvalue().encode("utf-8"),
        file_name=f"SkillDrift_Placement_{datetime.now().strftime('%Y_%m_%d')}.csv",
        mime="text/csv", type="primary", key="dl_placement")
    st.markdown("<div style='font-size:0.8rem;color:#515f74;margin-top:6px;font-family:Inter,sans-serif;'>Drift group, readiness group, entropy group, best track, urgency for every student.</div>",
                unsafe_allow_html=True)