# _sidebar.py — Shared sidebar renderer

import streamlit as st
import plotly.graph_objects as go
import streamlit.components.v1 as components

from session_store import clear_session

# ── Global CSS ─────────────────────────────────────────────────────────────
APPLE_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    /* ── Hide Streamlit chrome ─────────────────────────────────────── */
    [data-testid="stSidebarNav"]     { display: none !important; }
    .stDeployButton                  { display: none !important; }
    #MainMenu                        { display: none !important; }
    footer                           { display: none !important; }
    [data-testid="stDecoration"]     { display: none !important; }
    [data-testid="stStatusWidget"]   { display: none !important; }
    [data-testid="stMainMenu"]       { display: none !important; }
    [data-testid="stToolbarActions"] { display: none !important; }

    header[data-testid="stHeader"] {
        background:    transparent !important;
        border-bottom: none        !important;
        box-shadow:    none        !important;
    }

    /* ── Sidebar toggle buttons ─────────────────────────────────────── */
    [data-testid="stExpandSidebar"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] {
        display:        flex !important;
        visibility:     visible !important;
        opacity:        1       !important;
        z-index:        99999   !important;
        pointer-events: all     !important;
    }

    /* ── Root vars ────────────────────────────────────────────────── */
    :root {
        --blue:      #002c98;
        --blue-lt:   #eef2ff;
        --red:       #ba1a1a;
        --green:     #15803d;
        --amber:     #d97706;
        --text:      #171c1f;
        --muted:     #515f74;
        --border:    #e2e8f0;
        --surface:   #f6fafe;
        --card:      #ffffff;
        --radius:    12px;
    }

    /* ── Page background ──────────────────────────────────────────── */
    html, body, .stApp { background-color: var(--surface) !important; }

    /* ── Block container: centered, max-width ─────────────────────── */
    .block-container {
        padding-top:    2rem      !important;
        padding-bottom: 3rem      !important;
        max-width:      960px     !important;
        margin-left:    auto      !important;
        margin-right:   auto      !important;
        padding-left:   2rem      !important;
        padding-right:  2rem      !important;
    }

    /* ── Sidebar shell ────────────────────────────────────────────── */
    section[data-testid="stSidebar"] > div {
        background-color: var(--card);
        border-right:     1px solid var(--border);
        padding-top:      0 !important;
    }
    section[data-testid="stSidebar"] .stVerticalBlock { gap: 0 !important; }
    section[data-testid="stSidebar"] > div:first-child { padding-bottom: 0 !important; }
    section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] { padding-bottom: 10px !important; }

    /* ── Sidebar nav buttons (default state) ─────────────────────── */
    section[data-testid="stSidebar"] .stButton > button {
        background:      transparent !important;
        border:          none        !important;
        border-radius:   6px         !important;
        color:           var(--muted) !important;
        font-size:       0.875rem    !important;
        font-weight:     500         !important;
        font-family:     'Inter', sans-serif !important;
        text-align:      left        !important;
        padding:         10px 14px   !important;
        width:           100%        !important;
        transition:      background 0.12s ease, color 0.12s ease !important;
        justify-content: flex-start  !important;
        display:         flex        !important;
        align-items:     center      !important;
        letter-spacing:  0           !important;
        box-shadow:      none        !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #f1f5f9 !important;
        color:      var(--text) !important;
    }

    /* Sign-out button */
    section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"]:last-of-type {
        color: var(--muted) !important;
    }
    section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"]:last-of-type:hover {
        background: #fff0f0 !important;
        color:      var(--red) !important;
    }

    /* ── Typography ───────────────────────────────────────────────── */
    h1, h2, h3 { font-family: 'Manrope', sans-serif !important; color: var(--text) !important; }
    h1 { font-size: 1.75rem !important; font-weight: 800 !important; line-height: 1.2 !important; margin-bottom: 0.25rem !important; }
    h2 { font-size: 1.25rem !important; font-weight: 700 !important; margin-bottom: 0.25rem !important; }
    h3 { font-size: 1.05rem !important; font-weight: 700 !important; }
    p, li, div { font-family: 'Inter', sans-serif; }

    /* ── Main area buttons ────────────────────────────────────────── */
    .stButton > button {
        border-radius:  8px;
        border:         1.5px solid var(--border);
        background:     var(--card);
        color:          var(--text);
        font-weight:    600;
        font-size:      0.9rem;
        font-family:    'Inter', sans-serif;
        padding:        0.55rem 1.25rem;
        transition:     all 0.12s ease;
        letter-spacing: 0;
    }
    .stButton > button:hover { background: #f0f4f8; border-color: #c2cad4; }
    .stButton > button[kind="primary"] {
        background:   var(--blue);
        color:        #FFFFFF;
        border-color: var(--blue);
        font-weight:  700;
    }
    .stButton > button[kind="primary"]:hover {
        background:   #0038bf;
        border-color: #0038bf;
    }

    /* ── Progress / alert / tabs ───────────────────────────────────── */
    .stProgress > div > div { background-color: var(--blue); border-radius: 4px; }
    .stAlert { border-radius: var(--radius); }
    div[data-baseweb="tab"]                       { color: var(--muted); font-size: 0.875rem; font-family: 'Inter', sans-serif; }
    div[data-baseweb="tab"][aria-selected="true"] { color: var(--text); font-weight: 700; }

    /* ── Table headers ─────────────────────────────────────────────── */
    .stDataFrame thead tr th {
        background-color: #f8fafc !important;
        color:            var(--muted) !important;
        font-size:        0.72rem !important;
        font-weight:      700     !important;
        letter-spacing:   0.06em   !important;
        text-transform:   uppercase !important;
        font-family:      'Inter', sans-serif !important;
    }

    /* ── Score chips ───────────────────────────────────────────────── */
    .sd-score-chip {
        background:    #f8fafc;
        border:        1px solid var(--border);
        border-radius: 8px;
        padding:       8px 10px;
        margin-bottom: 6px;
        display:       flex;
        align-items:   center;
        gap:           8px;
        min-width:     0;
    }
    .sd-chip-label {
        font-size:      0.65rem;
        color:          var(--muted);
        font-weight:    700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        white-space:    nowrap;
        flex-shrink:    0;
        width:          62px;
        font-family:    'Inter', sans-serif;
    }
    .sd-chip-value {
        font-size:   0.92rem;
        font-weight: 800;
        font-family: 'Manrope', sans-serif;
        white-space: nowrap;
        flex-shrink: 0;
        min-width:   36px;
    }
    .sd-chip-badge {
        font-size:     0.60rem;
        padding:       2px 7px;
        border-radius: 10px;
        font-weight:   700;
        margin-left:   auto;
        flex-shrink:   0;
        white-space:   nowrap;
        font-family:   'Inter', sans-serif;
        overflow:      hidden;
        text-overflow: ellipsis;
        max-width:     90px;
    }
    .sd-badge-drift   { background: #ffdad6; color: var(--red); }
    .sd-badge-entropy { background: #d5e3fc; color: var(--blue); }

    /* ── Forms ──────────────────────────────────────────────────────── */
    .stForm           { border: none !important; padding: 0 !important; }
    .stRadio    label { font-size: 0.9rem  !important; color: var(--text) !important; font-family: 'Inter', sans-serif !important; }
    .stCheckbox label { color: var(--text) !important; font-size: 0.9rem !important; font-family: 'Inter', sans-serif !important; }
    .stSelectbox label { color: var(--text) !important; font-size: 0.9rem !important; font-weight: 600 !important; font-family: 'Inter', sans-serif !important; }
    .stTextInput label { color: var(--text) !important; font-size: 0.9rem !important; font-weight: 600 !important; font-family: 'Inter', sans-serif !important; }
    .stTextInput input { font-size: 1rem !important; font-family: 'Inter', sans-serif !important; }
    .stSelectbox select { font-size: 1rem !important; }

    /* ── Dashboard page title bar ───────────────────────────────────── */
    .sd-topbar {
        background:    var(--card);
        border-bottom: 1px solid var(--border);
        padding:       24px 0 20px 0;
        margin-bottom: 28px;
    }
    .sd-topbar-title {
        font-family: 'Manrope', sans-serif;
        font-size:   1.5rem;
        font-weight: 800;
        color:       var(--text);
        margin:      0;
    }
    .sd-topbar-sub {
        font-size:  0.875rem;
        color:      var(--muted);
        margin-top: 4px;
    }

    /* ── Cards ──────────────────────────────────────────────────────── */
    .sd-card {
        background:    var(--card);
        border:        1px solid var(--border);
        border-radius: var(--radius);
        padding:       24px;
        box-shadow:    0 2px 12px rgba(23,28,31,.04);
    }

    /* ── Metric card ────────────────────────────────────────────────── */
    .sd-metric {
        background:    var(--card);
        border:        1px solid var(--border);
        border-radius: var(--radius);
        padding:       24px 20px;
        text-align:    center;
    }
    .sd-metric-label {
        font-size:      0.7rem;
        font-weight:    700;
        color:          var(--muted);
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom:  10px;
        font-family:    'Inter', sans-serif;
    }
    .sd-metric-value {
        font-size:   3rem;
        font-weight: 800;
        line-height: 1;
        font-family: 'Manrope', sans-serif;
    }
    .sd-metric-sub {
        font-size:  0.82rem;
        color:      var(--muted);
        margin-top: 8px;
    }
</style>
"""

# ── Entropy label shortener ─────────────────────────────────────────────────
def _short_entropy_label(label: str) -> str:
    mapping = {
        "Highly Ordered — Strong Focus":    "Highly Ordered",
        "Moderately Ordered":               "Moderate",
        "Disordered — Showing Drift":       "Disordered",
        "Highly Disordered — Strong Drift": "High Disorder",
    }
    return mapping.get(label, label.split(" — ")[0] if " — " in label else label)

# ── Navigation ──────────────────────────────────────────────────────────────
NAV_PAGES = [
    ("Dashboard",            "pages/03_drift_score.py"),
    ("Time Left",            "pages/04_urgency.py"),
    ("Career Match",         "pages/05_career_match.py"),
    ("Next Skill to Learn",  "pages/06_next_skill.py"),
    ("Placement Odds",       "pages/07_peer_mirror.py"),
    ("Job Market",           "pages/08_market_intel.py"),
    ("My Report Card",       "pages/10_final_report.py"),
]

_PAGE_KEY_MAP = {
    "drift"  : "pages/03_drift_score.py",
    "urgency": "pages/04_urgency.py",
    "career" : "pages/05_career_match.py",
    "next"   : "pages/06_next_skill.py",
    "peer"   : "pages/07_peer_mirror.py",
    "market" : "pages/08_market_intel.py",
    "report" : "pages/10_final_report.py",
}


def _inject_active_nav_css(active_page: str) -> None:
    active_label = next(
        (label for label, page in NAV_PAGES if page == active_page), ""
    )
    if not active_label:
        return

    components.html(f"""
    <script>
    (function() {{
        const label = {repr(active_label)};
        function highlight() {{
            const sidebar = window.parent.document.querySelector('section[data-testid="stSidebar"]');
            if (!sidebar) return;
            sidebar.querySelectorAll('button').forEach(btn => {{
                const txt = btn.innerText.trim();
                if (txt === label) {{
                    btn.style.setProperty('background',  '#f1f5f9', 'important');
                    btn.style.setProperty('color',       '#171c1f', 'important');
                    btn.style.setProperty('font-weight', '700',     'important');
                }} else if (['Dashboard','Time Left',
                             'Career Match','Next Skill to Learn',
                             'Placement Odds','Job Market',
                             'My Report Card'].includes(txt)) {{
                    btn.style.removeProperty('background');
                    btn.style.removeProperty('color');
                    btn.style.removeProperty('font-weight');
                }}
            }});
        }}
        highlight();
        setTimeout(highlight, 200);
        setTimeout(highlight, 600);
    }})();
    </script>
    """, height=0, scrolling=False)


def render_sidebar():
    with st.sidebar:

        student_name = st.session_state.get("student_name", "Student")
        semester_val = st.session_state.get("semester", "?")

        # ── Profile header ────────────────────────────────────────────
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;
                    padding:22px 16px 16px 16px;
                    border-bottom:1px solid #e2e8f0;">
            <div style="flex-shrink:0;">
                <svg width="40" height="40" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="22" cy="22" r="22" fill="#e8edf4"/>
                    <circle cx="22" cy="18" r="8"  fill="#a3b1c6"/>
                    <ellipse cx="22" cy="36" rx="13" ry="9" fill="#a3b1c6"/>
                </svg>
            </div>
            <div style="min-width:0;">
                <div style="font-family:'Manrope',sans-serif;font-weight:800;font-size:0.92rem;
                            color:#171c1f;line-height:1.25;white-space:nowrap;
                            overflow:hidden;text-overflow:ellipsis;">
                    {student_name}
                </div>
                <div style="font-size:0.75rem;color:#515f74;margin-top:2px;font-family:'Inter',sans-serif;">
                    Semester {semester_val}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Score chips ───────────────────────────────────────────────
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

            short_entropy = _short_entropy_label(entropy_label)

            # Both chips use identical HTML structure: label | value | badge
            st.markdown(f"""
            <div style="padding:10px 10px 6px 10px;">
                <div class="sd-score-chip">
                    <span class="sd-chip-label">Drift</span>
                    <span class="sd-chip-value" style="color:{drift_color};">{drift_score}</span>
                    <span class="sd-chip-badge sd-badge-drift">{drift_label}</span>
                </div>
                <div class="sd-score-chip">
                    <span class="sd-chip-label">Entropy</span>
                    <span class="sd-chip-value" style="color:{entropy_color};">{entropy_score}</span>
                    <span class="sd-chip-badge sd-badge-entropy">{short_entropy}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Mini radar ────────────────────────────────────────────
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
                    fillcolor="rgba(0,44,152,0.10)",
                    line=dict(color="#002c98", width=2),
                ))
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, showticklabels=False, gridcolor="#e2e8f0"),
                        angularaxis=dict(tickfont=dict(size=7, color="#515f74"), gridcolor="#e2e8f0"),
                        bgcolor="#FFFFFF",
                    ),
                    paper_bgcolor="#FFFFFF",
                    showlegend=False,
                    margin=dict(l=12, r=12, t=22, b=8),
                    height=130,
                )
                st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
                page_key = st.session_state.get("_current_page", "default")
                st.plotly_chart(fig, use_container_width=True, key=f"sidebar_radar_{page_key}")

        else:
            st.markdown(
                "<div style='color:#515f74;font-size:0.82rem;text-align:center;"
                "padding:16px 14px;font-family:Inter,sans-serif;"
                "line-height:1.5;'>Complete the skill quiz to see your scores.</div>",
                unsafe_allow_html=True,
            )

        # ── Dashboard section label ───────────────────────────────────
        st.markdown("""
        <div style="margin:14px 12px 10px 12px;border-top:1px solid #e2e8f0;"></div>
        """, unsafe_allow_html=True)

        # ── Active page detection + CSS injection ─────────────────────
        active_page = _PAGE_KEY_MAP.get(st.session_state.get("_current_page", ""), "")
        _inject_active_nav_css(active_page)

        # ── Nav buttons with failure gate locking ─────────────────────
        quiz_results    = st.session_state.get("quiz_results", [])
        semester_val_n  = st.session_state.get("semester", 0)
        try:
            sem_int = int(str(semester_val_n).split()[0]) if semester_val_n else 0
        except Exception:
            sem_int = 0

        verified_count = sum(
            1 for r in quiz_results
            if r.get("status") in ("Confirmed", "Borderline")
        )
        total_claimed  = len(quiz_results)

        # Determine if gate is passed
        # Beginner (sem 1-2): need 2/3+; Intermediate/Advanced (sem 3-8): need 3/3+
        if sem_int <= 2:
            min_required = 2
        else:
            min_required = 3

        quiz_done   = st.session_state.get("quiz_complete", False)
        gate_passed = (not quiz_done) or (verified_count >= min_required) or (total_claimed >= 5 and verified_count >= 4)

        if quiz_done and not gate_passed:
            # Show locked status
            st.markdown(f"""
            <div style="margin:6px 12px 10px 12px;padding:10px 12px;
                        background:#fff8e1;border-radius:8px;
                        border-left:3px solid #d97706;">
                <div style="font-size:0.72rem;font-weight:700;color:#d97706;
                            text-transform:uppercase;letter-spacing:0.05em;
                            font-family:'Inter',sans-serif;">Results locked</div>
                <div style="font-size:0.8rem;color:#515f74;margin-top:3px;
                            font-family:'Inter',sans-serif;">
                    {verified_count} of {total_claimed} skills verified
                </div>
            </div>
            """, unsafe_allow_html=True)

        for label, page in NAV_PAGES:
            is_dashboard = (page == "pages/03_drift_score.py")
            if is_dashboard or gate_passed:
                if st.button(label, key=f"nav__{page}", use_container_width=True):
                    st.switch_page(page)
            else:
                # Greyed-out, non-clickable
                st.markdown(f"""
                <div style="padding:10px 14px;font-size:0.875rem;font-weight:500;
                            font-family:'Inter',sans-serif;color:#c0c8d4;
                            cursor:not-allowed;border-radius:6px;
                            user-select:none;">{label}</div>
                """, unsafe_allow_html=True)

        # ── Footer ────────────────────────────────────────────────────
        st.markdown(
            "<div style='border-top:1px solid #e2e8f0;margin:8px 0 0 0;'></div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div style='padding:12px 0;'></div>", unsafe_allow_html=True)

        if st.button("Sign Out", key="sidebar_signout", use_container_width=True):
            st.session_state["_show_signout_dialog"] = True

        if st.session_state.get("_show_signout_dialog"):
            cancel_clicked = st.button("_cancel_hidden", key="signout_cancel")
            confirm_clicked = st.button("_confirm_hidden", key="signout_confirm")

            if cancel_clicked:
                st.session_state["_show_signout_dialog"] = False
                st.rerun()
            if confirm_clicked:
                # Clear persisted session on disk AND in memory.
                clear_session()
                st.switch_page("pages/01_home.py")

            components.html("""
            <script>
            (function() {
                const doc = window.parent.document;

                // Remove existing overlay if any
                const existing = doc.getElementById('sd-logout-overlay');
                if (existing) existing.remove();

                const overlay = doc.createElement('div');
                overlay.id = 'sd-logout-overlay';
                overlay.style.cssText = `
                    position:fixed; inset:0; background:rgba(0,0,0,0.45);
                    display:flex; align-items:center; justify-content:center;
                    z-index:999999; font-family:'Inter',sans-serif;
                `;

                overlay.innerHTML = `
                    <div style="background:#fff;border-radius:16px;padding:40px 36px 32px;
                                width:420px;max-width:90vw;text-align:center;
                                box-shadow:0 20px 60px rgba(0,0,0,0.18);">
                        <div style="font-size:1.35rem;font-weight:700;color:#171c1f;margin-bottom:12px;
                                    font-family:'Inter',sans-serif;">Log Out?</div>
                        <div style="font-size:0.9rem;color:#515f74;line-height:1.6;margin-bottom:28px;
                                    font-family:'Inter',sans-serif;">
                            All your data will be lost. You will need to re-enter your name,
                            skills, and complete the verification quiz again from the beginning.
                        </div>
                        <div style="display:flex;gap:12px;">
                            <button id="sd-cancel-btn" style="flex:1;padding:11px 0;border-radius:8px;
                                border:1.5px solid #e2e8f0;background:#fff;color:#171c1f;
                                font-size:0.9rem;font-weight:600;cursor:pointer;font-family:'Inter',sans-serif;">
                                Cancel — Stay Here
                            </button>
                            <button id="sd-logout-btn" style="flex:1;padding:11px 0;border-radius:8px;
                                border:none;background:#ba1a1a;color:#fff;
                                font-size:0.9rem;font-weight:700;cursor:pointer;font-family:'Inter',sans-serif;">
                                Yes, Log Out
                            </button>
                        </div>
                    </div>
                `;

                doc.body.appendChild(overlay);

                doc.getElementById('sd-cancel-btn').onclick = function() {
                    overlay.remove();
                    // Click the hidden cancel button in Streamlit
                    const btns = doc.querySelectorAll('button');
                    btns.forEach(b => {
                        if (b.innerText.trim() === '_cancel_hidden') b.click();
                    });
                };

                doc.getElementById('sd-logout-btn').onclick = function() {
                    overlay.remove();
                    const btns = doc.querySelectorAll('button');
                    btns.forEach(b => {
                        if (b.innerText.trim() === '_confirm_hidden') b.click();
                    });
                };
            })();
            </script>
            """, height=0, scrolling=False)