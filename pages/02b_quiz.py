# pages/02b_quiz.py
# =============================================================
# SkillDrift proctored quiz - HARDENED FINAL VERSION
# =============================================================

import time
import streamlit as st
import streamlit.components.v1 as components

from session_store import init_session, save_session
from gemini_quiz import (
    ensure_quiz_data, score_all, reset_quiz_state,
)
from proctor import (
    render_proctor_camera, get_proctor_snapshot,
    add_tab_switch_violation, add_fullscreen_exit_violation,
    acknowledge_warning, reset_proctor_state, get_max_violations,
    get_no_face_threshold,
)
from brain import (
    calculate_drift_score, calculate_entropy, calculate_career_match,
    calculate_readiness_score, get_next_skill, get_urgency_level,
    calculate_focus_debt, get_peer_placement_rate,
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
# 0. CSS  (single block, no per-rerun re-injection)
# =============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800;900&family=Inter:wght@400;500;600;700&display=swap');

[data-testid="stSidebarNav"], [data-testid="collapsedControl"],
[data-testid="stExpandSidebar"], [data-testid="stSidebarCollapseButton"],
section[data-testid="stSidebar"], header[data-testid="stHeader"],
.stDeployButton, #MainMenu, footer { display: none !important; }

html, body, .stApp {
  background: #f6fafe;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  -webkit-user-select: none !important;
  -moz-user-select: none !important;
  user-select: none !important;
}
input, textarea {
  -webkit-user-select: text !important;
  user-select: text !important;
}

.block-container {
  padding-top: 1.25rem !important;
  padding-bottom: 3rem !important;
  max-width: 980px !important;
  margin-left: auto !important;
  margin-right: auto !important;
  padding-left: 2rem !important;
  padding-right: 2rem !important;
}
body.sd-test-running .block-container {
  max-width: 1100px !important;
  padding-right: 340px !important;
}

/* ---------- Header card ---------- */
.q-header {
  background: #002c98; color: #fff; border-radius: 12px;
  padding: 18px 24px; display: flex; justify-content: space-between;
  align-items: center; margin: 8px 0 22px 0; flex-wrap: wrap; gap: 12px;
}
.q-header .title {
  font-family: 'Manrope', sans-serif; font-size: 1.05rem;
  font-weight: 800; letter-spacing: 0.03em; text-transform: uppercase;
}
.q-header .sub { font-size: 0.8rem; opacity: 0.88; margin-top: 4px; }
.q-header .vio-badge {
  background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.25);
  border-radius: 20px; padding: 7px 18px; font-size: 0.78rem; font-weight: 700;
}
.q-header .vio-badge.warn { background: #f59e0b; color: #1a1a1a; border-color: #f59e0b; }
.q-header .vio-badge.bad  { background: #dc2626; color: #fff; border-color: #dc2626; }

/* ---------- Pre-start panel ---------- */
.pre-panel {
  background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px;
  padding: 32px 36px; margin: 0 0 24px 0;
}
.pre-panel .h {
  font-family: 'Manrope', sans-serif; font-size: 1.25rem;
  font-weight: 800; color: #171c1f; margin-bottom: 8px;
}
.pre-panel .p { font-size: 0.92rem; color: #515f74; line-height: 1.6; margin-bottom: 18px; }
.pre-panel .checks {
  display: grid; grid-template-columns: repeat(2, 1fr);
  gap: 10px; margin-bottom: 18px;
}
.pre-panel .check {
  background: #eef2ff; border-left: 3px solid #002c98;
  border-radius: 6px; padding: 10px 14px;
  font-size: 0.85rem; color: #171c1f; font-weight: 600;
}
.pre-panel .footnote {
  font-size: 0.82rem; color: #515f74; background: #f6fafe;
  border-radius: 8px; padding: 12px 14px;
  border: 1px solid #e2e8f0; line-height: 1.55;
}

/* ---------- Rules strip ---------- */
.q-instr {
  font-size: 0.84rem; color: #515f74; margin: 16px 0 22px 0;
  padding: 12px 16px; background: #ffffff;
  border: 1px solid #e2e8f0; border-left: 3px solid #002c98;
  border-radius: 8px; line-height: 1.55;
}
.q-instr b { color: #171c1f; }

/* ---------- Cam-wait ---------- */
.cam-wait {
  background: #ffffff; border: 1px solid #e2e8f0;
  border-left: 4px solid #f59e0b; border-radius: 10px;
  padding: 22px 26px; margin: 0 0 22px 0;
}
.cam-wait .h {
  font-family: 'Manrope', sans-serif; font-size: 1.05rem;
  font-weight: 800; color: #171c1f; margin-bottom: 6px;
}
.cam-wait .p { font-size: 0.9rem; color: #515f74; line-height: 1.6; }

/* ---------- Quiz card + 2x2 option grid ---------- */
.q-card {
  background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px;
  padding: 18px 22px; margin: 18px 0 0 0;
}
.q-card .skill {
  font-family: 'Manrope', sans-serif; font-size: 1.05rem;
  font-weight: 800; color: #002c98;
}
.q-card .meta { font-size: 0.8rem; color: #515f74; margin-top: 4px; }
.q-question {
  font-size: 0.95rem; font-weight: 600; color: #171c1f;
  margin: 22px 0 4px 0; line-height: 1.5;
}
.q-question .qnum { color: #002c98; font-weight: 800; }

div[data-testid="stRadio"] > div[role="radiogroup"] {
  display: grid !important;
  grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  gap: 8px 24px !important; width: 100% !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label {
  background: #f6fafe; border: 1px solid #e2e8f0;
  border-radius: 8px; padding: 10px 14px !important;
  margin: 0 !important; font-size: 0.9rem !important;
  color: #171c1f !important; white-space: normal !important;
  line-height: 1.45 !important; transition: all 0.12s ease;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
  border-color: #002c98; background: #eef2ff;
}

.q-fallback-badge {
  background: #fff7ed; color: #9a3412; border: 1px solid #fdba74;
  border-radius: 6px; padding: 2px 9px; font-size: 0.7rem;
  font-weight: 700; margin-left: 10px; vertical-align: middle;
}

/* ---------- Terminated ---------- */
.q-terminated {
  background: #fff5f5; border: 1.5px solid #dc2626;
  border-radius: 12px; padding: 32px; text-align: center; margin: 24px 0;
}
.q-terminated .title {
  font-family: 'Manrope', sans-serif; font-size: 1.5rem;
  font-weight: 800; color: #991b1b; margin-bottom: 14px;
}
.q-terminated .body {
  font-size: 0.95rem; color: #515f74; line-height: 1.65; margin-bottom: 8px;
}

/* ---------- Buttons ---------- */
.stButton > button, .stForm button {
  border-radius: 8px; border: 1.5px solid #e2e8f0; background: #ffffff;
  color: #171c1f; font-weight: 600; font-size: 0.92rem;
  padding: 0.62rem 1.1rem !important;
  height: 44px !important; min-height: 44px !important;
}
.stButton > button:hover, .stForm button:hover { background: #f0f4f8; }
.stButton > button[kind="primary"], .stForm button[kind="primary"] {
  background: #002c98; color: #fff; border-color: #002c98; font-weight: 700;
}
.stButton > button[kind="primary"]:hover,
.stForm button[kind="primary"]:hover { background: #0038bf; border-color: #0038bf; }

/* ---------- PINNED CAMERA SHELL ---------- */
div.sd-cam-pinned {
  position: fixed !important;
  top: 14px !important;
  right: 14px !important;
  width: 300px !important;
  z-index: 9999 !important;
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  border-top: 3px solid #002c98 !important;
  border-radius: 10px !important;
  padding: 12px 14px !important;
  box-shadow: 0 4px 16px rgba(23,28,31,0.08) !important;
  max-height: calc(100vh - 28px) !important;
  overflow-y: auto !important;
}
div.sd-cam-pinned .sd-cam-title {
  font-family: 'Manrope', sans-serif; font-size: 0.72rem;
  font-weight: 800; color: #002c98; text-transform: uppercase;
  letter-spacing: 0.06em; margin-bottom: 8px;
}
div.sd-cam-pinned [data-testid="stVerticalBlockBorderWrapper"],
div.sd-cam-pinned [data-testid="element-container"] { margin: 0 !important; }
div.sd-cam-pinned video {
  max-height: 165px !important;
  width: 100% !important;
  border-radius: 8px !important;
  background: #000 !important;
  pointer-events: none !important;  /* never let user click the video */
}
/* Kill native HTML5 media controls on the camera video. */
div.sd-cam-pinned video::-webkit-media-controls,
div.sd-cam-pinned video::-webkit-media-controls-enclosure,
div.sd-cam-pinned video::-webkit-media-controls-panel,
div.sd-cam-pinned video::-webkit-media-controls-play-button,
div.sd-cam-pinned video::-webkit-media-controls-timeline,
div.sd-cam-pinned video::-webkit-media-controls-current-time-display,
div.sd-cam-pinned video::-webkit-media-controls-time-remaining-display,
div.sd-cam-pinned video::-webkit-media-controls-mute-button,
div.sd-cam-pinned video::-webkit-media-controls-volume-slider,
div.sd-cam-pinned video::-webkit-media-controls-fullscreen-button,
div.sd-cam-pinned video::-internal-media-controls-overflow-button,
div.sd-cam-pinned video::-internal-media-controls-overlay-cast-button {
  display: none !important;
  -webkit-appearance: none !important;
  appearance: none !important;
  opacity: 0 !important;
  pointer-events: none !important;
}
div.sd-cam-pinned iframe { width: 100% !important; }

/* Compact webrtc widget controls */
div.sd-cam-pinned button {
  font-size: 0.74rem !important;
  padding: 4px 10px !important;
  min-height: 28px !important; height: 28px !important;
}
div.sd-cam-pinned select {
  font-size: 0.74rem !important; padding: 3px 6px !important;
}

/* Status panel */
div.sd-cam-pinned .sd-cam-status {
  margin-top: 10px; background: #f6fafe;
  border: 1px solid #e2e8f0; border-radius: 8px;
  padding: 10px 12px; font-size: 0.74rem;
  color: #171c1f; line-height: 1.6;
}
div.sd-cam-pinned .sd-cam-status .row {
  display: flex; justify-content: space-between; padding: 3px 0;
}
div.sd-cam-pinned .sd-cam-status .label { color: #515f74; }
div.sd-cam-pinned .sd-cam-status .val   { font-weight: 700; }

/* Hide streamlit-webrtc internal status banner */
div.sd-cam-pinned [data-testid="stStatusWidget"],
div.sd-cam-pinned [data-baseweb="notification"] { display: none !important; }

/* ---------- LOCKED CAMERA: bullet-proof control hiding ----------
   Once the camera is locked we render an opaque overlay div on top
   of the entire webrtc widget area. This blocks STOP / SELECT DEVICE
   regardless of how streamlit-webrtc structures its DOM internally.
*/
.sd-cam-locked-overlay {
  position: absolute;
  left: 0; right: 0; bottom: 0;
  height: 50px;          /* covers the controls row at the bottom */
  background: linear-gradient(180deg,
    rgba(255,255,255,0) 0%,
    rgba(255,255,255,0.85) 30%,
    rgba(255,255,255,1.0) 100%);
  z-index: 50;
  pointer-events: auto;  /* eat all clicks */
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding-bottom: 6px;
  font-family: 'Inter', sans-serif;
  font-size: 0.7rem;
  font-weight: 700;
  color: #002c98;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
div.sd-cam-pinned { position: fixed !important; }
div.sd-cam-pinned > div { position: relative; }

/* ---------- WARNING MODAL ---------- */
.sd-warn-overlay {
  position: fixed; inset: 0;
  background: rgba(15, 23, 42, 0.62);
  z-index: 100000; display: flex;
  align-items: center; justify-content: center;
}
.sd-warn-card {
  background: #ffffff; border-radius: 14px;
  padding: 30px 32px 22px 32px; width: 480px; max-width: 92vw;
  text-align: center; border-top: 5px solid #f59e0b;
  box-shadow: 0 24px 60px rgba(0,0,0,0.3);
}
.sd-warn-card .h {
  font-family: 'Manrope', sans-serif; font-size: 1.25rem;
  font-weight: 800; color: #991b1b; margin-bottom: 14px;
}
.sd-warn-card .p {
  font-size: 0.95rem; color: #171c1f; line-height: 1.6; margin-bottom: 22px;
}
.sd-warn-card .hint { font-size: 0.82rem; color: #515f74; margin-bottom: 14px; }

.sd-warn-ack-wrap {
  position: fixed; top: 50%; left: 50%;
  transform: translate(-50%, 80px);
  z-index: 100001; width: 320px; max-width: 80vw;
}

/* ---------- CONFIRM-DEVICE MODAL ---------- */
.sd-confirm-overlay {
  position: fixed; inset: 0;
  background: rgba(15, 23, 42, 0.55);
  z-index: 99998; display: flex;
  align-items: center; justify-content: center;
}
.sd-confirm-card {
  background: #ffffff; border-radius: 14px;
  padding: 28px 30px 20px 30px;
  width: 460px; max-width: 92vw; text-align: center;
  border-top: 4px solid #002c98;
  box-shadow: 0 20px 60px rgba(0,0,0,0.25);
}
.sd-confirm-card .h {
  font-family: 'Manrope', sans-serif; font-size: 1.15rem;
  font-weight: 800; color: #002c98; margin-bottom: 10px;
}
.sd-confirm-card .p {
  font-size: 0.92rem; color: #171c1f; line-height: 1.55; margin-bottom: 16px;
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
    st.success("Quiz already completed. Redirecting to your dashboard.")
    st.switch_page("pages/03_drift_score.py")
    st.stop()


# =============================================================
# 2. TERMINATED SCREEN
# (Do NOT call render_proctor_camera here - it triggers the
#  streamlit-webrtc shutdown crash. Just show the message and
#  let the user navigate away. The next page will not have
#  the widget so the camera ends naturally.)
# =============================================================

snap = get_proctor_snapshot()
st.session_state["proctor_violations"] = snap["violations"]

if snap["violations"] >= MAX_VIOLATIONS:
    st.session_state["quiz_terminated"] = True
    save_session()

if st.session_state.get("quiz_terminated"):
    st.markdown(
        f"""
        <div class="q-terminated">
          <div class="title">Test Terminated</div>
          <div class="body">
            Your test was terminated because you reached the maximum
            of {MAX_VIOLATIONS} proctoring violations. Reasons may
            include: face not detected, switching tabs or windows,
            or repeatedly exiting fullscreen.
          </div>
          <div class="body">Restart from the beginning to try again.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        if st.button("Restart from Beginning", type="primary",
                     use_container_width=True, key="qz_restart"):
            reset_quiz_state(full=True)
            reset_proctor_state()
            for k in ("quiz_terminated", "quiz_started", "_starting",
                      "_camera_locked", "_camera_confirmed",
                      "_proctor_reset_done", "_seen_ts", "_seen_fx",
                      "_confirm_cancel"):
                st.session_state.pop(k, None)
            save_session()
            if HAS_JS_EVAL:
                try:
                    streamlit_js_eval(
                        js_expressions="(document.exitFullscreen ? document.exitFullscreen() : null)",
                        key="exit_fs_term_r",
                    )
                except Exception:
                    pass
            st.switch_page("pages/01_home.py")
    with c2:
        if st.button("Go Back to Home", use_container_width=True,
                     key="qz_goback"):
            reset_quiz_state(full=True)
            reset_proctor_state()
            for k in ("quiz_terminated", "quiz_started", "_starting",
                      "_camera_locked", "_camera_confirmed",
                      "_proctor_reset_done", "_seen_ts", "_seen_fx",
                      "_confirm_cancel"):
                st.session_state.pop(k, None)
            save_session()
            if HAS_JS_EVAL:
                try:
                    streamlit_js_eval(
                        js_expressions="(document.exitFullscreen ? document.exitFullscreen() : null)",
                        key="exit_fs_term_g",
                    )
                except Exception:
                    pass
            st.switch_page("pages/01_home.py")
    st.stop()


# =============================================================
# 3. GENERATE QUESTIONS
# =============================================================

selected_skills = st.session_state["selected_skills"]
student_name    = st.session_state["student_name"]

if not st.session_state.get("_proctor_reset_done"):
    reset_proctor_state()
    st.session_state["_proctor_reset_done"] = True
    if not st.session_state.get("quiz_started"):
        st.session_state["quiz_started"] = False

quiz_data = ensure_quiz_data(selected_skills)
if not quiz_data:
    st.error("Failed to generate quiz questions. Please go back and try again.")
    if st.button("Go Back"):
        st.switch_page("pages/02_skill_input.py")
    st.stop()


# =============================================================
# 4. PRE-START GATE
# =============================================================

quiz_started = st.session_state.get("quiz_started", False)

if not quiz_started:
    # If a previous click set _starting=True but the rerun
    # hadn't yet flipped quiz_started, flip it NOW and rerun.
    # This kills the "two Start buttons" flash.
    if st.session_state.get("_starting"):
        st.session_state["quiz_started"] = True
        save_session()
        st.rerun()

    total_q = sum(len(x['questions']) for x in quiz_data)
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
            When you click <b>Start Proctored Test</b> the page will
            enter fullscreen and the camera will activate. Please
            confirm the following:
          </div>
          <div class="checks">
            <div class="check">Camera permission allowed</div>
            <div class="check">Face clearly visible</div>
            <div class="check">No other tabs open</div>
            <div class="check">Phone away from desk</div>
          </div>
          <div class="footnote">
            Each violation - face missing for more than {NO_FACE_THRESHOLD}
            seconds, switching tabs or windows, or exiting fullscreen
            - shows a warning. The test terminates only after
            {MAX_VIOLATIONS} violations.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    btn_col1, btn_col2 = st.columns(2, gap="medium")
    with btn_col1:
        start_clicked = st.button(
            "Start Proctored Test",
            type="primary",
            use_container_width=True,
            key="start_proctored_test",
        )
    with btn_col2:
        cancel_clicked_pre = st.button(
            "Cancel and Go Back",
            use_container_width=True,
            key="pre_cancel",
        )

    if cancel_clicked_pre:
        reset_quiz_state(full=False)
        reset_proctor_state()
        for k in ("_starting", "_camera_locked", "_camera_confirmed"):
            st.session_state.pop(k, None)
        save_session()
        st.switch_page("pages/01_home.py")

    if start_clicked:
        st.session_state["_starting"] = True
        st.session_state["quiz_started"] = True
        save_session()
        if HAS_JS_EVAL:
            try:
                streamlit_js_eval(
                    js_expressions=(
                        "(function(){"
                        "  var d = window.parent.document.documentElement;"
                        "  if (d.requestFullscreen) { d.requestFullscreen(); }"
                        "  else if (d.webkitRequestFullscreen) { d.webkitRequestFullscreen(); }"
                        "  else if (d.msRequestFullscreen) { d.msRequestFullscreen(); }"
                        "  return 1;"
                        "})()"
                    ),
                    key="enter_fs",
                )
            except Exception:
                pass
        st.rerun()

    st.stop()


# =============================================================
# 5. BODY CLASS  (test is running)
# =============================================================

camera_locked = st.session_state.get("_camera_locked", False)
classes = ["sd-test-running"]
if camera_locked:
    classes.append("sd-cam-locked")

components.html(
    f"""
    <script>
    (function(){{
      var b = window.parent.document.body;
      ['sd-test-running','sd-cam-locked'].forEach(function(c){{
        b.classList.remove(c);
      }});
      {''.join(f"b.classList.add('{c}');" for c in classes)}
    }})();
    </script>
    """,
    height=0,
)


# =============================================================
# 6. WARNING MODAL  (rendered FIRST, no autorefresh while open)
# =============================================================

pending = snap.get("pending_warning") or ""

if pending:
    st.markdown(
        f"""
        <div class="sd-warn-overlay">
          <div class="sd-warn-card">
            <div class="h">PROCTORING WARNING</div>
            <div class="p">{pending}</div>
            <div class="hint">Click below to acknowledge and continue the test.</div>
          </div>
        </div>
        <div class="sd-warn-ack-wrap" id="sd-warn-ack-wrap"></div>
        """,
        unsafe_allow_html=True,
    )

    ack_holder = st.empty()
    with ack_holder.container():
        st.markdown('<div id="sd-warn-ack-anchor"></div>', unsafe_allow_html=True)
        ack_clicked = st.button(
            "I understand, continue test",
            type="primary",
            use_container_width=True,
            key=f"ack_warning_{int(snap.get('pending_warning_at', 0))}",
        )

    components.html(
        """
        <script>
        (function(){
          var doc = window.parent.document;
          function move(){
            var anchor = doc.getElementById('sd-warn-ack-anchor');
            var dest   = doc.getElementById('sd-warn-ack-wrap');
            if (!anchor || !dest) return false;
            var btnBlock = anchor.closest('[data-testid="stVerticalBlock"]')
                        || anchor.parentElement;
            var btn = btnBlock ? btnBlock.querySelector('button') : null;
            if (!btn) return false;
            var holder = btn.closest('[data-testid="stButton"]')
                      || btn.closest('.element-container')
                      || btn.parentElement;
            if (holder && dest.firstChild !== holder) {
              dest.appendChild(holder);
            }
            return true;
          }
          var n = 0;
          var t = setInterval(function(){
            n++;
            if (move() || n > 20) clearInterval(t);
          }, 50);
        })();
        </script>
        """,
        height=0,
    )

    if ack_clicked:
        acknowledge_warning()
        if HAS_JS_EVAL:
            try:
                streamlit_js_eval(
                    js_expressions=(
                        "(function(){"
                        "  var d = window.parent.document.documentElement;"
                        "  if (d.requestFullscreen) { d.requestFullscreen(); }"
                        "  else if (d.webkitRequestFullscreen) { d.webkitRequestFullscreen(); }"
                        "  else if (d.msRequestFullscreen) { d.msRequestFullscreen(); }"
                        "  return 1;"
                        "})()"
                    ),
                    key=f"refs_{int(snap.get('pending_warning_at', 0))}",
                )
            except Exception:
                pass
        save_session()
        st.rerun()

    st.stop()


# =============================================================
# 7. AUTOREFRESH + JS BRIDGES (only when no warning)
# =============================================================

if HAS_AUTOREFRESH:
    st_autorefresh(interval=2500, key="quiz_autorefresh")

if HAS_JS_EVAL:
    js_attach = """
    (function() {
      var w = window.parent;
      var d = w.document;
      var root = d.documentElement;

      function reqFs() {
        if (d.fullscreenElement) return;
        try {
          if (root.requestFullscreen)        root.requestFullscreen();
          else if (root.webkitRequestFullscreen) root.webkitRequestFullscreen();
          else if (root.msRequestFullscreen)     root.msRequestFullscreen();
        } catch (e) {}
      }

      if (!w._sdProctorAttached) {
        w._sdProctorAttached = true;
        w._sdTabSwitches = 0;
        w._sdFsExits     = 0;

        d.addEventListener('visibilitychange', function() {
          if (d.hidden) { w._sdTabSwitches = (w._sdTabSwitches || 0) + 1; }
        });
        w.addEventListener('blur', function() {
          w._sdTabSwitches = (w._sdTabSwitches || 0) + 1;
        });
        d.addEventListener('fullscreenchange', function() {
          if (!d.fullscreenElement) {
            w._sdFsExits = (w._sdFsExits || 0) + 1;
            var oneShot = function() {
              reqFs();
              d.removeEventListener('click',   oneShot, true);
              d.removeEventListener('keydown', oneShot, true);
            };
            d.addEventListener('click',   oneShot, true);
            d.addEventListener('keydown', oneShot, true);
          }
        });

        d.addEventListener('contextmenu', function(e){ e.preventDefault(); }, true);
        d.addEventListener('copy',        function(e){ e.preventDefault(); }, true);
        d.addEventListener('cut',         function(e){ e.preventDefault(); }, true);
        d.addEventListener('paste',       function(e){ e.preventDefault(); }, true);
        d.addEventListener('selectstart', function(e){ e.preventDefault(); }, true);
        d.addEventListener('dragstart',   function(e){ e.preventDefault(); }, true);

        d.addEventListener('keydown', function(e){
          var k = (e.key || '').toLowerCase();
          if (k === 'escape' || k === 'esc') {
            try { e.preventDefault(); e.stopPropagation(); } catch (e2) {}
          }
          if ((e.ctrlKey || e.metaKey) && ['c','v','x','a','p','s','u','w','t','n','r'].indexOf(k) >= 0) {
            e.preventDefault(); e.stopPropagation();
          }
          if (k === 'f11' || k === 'f12') {
            e.preventDefault(); e.stopPropagation();
          }
          if (e.ctrlKey && e.shiftKey && ['i','j','c'].indexOf(k) >= 0) {
            e.preventDefault(); e.stopPropagation();
          }
        }, true);
      }

      if (!d.fullscreenElement) {
        var oneShot2 = function() {
          reqFs();
          d.removeEventListener('click',   oneShot2, true);
          d.removeEventListener('keydown', oneShot2, true);
        };
        d.addEventListener('click',   oneShot2, true);
        d.addEventListener('keydown', oneShot2, true);
      }

      // Read selected camera device label, if any.
      var camLabel = '';
      try {
        var vids = d.querySelectorAll('video');
        for (var vi = 0; vi < vids.length; vi++) {
          var v = vids[vi];
          if (v && v.srcObject && v.srcObject.getVideoTracks) {
            var ts = v.srcObject.getVideoTracks();
            if (ts && ts.length > 0 && ts[0].label) {
              camLabel = ts[0].label;
              // Also strip any native controls attribute
              try {
                v.removeAttribute('controls');
                v.controls = false;
                v.disablePictureInPicture = true;
                v.setAttribute('disablePictureInPicture','');
                v.setAttribute('controlslist','nodownload nofullscreen noremoteplayback noplaybackrate');
              } catch (eVid) {}
              break;
            }
          }
        }
      } catch (eLbl) {}

      return [w._sdTabSwitches || 0, w._sdFsExits || 0, camLabel];
    })()
    """
    js_result = streamlit_js_eval(
        js_expressions=js_attach,
        key="proctor_js_poll",
        want_output=True,
    )

    if isinstance(js_result, list) and len(js_result) >= 2:
        ts, fx = int(js_result[0] or 0), int(js_result[1] or 0)
        prev_ts = st.session_state.get("_seen_ts", 0)
        prev_fx = st.session_state.get("_seen_fx", 0)
        for _ in range(max(0, ts - prev_ts)):
            add_tab_switch_violation()
        for _ in range(max(0, fx - prev_fx)):
            add_fullscreen_exit_violation()
        st.session_state["_seen_ts"] = ts
        st.session_state["_seen_fx"] = fx
        if len(js_result) >= 3 and js_result[2]:
            st.session_state["_cam_label"] = str(js_result[2])
        snap = get_proctor_snapshot()
        st.session_state["proctor_violations"] = snap["violations"]
        if snap["violations"] >= MAX_VIOLATIONS:
            st.session_state["quiz_terminated"] = True
            save_session()
            st.rerun()


# =============================================================
# 8. HEADER (during test)
# =============================================================

violations = snap["violations"]
total_q = sum(len(x['questions']) for x in quiz_data)
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
# 9. PINNED CAMERA + STATUS PANEL
# =============================================================

st.markdown('<div id="sd-cam-wrap-marker" style="display:none;"></div>',
            unsafe_allow_html=True)

cam_container = st.container()
with cam_container:
    st.markdown('<div class="sd-cam-title">Live Camera Monitor</div>',
                unsafe_allow_html=True)
    try:
        ctx = render_proctor_camera()
    except Exception:
        ctx = None

cam_running = (
    snap["running"] and snap["last_frame_time"] is not None
    and (time.time() - snap["last_frame_time"]) < 5
)

if cam_running and not camera_locked:
    st.session_state["_camera_locked"] = True
    save_session()

face_status = "Detected" if snap["face_present"] else "Not detected"
face_color  = "#15803d" if snap["face_present"] else "#dc2626"
cam_status  = "Active" if cam_running else "Not started"
cam_color   = "#15803d" if cam_running else "#9a3412"
no_face_streak = snap["no_face_streak"]
recording_indicator = (
    "<span style='color:#dc2626;font-weight:800;'>&#9679; Recording</span>"
    if cam_running else
    "<span style='color:#9a3412;'>Awaiting camera</span>"
)
cam_label = st.session_state.get("_cam_label", "")
if cam_label and len(cam_label) > 28:
    cam_label_display = cam_label[:26] + "..."
else:
    cam_label_display = cam_label or "(none yet)"

with cam_container:
    st.markdown(
        f"""
        <div class="sd-cam-status">
          <div class="row"><span class="label">Status</span>
            <span class="val">{recording_indicator}</span></div>
          <div class="row"><span class="label">Camera</span>
            <span class="val" style="color:{cam_color};">{cam_status}</span></div>
          <div class="row"><span class="label">Device</span>
            <span class="val" title="{cam_label}">{cam_label_display}</span></div>
          <div class="row"><span class="label">Face</span>
            <span class="val" style="color:{face_color};">{face_status}</span></div>
          <div class="row"><span class="label">No-face streak</span>
            <span class="val">{no_face_streak:.1f}s / {NO_FACE_THRESHOLD}s</span></div>
          <div class="row"><span class="label">Violations</span>
            <span class="val" style="color:{'#dc2626' if violations >= 1 else '#171c1f'};">
              {violations} / {MAX_VIOLATIONS}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Pin the cam block + (when locked) inject the opaque overlay
# that physically covers STOP / SELECT DEVICE.
components.html("""
<script>
(function(){
  var doc = window.parent.document;
  function pinAndLock() {
    var blocks = doc.querySelectorAll('[data-testid="stVerticalBlock"]');
    var camBlock = null;
    for (var i = 0; i < blocks.length; i++) {
      var b = blocks[i];
      if (b.querySelector('iframe[title*="webrtc"], iframe[title*="streamlit_webrtc"]')) {
        var nested = b.querySelectorAll('[data-testid="stVerticalBlock"]');
        var deeper = false;
        for (var j = 0; j < nested.length; j++) {
          if (nested[j] !== b && nested[j].querySelector(
              'iframe[title*="webrtc"], iframe[title*="streamlit_webrtc"]')) {
            deeper = true; break;
          }
        }
        if (!deeper) { camBlock = b; break; }
      }
    }
    if (!camBlock) return false;
    if (!camBlock.classList.contains('sd-cam-pinned')) {
      camBlock.classList.add('sd-cam-pinned');
    }

    // Strip native controls from any <video> inside the cam shell.
    var vids = camBlock.querySelectorAll('video');
    for (var vi = 0; vi < vids.length; vi++) {
      var v = vids[vi];
      try {
        v.removeAttribute('controls');
        v.controls = false;
        v.disablePictureInPicture = true;
        v.setAttribute('disablePictureInPicture','');
        v.setAttribute('controlslist','nodownload nofullscreen noremoteplayback noplaybackrate');
      } catch (eVid) {}
    }

    // If body has sd-cam-locked, ensure the lock overlay exists
    // INSIDE the cam shell so it visually covers STOP/SELECT DEVICE.
    var locked = doc.body.classList.contains('sd-cam-locked');
    var existing = camBlock.querySelector('.sd-cam-locked-overlay');
    if (locked && !existing) {
      var ov = doc.createElement('div');
      ov.className = 'sd-cam-locked-overlay';
      ov.textContent = 'Camera locked for proctoring';
      ov.addEventListener('click',   function(e){ e.preventDefault(); e.stopPropagation(); }, true);
      ov.addEventListener('mousedown', function(e){ e.preventDefault(); e.stopPropagation(); }, true);
      camBlock.appendChild(ov);
    } else if (!locked && existing) {
      existing.remove();
    }
    return true;
  }
  var tries = 0;
  var t = setInterval(function(){
    tries++;
    pinAndLock();
    if (tries > 40) clearInterval(t);
  }, 100);
})();
</script>
""", height=0)


# =============================================================
# 10. CONFIRM-DEVICE MODAL  (first time camera goes live)
# =============================================================

if cam_running and not st.session_state.get("_camera_confirmed"):
    st.markdown(
        """
        <div class="sd-confirm-overlay">
          <div class="sd-confirm-card">
            <div class="h">Confirm camera selection</div>
            <div class="p">
              The camera is now active. Once you confirm, you will
              <b>not</b> be able to switch the camera device or stop
              the camera until the test is submitted. Make sure your
              face is clearly visible in the live preview.
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cc1, cc2 = st.columns(2, gap="medium")
    with cc1:
        if st.button("Confirm and continue",
                     type="primary",
                     use_container_width=True,
                     key="confirm_cam"):
            st.session_state["_camera_confirmed"] = True
            save_session()
            st.rerun()
    with cc2:
        if st.button("Cancel test",
                     use_container_width=True,
                     key="cancel_cam_confirm"):
            reset_quiz_state(full=False)
            reset_proctor_state()
            for k in ("_starting", "_camera_locked", "_camera_confirmed"):
                st.session_state.pop(k, None)
            save_session()
            if HAS_JS_EVAL:
                try:
                    streamlit_js_eval(
                        js_expressions="(document.exitFullscreen ? document.exitFullscreen() : null)",
                        key="exit_fs_cancel_confirm",
                    )
                except Exception:
                    pass
            st.switch_page("pages/01_home.py")
    st.stop()


# =============================================================
# 11. INSTRUCTIONS
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
# 12. CAM-WAIT NOTICE
# =============================================================

if not cam_running:
    st.markdown(
        """
        <div class="cam-wait">
          <div class="h">Waiting for camera</div>
          <div class="p">
            Click <b>START</b> on the camera widget in the top-right
            corner and allow camera access in your browser. The quiz
            unlocks automatically a few seconds after the camera is
            confirmed.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================
# 13. QUIZ FORM
# =============================================================

quiz_unlocked = cam_running and st.session_state.get("_camera_confirmed", False)

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
                f"No questions could be generated for {skill}. "
                "It will be marked as Unverified."
            )
            continue

        for q_idx, q in enumerate(questions):
            key = f"q_{skill_idx}_{q_idx}"
            if quiz_unlocked:
                qtext = q.get("question", "")
            else:
                qtext = "(locked - start camera to view question)"
            st.markdown(
                f"<div class='q-question'>"
                f"<span class='qnum'>Q{q_idx+1}.</span> {qtext}</div>",
                unsafe_allow_html=True,
            )
            options = [
                f"A. {q.get('option_a','')}",
                f"B. {q.get('option_b','')}",
                f"C. {q.get('option_c','')}",
                f"D. {q.get('option_d','')}",
            ] if quiz_unlocked else [
                "A. (locked)", "B. (locked)", "C. (locked)", "D. (locked)"
            ]
            existing_answer = st.session_state.get(key)
            try:
                idx = options.index(existing_answer) if existing_answer in options else None
            except Exception:
                idx = None
            st.radio(
                label=f"Question {skill_idx+1}.{q_idx+1}",
                options=options,
                key=key,
                label_visibility="collapsed",
                index=idx,
                disabled=not quiz_unlocked,
            )

    st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

    confirm_cancel = st.session_state.get("_confirm_cancel", False)

    submit_col, cancel_col = st.columns(2, gap="medium")
    with submit_col:
        submitted = st.form_submit_button(
            "Submit Test and Continue",
            type="primary",
            use_container_width=True,
            disabled=not quiz_unlocked,
        )
    with cancel_col:
        cancel_clicked = st.form_submit_button(
            "Confirm cancel - go to Home" if confirm_cancel else "Cancel and Go Back",
            use_container_width=True,
            type="secondary",
        )


# =============================================================
# 14. HANDLE CANCEL
# =============================================================

if cancel_clicked:
    if st.session_state.get("_confirm_cancel"):
        for k in ("_confirm_cancel", "_starting",
                  "_camera_locked", "_camera_confirmed"):
            st.session_state.pop(k, None)
        reset_quiz_state(full=False)
        reset_proctor_state()
        save_session()
        if HAS_JS_EVAL:
            try:
                streamlit_js_eval(
                    js_expressions="(document.exitFullscreen ? document.exitFullscreen() : null)",
                    key="exit_fs_cancel",
                )
            except Exception:
                pass
        st.switch_page("pages/01_home.py")
    else:
        st.session_state["_confirm_cancel"] = True
        save_session()
        st.warning(
            "Are you sure you want to cancel? Your answers will be lost "
            "and all proctoring state will be cleared. Click the button "
            "again to confirm."
        )
        st.stop()


# =============================================================
# 15. HANDLE SUBMIT
# =============================================================

if submitted and quiz_unlocked:
    save_session()

    verified = score_all(quiz_data)
    reset_proctor_state()

    if HAS_JS_EVAL:
        try:
            streamlit_js_eval(
                js_expressions="(document.exitFullscreen ? document.exitFullscreen() : null)",
                key="exit_fs_submit",
            )
        except Exception:
            pass

    with st.spinner("Calculating your final score and skill evaluation..."):
        try:
            drift_score, drift_label, track_counts = calculate_drift_score(verified)
            entropy_score, entropy_label = calculate_entropy(track_counts)
            career_matches = calculate_career_match(verified)
            best_match = career_matches[0] if career_matches else {}
            best_track = best_match.get("track", "Unknown")
            match_pct  = best_match.get("match_pct", 0.0)
            readiness  = calculate_readiness_score(verified, best_track)
            next_skill = get_next_skill(best_match.get("missing_skills", []), best_track)
            urgency    = get_urgency_level(st.session_state.get("semester", 4))
            debt       = calculate_focus_debt(verified, best_track)
            peer       = get_peer_placement_rate(drift_score, best_track)

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
    st.success("Submission received. Opening your result dashboard...")
    time.sleep(0.5)
    st.switch_page("pages/03_drift_score.py")