# gemini_quiz.py — SkillDrift Proctored Quiz Engine
# All quiz logic and monitoring live here.
# The entire quiz runs inside one HTML component.
# Python generates questions, passes them to JS, JS runs the proctored test,
# JS sends answers back to Python via Streamlit component value.

import json
import re
import time
import streamlit as st
import streamlit.components.v1 as components
from google import genai


# =============================================================
# SECTION 1 — GEMINI CONFIGURATION
# =============================================================

def configure_gemini():
    try:
        api_key = st.secrets["gemini"]["api_key"]
        st.session_state["gemini_client"] = genai.Client(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"Gemini API configuration failed: {str(e)}")
        return False


# =============================================================
# SECTION 2 — PROMPT BUILDER
# =============================================================

def build_quiz_prompt(skill: str, level: str) -> str:
    return f"""You are an expert technical interviewer for Indian CSE placement preparation.

Generate exactly 3 multiple choice questions to test a B.Tech CSE student's knowledge of {skill} at {level} level.

Rules:
- Questions must be practical and specific to {skill}
- Difficulty must match {level} level exactly
- Each question must have exactly 4 options: A, B, C, D
- Exactly one option must be correct
- The correct answers must be randomly distributed among A, B, C, and D
- Do NOT repeat the same correct option more than twice
- Output MUST contain exactly 3 questions

Output format (STRICT JSON, no extra text):
[
  {{
    "question": "Question 1?",
    "option_a": "Option A",
    "option_b": "Option B",
    "option_c": "Option C",
    "option_d": "Option D",
    "correct": "A"
  }},
  {{
    "question": "Question 2?",
    "option_a": "Option A",
    "option_b": "Option B",
    "option_c": "Option C",
    "option_d": "Option D",
    "correct": "B"
  }},
  {{
    "question": "Question 3?",
    "option_a": "Option A",
    "option_b": "Option B",
    "option_c": "Option C",
    "option_d": "Option D",
    "correct": "C"
  }}
]

- The correct field must be exactly one of: A, B, C, or D (uppercase only)
- Return ONLY the JSON array
- No explanation, no markdown, no code block"""


# =============================================================
# SECTION 3 — GEMINI API CALLER
# =============================================================

GEMINI_MODEL = "gemini-2.5-flash"


def call_gemini_with_retry(prompt: str, skill: str) -> list:
    try:
        api_key = st.secrets["gemini"]["api_key"]
    except Exception as e:
        st.error(f"Gemini API key missing. Check secrets.toml. Error: {e}")
        return []

    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"Could not create Gemini client: {e}")
        return []

    for attempt in range(2):
        try:
            response  = client.models.generate_content(
                model=GEMINI_MODEL, contents=prompt
            )
            raw_text  = response.text.strip()
            questions = parse_gemini_response(raw_text, skill, attempt + 1)
            if questions:
                return questions
            if attempt == 0:
                time.sleep(1)
        except Exception as e:
            if attempt == 0:
                time.sleep(2)
            else:
                st.warning(
                    f"Gemini API error for {skill}: {e}. "
                    "Skill accepted as Unverified."
                )
                return []

    return []


def parse_gemini_response(raw_text: str, skill: str, attempt: int) -> list:
    cleaned = re.sub(r"```(?:json)?\s*", "", raw_text)
    cleaned = re.sub(r"```", "", cleaned).strip()

    try:
        questions = json.loads(cleaned)
        if validate_questions(questions):
            return questions
    except json.JSONDecodeError:
        pass

    array_match = re.search(r"\[.*?\]", cleaned, re.DOTALL)
    if array_match:
        try:
            questions = json.loads(array_match.group())
            if validate_questions(questions):
                return questions
        except json.JSONDecodeError:
            pass

    return []


def validate_questions(questions: list) -> bool:
    if not isinstance(questions, list) or len(questions) != 3:
        return False
    required_keys = {
        "question", "option_a", "option_b",
        "option_c", "option_d", "correct"
    }
    for q in questions:
        if not isinstance(q, dict):
            return False
        if not required_keys.issubset(q.keys()):
            return False
        if str(q.get("correct", "")).upper() not in {"A", "B", "C", "D"}:
            return False
    return True


# =============================================================
# SECTION 4 — ANSWER SCORER
# =============================================================

def score_quiz_answers(
    skill: str,
    claimed_level: str,
    questions: list,
    student_answers: list
) -> dict:

    if not questions:
        return {
            "skill":           skill,
            "claimed_level":   claimed_level,
            "verified_level":  claimed_level,
            "status":          "Unverified",
            "correct_count":   0,
            "total_questions": 0,
        }

    total         = len(questions)
    correct_count = 0

    for i, question in enumerate(questions):
        if i >= len(student_answers):
            break
        student_answer = str(student_answers[i]).upper().strip()
        correct_answer = str(question.get("correct", "")).upper().strip()
        if student_answer == correct_answer:
            correct_count += 1

    ratio = correct_count / total if total > 0 else 0

    if ratio >= 0.67:
        status         = "Confirmed"
        verified_level = claimed_level
    elif ratio >= 0.34:
        status         = "Borderline"
        verified_level = (
            claimed_level
            if claimed_level == "Beginner"
            else downgrade_level(claimed_level)
        )
    else:
        status         = "Not Verified"
        verified_level = "Not Verified"

    return {
        "skill":           skill,
        "claimed_level":   claimed_level,
        "verified_level":  verified_level,
        "status":          status,
        "correct_count":   correct_count,
        "total_questions": total,
    }


def downgrade_level(level: str) -> str:
    return {
        "Advanced":     "Intermediate",
        "Intermediate": "Beginner",
        "Beginner":     "Beginner",
    }.get(level, "Beginner")


# =============================================================
# SECTION 5 — HTML BUILDER
# Builds the complete self-contained proctored quiz HTML.
# All questions, camera, monitoring, and submit live here.
# Python passes questions as JSON. JS renders everything.
# JS sends answers back via Streamlit component value.
# =============================================================

def build_proctored_quiz_html(
    quiz_data: list,
    student_name: str
) -> str:
    """
    Builds the complete HTML string for the proctored quiz.

    Parameters
    ----------
    quiz_data : list
        List of dicts. Each dict has keys:
            skill     : str
            level     : str
            questions : list of question dicts (may be empty)
    student_name : str

    Returns
    -------
    str : complete self-contained HTML
    """

    # Serialize quiz data to JSON for JS consumption
    quiz_json = json.dumps(quiz_data, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SkillDrift Proctored Quiz</title>
<style>

* {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  background: #f6fafe;
  color: #171c1f;
  min-height: 100vh;
}}

/* ── SCREEN SYSTEM ─────────────────────────────── */
/* Only one screen visible at a time               */

.screen {{ display: none; min-height: 100vh; }}
.screen.active {{ display: flex; flex-direction: column; }}

/* ── SCREEN 1 — CAMERA PERMISSION ─────────────── */

#screen-permission {{
  align-items: center;
  justify-content: center;
  background: #ffffff;
  text-align: center;
  padding: 3rem 2rem;
}}

.perm-card {{
  background: #ffffff;
  border: 1.5px solid #e2e8f0;
  border-radius: 18px;
  padding: 2.5rem 2rem;
  max-width: 420px;
  width: 100%;
  box-shadow: 0 4px 24px rgba(0,44,152,0.07);
}}

.perm-icon  {{
  font-size: 3.5rem;
  margin-bottom: 1rem;
}}

.perm-title {{
  font-size: 1.25rem;
  font-weight: 800;
  color: #002c98;
  margin-bottom: 0.6rem;
}}

.perm-sub {{
  font-size: 0.85rem;
  color: #515f74;
  line-height: 1.6;
  margin-bottom: 1.5rem;
}}

.perm-rules {{
  background: #f0f4ff;
  border-radius: 10px;
  padding: 1rem;
  margin-bottom: 1.5rem;
  text-align: left;
}}

.perm-rules li {{
  font-size: 0.8rem;
  color: #171c1f;
  margin-bottom: 0.4rem;
  list-style: none;
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}}

#btn-allow-camera {{
  background: #002c98;
  color: #ffffff;
  border: none;
  border-radius: 10px;
  padding: 0.75rem 2rem;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  width: 100%;
  transition: background 0.15s;
}}

#btn-allow-camera:hover {{ background: #0038bf; }}
#btn-allow-camera:disabled {{
  background: #c7d0e0;
  cursor: not-allowed;
}}

#cam-error-msg {{
  color: #ba1a1a;
  font-size: 0.82rem;
  margin-top: 0.75rem;
  display: none;
  line-height: 1.5;
}}

/* ── SCREEN 2 — QUIZ (FULLSCREEN) ──────────────── */

#screen-quiz {{
  background: #f6fafe;
  flex-direction: column;
  align-items: stretch;
  padding: 0;
}}

/* Proctor bar — fixed at top */
#proctor-bar {{
  background: #002c98;
  color: #ffffff;
  padding: 10px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
  position: sticky;
  top: 0;
  z-index: 100;
}}

.pb-left {{
  display: flex;
  align-items: center;
  gap: 10px;
}}

#rec-dot {{
  width: 10px; height: 10px;
  border-radius: 50%;
  background: #ff3b30;
  animation: blink 1.2s infinite;
  flex-shrink: 0;
}}

@keyframes blink {{
  0%, 100% {{ opacity: 1; }}
  50%       {{ opacity: 0.15; }}
}}

.pb-title {{
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.04em;
}}

.pb-sub {{
  font-size: 0.72rem;
  opacity: 0.7;
}}

#vio-badge {{
  background: rgba(255,255,255,0.15);
  border-radius: 20px;
  padding: 4px 14px;
  font-size: 0.75rem;
  font-weight: 700;
}}

#vio-count {{ color: #ff9500; }}

/* Main quiz area */
#quiz-main {{
  display: flex;
  flex: 1;
  gap: 0;
  overflow: hidden;
  height: calc(100vh - 48px);
}}

/* Camera panel — left sidebar */
#cam-panel {{
  width: 220px;
  min-width: 220px;
  background: #0e1117;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 10px;
  gap: 10px;
  overflow-y: auto;
  flex-shrink: 0;
}}

#cam-feed {{
  width: 100%;
  border-radius: 10px;
  overflow: hidden;
  position: relative;
  background: #000;
  aspect-ratio: 4/3;
}}

#cam-video {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scaleX(-1);
  display: block;
}}

#face-dot {{
  position: absolute;
  top: 6px; right: 6px;
  width: 11px; height: 11px;
  border-radius: 50%;
  background: #34c759;
  border: 2px solid #fff;
  transition: background 0.3s;
}}

#snap-flash {{
  position: absolute;
  inset: 0;
  background: rgba(255,255,255,0.7);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.08s;
  border-radius: 10px;
}}

#cam-live-label {{
  position: absolute;
  bottom: 5px; left: 5px;
  background: rgba(0,0,0,0.6);
  color: #fff;
  font-size: 0.6rem;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  letter-spacing: 0.05em;
}}

.stat-row {{
  width: 100%;
  background: rgba(255,255,255,0.06);
  border-radius: 8px;
  padding: 7px 10px;
  font-size: 0.72rem;
  color: rgba(255,255,255,0.6);
  display: flex;
  flex-direction: column;
  gap: 2px;
}}

.stat-val {{
  font-size: 0.8rem;
  font-weight: 700;
  color: #ffffff;
}}

.stat-green {{ color: #34c759 !important; }}
.stat-red   {{ color: #ff3b30 !important; }}
.stat-amber {{ color: #ff9500 !important; }}

/* Quiz content — right scrollable area */
#quiz-content {{
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
}}

.skill-block {{
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 20px;
  margin-bottom: 18px;
}}

.skill-header {{
  border-left: 4px solid #002c98;
  padding-left: 12px;
  margin-bottom: 14px;
}}

.skill-name  {{
  font-size: 1rem;
  font-weight: 800;
  color: #002c98;
}}

.skill-level {{
  font-size: 0.75rem;
  color: #515f74;
  margin-top: 2px;
}}

.q-block {{ margin-bottom: 16px; }}

.q-text {{
  font-size: 0.88rem;
  font-weight: 600;
  color: #171c1f;
  line-height: 1.5;
  margin-bottom: 10px;
}}

.options-grid {{
  display: flex;
  flex-direction: column;
  gap: 7px;
}}

.opt-btn {{
  width: 100%;
  text-align: left;
  background: #f6fafe;
  border: 1.5px solid #e2e8f0;
  border-radius: 8px;
  padding: 9px 14px;
  font-size: 0.83rem;
  color: #171c1f;
  cursor: pointer;
  transition: all 0.1s;
  font-family: inherit;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}}

.opt-btn:hover {{
  border-color: #002c98;
  background: #eef2ff;
}}

.opt-btn.selected {{
  border-color: #002c98;
  background: #eef2ff;
  font-weight: 700;
}}

.opt-letter {{
  font-weight: 800;
  color: #002c98;
  min-width: 16px;
  flex-shrink: 0;
}}

.unverified-note {{
  font-size: 0.82rem;
  color: #86868b;
  font-style: italic;
  padding: 8px 0;
}}

/* Submit zone */
#submit-zone {{
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 20px;
  margin-bottom: 18px;
  text-align: center;
}}

#submit-info {{
  font-size: 0.82rem;
  color: #515f74;
  margin-bottom: 12px;
  line-height: 1.5;
}}

#btn-submit {{
  background: #002c98;
  color: #ffffff;
  border: none;
  border-radius: 10px;
  padding: 0.75rem 2.5rem;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
  font-family: inherit;
}}

#btn-submit:hover {{ background: #0038bf; }}
#btn-submit:disabled {{
  background: #c7d0e0;
  cursor: not-allowed;
}}

#unanswered-warning {{
  color: #ba1a1a;
  font-size: 0.82rem;
  margin-top: 8px;
  display: none;
}}

#timer-text {{
  font-size: 0.85rem;
  font-weight: 700;
  color: rgba(255,255,255,0.9);
  margin-top: 4px;
}}

/* ── VIOLATION OVERLAY ──────────────────────────── */

#violation-overlay {{
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(255,59,48,0.96);
  z-index: 9999;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 2rem;
  color: #ffffff;
}}

#violation-overlay.show {{ display: flex; }}

.vio-icon  {{ font-size: 4rem; margin-bottom: 1rem; }}
.vio-title {{
  font-size: 1.5rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
}}
.vio-sub {{
  font-size: 0.9rem;
  opacity: 0.85;
  max-width: 400px;
  line-height: 1.6;
  margin-bottom: 1rem;
}}
.vio-count {{
  font-size: 0.8rem;
  opacity: 0.7;
  margin-bottom: 1.5rem;
}}
#btn-resume {{
  background: #ffffff;
  color: #ff3b30;
  border: none;
  border-radius: 10px;
  padding: 0.65rem 2rem;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  font-family: inherit;
}}

/* ── TERMINATED SCREEN ──────────────────────────── */

#screen-terminated {{
  align-items: center;
  justify-content: center;
  background: #1a0a0a;
  text-align: center;
  padding: 3rem 2rem;
  color: #ffffff;
}}

.term-icon  {{ font-size: 5rem; margin-bottom: 1.5rem; }}
.term-title {{
  font-size: 2rem;
  font-weight: 800;
  color: #ff3b30;
  margin-bottom: 1rem;
}}
.term-sub {{
  font-size: 0.95rem;
  opacity: 0.75;
  max-width: 460px;
  line-height: 1.65;
  margin-bottom: 2rem;
}}
#btn-restart {{
  background: #ff3b30;
  color: #ffffff;
  border: none;
  border-radius: 10px;
  padding: 0.75rem 2rem;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  font-family: inherit;
}}

/* ── Hidden canvas for snapshots ────────────────── */
#snap-canvas {{ display: none; }}

/* ── Toast ─────────────────────────────────────── */
#sd-toast {{
  position: fixed;
  bottom: 20px; right: 20px;
  background: #1d1d1f;
  color: #ffffff;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 600;
  z-index: 99999;
  max-width: 300px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
  display: none;
}}

</style>
</head>
<body>

<!-- ══════════════════════════════════════════════
     SCREEN 1 — CAMERA PERMISSION
══════════════════════════════════════════════ -->
<div class="screen active" id="screen-permission">
  <div class="perm-card">
    <div class="perm-icon">📷</div>
    <div class="perm-title">Camera Access Required</div>
    <div class="perm-sub">
      SkillDrift runs a proctored verification quiz.
      You must allow camera access before the quiz begins.
      Your camera is visible only to you — nothing is recorded or sent anywhere.
    </div>
    <ul class="perm-rules">
      <li>🔒 Stay visible in the camera at all times</li>
      <li>🚫 Do not switch tabs or windows</li>
      <li>⛔ Do not copy or paste answers</li>
      <li>📺 Keep the test in fullscreen throughout</li>
      <li>⚠️ 3 violations will terminate the test</li>
    </ul>
    <button id="btn-allow-camera" onclick="startCamera()">
      Allow Camera and Enter Quiz
    </button>
    <div id="cam-error-msg"></div>
  </div>
</div>

<!-- ══════════════════════════════════════════════
     SCREEN 2 — PROCTORED QUIZ (FULLSCREEN)
══════════════════════════════════════════════ -->
<div class="screen" id="screen-quiz">

  <!-- Proctor top bar -->
  <div id="proctor-bar">
    <div class="pb-left">
      <div id="rec-dot"></div>
      <div>
        <div class="pb-title">PROCTORED TEST IN PROGRESS</div>
        <div class="pb-sub">Student: {student_name}</div>
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:16px;">
      <div id="timer-text">00:00</div>
      <div id="vio-badge">⚠️ Violations: <span id="vio-count">0</span>/3</div>
    </div>
  </div>

  <!-- Main area: camera left, questions right -->
  <div id="quiz-main">

    <!-- Camera panel -->
    <div id="cam-panel">
      <div id="cam-feed">
        <video id="cam-video" autoplay muted playsinline></video>
        <div id="face-dot"></div>
        <div id="snap-flash"></div>
        <div id="cam-live-label">LIVE</div>
      </div>

      <div class="stat-row">
        <span>👤 Face</span>
        <span class="stat-val" id="stat-face">Checking...</span>
      </div>
      <div class="stat-row">
        <span>🖥️ Tab</span>
        <span class="stat-val stat-green" id="stat-tab">Active</span>
      </div>
      <div class="stat-row">
        <span>📸 Snapshot</span>
        <span class="stat-val" id="stat-snap">Pending</span>
      </div>
      <div class="stat-row">
        <span>🔒 Copy/Paste</span>
        <span class="stat-val stat-green">Disabled</span>
      </div>
    </div>

    <!-- Quiz questions -->
    <div id="quiz-content">
      <div id="questions-container">
        <!-- Questions injected by JS -->
      </div>

      <div id="submit-zone">
        <div id="submit-info">
          Answer every question above, then click Submit.
          You cannot go back after submitting.
        </div>
        <button id="btn-submit" onclick="submitQuiz()" disabled>
          Submit Quiz and See My Results
        </button>
        <div id="unanswered-warning">
          Please answer all questions before submitting.
        </div>
      </div>
    </div>

  </div>

  <!-- Violation overlay — inside quiz screen so fullscreen contains it -->
  <div id="violation-overlay">
    <div class="vio-icon">⚠️</div>
    <div class="vio-title" id="vio-title-text">Violation Detected</div>
    <div class="vio-sub"   id="vio-sub-text"></div>
    <div class="vio-count" id="vio-count-text"></div>
    <button id="btn-resume" onclick="resumeTest()">
      I Understand — Resume Test
    </button>
  </div>

</div>

<!-- ══════════════════════════════════════════════
     SCREEN 3 — TERMINATED
══════════════════════════════════════════════ -->
<div class="screen" id="screen-terminated">
  <div class="term-icon">🚫</div>
  <div class="term-title">Test Terminated</div>
  <div class="term-sub">
    You have exceeded the maximum number of violations (3).
    Your test session has been permanently closed.
    Please go back to the Skill Input page and restart the entire process honestly.
  </div>
  <button id="btn-restart" onclick="signalTerminated()">
    Go Back and Restart
  </button>
</div>

<!-- Hidden canvas -->
<canvas id="snap-canvas" width="320" height="240"></canvas>

<!-- Toast -->
<div id="sd-toast"></div>

<script>

// ════════════════════════════════════════════════
// DATA FROM PYTHON
// ════════════════════════════════════════════════

const QUIZ_DATA    = {quiz_json};
const MAX_VIO      = 3;
const SNAP_MS      = 60000;
const FACE_CHK_MS  = 2000;
const NO_FACE_GRACE = 5000;

// ════════════════════════════════════════════════
// STATE
// ════════════════════════════════════════════════

let violations     = 0;
let terminated     = false;
let paused         = false;
let stream         = null;
let snapTimer      = null;
let timerInterval  = null;
let faceInterval   = null;
let noFaceTimeout  = null;
let startTime      = null;
let answers        = {{}};   // skill_qidx -> selected letter
let totalQuestions = 0;
let answeredCount  = 0;

// ════════════════════════════════════════════════
// SCREEN MANAGER
// ════════════════════════════════════════════════

function showScreen(id) {{
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}}

// ════════════════════════════════════════════════
// SCREEN 1 — CAMERA STARTUP
// ════════════════════════════════════════════════

async function startCamera() {{
  const btn = document.getElementById('btn-allow-camera');
  const err = document.getElementById('cam-error-msg');

  btn.textContent = 'Starting camera...';
  btn.disabled    = true;
  err.style.display = 'none';

  try {{
    stream = await navigator.mediaDevices.getUserMedia({{
      video: {{ width: 320, height: 240, facingMode: 'user' }},
      audio: false,
    }});

    const video   = document.getElementById('cam-video');
    video.srcObject = stream;
    await new Promise(r => video.onloadedmetadata = r);
    video.play();

    // Camera granted — move to quiz screen and go fullscreen
    showScreen('screen-quiz');
    buildQuestions();
    initMonitoring();
    enterFullscreen();

  }} catch (e) {{
    err.style.display = 'block';
    err.textContent   = 'Camera error: ' + e.message +
      '. Please allow camera access in your browser settings and try again.';
    btn.textContent = 'Allow Camera and Enter Quiz';
    btn.disabled    = false;
  }}
}}

// ════════════════════════════════════════════════
// SCREEN 2 — BUILD QUESTIONS FROM QUIZ_DATA
// ════════════════════════════════════════════════

function buildQuestions() {{
  const container = document.getElementById('questions-container');
  container.innerHTML = '';
  totalQuestions  = 0;
  answeredCount   = 0;

  QUIZ_DATA.forEach((item, skillIdx) => {{
    const block = document.createElement('div');
    block.className = 'skill-block';

    const header = document.createElement('div');
    header.className = 'skill-header';
    header.innerHTML = `
      <div class="skill-name">${{item.skill}}</div>
      <div class="skill-level">${{item.level}} level</div>
    `;
    block.appendChild(header);

    if (!item.questions || item.questions.length === 0) {{
      const note = document.createElement('div');
      note.className   = 'unverified-note';
      note.textContent = 'No questions generated for this skill. It will be accepted as Unverified.';
      block.appendChild(note);
      container.appendChild(block);
      return;
    }}

    item.questions.forEach((q, qIdx) => {{
      totalQuestions++;
      const key = skillIdx + '_' + qIdx;

      const qBlock = document.createElement('div');
      qBlock.className = 'q-block';

      const qText = document.createElement('div');
      qText.className   = 'q-text';
      qText.textContent = 'Q' + (qIdx + 1) + '. ' + q.question;
      qBlock.appendChild(qText);

      const optGrid = document.createElement('div');
      optGrid.className = 'options-grid';

      [['A', q.option_a], ['B', q.option_b],
       ['C', q.option_c], ['D', q.option_d]].forEach(([letter, text]) => {{

        const btn = document.createElement('button');
        btn.className   = 'opt-btn';
        btn.dataset.key = key;
        btn.dataset.val = letter;
        btn.innerHTML   = `<span class="opt-letter">${{letter}}</span><span>${{text}}</span>`;

        btn.onclick = function() {{
          if (terminated || paused) return;

          // Deselect others in same question
          document.querySelectorAll(`.opt-btn[data-key="${{key}}"]`)
            .forEach(b => b.classList.remove('selected'));

          btn.classList.add('selected');

          const wasAnswered = key in answers;
          answers[key] = letter;

          if (!wasAnswered) {{
            answeredCount++;
            updateSubmitButton();
          }}
        }};

        optGrid.appendChild(btn);
      }});

      qBlock.appendChild(optGrid);
      block.appendChild(qBlock);
    }});

    container.appendChild(block);
  }});

  updateSubmitButton();
}}

function updateSubmitButton() {{
  const btn = document.getElementById('btn-submit');
  const all = totalQuestions > 0 && answeredCount >= totalQuestions;
  btn.disabled = !all;
  btn.textContent = all
    ? 'Submit Quiz and See My Results'
    : 'Submit Quiz and See My Results (' +
      answeredCount + '/' + totalQuestions + ' answered)';
}}

// ════════════════════════════════════════════════
// MONITORING SETUP
// ════════════════════════════════════════════════

function initMonitoring() {{
  startTime = Date.now();
  setupCopyPasteBlock();
  setupTabDetection();
  setupFaceDetection();
  startSnapshots();
  startTimerDisplay();
  setupFullscreenExit();
}}

// ── Copy / Paste / Right click block ─────────────

function setupCopyPasteBlock() {{
  document.addEventListener('keydown', e => {{
    if (terminated) return;
    const blocked = (e.ctrlKey || e.metaKey) &&
      ['c','v','x','a','u','s','p'].includes(e.key.toLowerCase());
    if (blocked) {{
      e.preventDefault();
      e.stopPropagation();
      toast('Copy and paste is disabled during the test.');
    }}
    if (e.key === 'F11')  e.preventDefault();
  }}, true);

  document.addEventListener('contextmenu', e => {{
    if (terminated) return;
    e.preventDefault();
    toast('Right click is disabled during the test.');
  }});

  ['copy','cut','paste'].forEach(evt =>
    document.addEventListener(evt, e => {{
      if (!terminated) e.preventDefault();
    }})
  );
}}

// ── Tab / Window switch detection ─────────────────

function setupTabDetection() {{
  document.addEventListener('visibilitychange', () => {{
    if (terminated || paused) return;
    if (document.hidden) {{
      document.getElementById('stat-tab').textContent = 'Left ⚠️';
      document.getElementById('stat-tab').className   = 'stat-val stat-red';
      triggerViolation(
        'Tab Switch Detected',
        'You navigated away from the test. ' +
        'Do not switch tabs or windows during the quiz.'
      );
    }} else {{
      document.getElementById('stat-tab').textContent = 'Active';
      document.getElementById('stat-tab').className   = 'stat-val stat-green';
    }}
  }});

  window.addEventListener('blur', () => {{
    if (terminated || paused) return;
    triggerViolation(
      'Window Focus Lost',
      'You switched to another application. ' +
      'Keep this window active throughout the test.'
    );
  }});
}}

// ── Fullscreen exit detection ─────────────────────

function setupFullscreenExit() {{
  document.addEventListener('fullscreenchange', () => {{
    if (terminated || paused) return;
    if (!document.fullscreenElement) {{
      triggerViolation(
        'Fullscreen Exited',
        'You exited fullscreen mode. ' +
        'The test must remain in fullscreen at all times.'
      );
    }}
  }});

  document.addEventListener('keydown', e => {{
    if (e.key === 'Escape' && !terminated) e.preventDefault();
  }}, true);
}}

// ── Face detection via skin pixel sampling ────────

function setupFaceDetection() {{
  const video  = document.getElementById('cam-video');
  const canvas = document.getElementById('snap-canvas');
  const ctx    = canvas.getContext('2d');

  faceInterval = setInterval(() => {{
    if (terminated || paused) return;
    try {{
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      const imageData  = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const faceFound  = detectSkin(imageData);
      updateFaceUI(faceFound);
    }} catch(e) {{ /* canvas taint — skip */ }}
  }}, FACE_CHK_MS);
}}

function detectSkin(imageData) {{
  const d = imageData.data;
  let skin = 0;
  const total = d.length / 4;
  for (let i = 0; i < d.length; i += 32) {{
    const r = d[i], g = d[i+1], b = d[i+2];
    const Y  =  0.299*r + 0.587*g + 0.114*b;
    const Cb = -0.169*r - 0.331*g + 0.500*b + 128;
    const Cr =  0.500*r - 0.419*g - 0.081*b + 128;
    if (Y > 80 && Cb >= 77 && Cb <= 127 && Cr >= 133 && Cr <= 173) skin++;
  }}
  return (skin / (total / 8)) > 0.025;
}}

function updateFaceUI(found) {{
  const dot  = document.getElementById('face-dot');
  const stat = document.getElementById('stat-face');

  if (found) {{
    dot.style.background = '#34c759';
    stat.textContent = 'Detected ✓';
    stat.className   = 'stat-val stat-green';
    if (noFaceTimeout) {{ clearTimeout(noFaceTimeout); noFaceTimeout = null; }}
  }} else {{
    dot.style.background = '#ff3b30';
    stat.textContent = 'Not detected ⚠️';
    stat.className   = 'stat-val stat-red';
    if (!noFaceTimeout && !paused) {{
      noFaceTimeout = setTimeout(() => {{
        if (!terminated && !paused) {{
          triggerViolation(
            'Face Not Detected',
            'Your face is not visible in the camera. ' +
            'Stay within the camera frame at all times.'
          );
        }}
        noFaceTimeout = null;
      }}, NO_FACE_GRACE);
    }}
  }}
}}

// ── Snapshot system ───────────────────────────────

function startSnapshots() {{
  setTimeout(takeSnap, 5000);
  snapTimer = setInterval(takeSnap, SNAP_MS);
}}

function takeSnap() {{
  if (terminated) return;
  const video  = document.getElementById('cam-video');
  const canvas = document.getElementById('snap-canvas');
  const ctx    = canvas.getContext('2d');
  const flash  = document.getElementById('snap-flash');
  try {{
    ctx.save();
    ctx.scale(-1, 1);
    ctx.drawImage(video, -canvas.width, 0, canvas.width, canvas.height);
    ctx.restore();
    const t = new Date().toLocaleTimeString();
    document.getElementById('stat-snap').textContent = t;
    flash.style.opacity = '1';
    setTimeout(() => flash.style.opacity = '0', 120);
  }} catch(e) {{}}
}}

// ── Timer display ─────────────────────────────────

function startTimerDisplay() {{
  timerInterval = setInterval(() => {{
    if (terminated) return;
    const s    = Math.floor((Date.now() - startTime) / 1000);
    const mm   = String(Math.floor(s / 60)).padStart(2,'0');
    const ss   = String(s % 60).padStart(2,'0');
    document.getElementById('timer-text').textContent = mm + ':' + ss;
  }}, 1000);
}}

// ════════════════════════════════════════════════
// FULLSCREEN
// ════════════════════════════════════════════════

function enterFullscreen() {{
  const el = document.getElementById('screen-quiz');
  if (el.requestFullscreen)            el.requestFullscreen();
  else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen();
  else if (el.mozRequestFullScreen)    el.mozRequestFullScreen();
}}

function reEnterFullscreen() {{
  setTimeout(enterFullscreen, 400);
}}

// ════════════════════════════════════════════════
// VIOLATION SYSTEM
// ════════════════════════════════════════════════

function triggerViolation(title, message) {{
  if (terminated || paused) return;
  paused = true;
  violations++;

  document.getElementById('vio-count').textContent = violations;

  if (violations >= MAX_VIO) {{
    terminateTest();
    return;
  }}

  document.getElementById('vio-title-text').textContent = '⚠️ ' + title;
  document.getElementById('vio-sub-text').textContent   = message;
  document.getElementById('vio-count-text').textContent =
    'Violation ' + violations + ' of ' + MAX_VIO +
    ' — ' + (MAX_VIO - violations) + ' more will terminate the test.';

  document.getElementById('violation-overlay').classList.add('show');
  takeSnap();
}}

function resumeTest() {{
  if (terminated) return;
  document.getElementById('violation-overlay').classList.remove('show');
  paused = false;
  reEnterFullscreen();
}}

function terminateTest() {{
  terminated = true;
  clearInterval(snapTimer);
  clearInterval(timerInterval);
  clearInterval(faceInterval);
  if (noFaceTimeout) clearTimeout(noFaceTimeout);
  if (stream) stream.getTracks().forEach(t => t.stop());

  document.getElementById('violation-overlay').classList.remove('show');

  // Exit fullscreen first then show terminated screen
  if (document.fullscreenElement) {{
    document.exitFullscreen().then(() => showScreen('screen-terminated'));
  }} else {{
    showScreen('screen-terminated');
  }}
}}

function signalTerminated() {{
  // Send terminated signal to Streamlit
  window.parent.postMessage({{
    type: 'streamlit:setComponentValue',
    value: JSON.stringify({{ terminated: true, answers: {{}} }})
  }}, '*');
}}

// ════════════════════════════════════════════════
// QUIZ SUBMISSION
// ════════════════════════════════════════════════

function submitQuiz() {{
  if (terminated) return;

  // Final check — all questions answered
  const warn = document.getElementById('unanswered-warning');
  if (answeredCount < totalQuestions) {{
    warn.style.display = 'block';
    return;
  }}
  warn.style.display = 'none';

  document.getElementById('btn-submit').disabled     = true;
  document.getElementById('btn-submit').textContent  = 'Submitting...';

  // Build structured answer payload
  // Format: {{ "SkillName_qIdx": "A", ... }}
  const payload = {{
    terminated: false,
    answers:    answers,
    quiz_data:  QUIZ_DATA,
  }};

  // Send to Streamlit via postMessage
  window.parent.postMessage({{
    type:  'streamlit:setComponentValue',
    value: JSON.stringify(payload),
  }}, '*');
}}

// ════════════════════════════════════════════════
// TOAST
// ════════════════════════════════════════════════

function toast(msg) {{
  const t = document.getElementById('sd-toast');
  t.textContent    = msg;
  t.style.display  = 'block';
  clearTimeout(t._timer);
  t._timer = setTimeout(() => t.style.display = 'none', 3000);
}}

</script>
</body>
</html>"""

    return html


# =============================================================
# SECTION 6 — MAIN QUIZ RUNNER
# =============================================================

def run_skill_verification_quiz(selected_skills: dict) -> dict:
    """
    Runs the complete proctored quiz.

    Flow:
    1. Generate questions via Gemini (with caching)
    2. Render the entire proctored quiz as one HTML component
    3. Wait for component to return answers via component value
    4. Score answers and return verified_skills

    Parameters
    ----------
    selected_skills : dict  {skill_name: claimed_level}

    Returns
    -------
    verified_skills : dict  {skill_name: verified_level}
    Empty dict if quiz not yet submitted or terminated.
    """

    if not configure_gemini():
        st.error("Cannot run quiz — Gemini API not configured.")
        return {}

    student_name = st.session_state.get("student_name", "Student")

    # ── Generate questions once — cache in session_state ──────
    selected_sig = tuple(sorted(selected_skills.items()))

    if (
        "quiz_data_sig" not in st.session_state
        or st.session_state["quiz_data_sig"] != selected_sig
    ):
        with st.spinner("Generating quiz questions via Gemini AI... Please wait."):
            quiz_data = []
            for skill, level in selected_skills.items():
                prompt    = build_quiz_prompt(skill, level)
                questions = call_gemini_with_retry(prompt, skill)
                quiz_data.append({
                    "skill":     skill,
                    "level":     level,
                    "questions": questions,
                })
                time.sleep(0.5)

            st.session_state["quiz_data"]     = quiz_data
            st.session_state["quiz_data_sig"] = selected_sig

    quiz_data = st.session_state["quiz_data"]

    # ── Check if already terminated this session ──────────────
    if st.session_state.get("quiz_terminated"):
        st.error(
            "🚫 Your test was terminated due to violations. "
            "Please restart the skill input process."
        )
        if st.button("← Restart Skill Input", type="primary"):
            keys_to_clear = [
                "student_name", "semester", "selected_skills",
                "verified_skills", "quiz_results", "quiz_complete",
                "quiz_data", "quiz_data_sig", "quiz_terminated",
            ]
            for k in keys_to_clear:
                if k in st.session_state:
                    del st.session_state[k]
            st.switch_page("pages/02_skill_input.py")
        return {}

    # ── Render the proctored quiz component ───────────────────
    st.markdown(
        "<div style='font-size:0.85rem; color:#515f74; "
        "margin-bottom:0.75rem; line-height:1.5;'>"
        "Allow camera access when prompted. "
        "The quiz will begin after your camera is active. "
        "Stay in fullscreen and do not switch tabs."
        "</div>",
        unsafe_allow_html=True,
    )

    quiz_html = build_proctored_quiz_html(quiz_data, student_name)

    # Calculate component height
    # Each skill: ~60px header + questions * ~180px + 40px padding
    total_q_count = sum(
        len(item["questions"]) for item in quiz_data
        if item["questions"]
    )
    estimated_height = max(
        700,
        48 + 60 + (total_q_count * 180) + 120
    )
    # Cap at 900px — page scrolls inside the component
    component_height = min(estimated_height, 900)

    # Render component and capture return value
    component_value = components.html(
        quiz_html,
        height=component_height,
        scrolling=False,
    )

    # ── Process component return value ────────────────────────
    if component_value is None:
        return {}

    # Parse the JSON payload sent from JavaScript
    try:
        if isinstance(component_value, str):
            payload = json.loads(component_value)
        elif isinstance(component_value, dict):
            payload = component_value
        else:
            return {}
    except (json.JSONDecodeError, TypeError):
        return {}

    # Handle termination signal
    if payload.get("terminated"):
        st.session_state["quiz_terminated"] = True
        st.error(
            "🚫 Your test was terminated due to repeated violations. "
            "Please restart the skill input process."
        )
        if st.button("← Restart Skill Input", type="primary"):
            keys_to_clear = [
                "student_name", "semester", "selected_skills",
                "verified_skills", "quiz_results", "quiz_complete",
                "quiz_data", "quiz_data_sig", "quiz_terminated",
            ]
            for k in keys_to_clear:
                if k in st.session_state:
                    del st.session_state[k]
            st.switch_page("pages/02_skill_input.py")
        return {}

    # ── Score the answers ─────────────────────────────────────
    raw_answers = payload.get("answers", {})
    returned_quiz_data = payload.get("quiz_data", quiz_data)

    quiz_results    = []
    verified_skills = {}

    for skill_idx, item in enumerate(returned_quiz_data):
        skill     = item["skill"]
        level     = item["level"]
        questions = item.get("questions", [])

        # Collect answers for this skill
        student_answers = []
        for q_idx in range(len(questions)):
            key    = f"{skill_idx}_{q_idx}"
            letter = raw_answers.get(key, None)
            student_answers.append(letter if letter else "")

        result = score_quiz_answers(skill, level, questions, student_answers)
        quiz_results.append(result)

        if result["verified_level"] != "Not Verified":
            verified_skills[skill] = result["verified_level"]

    # Fallback — if everything Not Verified, use claimed levels
    if not verified_skills:
        for r in quiz_results:
            verified_skills[r["skill"]] = r["claimed_level"]

    st.session_state["quiz_results"]    = quiz_results
    st.session_state["verified_skills"] = verified_skills
    st.session_state["quiz_complete"]   = True

    return verified_skills

