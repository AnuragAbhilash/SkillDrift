# _sidebar.py — Shared sidebar renderer

import streamlit as st
import plotly.graph_objects as go

APPLE_CSS = """
<style>
    [data-testid="stSidebarNav"] { display: none !important; }
    header[data-testid="stHeader"] { display: none !important; }
    .stDeployButton { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    #MainMenu { display: none !important; }
    footer { display: none !important; }

    .stApp { background-color: #F5F5F7; }
    .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1100px; }

    section[data-testid="stSidebar"] > div {
        background-color: #FFFFFF;
        border-right: 1px solid #D2D2D7;
        padding-top: 0 !important;
    }
    section[data-testid="stSidebar"] .stVerticalBlock { gap: 0; }

    h1 { font-size: 1.7rem !important; font-weight: 700 !important; color: #1D1D1F !important; margin-bottom: 0.25rem !important; }
    h2 { font-size: 1.25rem !important; font-weight: 600 !important; color: #1D1D1F !important; }
    h3 { font-size: 1.05rem !important; font-weight: 600 !important; color: #1D1D1F !important; }

    .stButton > button {
        border-radius: 8px;
        border: 1px solid #D2D2D7;
        background: #F5F5F7;
        color: #1D1D1F;
        font-weight: 500;
        font-size: 0.875rem;
        padding: 0.45rem 1rem;
        transition: all 0.12s ease;
    }
    .stButton > button:hover { background: #E8E8ED; border-color: #C7C7CC; }
    .stButton > button[kind="primary"] {
        background: #6C63FF;
        color: #FFFFFF;
        border-color: #6C63FF;
        font-weight: 600;
    }
    .stButton > button[kind="primary"]:hover { background: #5A52E0; border-color: #5A52E0; }

    .stProgress > div > div { background-color: #6C63FF; border-radius: 4px; }
    .stAlert { border-radius: 10px; }

    div[data-baseweb="tab"] { color: #86868B; font-size: 0.875rem; }
    div[data-baseweb="tab"][aria-selected="true"] { color: #1D1D1F; font-weight: 600; }

    .stDataFrame thead tr th {
        background-color: #F5F5F7 !important;
        color: #86868B !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
    }

    .sd-score-card {
        background: #F5F5F7;
        border: 1px solid #E5E5EA;
        border-radius: 10px;
        padding: 0.65rem 0.85rem;
        margin-bottom: 0.35rem;
    }
    .sd-score-label {
        color: #86868B;
        font-size: 0.62rem;
        font-weight: 600;
        letter-spacing: 0.8px;
        text-transform: uppercase;
    }
    .sd-score-value {
        font-size: 1.5rem;
        font-weight: 700;
        line-height: 1.2;
    }
    .sd-score-desc {
        color: #86868B;
        font-size: 0.7rem;
        margin-top: 0.08rem;
    }

    /* Form styling */
    .stForm { border: none !important; padding: 0 !important; }
    .stRadio > label { font-size: 0.9rem !important; color: #1D1D1F !important; }
    .stCheckbox > label { color: #1D1D1F !important; font-size: 0.9rem !important; }
    .stSelectbox > label { color: #1D1D1F !important; font-size: 0.875rem !important; font-weight: 500 !important; }
    .stTextInput > label { color: #1D1D1F !important; font-size: 0.875rem !important; font-weight: 500 !important; }
</style>
"""

NAV_PAGES = [
    ("Drift & Entropy Scores", "pages/03_drift_score.py"),
    ("Urgency Engine",          "pages/04_urgency.py"),
    ("Career Track Match",      "pages/05_career_match.py"),
    ("Next Skill & Readiness",  "pages/06_next_skill.py"),
    ("Peer Mirror",             "pages/07_peer_mirror.py"),
    ("Market Intelligence",     "pages/08_market_intel.py"),
    ("Final Report",            "pages/10_final_report.py"),
]


def render_sidebar():
    with st.sidebar:
        student_name = st.session_state.get("student_name", "Student")
        semester_val = st.session_state.get("semester", "?")

        # Compact profile — avatar + name in one tight row
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:0.6rem;
                    padding:0.75rem 0.9rem 0.5rem 0.9rem;
                    border-bottom:1px solid #F0F0F5;">
            <div style="width:34px; height:34px; border-radius:50%; background:#F0EFFF;
                        display:flex; align-items:center; justify-content:center; flex-shrink:0;">
                <svg width="20" height="20" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="40" cy="28" r="19" fill="#6C63FF"/>
                    <ellipse cx="40" cy="66" rx="27" ry="17" fill="#6C63FF"/>
                </svg>
            </div>
            <div>
                <div style="font-weight:700; font-size:0.92rem; color:#1D1D1F; line-height:1.2;">
                    {student_name}
                </div>
                <div style="color:#86868B; font-size:0.75rem; margin-top:0.05rem;">
                    Semester {semester_val}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        drift_score   = st.session_state.get("drift_score")
        drift_label   = st.session_state.get("drift_label", "")
        entropy_score = st.session_state.get("entropy_score") or 0
        entropy_label = st.session_state.get("entropy_label", "")

        if drift_score is not None:
            drift_color = (
                "#34C759" if drift_score <= 20
                else "#FF9500" if drift_score <= 60
                else "#FF3B30"
            )
            entropy_color = (
                "#34C759" if entropy_score < 1.2
                else "#FF9500" if entropy_score < 2.0
                else "#FF3B30"
            )

            st.markdown(f"""
            <div style="padding:0.5rem 0.75rem 0 0.75rem;">
            <div class="sd-score-card">
                <div class="sd-score-label">Drift Score</div>
                <div class="sd-score-value" style="color:{drift_color};">{drift_score}</div>
                <div class="sd-score-desc">{drift_label}</div>
            </div>
            <div class="sd-score-card">
                <div class="sd-score-label">Entropy Score</div>
                <div class="sd-score-value" style="color:{entropy_color};">
                    {entropy_score}<span style="font-size:0.8rem; font-weight:400;"> bits</span>
                </div>
                <div class="sd-score-desc">{entropy_label}</div>
            </div>
            </div>
            """, unsafe_allow_html=True)

            track_counts = st.session_state.get("track_counts") or {}
            if track_counts and any(v > 0 for v in track_counts.values()):
                tracks  = list(track_counts.keys())
                counts  = list(track_counts.values())
                counts_closed = counts + [counts[0]]
                tracks_closed = tracks + [tracks[0]]

                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(
                    r=counts_closed,
                    theta=tracks_closed,
                    fill="toself",
                    fillcolor="rgba(108, 99, 255, 0.15)",
                    line=dict(color="#6C63FF", width=2),
                ))
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, showticklabels=False, gridcolor="#D2D2D7"),
                        angularaxis=dict(tickfont=dict(size=7, color="#86868B"), gridcolor="#D2D2D7"),
                        bgcolor="#FFFFFF",
                    ),
                    paper_bgcolor="#FFFFFF",
                    showlegend=False,
                    margin=dict(l=15, r=15, t=8, b=8),
                    height=200,
                )
                st.plotly_chart(fig_radar, use_container_width=True)
        else:
            st.markdown(
                "<div style='color:#86868B; font-size:0.8rem; text-align:center; "
                "padding:0.6rem 0.9rem;'>Complete the skill quiz to see your scores.</div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            "<div style='color:#86868B; font-size:0.62rem; font-weight:600; "
            "letter-spacing:0.8px; text-transform:uppercase; padding:0.35rem 0.9rem 0.15rem 0.9rem;'>"
            "DASHBOARD</div>",
            unsafe_allow_html=True,
        )

        for label, page in NAV_PAGES:
            if st.button(label, key=f"nav_{page}", use_container_width=True):
                st.switch_page(page)

        st.markdown("<div style='padding:0.25rem 0.5rem 0.75rem 0.5rem;'>", unsafe_allow_html=True)
        if st.button("Sign Out", key="sidebar_signout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("pages/01_home.py")
        st.markdown("</div>", unsafe_allow_html=True)
