# pages/02b_quiz.py
# =============================================================
# SkillDrift  —  Proctored Quiz Page
# =============================================================
#
# Fix log (this revision):
#
# Issue 1 — Terminated screen card floats left / misaligned:
#   The terminated screen now injects its own centring wrapper so
#   it is always centred regardless of the body class or layout mode.
#
# Issues 2 & 3 — After termination, re-entering the quiz shows
#   misaligned UI and immediately fires violation 1/3:
#
#   Root cause A — body class:
#     The sd-in-test class added to <body> by the in-test JS snippet
#     persists across Streamlit page navigations because the browser
#     does not reload the page, only the React tree changes. So when
#     the student returns to the pre-start gate after termination the
#     body still has sd-in-test, making the layout wide and broken.
#     Fix: on EVERY page load we emit a JS snippet that REMOVES
#     sd-in-test from body unconditionally. Only the in-test section
#     re-adds it if we are actually in-test.
#
#   Root cause B — stale JS counters:
#     window._sdTabSwitches and window._sdFsExits live on the parent
#     window object and survive Streamlit's client-side navigation.
#     After a termination the counters are non-zero. On the next quiz
#     start _nuke_and_go_home() sets _seen_ts=0 and _seen_fx=0 in
#     session_state, so the first JS poll sees ts > prev_ts and fires
#     a violation immediately.
#     Fix: the very first thing the JS poll does is check whether
#     window._sdResetSerial matches st.session_state["_js_serial"].
#     If not, it resets ALL window counters to zero and records the
#     new serial. _nuke_and_go_home() increments _js_serial so the
#     next poll always resets the browser-side counters before
#     reading them.
#
#   Root cause C — _sdProctorAttached sticks True:
#     The event listeners from the previous session are already
#     attached and the guards fire immediately (blur fires when
#     Streamlit rebuilds the iframe). The serial-reset clears the
#     counters so even if an event fires during the reset window it
#     will be zeroed out before being compared.
# =============================================================

import time
import streamlit as st
import streamlit.components.v1 as components

from session_store import init_session, save_session
from gemini_quiz import ensure_quiz_data, score_all, reset_quiz_state
from proctor import (
    render_proctor_camera,
    get_proctor_snapshot,
    add_tab_switch_violation,
    add_fullscreen_exit_violation,
    acknowledge_warning,
    reset_proctor_state,
    get_max_violations,
    get_no_face_threshold,
)
from brain import (
    calculate_drift_score,
    calculate_entropy,
    calculate_career_match,
    calculate_readiness_score,
    get_next_skill,
    get_urgency_level,
    calculate_focus_debt,
    get_peer_placement_rate,
)

try:
    from streamlit_autorefresh import st_autorefresh
    HAS_AUTOREFRESH = True
except Exception:
    HAS_AUTOREFRESH = False

try:
    from streamlit_js_eval import streamlit_js_eval
    HAS_JS_EVAL = True
except Exception:
    HAS_JS_EVAL = False


# =============================================================
# PAGE CONFIG
# =============================================================

st.set_page_config(
    page_title="SkillDrift - Proctored Quiz",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_session()

MAX_VIOLATIONS    = get_max_violations()
NO_FACE_THRESHOLD = int(get_no_face_threshold())


# =============================================================
# HELPERS
# =============================================================

def _nuke_and_go_home():
    """Wipe ALL state — student identity, quiz, proctor — so home
    page and skill-input page are completely blank on next visit.
    Also bumps _js_serial so the next JS poll resets window counters.
    """
    reset_proctor_state()
    reset_quiz_state(full=True)

    # Wipe every key except the session-file identifier (_sid*).
    for k in list(st.session_state.keys()):
        if not k.startswith("_sid"):
            st.session_state.pop(k, None)

    # Bump the JS reset serial so the browser-side counters are wiped
    # on the very next poll, before any comparison happens.
    st.session_state["_js_serial"] = int(time.time() * 1000)

    # Minimal boolean defaults so save_session() writes clean state.
    st.session_state["quiz_terminated"] = False
    st.session_state["quiz_started"]    = False
    st.session_state["quiz_complete"]   = False

    save_session()


def _js(code: str, key: str):
    """Fire JS expression silently."""
    if not HAS_JS_EVAL:
        return
    try:
        streamlit_js_eval(js_expressions=code, key=key)
    except Exception:
        pass


def _fs_enter():
    return (
        "(function(){"
        "var d=window.parent.document.documentElement;"
        "try{"
        "  if(d.requestFullscreen) d.requestFullscreen();"
        "  else if(d.webkitRequestFullscreen) d.webkitRequestFullscreen();"
        "  else if(d.msRequestFullscreen) d.msRequestFullscreen();"
        "}catch(e){} return 1;})()"
    )


def _fs_exit_and_home():
    return (
        "(function(){"
        "if(document.exitFullscreen) document.exitFullscreen();"
        "window.parent.location.href=window.parent.location.pathname;"
        "})()"
    )


# =============================================================
# STEP 0 — ALWAYS remove sd-in-test from body on every page load.
#
# This runs unconditionally so that even if the student arrives at
# the pre-start gate or the terminated screen after a previous test
# session, the wide-layout body class is not left over from before.
# The in-test section (step 6) re-adds it only when actually needed.
# =============================================================

components.html(
    "<script>"
    "(function(){"
    "  var b=window.parent.document.body;"
    "  b.classList.remove('sd-in-test');"
    "})();"
    "</script>",
    height=0,
)


# =============================================================
# CSS
# =============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800;900&family=Inter:wght@400;500;600;700&display=swap');

[data-testid="stSidebarNav"],
[data-testid="collapsedControl"],
[data-testid="stExpandSidebar"],
[data-testid="stSidebarCollapseButton"],
section[data-testid="stSidebar"],
header[data-testid="stHeader"],
.stDeployButton, #MainMenu, footer { display: none !important; }

html, body, .stApp {
  background: #f6fafe;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  -webkit-user-select: none; user-select: none;
}
input, textarea { -webkit-user-select: text !important; user-select: text !important; }

/* Hide all zero-height utility iframes (body-class injectors, JS runners).
   These are components.html(height=0) calls and must not create visual gaps. */
/* Hide utility iframes (components.html height=0) but NOT inside the cam shell. */
.element-container > iframe[height="0"],
[data-testid="stCustomComponentV1"] > iframe[height="0"] {
  display: none !important;
  height: 0 !important;
  width: 0 !important;
  position: absolute !important;
  pointer-events: none !important;
}

/* Always show iframes inside the camera panel — never hide them. */
.sd-cam-shell iframe {
  display: block !important;
  width: 100% !important;
  height: auto !important;
}

/* Default (pre-test / terminated) layout — centred narrow */
.block-container {
  padding-top:    1.5rem !important;
  padding-bottom: 3rem   !important;
  max-width:      760px  !important;
  margin-left:    auto   !important;
  margin-right:   auto   !important;
  padding-left:   2rem   !important;
  padding-right:  2rem   !important;
}

/* In-test layout — wide with right gutter for camera panel */
body.sd-in-test .block-container {
  max-width:     1080px  !important;
  padding-right: 22rem   !important;
}

.element-container:empty,
.element-container:has(> div:empty) { display: none !important; }

/* ---- Terminated / centred wrapper ---- */
/* Used for terminated screen and error states that must be centred
   even though layout="wide" means .block-container fills the viewport. */
.sd-centred-page {
  max-width: 680px;
  margin: 60px auto 0 auto;
}

/* ---- Assessment header ---- */
.q-header {
  background: #002c98; color: #fff;
  border-radius: 12px; padding: 18px 24px;
  display: flex; justify-content: space-between; align-items: center;
  margin: 8px 0 22px 0; flex-wrap: wrap; gap: 10px;
}
.q-header .title {
  font-family: 'Manrope', sans-serif; font-size: 1.0rem;
  font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase;
}
.q-header .sub { font-size: 0.78rem; opacity: 0.88; margin-top: 3px; }
.q-header .vio-badge {
  background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.25);
  border-radius: 20px; padding: 6px 16px;
  font-size: 0.78rem; font-weight: 700; white-space: nowrap;
}
.q-header .vio-badge.warn { background: #f59e0b; color: #1a1a1a; border-color: #f59e0b; }
.q-header .vio-badge.bad  { background: #dc2626; color: #fff;    border-color: #dc2626; }

/* ---- Pre-start panel ---- */
.pre-panel {
  background: #fff; border: 1px solid #e2e8f0;
  border-radius: 14px; padding: 32px 36px;
  margin-bottom: 24px; box-shadow: 0 2px 12px rgba(23,28,31,0.04);
}
.pre-panel .h {
  font-family: 'Manrope', sans-serif; font-size: 1.25rem;
  font-weight: 800; color: #171c1f; margin-bottom: 8px;
}
.pre-panel .p { font-size: 0.92rem; color: #515f74; line-height: 1.6; margin-bottom: 18px; }
.pre-panel .checks {
  display: grid; grid-template-columns: repeat(2,1fr); gap: 10px; margin-bottom: 18px;
}
.pre-panel .check {
  background: #eef2ff; border-left: 3px solid #002c98;
  border-radius: 6px; padding: 11px 14px;
  font-size: 0.86rem; color: #171c1f; font-weight: 600;
}
.pre-panel .footnote {
  font-size: 0.83rem; color: #515f74; background: #f6fafe;
  border-radius: 8px; padding: 12px 16px;
  border: 1px solid #e2e8f0; line-height: 1.6;
}

/* ---- Starting overlay ---- */
.sd-starting-overlay {
  position: fixed; inset: 0; background: #f6fafe;
  z-index: 99999; display: flex; align-items: center; justify-content: center;
}
.sd-starting-card {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 14px;
  padding: 36px 44px; text-align: center; box-shadow: 0 8px 30px rgba(23,28,31,0.07);
}
.sd-starting-card .h {
  font-family: 'Manrope', sans-serif; font-size: 1.08rem;
  font-weight: 800; color: #002c98; margin-bottom: 6px;
}
.sd-starting-card .p { font-size: 0.88rem; color: #515f74; }
.sd-starting-spin {
  width: 36px; height: 36px; border: 3px solid #e2e8f0;
  border-top-color: #002c98; border-radius: 50%;
  margin: 0 auto 18px auto; animation: sd-spin 0.85s linear infinite;
}
@keyframes sd-spin { to { transform: rotate(360deg); } }

/* ---- Rules strip ---- */
.q-instr {
  font-size: 0.84rem; color: #515f74; margin: 0 0 20px 0;
  padding: 12px 16px; background: #fff;
  border: 1px solid #e2e8f0; border-left: 3px solid #002c98;
  border-radius: 8px; line-height: 1.55;
}
.q-instr b { color: #171c1f; }

/* ---- Cam/face-wait notice ---- */
.cam-wait {
  background: #fff; border: 1px solid #e2e8f0;
  border-left: 4px solid #f59e0b; border-radius: 10px;
  padding: 20px 24px; margin-bottom: 20px;
}
.cam-wait .h {
  font-family: 'Manrope', sans-serif; font-size: 1.0rem;
  font-weight: 800; color: #171c1f; margin-bottom: 6px;
}
.cam-wait .p { font-size: 0.88rem; color: #515f74; line-height: 1.6; }

/* ---- Terminated card ---- */
.q-terminated {
  background: #fff5f5; border: 1.5px solid #dc2626;
  border-radius: 12px; padding: 32px 28px;
  text-align: center; margin-bottom: 20px;
}
.q-terminated .title {
  font-family: 'Manrope', sans-serif; font-size: 1.4rem;
  font-weight: 800; color: #991b1b; margin-bottom: 12px;
}
.q-terminated .body { font-size: 0.92rem; color: #515f74; line-height: 1.65; margin-bottom: 8px; }

/* ---- Question cards ---- */
.q-card {
  background: #fff; border: 1px solid #e2e8f0;
  border-radius: 10px; padding: 16px 20px; margin: 18px 0 0 0;
}
.q-card .skill {
  font-family: 'Manrope', sans-serif; font-size: 1.0rem;
  font-weight: 800; color: #002c98;
}
.q-card .meta { font-size: 0.78rem; color: #515f74; margin-top: 3px; }
.q-question {
  font-size: 0.93rem; font-weight: 600; color: #171c1f;
  margin: 18px 0 4px 0; line-height: 1.5;
}
.q-question .qnum { color: #002c98; font-weight: 800; }

div[data-testid="stRadio"] > div[role="radiogroup"] {
  display: grid !important;
  grid-template-columns: repeat(2,minmax(0,1fr)) !important;
  gap: 8px 20px !important; width: 100% !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label {
  background: #f6fafe; border: 1px solid #e2e8f0;
  border-radius: 8px; padding: 10px 14px !important; margin: 0 !important;
  font-size: 0.88rem !important; color: #171c1f !important;
  white-space: normal !important; line-height: 1.45 !important;
  transition: border-color 0.12s, background 0.12s;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
  border-color: #002c98; background: #eef2ff;
}
.q-fallback-badge {
  background: #fff7ed; color: #9a3412; border: 1px solid #fdba74;
  border-radius: 6px; padding: 2px 8px;
  font-size: 0.68rem; font-weight: 700; margin-left: 8px; vertical-align: middle;
}

/* ---- Buttons ---- */
.stButton > button, .stForm button {
  border-radius: 8px; border: 1.5px solid #e2e8f0; background: #fff;
  color: #171c1f; font-weight: 600; font-size: 0.92rem;
  padding: 0.6rem 1.1rem !important; height: 44px !important; min-height: 44px !important;
}
.stButton > button:hover, .stForm button:hover { background: #f0f4f8; }
.stButton > button[kind="primary"], .stForm button[kind="primary"] {
  background: #002c98; color: #fff; border-color: #002c98; font-weight: 700;
}
.stButton > button[kind="primary"]:hover,
.stForm button[kind="primary"]:hover { background: #0038bf; border-color: #0038bf; }

/* ---- Fixed camera panel ---- */
.sd-cam-shell {
  position: fixed !important; top: 14px !important; right: 14px !important;
  width: 290px !important; z-index: 9999 !important;
  background: #fff !important; border: 1px solid #e2e8f0 !important;
  border-top: 3px solid #002c98 !important; border-radius: 10px !important;
  padding: 12px 14px !important; box-shadow: 0 4px 20px rgba(23,28,31,0.09) !important;
  max-height: calc(100vh - 28px) !important; overflow-y: auto !important;
}
.sd-cam-shell .sd-cam-title {
  font-family: 'Manrope', sans-serif; font-size: 0.68rem; font-weight: 800;
  color: #002c98; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 8px;
}
.sd-cam-shell video {
  max-height: 160px !important; width: 100% !important;
  border-radius: 8px !important; background: #000 !important; pointer-events: none !important;
}
.sd-cam-shell video::-webkit-media-controls,
.sd-cam-shell video::-webkit-media-controls-enclosure,
.sd-cam-shell video::-webkit-media-controls-panel,
.sd-cam-shell video::-webkit-media-controls-play-button,
.sd-cam-shell video::-webkit-media-controls-timeline,
.sd-cam-shell video::-webkit-media-controls-mute-button,
.sd-cam-shell video::-webkit-media-controls-fullscreen-button,
.sd-cam-shell video::-internal-media-controls-overflow-button {
  display: none !important; opacity: 0 !important; pointer-events: none !important;
}
.sd-cam-shell button, .sd-cam-shell select { display: none !important; }
.sd-cam-shell iframe { width: 100% !important; }
.sd-cam-shell .sd-cam-status {
  margin-top: 10px; background: #f6fafe; border: 1px solid #e2e8f0;
  border-radius: 8px; padding: 10px 12px; font-size: 0.73rem;
  color: #171c1f; line-height: 1.7;
}
.sd-cam-shell .sd-cam-status .row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 2px 0; border-bottom: 1px solid #f0f4f8;
}
.sd-cam-shell .sd-cam-status .row:last-child { border-bottom: none; }
.sd-cam-shell .sd-cam-status .lbl { color: #515f74; }
.sd-cam-shell .sd-cam-status .val { font-weight: 700; }

/* ---- Warning modal ---- */
.sd-warn-overlay {
  position: fixed; inset: 0; background: rgba(15,23,42,0.60);
  z-index: 100000; display: flex; align-items: center; justify-content: center;
}
.sd-warn-card {
  background: #fff; border-radius: 14px; padding: 28px 30px 20px 30px;
  width: 460px; max-width: 92vw; text-align: center;
  border-top: 5px solid #f59e0b; box-shadow: 0 24px 60px rgba(0,0,0,0.28);
}
.sd-warn-card.terminate { border-top-color: #dc2626; }
.sd-warn-card .h {
  font-family: 'Manrope', sans-serif; font-size: 1.15rem;
  font-weight: 800; color: #991b1b; margin-bottom: 12px;
}
.sd-warn-card .p { font-size: 0.92rem; color: #171c1f; line-height: 1.6; margin-bottom: 18px; }
.sd-warn-ack-wrap {
  position: fixed; top: 50%; left: 50%; transform: translate(-50%,88px);
  z-index: 100001; width: 380px; max-width: 88vw;
}
</style>
""", unsafe_allow_html=True)


# =============================================================
# 1. GUARDS
# =============================================================

if not st.session_state.get("student_name"):
    st.warning("Please enter your name on the previous page first.")
    if st.button("Go Back"):
        st.switch_page("pages/02_skill_input.py")
    st.stop()

if not st.session_state.get("selected_skills"):
    st.warning("Please select your skills first.")
    if st.button("Go Back"):
        st.switch_page("pages/02_skill_input.py")
    st.stop()

if st.session_state.get("quiz_complete"):
    st.switch_page("pages/03_drift_score.py")
    st.stop()


# =============================================================
# 2. TERMINATED SCREEN
#    Rendered inside .sd-centred-page so it is always centred
#    regardless of whether body.sd-in-test is still set.
# =============================================================

snap = get_proctor_snapshot()

if snap["violations"] >= MAX_VIOLATIONS:
    st.session_state["quiz_terminated"] = True
    save_session()

if st.session_state.get("quiz_terminated"):
    st.markdown('<div class="sd-centred-page">', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="q-terminated">
          <div class="title">Test Terminated</div>
          <div class="body">
            Your test was terminated because you reached the maximum of
            {MAX_VIOLATIONS} proctoring violations. Reasons include:
            face not detected for more than {NO_FACE_THRESHOLD} seconds,
            switching tabs, or exiting fullscreen.
          </div>
          <div class="body">
            All session data has been cleared. Click below to start
            completely from the beginning.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "Return to Home and Start Over",
        type="primary",
        use_container_width=True,
        key="qz_terminate_home",
    ):
        _nuke_and_go_home()
        _js(_fs_exit_and_home(), "terminate_redirect")
        st.switch_page("pages/01_home.py")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


# =============================================================
# 3. GENERATE QUIZ DATA
# =============================================================

quiz_data = ensure_quiz_data(st.session_state["selected_skills"])
if not quiz_data:
    st.markdown('<div class="sd-centred-page">', unsafe_allow_html=True)
    st.error("Failed to generate quiz questions. Please go back and try again.")
    if st.button("Go Back"):
        st.switch_page("pages/02_skill_input.py")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


# =============================================================
# 4. STARTING OVERLAY
# =============================================================

if st.session_state.get("_starting") and not st.session_state.get("quiz_started"):
    st.session_state["quiz_started"] = True
    save_session()

if st.session_state.get("_starting") and not st.session_state.get("_starting_dismissed"):
    st.markdown(
        """
        <div class="sd-starting-overlay">
          <div class="sd-starting-card">
            <div class="sd-starting-spin"></div>
            <div class="h">Starting proctored test</div>
            <div class="p">Entering fullscreen and activating camera...</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    time.sleep(0.35)
    st.session_state["_starting_dismissed"] = True
    save_session()
    st.rerun()


# =============================================================
# 5. PRE-START GATE
# =============================================================

if not st.session_state.get("quiz_started"):
    student_name    = st.session_state["student_name"]
    selected_skills = st.session_state["selected_skills"]

    # Reset proctor in-memory state cleanly the first time we reach
    # the gate. This also clears any leftover violations from a
    # previous terminated session that still live in the proctor module.
    if not st.session_state.get("_proctor_reset_done"):
        reset_proctor_state()
        st.session_state["_proctor_reset_done"] = True

    # Make sure the JS serial is initialised so the first poll knows
    # what baseline to compare against.
    if "_js_serial" not in st.session_state:
        st.session_state["_js_serial"] = int(time.time() * 1000)

    total_q = sum(len(x["questions"]) for x in quiz_data)

    st.markdown(
        f"""
        <div class="q-header">
          <div>
            <div class="title">SkillDrift Proctored Assessment</div>
            <div class="sub">
              Candidate: {student_name} &nbsp;&middot;&nbsp;
              Skills: {len(quiz_data)} &nbsp;&middot;&nbsp;
              Total questions: {total_q}
            </div>
          </div>
          <div class="vio-badge">Ready to start</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="pre-panel">
          <div class="h">Before you begin</div>
          <div class="p">
            When you click <strong>Start Proctored Test</strong> the page will
            enter fullscreen and the camera will activate automatically.
            Confirm the following before starting:
          </div>
          <div class="checks">
            <div class="check">Camera permission allowed in browser</div>
            <div class="check">Face clearly visible and well-lit</div>
            <div class="check">No other tabs open</div>
            <div class="check">Phone kept away from desk</div>
          </div>
          <div class="footnote">
            Each violation — face missing for more than {NO_FACE_THRESHOLD}
            seconds, switching tabs, or exiting fullscreen — records a warning.
            The test terminates after {MAX_VIOLATIONS} violations. The quiz
            unlocks automatically once your face is detected.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        start_clicked = st.button(
            "Start Proctored Test",
            type="primary",
            use_container_width=True,
            key="start_proctored_test",
        )
    with col2:
        cancel_pre = st.button(
            "Cancel and Go Back",
            use_container_width=True,
            key="pre_cancel",
        )

    if cancel_pre:
        _nuke_and_go_home()
        st.switch_page("pages/01_home.py")

    if start_clicked:
        # Generate a new JS serial before entering the test so the
        # first poll resets the browser-side counters to zero and
        # sets seen_ts/seen_fx to zero simultaneously.
        new_serial = int(time.time() * 1000)
        st.session_state["_js_serial"] = new_serial
        st.session_state["_seen_ts"]   = 0
        st.session_state["_seen_fx"]   = 0
        save_session()

        # Request fullscreen. Counter reset is handled by the new serial.
        _js(_fs_enter(), "enter_fs_start")

        st.session_state["_starting"] = True
        save_session()
        st.rerun()

    st.stop()


# =============================================================
# 6. IN-TEST — add body class for wide layout
#    This is placed AFTER the pre-start gate so it only fires
#    when we are actually in the test.
# =============================================================

selected_skills = st.session_state["selected_skills"]
student_name    = st.session_state["student_name"]

components.html(
    "<script>"
    "(function(){"
    "  var b=window.parent.document.body;"
    "  if(!b.classList.contains('sd-in-test')) b.classList.add('sd-in-test');"
    "})();"
    "</script>",
    height=0,
)


# =============================================================
# 7. CAMERA — rendered ALWAYS before any st.stop()
#    The WebRTC iframe must exist in the DOM on every rerun,
#    even while a warning modal is shown, so the WebRTC session
#    does not drop after violation acknowledgement.
# =============================================================

cam_container = st.container()
with cam_container:
    st.markdown(
        '<div class="sd-cam-title">Live Camera Monitor</div>',
        unsafe_allow_html=True,
    )
    try:
        render_proctor_camera()
    except Exception:
        pass

# Re-read snapshot after camera has had a chance to process frames.
snap = get_proctor_snapshot()

cam_running    = (
    snap["running"]
    and snap["last_frame_time"] is not None
    and (time.time() - snap["last_frame_time"]) < 5
)
face_present   = snap["face_present"] and cam_running
violations     = snap["violations"]
no_face_streak = snap["no_face_streak"]

face_status  = "Detected"   if face_present else "Not detected"
face_color   = "#15803d"    if face_present else "#dc2626"
cam_status   = "Active"     if cam_running  else "Starting up..."
cam_color    = "#15803d"    if cam_running  else "#f59e0b"
streak_color = "#dc2626" if no_face_streak > NO_FACE_THRESHOLD * 0.55 else "#515f74"
rec_html = (
    "<span style='color:#dc2626;font-weight:800;'>&#9679; Recording</span>"
    if cam_running else
    "<span style='color:#f59e0b;'>Starting up...</span>"
)

with cam_container:
    st.markdown(
        f"""
        <div class="sd-cam-status">
          <div class="row">
            <span class="lbl">Status</span>
            <span class="val">{rec_html}</span>
          </div>
          <div class="row">
            <span class="lbl">Camera</span>
            <span class="val" style="color:{cam_color};">{cam_status}</span>
          </div>
          <div class="row">
            <span class="lbl">Face</span>
            <span class="val" style="color:{face_color};">{face_status}</span>
          </div>
          <div class="row">
            <span class="lbl">No-face streak</span>
            <span class="val" style="color:{streak_color};">
              {no_face_streak:.1f}s / {NO_FACE_THRESHOLD}s
            </span>
          </div>
          <div class="row">
            <span class="lbl">Violations</span>
            <span class="val" style="color:{'#dc2626' if violations>=1 else '#171c1f'};">
              {violations} / {MAX_VIOLATIONS}
            </span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Pin the WebRTC block as sd-cam-shell
components.html(
    """
    <script>
    (function(){
      var doc=window.parent.document;
      function pin(){
        var blocks=doc.querySelectorAll('[data-testid="stVerticalBlock"]');
        var target=null;
        for(var i=0;i<blocks.length;i++){
          var b=blocks[i];
          if(b.querySelector('iframe[title*="webrtc"],iframe[title*="streamlit_webrtc"]')){
            var nested=b.querySelectorAll('[data-testid="stVerticalBlock"]');
            var deeper=false;
            for(var j=0;j<nested.length;j++){
              if(nested[j]!==b &&
                 nested[j].querySelector('iframe[title*="webrtc"],iframe[title*="streamlit_webrtc"]')){
                deeper=true; break;
              }
            }
            if(!deeper){target=b;break;}
          }
        }
        if(!target) return false;
        if(!target.classList.contains('sd-cam-shell'))
          target.classList.add('sd-cam-shell');
        target.querySelectorAll('video').forEach(function(v){
          try{
            v.removeAttribute('controls'); v.controls=false;
            v.disablePictureInPicture=true;
            v.setAttribute('disablePictureInPicture','');
            v.setAttribute('controlslist','nodownload nofullscreen noremoteplayback');
          }catch(e){}
        });
        target.querySelectorAll('button,select').forEach(function(el){
          el.style.setProperty('display','none','important');
        });
        return true;
      }
      var tries=0;
      var t=setInterval(function(){ tries++; pin(); if(tries>60) clearInterval(t); },100);
    })();
    </script>
    """,
    height=0,
)


# =============================================================
# 8. WARNING MODAL
#    Camera already rendered above — stays alive through st.stop().
# =============================================================

pending = snap.get("pending_warning") or ""

if pending:
    is_final  = snap["violations"] >= MAX_VIOLATIONS
    card_cls  = "sd-warn-card terminate" if is_final else "sd-warn-card"
    ack_label = "Return to Home and Start Over" if is_final else "I understand, continue test"

    st.markdown(
        f"""
        <div class="sd-warn-overlay">
          <div class="{card_cls}">
            <div class="h">{"TEST TERMINATED" if is_final else "PROCTORING WARNING"}</div>
            <div class="p">{pending}</div>
          </div>
        </div>
        <div class="sd-warn-ack-wrap" id="sd-warn-ack-wrap"></div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div id="sd-warn-ack-anchor"></div>', unsafe_allow_html=True)

    ack_clicked = st.button(
        ack_label,
        type="primary",
        use_container_width=True,
        key=f"ack_{int(snap.get('pending_warning_at', 0))}",
    )

    components.html(
        """
        <script>
        (function(){
          var doc=window.parent.document;
          function move(){
            var anchor=doc.getElementById('sd-warn-ack-anchor');
            var dest=doc.getElementById('sd-warn-ack-wrap');
            if(!anchor||!dest) return false;
            var block=anchor.closest('[data-testid="stVerticalBlock"]')||anchor.parentElement;
            var btn=block?block.querySelector('button'):null;
            if(!btn) return false;
            var holder=btn.closest('[data-testid="stButton"]')||
                       btn.closest('.element-container')||btn.parentElement;
            if(holder&&dest.firstChild!==holder) dest.appendChild(holder);
            return true;
          }
          var n=0;
          var t=setInterval(function(){ n++; if(move()||n>30) clearInterval(t); },40);
        })();
        </script>
        """,
        height=0,
    )

    if ack_clicked:
        if is_final:
            _nuke_and_go_home()
            _js(_fs_exit_and_home(), "terminate_ack_redirect")
            st.switch_page("pages/01_home.py")
        else:
            acknowledge_warning()
            _js(_fs_enter(), f"refs_{int(snap.get('pending_warning_at', 0))}")
            save_session()
            st.rerun()

    st.stop()


# =============================================================
# 9. AUTOREFRESH + JS PROCTOR BRIDGE
#
# The JS poll uses a serial-number mechanism to reliably reset
# window-level counters after a termination/restart:
#
#   Python writes _js_serial = <timestamp> into session_state.
#   JS reads window._sdSerial and compares it to the value passed
#   from Python. If they differ:
#     - window._sdTabSwitches = 0
#     - window._sdFsExits     = 0
#     - window._sdLastEventAt = 0
#     - window._sdSerial      = new serial
#   Only THEN does the JS return the counter values.
#
# Because _nuke_and_go_home() bumps _js_serial, the very first poll
# after a restart always resets the counters to zero before returning
# them, so no stale events from the previous session are counted.
# =============================================================

if HAS_AUTOREFRESH:
    st_autorefresh(interval=2500, key="quiz_autorefresh")

# Pass the current serial to JS so it can detect a reset.
current_serial = st.session_state.get("_js_serial", 0)

if HAS_JS_EVAL:
    js_poll = f"""
    (function(){{
      var w=window.parent, d=w.document, root=d.documentElement;
      var newSerial={current_serial};

      function reqFs(){{
        if(d.fullscreenElement) return;
        try{{
          if(root.requestFullscreen)            root.requestFullscreen();
          else if(root.webkitRequestFullscreen) root.webkitRequestFullscreen();
          else if(root.msRequestFullscreen)     root.msRequestFullscreen();
        }}catch(e){{}}
      }}

      // Serial-based counter reset: if Python bumped the serial
      // (new test session), wipe all browser-side counters first.
      if(w._sdSerial !== newSerial){{
        w._sdTabSwitches     = 0;
        w._sdFsExits         = 0;
        w._sdLastEventAt     = 0;
        w._sdProctorAttached = false;   // Force re-attach of listeners
        w._sdSerial          = newSerial;
      }}

      if(!w._sdProctorAttached){{
        w._sdProctorAttached = true;

        function bumpTab(){{
          var now=Date.now();
          if(now-w._sdLastEventAt<1500) return;
          w._sdLastEventAt=now; w._sdTabSwitches=(w._sdTabSwitches||0)+1;
        }}
        function bumpFs(){{
          var now=Date.now();
          if(now-w._sdLastEventAt<1500) return;
          w._sdLastEventAt=now; w._sdFsExits=(w._sdFsExits||0)+1;
        }}

        d.addEventListener('visibilitychange',function(){{ if(d.hidden) bumpTab(); }});
        w.addEventListener('blur',function(){{ bumpTab(); }});
        d.addEventListener('fullscreenchange',function(){{
          if(!d.fullscreenElement){{
            bumpFs();
            var os=function(){{ reqFs();
              d.removeEventListener('click',os,true);
              d.removeEventListener('keydown',os,true);
            }};
            d.addEventListener('click',os,true);
            d.addEventListener('keydown',os,true);
          }}
        }});

        d.addEventListener('contextmenu',function(e){{e.preventDefault();}},true);
        d.addEventListener('copy',function(e){{e.preventDefault();}},true);
        d.addEventListener('cut',function(e){{e.preventDefault();}},true);
        d.addEventListener('paste',function(e){{e.preventDefault();}},true);
        d.addEventListener('keydown',function(e){{
          var k=(e.key||'').toLowerCase();
          if(k==='escape'||k==='esc'){{try{{e.preventDefault();e.stopPropagation();}}catch(x){{}}}}
          if((e.ctrlKey||e.metaKey)&&
             ['c','v','x','a','p','s','u','w','t','n','r'].indexOf(k)>=0){{
            e.preventDefault(); e.stopPropagation();
          }}
          if(k==='f11'||k==='f12'){{e.preventDefault();e.stopPropagation();}}
          if(e.ctrlKey&&e.shiftKey&&['i','j','c'].indexOf(k)>=0){{
            e.preventDefault();e.stopPropagation();
          }}
        }},true);
      }}

      if(!d.fullscreenElement){{
        var os2=function(){{ reqFs();
          d.removeEventListener('click',os2,true);
          d.removeEventListener('keydown',os2,true);
        }};
        d.addEventListener('click',os2,true);
        d.addEventListener('keydown',os2,true);
      }}

      return [w._sdTabSwitches||0, w._sdFsExits||0];
    }})()
    """
    js_result = streamlit_js_eval(
        js_expressions=js_poll,
        key="proctor_js_poll",
        want_output=True,
    )
    if isinstance(js_result, list) and len(js_result) >= 2:
        ts = int(js_result[0] or 0)
        fx = int(js_result[1] or 0)
        prev_ts = st.session_state.get("_seen_ts", 0)
        prev_fx = st.session_state.get("_seen_fx", 0)
        if ts > prev_ts:
            add_tab_switch_violation()
            st.session_state["_seen_ts"] = ts
        if fx > prev_fx:
            add_fullscreen_exit_violation()
            st.session_state["_seen_fx"] = fx
        snap = get_proctor_snapshot()
        if snap["violations"] >= MAX_VIOLATIONS:
            st.session_state["quiz_terminated"] = True
            save_session()
            st.rerun()


# =============================================================
# 10. IN-TEST HEADER
# =============================================================

total_q   = sum(len(x["questions"]) for x in quiz_data)
vio_class = "vio-badge"
if   violations >= MAX_VIOLATIONS: vio_class += " bad"
elif violations >= 1:              vio_class += " warn"

st.markdown(
    f"""
    <div class="q-header">
      <div>
        <div class="title">SkillDrift Proctored Assessment</div>
        <div class="sub">
          Candidate: {student_name} &nbsp;&middot;&nbsp;
          Skills: {len(quiz_data)} &nbsp;&middot;&nbsp;
          Questions: {total_q}
        </div>
      </div>
      <div class="{vio_class}">Violations: {violations} / {MAX_VIOLATIONS}</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =============================================================
# 11. RULES STRIP
# =============================================================

st.markdown(
    f"""
    <div class="q-instr">
      <b>Rules.</b> Stay in fullscreen. Keep your face clearly visible.
      Do not switch tabs or windows. Right-click, copy, paste, and
      developer tools are disabled. Each violation shows a warning;
      the test terminates after {MAX_VIOLATIONS} violations.
    </div>
    """,
    unsafe_allow_html=True,
)


# =============================================================
# 12. CAM-WAIT / FACE-WAIT NOTICE
# =============================================================

if not cam_running:
    st.markdown(
        """
        <div class="cam-wait">
          <div class="h">Waiting for camera</div>
          <div class="p">
            The camera monitor is loading in the top-right corner.
            Allow camera access when your browser prompts. The quiz
            unlocks automatically once your face is detected.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
elif not face_present:
    st.markdown(
        f"""
        <div class="cam-wait">
          <div class="h">Face not detected</div>
          <div class="p">
            Camera is active but your face is not visible. Move closer
            and ensure your face is well-lit. The quiz unlocks once your
            face is detected. A violation is recorded after
            {NO_FACE_THRESHOLD} seconds without a face.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================
# 13. QUIZ FORM — Submit only, no Cancel
# =============================================================

quiz_unlocked = cam_running and face_present

# ------------------------------------------------------------------
# Answer persistence across violation reruns.
#
# When the camera locks (face lost) the options list switches to
# ["A. (locked)", ...]. Streamlit sees the old answer like "A. tho"
# is no longer in the new options list, so it resets index=None and
# overwrites the session_state key with None on the next interaction.
# After a violation ack rerun the answers appear gone.
#
# Fix: maintain a separate _quiz_answers dict that stores the REAL
# answers (unlocked option strings). Every time quiz_unlocked=True we
# copy current radio values into _quiz_answers. When rendering, we
# ALWAYS derive index from _quiz_answers (not from the radio key
# directly) so the real answer is preserved across lock/unlock cycles.
# ------------------------------------------------------------------

if "_quiz_answers" not in st.session_state:
    st.session_state["_quiz_answers"] = {}

# Snapshot current answers while unlocked before rendering the form.
if quiz_unlocked:
    for si, itm in enumerate(quiz_data):
        for qi in range(len(itm.get("questions", []))):
            k = f"q_{si}_{qi}"
            v = st.session_state.get(k)
            if v and not v.startswith("A. (locked)"):
                st.session_state["_quiz_answers"][k] = v

with st.form("skill_quiz_form", clear_on_submit=False):
    for skill_idx, item in enumerate(quiz_data):
        skill     = item["skill"]
        level     = item["level"]
        questions = item.get("questions", [])
        source    = item.get("source", "gemini")

        badge = ""
        if source == "fallback":
            badge = "<span class='q-fallback-badge'>Self-assessment</span>"

        st.markdown(
            f"""
            <div class="q-card">
              <div class="skill">{skill}{badge}</div>
              <div class="meta">
                Claimed level: <b>{level}</b> &nbsp;&middot;&nbsp;
                {len(questions)} question{'s' if len(questions)!=1 else ''}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not questions:
            st.warning(
                f"No questions generated for {skill}. It will be marked Unverified."
            )
            continue

        for q_idx, q in enumerate(questions):
            key   = f"q_{skill_idx}_{q_idx}"
            qtext = (
                q.get("question", "")
                if quiz_unlocked
                else "(locked — camera must be active)"
            )
            st.markdown(
                f"<div class='q-question'>"
                f"<span class='qnum'>Q{q_idx+1}.</span> {qtext}</div>",
                unsafe_allow_html=True,
            )
            if quiz_unlocked:
                options = [
                    f"A. {q.get('option_a','')}",
                    f"B. {q.get('option_b','')}",
                    f"C. {q.get('option_c','')}",
                    f"D. {q.get('option_d','')}",
                ]
                # Restore from backup if available (survives violation reruns).
                saved = st.session_state["_quiz_answers"].get(key)
                try:
                    idx = options.index(saved) if saved in options else None
                except Exception:
                    idx = None
                # Keep session_state in sync with backup so the radio
                # renders with the correct selection.
                if idx is not None:
                    st.session_state[key] = options[idx]
            else:
                options = ["A. (locked)", "B. (locked)", "C. (locked)", "D. (locked)"]
                idx = None
                # Do NOT update session_state[key] when locked — the
                # backup in _quiz_answers still holds the real answer.

            st.radio(
                label=f"Q{skill_idx+1}.{q_idx+1}",
                options=options,
                key=key,
                label_visibility="collapsed",
                index=idx,
                disabled=not quiz_unlocked,
            )

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    submitted = st.form_submit_button(
        "Submit Test and Continue",
        type="primary",
        use_container_width=True,
        disabled=not quiz_unlocked,
    )


# =============================================================
# 14. SUBMIT HANDLER
# =============================================================

if submitted and quiz_unlocked:
    save_session()
    verified = score_all(quiz_data)
    reset_proctor_state()
    _js("(document.exitFullscreen?document.exitFullscreen():null)", "exit_fs_submit")

    with st.spinner("Calculating your score and skill evaluation..."):
        try:
            drift_score, drift_label, track_counts = calculate_drift_score(verified)
            entropy_score, entropy_label           = calculate_entropy(track_counts)
            career_matches = calculate_career_match(verified)
            best_match     = career_matches[0] if career_matches else {}
            best_track     = best_match.get("track", "Unknown")
            match_pct      = best_match.get("match_pct", 0.0)
            readiness      = calculate_readiness_score(verified, best_track)
            next_skill     = get_next_skill(best_match.get("missing_skills", []), best_track)
            urgency        = get_urgency_level(st.session_state.get("semester", 4))
            debt           = calculate_focus_debt(verified, best_track)
            peer           = get_peer_placement_rate(drift_score, best_track)

            st.session_state["drift_score"]     = drift_score
            st.session_state["drift_label"]     = drift_label
            st.session_state["track_counts"]    = track_counts
            st.session_state["entropy_score"]   = entropy_score
            st.session_state["entropy_label"]   = entropy_label
            st.session_state["career_matches"]  = career_matches
            st.session_state["best_track"]      = best_track
            st.session_state["match_pct"]       = match_pct
            st.session_state["readiness_score"] = readiness
            st.session_state["next_skill_info"] = next_skill
            st.session_state["urgency_info"]    = urgency
            st.session_state["focus_debt_info"] = debt
            st.session_state["peer_info"]       = peer
        except Exception as e:
            st.error(f"Analysis error: {e}")
            st.stop()

    st.session_state["quiz_complete"] = True
    save_session()
    time.sleep(0.4)
    st.switch_page("pages/03_drift_score.py")
