# _sidebar.py — Shared sidebar renderer (matches ui_idea.html exactly)

import streamlit as st
import plotly.graph_objects as go

# ── CSS injected on every dashboard page (03–08, 10) ────────────────────────
APPLE_CSS = """
<style>
    /* Hide Streamlit chrome */
    [data-testid="stSidebarNav"]   { display: none !important; }
    header[data-testid="stHeader"] { display: none !important; }
    .stDeployButton                { display: none !important; }
    #MainMenu                      { display: none !important; }
    footer                         { display: none !important; }

    /* Keep the collapse-arrow visible on dashboard pages */
    [data-testid="collapsedControl"] {
        display:    block   !important;
        visibility: visible !important;
        opacity:    1       !important;
        z-index:    9999    !important;
    }

    /* Page background */
    .stApp           { background-color: #f6fafe; }
    .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1100px; }

    /* Sidebar shell */
    section[data-testid="stSidebar"]       { width: 268px !important; min-width: 268px !important; }
    section[data-testid="stSidebar"] > div {
        background-color: #FFFFFF;
        border-right:     1px solid #e2e8f0;
        padding-top:      0 !important;
        height:           100vh;
    }
    section[data-testid="stSidebar"] .stVerticalBlock { gap: 0 !important; }

    /* Sidebar nav buttons — default state */
    section[data-testid="stSidebar"] .stButton > button {
        background:     transparent !important;
        border:         none        !important;
        border-right:   3px solid transparent !important;
        border-radius:  8px         !important;
        color:          #515f74     !important;
        font-size:      0.85rem     !important;
        font-weight:    500         !important;
        text-align:     left        !important;
        padding:        11px 14px   !important;
        width:          100%        !important;
        transition:     all 0.12s ease !important;
        justify-content: flex-start !important;
        display:        flex        !important;
        align-items:    center      !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #f0f4f8 !important;
        color:      #171c1f !important;
    }

    /* Sign-out button */
    section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"]:last-of-type {
        color: #515f74 !important;
    }
    section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"]:last-of-type:hover {
        background: #fff0f0 !important;
        color:      #ba1a1a !important;
    }

    /* Global typography */
    h1 { font-size: 2rem   !important; font-weight: 700 !important; color: #171c1f !important; margin-bottom: 0.25rem !important; }
    h2 { font-size: 1.5rem !important; font-weight: 600 !important; color: #171c1f !important; }
    h3 { font-size: 1.2rem !important; font-weight: 600 !important; color: #171c1f !important; }

    /* Main-area buttons */
    .stButton > button {
        border-radius: 8px;
        border:        1.5px solid #D2D2D7;
        background:    #F5F5F7;
        color:         #171c1f;
        font-weight:   500;
        font-size:     0.875rem;
        padding:       0.5rem 1rem;
        transition:    all 0.12s ease;
    }
    .stButton > button:hover { background: #E8E8ED; border-color: #C7C7CC; }
    .stButton > button[kind="primary"] {
        background:   #002c98;
        color:        #FFFFFF;
        border-color: #002c98;
        font-weight:  600;
    }
    .stButton > button[kind="primary"]:hover { background: #0038bf; border-color: #0038bf; }

    /* Misc */
    .stProgress > div > div { background-color: #002c98; border-radius: 4px; }
    .stAlert { border-radius: 10px; }
    div[data-baseweb="tab"]                       { color: #515f74; font-size: 0.875rem; }
    div[data-baseweb="tab"][aria-selected="true"] { color: #171c1f; font-weight: 600; }
    .stDataFrame thead tr th {
        background-color: #f8fafc !important;
        color:            #515f74 !important;
        font-size:        0.78rem !important;
        font-weight:      600     !important;
        letter-spacing:   0.5px   !important;
        text-transform:   uppercase !important;
    }

    /* Score chips */
    .sd-score-chip {
        background:    #f8fafc;
        border:        1px solid #e2e8f0;
        border-radius: 8px;
        padding:       8px 12px;
        margin-bottom: 6px;
        display:       flex;
        align-items:   center;
        gap:           8px;
    }
    .sd-chip-label {
        font-size:      0.72rem;
        color:          #515f74;
        font-weight:    600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        min-width:      52px;
    }
    .sd-chip-value  { font-size: 0.9rem; font-weight: 700; }
    .sd-chip-badge  {
        font-size:     0.68rem;
        padding:       2px 7px;
        border-radius: 10px;
        font-weight:   700;
        margin-left:   auto;
    }
    .sd-badge-drift   { background: #ffdad6; color: #ba1a1a; }
    .sd-badge-entropy { background: #d5e3fc; color: #002c98; }

    /* Active nav highlight — injected inline per item */
    .sd-nav-active-btn button {
        background:   #eef2ff !important;
        color:        #002c98 !important;
        font-weight:  700     !important;
        border-right: 3px solid #002c98 !important;
    }

    /* Form */
    .stForm           { border: none !important; padding: 0 !important; }
    .stRadio    label { font-size: 0.9rem  !important; color: #171c1f !important; }
    .stCheckbox label { color: #171c1f    !important; font-size: 0.9rem !important; }
    .stSelectbox label{ color: #171c1f   !important; font-size: 0.875rem !important; font-weight: 500 !important; }
    .stTextInput label{ color: #171c1f   !important; font-size: 0.875rem !important; font-weight: 500 !important; }
</style>
"""

# ── Navigation definition ──────────────────────────────────────────────────
NAV_PAGES = [
    ("Drift & Entropy Scores", "pages/03_drift_score.py"),
    ("Urgency Engine",         "pages/04_urgency.py"),
    ("Career Track Match",     "pages/05_career_match.py"),
    ("Next Skill & Readiness", "pages/06_next_skill.py"),
    ("Peer Mirror & Survival", "pages/07_peer_mirror.py"),
    ("Market Intelligence",    "pages/08_market_intel.py"),
    ("Final Report",           "pages/10_final_report.py"),
]

# Map session key → page file for active-nav detection
_PAGE_KEY_MAP = {
    "drift"  : "pages/03_drift_score.py",
    "urgency": "pages/04_urgency.py",
    "career" : "pages/05_career_match.py",
    "next"   : "pages/06_next_skill.py",
    "peer"   : "pages/07_peer_mirror.py",
    "market" : "pages/08_market_intel.py",
    "report" : "pages/10_final_report.py",
}


def render_sidebar():
    """Render the complete sidebar matching ui_idea.html design."""
    with st.sidebar:

        student_name = st.session_state.get("student_name", "Student")
        semester_val = st.session_state.get("semester", "?")

        # ── Profile header ────────────────────────────────────────────────
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;
                    padding:20px 16px 12px 16px;
                    border-bottom:1px solid #f0f4f8;">
            <div style="flex-shrink:0;">
                <svg width="44" height="44" viewBox="0 0 44 44" fill="none"
                     xmlns="http://www.w3.org/2000/svg">
                    <circle cx="22" cy="22" r="22" fill="#e2e8f0"/>
                    <circle cx="22" cy="18" r="8"  fill="#94a3b8"/>
                    <ellipse cx="22" cy="36" rx="13" ry="9" fill="#94a3b8"/>
                </svg>
            </div>
            <div>
                <div style="font-weight:700;font-size:0.95rem;color:#171c1f;
                            line-height:1.25;font-family:-apple-system,BlinkMacSystemFont,
                            'Inter',sans-serif;">
                    {student_name}
                </div>
                <div style="font-size:0.75rem;color:#515f74;margin-top:2px;">
                    Semester {semester_val}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Score chips ───────────────────────────────────────────────────
        drift_score   = st.session_state.get("drift_score")
        drift_label   = st.session_state.get("drift_label", "")
        entropy_score = st.session_state.get("entropy_score") or 0
        entropy_label = st.session_state.get("entropy_label", "")

        if drift_score is not None:
            drift_color = (
                "#15803d" if drift_score <= 20
                else "#d97706" if drift_score <= 60
                else "#ba1a1a"
            )
            entropy_color = (
                "#15803d" if entropy_score < 1.2
                else "#d97706" if entropy_score < 2.0
                else "#ba1a1a"
            )
            st.markdown(f"""
            <div style="padding:10px 12px 0 12px;">
                <div class="sd-score-chip">
                    <span class="sd-chip-label">Drift</span>
                    <span class="sd-chip-value" style="color:{drift_color};">{drift_score}</span>
                    <span class="sd-chip-badge sd-badge-drift">{drift_label}</span>
                </div>
                <div class="sd-score-chip">
                    <span class="sd-chip-label">Entropy</span>
                    <span class="sd-chip-value" style="color:{entropy_color};">
                        {entropy_score}<span style="font-size:0.72rem;font-weight:400;"> bits</span>
                    </span>
                    <span class="sd-chip-badge sd-badge-entropy">{entropy_label}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Mini radar chart
            track_counts = st.session_state.get("track_counts") or {}
            if track_counts and any(v > 0 for v in track_counts.values()):
                tracks        = list(track_counts.keys())
                counts        = list(track_counts.values())
                counts_closed = counts + [counts[0]]
                tracks_closed = tracks + [tracks[0]]

                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=counts_closed,
                    theta=tracks_closed,
                    fill="toself",
                    fillcolor="rgba(0,44,152,0.12)",
                    line=dict(color="#002c98", width=2),
                ))
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            showticklabels=False,
                            gridcolor="#e2e8f0",
                        ),
                        angularaxis=dict(
                            tickfont=dict(size=7, color="#515f74"),
                            gridcolor="#e2e8f0",
                        ),
                        bgcolor="#FFFFFF",
                    ),
                    paper_bgcolor="#FFFFFF",
                    showlegend=False,
                    margin=dict(l=12, r=12, t=8, b=8),
                    height=130,
                )
                page_key = st.session_state.get("_current_page", "default")
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    key=f"sidebar_radar_{page_key}",
                )
        else:
            st.markdown(
                "<div style='color:#515f74;font-size:0.8rem;text-align:center;"
                "padding:12px 14px;'>Complete the skill quiz to see your scores.</div>",
                unsafe_allow_html=True,
            )

        # ── Nav section label ─────────────────────────────────────────────
        st.markdown(
            "<div style='color:#515f74;font-size:0.62rem;font-weight:700;"
            "letter-spacing:0.8px;text-transform:uppercase;"
            "padding:8px 14px 4px 14px;'>DASHBOARD</div>",
            unsafe_allow_html=True,
        )

        # ── Nav buttons ───────────────────────────────────────────────────
        active_page = _PAGE_KEY_MAP.get(st.session_state.get("_current_page", ""), "")

        for label, page in NAV_PAGES:
            is_active = (page == active_page)

            if is_active:
                # Wrap in a div with the active class so the CSS selector fires
                st.markdown(
                    "<div class='sd-nav-active-btn'>",
                    unsafe_allow_html=True,
                )

            if st.button(label, key=f"nav__{page}", use_container_width=True):
                st.switch_page(page)

            if is_active:
                st.markdown("</div>", unsafe_allow_html=True)

        # ── Footer divider + sign-out ─────────────────────────────────────
        st.markdown(
            "<div style='border-top:1px solid #e2e8f0;margin:6px 0 0 0;'></div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div style='padding:4px 0 8px 0;'></div>", unsafe_allow_html=True)

        if st.button("Sign Out", key="sidebar_signout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("pages/01_home.py")
