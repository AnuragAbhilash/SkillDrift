# pages/09b_student_view.py
# ─────────────────────────────────────────────────────────────────────────────
# Faculty: Per-Student Dashboard View
# Opened from pages/09_faculty.py when "View Dashboard" is clicked.
# Renders a read-only version of all 8 student analysis windows
# using data already computed in brain.py by the batch processor.
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="SkillDrift — Student View",
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
    .block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1080px; }
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

    .metric-card {
        background: #FFFFFF; border: 1px solid #D2D2D7; border-radius: 12px;
        padding: 1rem 1.2rem; height: 100%;
    }
    .metric-label { font-size: 0.75rem; color: #86868B; margin-bottom: 4px; }
    .metric-value { font-size: 1.5rem; font-weight: 700; color: #1D1D1F; line-height: 1.2; }
    .metric-sub   { font-size: 0.8rem;  color: #86868B; margin-top: 4px; }

    .section-card {
        background: #FFFFFF; border: 1px solid #D2D2D7; border-radius: 14px;
        padding: 1.25rem 1.4rem; margin-bottom: 1rem;
    }
    .row-item {
        display: flex; justify-content: space-between; align-items: center;
        padding: 0.5rem 0; border-bottom: 1px solid #F0F0F0;
    }
    .row-label { color: #86868B; font-size: 0.88rem; }
    .row-val   { color: #1D1D1F; font-weight: 600; font-size: 0.88rem; text-align: right; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# GUARD: must come from the faculty dashboard
# ─────────────────────────────────────────────────────────────────────────────

if not st.session_state.get("faculty_logged_in"):
    st.error("Access denied. Please log in via the Faculty Dashboard.")
    if st.button("Go to Faculty Login"):
        st.switch_page("pages/09_faculty.py")
    st.stop()

selected_name = st.session_state.get("faculty_viewing_student")
student_lookup = st.session_state.get("faculty_student_lookup", {})

if not selected_name or selected_name not in student_lookup:
    st.warning("No student selected. Go back to the Faculty Dashboard and click 'View Dashboard'.")
    if st.button("← Back to Faculty Dashboard"):
        st.switch_page("pages/09_faculty.py")
    st.stop()

# Pull the full analysis dict (computed by brain.compute_full_student_analysis)
a = student_lookup[selected_name]

# Unpack everything
student_name    = a["student_name"]
semester        = a["semester"]
verified_skills = a["verified_skills"]
drift_score     = a["drift_score"]
drift_label     = a["drift_label"]
track_counts    = a["track_counts"]
entropy_score   = a["entropy_score"]
entropy_label   = a["entropy_label"]
career_matches  = a["career_matches"]
best_track      = a["best_track"]
match_pct       = a["match_pct"]
readiness_score = a["readiness_score"]
next_skill_info = a["next_skill_info"]
urgency_info    = a["urgency_info"]
focus_debt_info = a["focus_debt_info"]
peer_info       = a["peer_info"]

next_skill       = next_skill_info.get("skill", "N/A") if next_skill_info else "N/A"
urgency_level    = urgency_info.get("urgency_level", "Unknown") if urgency_info else "Unknown"
urgency_color    = urgency_info.get("urgency_color", "#6C63FF") if urgency_info else "#6C63FF"
urgency_message  = urgency_info.get("urgency_message", "") if urgency_info else ""
days_remaining   = urgency_info.get("days_remaining", 0) if urgency_info else 0
focus_debt_hours = focus_debt_info.get("focus_debt_hours", 0) if focus_debt_info else 0
days_to_recover  = focus_debt_info.get("days_to_recover", 0) if focus_debt_info else 0
distraction_skills = focus_debt_info.get("distraction_skills", []) if focus_debt_info else []
on_track_skills    = focus_debt_info.get("on_track_skills", []) if focus_debt_info else []
student_rate     = peer_info.get("student_placement_rate", "N/A") if peer_info else "N/A"
focused_rate     = peer_info.get("focused_placement_rate", "N/A") if peer_info else "N/A"
survival_rates   = peer_info.get("survival_rates", {}) if peer_info else {}
best_match_data  = career_matches[0] if career_matches else {}
missing_skills   = best_match_data.get("missing_skills", [])

URGENCY_COLORS = {"Red": "#FF3B30", "Yellow": "#FF9500", "Green": "#34C759"}
urgency_badge_color = URGENCY_COLORS.get(urgency_level, "#6C63FF")

# ─────────────────────────────────────────────────────────────────────────────
# NAVIGATION BAR
# ─────────────────────────────────────────────────────────────────────────────

nav_col, title_col = st.columns([2, 8])
with nav_col:
    if st.button("← All Students", use_container_width=True):
        st.switch_page("pages/09_faculty.py")

st.markdown(f"""
<div style="background:#FFFFFF; border:2px solid #6C63FF; border-radius:14px;
            padding:1rem 1.4rem; margin-bottom:1.5rem;
            display:flex; align-items:center; gap:1rem;">
    <div style="width:44px; height:44px; border-radius:50%; background:#F0EFFF;
                display:flex; align-items:center; justify-content:center; flex-shrink:0;">
        <svg width="26" height="26" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
            <circle cx="40" cy="28" r="18" fill="#6C63FF"/>
            <ellipse cx="40" cy="66" rx="26" ry="17" fill="#6C63FF"/>
        </svg>
    </div>
    <div>
        <div style="font-size:1.3rem; font-weight:700; color:#1D1D1F;">{student_name}</div>
        <div style="color:#86868B; font-size:0.82rem;">
            Semester {semester} &nbsp;·&nbsp;
            {len(verified_skills)} verified skills &nbsp;·&nbsp;
            <span style="background:{urgency_badge_color}22; color:{urgency_badge_color};
                         border-radius:5px; padding:1px 8px; font-weight:700;">
                {urgency_level} Urgency
            </span>
        </div>
    </div>
    <div style="margin-left:auto; text-align:right;">
        <div style="font-size:0.75rem; color:#86868B;">Faculty read-only view</div>
        <div style="font-size:0.8rem; color:#6C63FF; font-weight:600;">SkillDrift Analysis</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# WINDOW 1 — DRIFT SCORE & ENTROPY
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("### 📊 Drift Score & Entropy")

col_ds, col_ent, col_radar = st.columns([2, 2, 4])

ds_color = "#34C759" if drift_score <= 20 else "#FF9500" if drift_score <= 60 else "#FF3B30"
es_color = "#34C759" if entropy_score < 1.2 else "#FF9500" if entropy_score < 2.0 else "#FF3B30"

with col_ds:
    st.markdown(f"""
    <div class="metric-card" style="border-left:4px solid {ds_color};">
        <div class="metric-label">Drift Score</div>
        <div class="metric-value" style="color:{ds_color};">{drift_score}</div>
        <div class="metric-sub">{drift_label}</div>
        <div style="margin-top:8px; font-size:0.78rem; color:#86868B;">
            0 = no drift · 100 = max scatter
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_ent:
    st.markdown(f"""
    <div class="metric-card" style="border-left:4px solid {es_color};">
        <div class="metric-label">Entropy Score</div>
        <div class="metric-value" style="color:{es_color};">{entropy_score} bits</div>
        <div class="metric-sub">{entropy_label}</div>
        <div style="margin-top:8px; font-size:0.78rem; color:#86868B;">
            0 = focused · ~3 = max disorder
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_radar:
    tracks  = list(track_counts.keys())
    counts  = list(track_counts.values())
    fig_radar = go.Figure(go.Scatterpolar(
        r=counts + [counts[0]],
        theta=tracks + [tracks[0]],
        fill="toself",
        fillcolor="rgba(108,99,255,0.15)",
        line=dict(color="#6C63FF", width=2),
        name=student_name,
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor="#F5F5F7",
            radialaxis=dict(visible=True, color="#86868B", gridcolor="#D2D2D7"),
            angularaxis=dict(color="#1D1D1F"),
        ),
        paper_bgcolor="#FFFFFF",
        font=dict(color="#1D1D1F", size=11),
        showlegend=False,
        margin=dict(t=30, b=30, l=30, r=30),
        height=260,
    )
    st.plotly_chart(fig_radar, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# WINDOW 2 — URGENCY ENGINE
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("### ⏱️ Urgency Level")

col_u1, col_u2 = st.columns([3, 5])
with col_u1:
    st.markdown(f"""
    <div class="metric-card" style="border-left:4px solid {urgency_badge_color};">
        <div class="metric-label">Urgency</div>
        <div class="metric-value" style="color:{urgency_badge_color};">{urgency_level}</div>
        <div class="metric-sub">Semester {semester}</div>
        <div style="margin-top:12px;">
            <div class="metric-label">Days to placement season</div>
            <div style="font-size:1.2rem; font-weight:700; color:#1D1D1F;">{days_remaining}</div>
        </div>
        <div style="margin-top:12px;">
            <div class="metric-label">Focus Debt</div>
            <div style="font-size:1.2rem; font-weight:700; color:#FF3B30;">
                {focus_debt_hours} hrs
            </div>
            <div class="metric-sub">{days_to_recover} days at 2 hrs/day</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_u2:
    st.markdown(f"""
    <div style="background:{urgency_badge_color}11; border:1px solid {urgency_badge_color}44;
                border-radius:12px; padding:1.1rem 1.2rem; height:100%;">
        <div style="font-weight:700; color:{urgency_badge_color}; margin-bottom:8px;">
            Urgency Assessment
        </div>
        <div style="color:#1D1D1F; line-height:1.7; font-size:0.92rem;">
            {urgency_message}
        </div>
        <div style="margin-top:1rem;">
            <div style="font-size:0.78rem; color:#86868B; margin-bottom:4px;">
                On-track skills: {len(on_track_skills)} · Distraction skills: {len(distraction_skills)}
            </div>
            {"<div style='font-size:0.82rem; color:#FF3B30;'>Distraction skills: " + ", ".join(distraction_skills[:8]) + ("…" if len(distraction_skills) > 8 else "") + "</div>" if distraction_skills else ""}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# WINDOW 3 — CAREER TRACK MATCH
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("### 🎯 Career Track Match")

col_match_chart, col_gap = st.columns([5, 4])

with col_match_chart:
    if career_matches:
        fig_match = go.Figure(go.Bar(
            x=[m["match_pct"] for m in career_matches],
            y=[m["track"] for m in career_matches],
            orientation="h",
            marker=dict(
                color=[
                    "#6C63FF" if m["track"] == best_track else "#D2D2D7"
                    for m in career_matches
                ]
            ),
            text=[f"{m['match_pct']}%" for m in career_matches],
            textposition="outside",
            textfont=dict(color="#1D1D1F"),
        ))
        fig_match.update_layout(
            paper_bgcolor="#FFFFFF", plot_bgcolor="#F5F5F7",
            font=dict(color="#1D1D1F"),
            xaxis=dict(gridcolor="#D2D2D7", color="#1D1D1F", range=[0, 110]),
            yaxis=dict(gridcolor="#D2D2D7", color="#1D1D1F"),
            margin=dict(t=10, b=10, l=10, r=50),
            height=280,
        )
        st.plotly_chart(fig_match, use_container_width=True)

with col_gap:
    st.markdown(f"""
    <div class="section-card">
        <div style="font-weight:700; color:#6C63FF; margin-bottom:8px;">
            Best match: {best_track} ({match_pct}%)
        </div>
    """, unsafe_allow_html=True)

    for ms in missing_skills[:8]:
        freq = ms["frequency_pct"]
        color = "#FF3B30" if freq >= 70 else "#FF9500" if freq >= 40 else "#86868B"
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between;
                    padding:0.3rem 0; border-bottom:1px solid #F0F0F0;">
            <span style="color:#1D1D1F; font-size:0.85rem;">{ms['skill']}</span>
            <span style="color:{color}; font-size:0.82rem; font-weight:600;">
                {freq:.0f}% of JDs
            </span>
        </div>
        """, unsafe_allow_html=True)

    if not missing_skills:
        st.markdown('<div style="color:#34C759; font-weight:600;">All required skills verified ✓</div>',
                    unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# WINDOW 4 — READINESS & NEXT SKILL
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("### 🚀 Readiness & Next Skill")

col_gauge, col_next = st.columns(2)

rs_color = "#34C759" if readiness_score >= 70 else "#FF9500" if readiness_score >= 40 else "#FF3B30"

with col_gauge:
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=readiness_score,
        title={"text": f"Readiness for {best_track}", "font": {"color": "#1D1D1F", "size": 13}},
        number={"suffix": "%", "font": {"color": "#1D1D1F", "size": 28}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#86868B"},
            "bar": {"color": rs_color},
            "bgcolor": "#F5F5F7",
            "steps": [
                {"range": [0, 40], "color": "#FFE0DE"},
                {"range": [40, 70], "color": "#FFF3D6"},
                {"range": [70, 100], "color": "#D6F5E2"},
            ],
            "threshold": {
                "line": {"color": "#1D1D1F", "width": 2},
                "thickness": 0.75,
                "value": 70,
            },
        },
    ))
    fig_gauge.update_layout(
        paper_bgcolor="#FFFFFF",
        font=dict(color="#1D1D1F"),
        margin=dict(t=40, b=20, l=20, r=20),
        height=240,
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_next:
    if next_skill_info:
        reason = next_skill_info.get("reason", "")
        freq   = next_skill_info.get("frequency_pct", 0)
        st.markdown(f"""
        <div class="section-card">
            <div style="font-size:0.75rem; color:#86868B; margin-bottom:4px;">Next Skill to Learn</div>
            <div style="font-size:1.4rem; font-weight:800; color:#FF9500; margin-bottom:8px;">
                {next_skill}
            </div>
            <div style="font-size:0.82rem; color:#86868B; margin-bottom:4px;">
                Appears in <strong style="color:#1D1D1F;">{freq:.0f}%</strong> of {best_track} JDs
            </div>
            <div style="font-size:0.85rem; color:#1D1D1F; line-height:1.6; margin-top:8px;">
                {reason}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# WINDOW 5 — PEER PLACEMENT RATES
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("### 👥 Peer Comparison")

col_peer1, col_peer2 = st.columns(2)

with col_peer1:
    rate_color = "#34C759" if student_rate >= 60 else "#FF9500" if student_rate >= 40 else "#FF3B30"
    st.markdown(f"""
    <div class="section-card">
        <div style="display:flex; gap:2rem; align-items:center;">
            <div style="text-align:center;">
                <div style="font-size:0.75rem; color:#86868B;">This student's est. placement rate</div>
                <div style="font-size:2rem; font-weight:800; color:{rate_color};">{student_rate}%</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:0.75rem; color:#86868B;">Focused {best_track} student</div>
                <div style="font-size:2rem; font-weight:800; color:#34C759;">{focused_rate}%</div>
            </div>
        </div>
        <div style="font-size:0.78rem; color:#86868B; margin-top:0.75rem;">
            Based on NASSCOM & AICTE published outcome data.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_peer2:
    if survival_rates:
        tracks_sr = list(survival_rates.keys())
        rates_sr  = list(survival_rates.values())
        fig_sr = go.Figure(go.Bar(
            x=rates_sr, y=tracks_sr, orientation="h",
            marker=dict(
                color=["#6C63FF" if t == best_track else "#D2D2D7" for t in tracks_sr]
            ),
            text=[f"{r}%" for r in rates_sr], textposition="outside",
            textfont=dict(color="#1D1D1F"),
        ))
        fig_sr.update_layout(
            paper_bgcolor="#FFFFFF", plot_bgcolor="#F5F5F7",
            title=dict(text="Track Survival Rates", font=dict(color="#1D1D1F", size=12)),
            font=dict(color="#1D1D1F"),
            xaxis=dict(gridcolor="#D2D2D7", range=[0, 110]),
            yaxis=dict(gridcolor="#D2D2D7"),
            margin=dict(t=30, b=10, l=10, r=50),
            height=240,
        )
        st.plotly_chart(fig_sr, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# WINDOW 6 — VERIFIED SKILLS TABLE
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("### 🧠 Verified Skills Profile")

if verified_skills:
    skill_rows = []
    for skill, level in verified_skills.items():
        on_track = skill in on_track_skills
        skill_rows.append({
            "Skill": skill,
            "Verified Level": level,
            "On-Track for Best Career": "✅ Yes" if on_track else "⚠️ Distraction",
        })

    skills_df = pd.DataFrame(skill_rows)
    st.dataframe(skills_df, use_container_width=True, hide_index=True)
else:
    st.warning("No verified skills found for this student.")

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# FACULTY RECOMMENDATION BOX
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("### 💡 Faculty Recommendation")

if readiness_score >= 70:
    st.success(
        f"**{student_name}** is approaching placement readiness for **{best_track}**. "
        f"At {readiness_score}% readiness, they are ahead of most peers. "
        f"Encourage them to deepen top skills to Advanced level and build an end-to-end project."
    )
elif readiness_score >= 40:
    st.warning(
        f"**{student_name}** is partially ready for **{best_track}** at {readiness_score}% readiness. "
        f"Key gap: start with **{next_skill}** — highest impact for their track. "
        f"Advise them to stop adding new technologies until readiness crosses 70%."
    )
else:
    st.error(
        f"**{student_name}** requires urgent intervention. At {readiness_score}% readiness, "
        f"they are not yet competitive for **{best_track}** placements. "
        f"Recommend a focused 30-day commitment to **{next_skill}**. "
        f"Schedule a one-on-one mentoring session."
    )

st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

# Bottom navigation
col_back, col_spacer = st.columns([2, 6])
with col_back:
    if st.button("← Back to All Students", type="primary", use_container_width=True):
        st.switch_page("pages/09_faculty.py")