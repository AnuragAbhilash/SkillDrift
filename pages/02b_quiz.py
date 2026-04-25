import time
import streamlit as st
import streamlit.components.v1 as components

from gemini_quiz import (
    ensure_quiz_data, score_all, reset_quiz_state,
)
from proctor import (
    render_proctor_camera, get_proctor_snapshot,
    add_tab_switch_violation, reset_proctor_state,
)
from brain import (
    calculate_drift_score, calculate_entropy, calculate_career_match,
    calculate_readiness_score, get_next_skill, get_urgency_level,
    calculate_focus_debt, get_peer_placement_rate,
)

# Optional: streamlit-autorefresh for periodic polling
try:
    from streamlit_autorefresh import st_autorefresh
    HAS_AUTOREFRESH = True
except Exception:
    HAS_AUTOREFRESH = False


st.set_page_config(
    page_title="SkillDrift — Proctored Quiz",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide Streamlit chrome
st.markdown("""
<style>
[data-testid="stSidebarNav"], [data-testid="collapsedControl"],
[data-testid="stExpandSidebar"], [data-testid="stSidebarCollapseButton"],
section[data-testid="stSidebar"], header[data-testid="stHeader"],
.stDeployButton, #MainMenu, footer { display: none !important; }

html, body, .stApp { background: #f6fafe; font-family: 'Inter', sans-serif; }
.block-container { padding-top: 1rem !important; max-width: 1100px !important; }

.q-header {
  background: #002c98; color: #fff; border-radius: 12px;
  padding: 16px 22px; display: flex; justify-content: space-between;
  align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 8px;
}
.q-header .title {
  font-family: 'Manrope', sans-serif; font-size: 1rem;
  font-weight: 800; letter-spacing: 0.02em;
}
.q-header .sub { font-size: 0.78rem; opacity: 0.85; margin-top: 2px; }
.q-header .vio-badge {
  background: rgba(255,255,255,0.18); border-radius: 18px;
  padding: 6px 16px; font-size: 0.8rem; font-weight: 700;
}
.q-header .vio-badge.warn { background: #ff9500; color: #000; }
.q-header .vio-badge.bad  { background: #ff3b30; color: #fff; }

.q-card {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 10px;
  padding: 14px 18px; margin-top: 18px; margin-bottom: 8px;
}
.q-card .skill {
  font-family: 'Manrope', sans-serif; font-size: 1.05rem;
  font-weight: 800; color: #002c98;
}
.q-card .meta { font-size: 0.8rem; color: #515f74; margin-top: 3px; }

.q-instr {
  font-size: 0.82rem; color: #515f74; margin: 12px 0 18px 0;
  padding: 10px 14px; background: #eef2ff; border-radius: 8px;
  border-left: 3px solid #002c98;
}

.q-fallback-badge {
  background: #fff7ed; color: #9a3412; border: 1px solid #fdba74;
  border-radius: 10px; padding: 2px 10px; font-size: 0.7rem;
  font-weight: 700; margin-left: 8px;
}

.q-terminated {
  background: #fff5f5; border: 1.5px solid #ff3b30; border-radius: 14px;
  padding: 32px; text-align: center; margin: 20px 0;
}
.q-terminated .title {
  font-family: 'Manrope', sans-serif; font-size: 1.6rem;
  font-weight: 800; color: #ba1a1a; margin-bottom: 14px;
}
.q-terminated .body {
  font-size: 0.95rem; color: #515f74; line-height: 1.6;
  margin-bottom: 8px;
}

.stButton > button {
  border-radius: 8px; border: 1.5px solid #e2e8f0; background: #fff;
  color: #171c1f; font-weight: 600;
}
.stButton > button[kind="primary"] {
  background: #002c98; color: #fff; border-color: #002c98; font-weight: 700;
}
.stButton > button[kind="primary"]:hover { background: #0038bf; }
</style>
""", unsafe_allow_html=True)


# =============================================================
# 1. GUARDS — must come from skill_input page with valid state
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

# If quiz already completed, send to drift score
if st.session_state.get("quiz_complete"):
    st.success("Quiz already completed. Redirecting to your dashboard.")
    st.switch_page("pages/03_drift_score.py")
    st.stop()


# =============================================================
# 2. TAB-SWITCH BRIDGE via query params
# We intentionally use st.query_params (not URL hashing): a tiny
# JS snippet writes ?ts_event=N when visibility goes hidden. On
# next rerun (forced by autorefresh), we read it and increment
# the violation counter, then immediately consume the param.
# =============================================================

qp = st.query_params
if "ts_event" in qp:
    try:
        # Each unique value triggers exactly one violation
        last_seen = st.session_state.get("ts_last_seen", "")
        cur = qp.get("ts_event") or ""
        if cur and cur != last_seen:
            add_tab_switch_violation()
            st.session_state["ts_last_seen"] = cur
    except Exception:
        pass
    finally:
        try:
            del st.query_params["ts_event"]
        except Exception:
            pass


# =============================================================
# 3. TERMINATED SCREEN
# =============================================================

snap = get_proctor_snapshot()
if snap["violations"] >= 3:
    st.session_state["quiz_terminated"] = True

if st.session_state.get("quiz_terminated"):
    st.markdown(
        """
        <div class="q-terminated">
          <div class="title">Test Terminated</div>
          <div class="body">
            Your test was terminated due to repeated proctoring violations
            (face not detected for an extended period, or tab/window
            switching).
          </div>
          <div class="body">
            All session data has been cleared. You can restart from the
            beginning below.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Restart from Beginning", type="primary",
                     use_container_width=True, key="qz_restart"):
            reset_quiz_state(full=True)
            reset_proctor_state()
            st.switch_page("pages/01_home.py")
    with c2:
        if st.button("Go Back to Home", use_container_width=True,
                     key="qz_goback"):
            reset_quiz_state(full=True)
            reset_proctor_state()
            st.switch_page("pages/01_home.py")
    st.stop()


# =============================================================
# 4. GENERATE QUESTIONS
# =============================================================

selected_skills = st.session_state["selected_skills"]
student_name    = st.session_state["student_name"]

# First time entering this page → reset proctor state once
if not st.session_state.get("_proctor_reset_done"):
    reset_proctor_state()
    st.session_state["_proctor_reset_done"] = True

quiz_data = ensure_quiz_data(selected_skills)
if not quiz_data:
    st.error("Failed to generate quiz questions. Please go back and try again.")
    if st.button("Go Back"):
        st.switch_page("pages/02_skill_input.py")
    st.stop()


# =============================================================
# 5. AUTO-REFRESH so violation counter from camera thread
#    actually reaches this page's state. Polls every 3 seconds.
# =============================================================

if HAS_AUTOREFRESH:
    st_autorefresh(interval=3000, key="quiz_autorefresh")
else:
    st.warning(
        "streamlit-autorefresh not installed — violation polling disabled. "
        "Install with: pip install streamlit-autorefresh"
    )


# =============================================================
# 6. HEADER
# =============================================================

violations = snap["violations"]
total_q = sum(len(x['questions']) for x in quiz_data)

vio_class = "vio-badge"
if   violations >= 3: vio_class += " bad"
elif violations >= 1: vio_class += " warn"

st.markdown(
    f"""
    <div class="q-header">
      <div>
        <div class="title">SKILLDRIFT PROCTORED ASSESSMENT</div>
        <div class="sub">
          Candidate: {student_name} &nbsp;·&nbsp; Skills: {len(quiz_data)}
          &nbsp;·&nbsp; Total questions: {total_q}
        </div>
      </div>
      <div class="{vio_class}">Violations: {violations} / 3</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =============================================================
# 7. CAMERA + STATUS PANEL
# =============================================================

cam_col, status_col = st.columns([1, 1])

with cam_col:
    st.markdown("**Live Camera (Face Detection Active)**")
    ctx = render_proctor_camera()
    st.caption(
        "Click START to begin. The camera must remain on for the full quiz. "
        "Keep your face clearly visible and centered."
    )

with status_col:
    st.markdown("**Proctoring Status**")
    face_status = "Detected" if snap["face_present"] else "Not detected"
    face_color  = "#15803d" if snap["face_present"] else "#ba1a1a"
    no_face_streak = snap["no_face_streak"]
    cam_running = snap["running"] and (
        snap["last_frame_time"] is not None
        and (time.time() - snap["last_frame_time"]) < 5
    )
    cam_status = "Active" if cam_running else "Not started"
    cam_color  = "#15803d" if cam_running else "#9a3412"

    st.markdown(
        f"""
        <div style="background:#fff;border:1px solid #e2e8f0;
                    border-radius:10px;padding:14px 18px;">
          <div style="display:flex;justify-content:space-between;
                      padding:6px 0;border-bottom:1px solid #f0f4f8;">
            <span style="color:#515f74;">Camera</span>
            <span style="color:{cam_color};font-weight:700;">{cam_status}</span>
          </div>
          <div style="display:flex;justify-content:space-between;
                      padding:6px 0;border-bottom:1px solid #f0f4f8;">
            <span style="color:#515f74;">Face</span>
            <span style="color:{face_color};font-weight:700;">{face_status}</span>
          </div>
          <div style="display:flex;justify-content:space-between;
                      padding:6px 0;border-bottom:1px solid #f0f4f8;">
            <span style="color:#515f74;">No-face streak</span>
            <span style="color:#171c1f;font-weight:700;">{no_face_streak:.1f}s / 8s</span>
          </div>
          <div style="display:flex;justify-content:space-between;padding:6px 0;">
            <span style="color:#515f74;">Violations</span>
            <span style="color:#171c1f;font-weight:700;">{violations} / 3</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================
# 8. TAB-SWITCH DETECTOR (JS → query param bridge)
# =============================================================

components.html(
    """
<!DOCTYPE html><html><body>
<script>
(function() {
  let counter = 0;
  function reportSwitch() {
    try {
      counter++;
      const url = new URL(window.top.location.href);
      url.searchParams.set('ts_event', String(Date.now()) + '_' + counter);
      window.top.location.href = url.toString();
    } catch(e) {}
  }
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) reportSwitch();
  });
  // Block right-click, copy, paste in this iframe
  ['contextmenu','copy','paste','cut'].forEach(ev =>
    document.addEventListener(ev, e => e.preventDefault())
  );
})();
</script>
</body></html>
""",
    height=0,
)


# =============================================================
# 9. INSTRUCTIONS
# =============================================================

st.markdown(
    """
    <div class="q-instr">
      <b>Rules.</b> Click START on the camera before answering questions.
      Keep your face clearly visible. Do not switch tabs or windows. The
      test terminates after 3 violations. Right-click, copy, and paste
      are disabled.
    </div>
    """,
    unsafe_allow_html=True,
)


# =============================================================
# 10. THE QUIZ FORM (native Streamlit)
# =============================================================

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
                Claimed level: <b>{level}</b> &nbsp;·&nbsp;
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
            st.markdown(
                f"<div style='font-weight:600;font-size:0.92rem;"
                f"color:#171c1f;margin:14px 0 6px 0;'>"
                f"Q{q_idx+1}. {q.get('question','')}</div>",
                unsafe_allow_html=True,
            )
            options = [
                f"A. {q.get('option_a','')}",
                f"B. {q.get('option_b','')}",
                f"C. {q.get('option_c','')}",
                f"D. {q.get('option_d','')}",
            ]
            st.radio(
                label=f"Question {skill_idx+1}.{q_idx+1}",
                options=options,
                key=key,
                label_visibility="collapsed",
                index=None,
            )

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
    col_a, col_b = st.columns([2, 1])
    with col_a:
        submitted = st.form_submit_button(
            "Submit Test and Continue",
            type="primary",
            use_container_width=True,
        )
    with col_b:
        cancelled = st.form_submit_button(
            "Cancel and Go Back",
            use_container_width=True,
        )


# =============================================================
# 11. HANDLE CANCEL
# =============================================================

if cancelled:
    reset_quiz_state(full=False)
    reset_proctor_state()
    st.switch_page("pages/01_home.py")


# =============================================================
# 12. HANDLE SUBMIT — score, run analysis, redirect
# =============================================================

if submitted:
    verified = score_all(quiz_data)
    reset_proctor_state()

    with st.spinner("Running full career analysis..."):
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

    st.success("Analysis complete. Opening your dashboard...")
    st.switch_page("pages/03_drift_score.py")
