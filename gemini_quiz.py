# gemini_quiz.py — SkillDrift Proctored Quiz Engine

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
# =============================================================

def build_proctored_quiz_html(quiz_data: list, student_name: str) -> str:
    """
    Builds the complete self-contained proctored quiz HTML.

    FIX: Instead of writing to localStorage and reloading the page,
    the JS now calls window.parent.postMessage with the Streamlit
    component protocol directly. This is the correct way for an
    HTML component iframe to return a value to Python.
    """

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

.screen {{ display: none; min-height: 100vh; }}
.screen.active {{ display: flex; flex-direction: column; }}

/* ── SCREEN 1 — CAMERA PERMISSION ── */

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
  max-width: 440px;
  width: 100%;
  box-shadow: 0 4px 24px rgba(0,44,152,0.07);
}}

.perm-logo {{
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  color: #002c98;
  text-transform: uppercase;
  margin-bottom: 1.5rem;
}}

.perm-title {{
  font-size: 1.2rem;
  font-weight: 800;
  color: #171c1f;
  margin-bottom: 0.5rem;
}}

.perm-sub {{
  font-size: 0.83rem;
  color: #515f74;
  line-height: 1.65;
  margin-bottom: 1.5rem;
}}

.perm-rules {{
  background: #f6fafe;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 1rem 1rem 0.6rem 1rem;
  margin-bottom: 1.5rem;
  text-align: left;
}}

.perm-rules-title {{
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #515f74;
  margin-bottom: 0.6rem;
}}

.perm-rule-item {{
  font-size: 0.8rem;
  color: #171c1f;
  margin-bottom: 0.4rem;
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  line-height: 1.4;
}}

.rule-dot {{
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #002c98;
  flex-shrink: 0;
  margin-top: 5px;
}}

#btn-allow-camera {{
  background: #002c98;
  color: #ffffff;
  border: none;
  border-radius: 10px;
  padding: 0.75rem 2rem;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  width: 100%;
  transition: background 0.15s;
  font-family: inherit;
  letter-spacing: 0.01em;
}}

#btn-allow-camera:hover {{ background: #0038bf; }}
#btn-allow-camera:disabled {{
  background: #c7d0e0;
  cursor: not-allowed;
}}

#cam-error-msg {{
  color: #ba1a1a;
  font-size: 0.8rem;
  margin-top: 0.75rem;
  display: none;
  line-height: 1.5;
  text-align: left;
  background: #fff5f5;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 0.6rem 0.8rem;
}}

/* ── SCREEN 2 — QUIZ ── */

#screen-quiz {{
  background: #f0f4f8;
  flex-direction: column;
  align-items: stretch;
  padding: 0;
}}

#proctor-bar {{
  background: #001a5e;
  color: #ffffff;
  padding: 0 20px;
  height: 48px;
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
  gap: 12px;
}}

#rec-dot {{
  width: 8px; height: 8px;
  border-radius: 50%;
  background: #e74c3c;
  animation: blink 1.4s infinite;
  flex-shrink: 0;
}}

@keyframes blink {{
  0%, 100% {{ opacity: 1; }}
  50%       {{ opacity: 0.1; }}
}}

.pb-brand {{
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  opacity: 0.9;
}}

.pb-label {{
  font-size: 0.7rem;
  font-weight: 500;
  opacity: 0.55;
  margin-top: 1px;
}}

.pb-right {{
  display: flex;
  align-items: center;
  gap: 20px;
}}

#timer-display {{
  font-size: 0.82rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  opacity: 0.85;
}}

.vio-indicator {{
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 6px;
  padding: 3px 10px;
  font-size: 0.72rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 6px;
}}

.vio-dot {{
  width: 6px; height: 6px;
  border-radius: 50%;
  background: #f39c12;
}}

#vio-count {{ color: #f39c12; }}

#quiz-main {{
  display: flex;
  flex: 1;
  overflow: hidden;
  height: calc(100vh - 48px);
}}

/* Camera sidebar */
#cam-panel {{
  width: 200px;
  min-width: 200px;
  background: #0a0d14;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 14px 12px;
  gap: 10px;
  overflow-y: auto;
  flex-shrink: 0;
  border-right: 1px solid #1a2035;
}}

#cam-feed {{
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  background: #000;
  aspect-ratio: 4/3;
  border: 1px solid #1e2a45;
}}

#cam-video {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scaleX(-1);
  display: block;
}}

#face-indicator {{
  position: absolute;
  top: 6px; right: 6px;
  width: 10px; height: 10px;
  border-radius: 50%;
  background: #27ae60;
  border: 1.5px solid rgba(255,255,255,0.8);
  transition: background 0.3s;
}}

#snap-flash {{
  position: absolute;
  inset: 0;
  background: rgba(255,255,255,0.65);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.08s;
  border-radius: 8px;
}}

.cam-label {{
  position: absolute;
  bottom: 5px; left: 5px;
  background: rgba(0,0,0,0.65);
  color: rgba(255,255,255,0.9);
  font-size: 0.58rem;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 3px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}}

.monitor-stat {{
  width: 100%;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 6px;
  padding: 8px 10px;
}}

.mstat-label {{
  font-size: 0.63rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.35);
  margin-bottom: 3px;
}}

.mstat-value {{
  font-size: 0.75rem;
  font-weight: 700;
  color: rgba(255,255,255,0.85);
}}

.mstat-ok   {{ color: #27ae60 !important; }}
.mstat-warn {{ color: #e74c3c !important; }}
.mstat-off  {{ color: rgba(255,255,255,0.85) !important; }}

/* Quiz content area */
#quiz-content {{
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px 32px 24px;
}}

.section-label {{
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #515f74;
  margin-bottom: 12px;
}}

.skill-block {{
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 18px 20px;
  margin-bottom: 14px;
}}

.skill-header {{
  display: flex;
  align-items: baseline;
  gap: 10px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f4f8;
  margin-bottom: 14px;
}}

.skill-name {{
  font-size: 0.95rem;
  font-weight: 800;
  color: #002c98;
}}

.skill-level-tag {{
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #515f74;
  background: #f0f4f8;
  padding: 2px 8px;
  border-radius: 4px;
}}

.q-block {{ margin-bottom: 18px; }}
.q-block:last-child {{ margin-bottom: 0; }}

.q-number {{
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #515f74;
  margin-bottom: 4px;
}}

.q-text {{
  font-size: 0.875rem;
  font-weight: 600;
  color: #171c1f;
  line-height: 1.55;
  margin-bottom: 10px;
}}

.options-grid {{
  display: flex;
  flex-direction: column;
  gap: 6px;
}}

.opt-btn {{
  width: 100%;
  text-align: left;
  background: #f8fafc;
  border: 1.5px solid #e2e8f0;
  border-radius: 8px;
  padding: 9px 14px;
  font-size: 0.82rem;
  color: #171c1f;
  cursor: pointer;
  transition: border-color 0.1s, background 0.1s;
  font-family: inherit;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  line-height: 1.45;
}}

.opt-btn:hover {{
  border-color: #002c98;
  background: #f0f4ff;
}}

.opt-btn.selected {{
  border-color: #002c98;
  background: #eef2ff;
}}

.opt-letter {{
  font-size: 0.72rem;
  font-weight: 800;
  color: #002c98;
  min-width: 18px;
  height: 18px;
  border-radius: 4px;
  background: #eef2ff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 1px;
}}

.opt-btn.selected .opt-letter {{
  background: #002c98;
  color: #ffffff;
}}

.unverified-note {{
  font-size: 0.8rem;
  color: #86868b;
  font-style: italic;
  padding: 6px 0;
  line-height: 1.5;
}}

/* Submit block */
.submit-block {{
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 14px;
}}

.submit-progress {{
  font-size: 0.8rem;
  color: #515f74;
  margin-bottom: 14px;
  line-height: 1.5;
}}

.progress-bar-track {{
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  margin-bottom: 14px;
  overflow: hidden;
}}

.progress-bar-fill {{
  height: 100%;
  background: #002c98;
  border-radius: 2px;
  transition: width 0.3s ease;
}}

#btn-submit {{
  background: #002c98;
  color: #ffffff;
  border: none;
  border-radius: 10px;
  padding: 0.7rem 2rem;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.15s;
  font-family: inherit;
  width: 100%;
  letter-spacing: 0.01em;
}}

#btn-submit:hover:not(:disabled) {{ background: #0038bf; }}

#btn-submit:disabled {{
  background: #c7d0e0;
  cursor: not-allowed;
}}

#unanswered-msg {{
  color: #ba1a1a;
  font-size: 0.8rem;
  margin-top: 10px;
  display: none;
  line-height: 1.5;
}}

/* ── VIOLATION OVERLAY ── */

#violation-overlay {{
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(220, 38, 38, 0.97);
  z-index: 9999;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 3rem 2rem;
  color: #ffffff;
}}

#violation-overlay.show {{ display: flex; }}

.vio-badge-large {{
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  background: rgba(255,255,255,0.15);
  padding: 4px 14px;
  border-radius: 20px;
  margin-bottom: 1.25rem;
}}

.vio-title {{
  font-size: 1.5rem;
  font-weight: 800;
  margin-bottom: 0.75rem;
  line-height: 1.3;
}}

.vio-sub {{
  font-size: 0.875rem;
  opacity: 0.85;
  max-width: 380px;
  line-height: 1.65;
  margin-bottom: 0.75rem;
}}

.vio-remaining {{
  font-size: 0.75rem;
  opacity: 0.6;
  margin-bottom: 2rem;
}}

#btn-resume {{
  background: #ffffff;
  color: #dc2626;
  border: none;
  border-radius: 10px;
  padding: 0.7rem 2rem;
  font-size: 0.875rem;
  font-weight: 700;
  cursor: pointer;
  font-family: inherit;
  transition: transform 0.1s;
}}

#btn-resume:hover {{ transform: scale(1.02); }}

/* ── TERMINATED SCREEN ── */

#screen-terminated {{
  align-items: center;
  justify-content: center;
  background: #0f0a0a;
  text-align: center;
  padding: 3rem 2rem;
  color: #ffffff;
}}

.term-badge {{
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: #e74c3c;
  border: 1px solid #e74c3c;
  padding: 4px 14px;
  border-radius: 20px;
  margin-bottom: 2rem;
  display: inline-block;
}}

.term-title {{
  font-size: 1.75rem;
  font-weight: 800;
  color: #ffffff;
  margin-bottom: 1rem;
  line-height: 1.3;
}}

.term-sub {{
  font-size: 0.875rem;
  color: rgba(255,255,255,0.55);
  max-width: 420px;
  line-height: 1.7;
  margin-bottom: 2.5rem;
}}

#btn-restart {{
  background: #e74c3c;
  color: #ffffff;
  border: none;
  border-radius: 10px;
  padding: 0.75rem 2rem;
  font-size: 0.875rem;
  font-weight: 700;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.15s;
}}

#btn-restart:hover {{ background: #c0392b; }}

#snap-canvas {{ display: none; }}

#sd-toast {{
  position: fixed;
  bottom: 20px; right: 20px;
  background: #1d2533;
  color: #ffffff;
  padding: 0.6rem 1rem;
  border-radius: 8px;
  font-size: 0.78rem;
  font-weight: 600;
  z-index: 99999;
  max-width: 280px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.35);
  display: none;
  line-height: 1.45;
}}

</style>
</head>
<body>

<!-- SCREEN 1 — CAMERA PERMISSION -->
<div class="screen active" id="screen-permission">
  <div class="perm-card">
    <div class="perm-logo">SkillDrift</div>
    <div class="perm-title">Camera Access Required</div>
    <div class="perm-sub">
      This is a proctored skill verification test.
      Camera access is required before the quiz begins.
      Your camera feed is visible only to you on this screen.
      Nothing is recorded or stored on any server.
    </div>
    <div class="perm-rules">
      <div class="perm-rules-title">Test Rules</div>
      <div class="perm-rule-item">
        <span class="rule-dot"></span>
        Stay visible in the camera frame at all times
      </div>
      <div class="perm-rule-item">
        <span class="rule-dot"></span>
        Do not switch tabs or windows during the test
      </div>
      <div class="perm-rule-item">
        <span class="rule-dot"></span>
        Do not copy, paste, or use right-click
      </div>
      <div class="perm-rule-item">
        <span class="rule-dot"></span>
        Keep the test in fullscreen mode throughout
      </div>
      <div class="perm-rule-item">
        <span class="rule-dot"></span>
        Three violations will permanently terminate the test
      </div>
    </div>
    <button id="btn-allow-camera" onclick="startCamera()">
      Allow Camera and Begin Test
    </button>
    <div id="cam-error-msg"></div>
  </div>
</div>

<!-- SCREEN 2 — PROCTORED QUIZ -->
<div class="screen" id="screen-quiz">

  <div id="proctor-bar">
    <div class="pb-left">
      <div id="rec-dot"></div>
      <div>
        <div class="pb-brand">SkillDrift — Proctored Test</div>
        <div class="pb-label">Student: {student_name}</div>
      </div>
    </div>
    <div class="pb-right">
      <div id="timer-display">00:00</div>
      <div class="vio-indicator">
        <div class="vio-dot"></div>
        Violations: <span id="vio-count">0</span> / 3
      </div>
    </div>
  </div>

  <div id="quiz-main">

    <!-- Camera panel -->
    <div id="cam-panel">
      <div id="cam-feed">
        <video id="cam-video" autoplay muted playsinline></video>
        <div id="face-indicator"></div>
        <div id="snap-flash"></div>
        <div class="cam-label">Live</div>
      </div>

      <div class="monitor-stat">
        <div class="mstat-label">Face</div>
        <div class="mstat-value mstat-off" id="stat-face">Checking</div>
      </div>
      <div class="monitor-stat">
        <div class="mstat-label">Tab</div>
        <div class="mstat-value mstat-ok" id="stat-tab">Active</div>
      </div>
      <div class="monitor-stat">
        <div class="mstat-label">Snapshot</div>
        <div class="mstat-value mstat-off" id="stat-snap">Pending</div>
      </div>
      <div class="monitor-stat">
        <div class="mstat-label">Copy / Paste</div>
        <div class="mstat-value mstat-ok">Blocked</div>
      </div>
      <div class="monitor-stat">
        <div class="mstat-label">Right Click</div>
        <div class="mstat-value mstat-ok">Blocked</div>
      </div>
    </div>

    <!-- Questions area -->
    <div id="quiz-content">
      <div class="section-label">Skill Verification Questions</div>
      <div id="questions-container"></div>

      <div class="submit-block">
        <div class="submit-progress" id="submit-progress-text">
          Answer all questions to enable submission.
        </div>
        <div class="progress-bar-track">
          <div class="progress-bar-fill" id="progress-bar" style="width:0%"></div>
        </div>
        <button id="btn-submit" onclick="submitQuiz()" disabled>
          Submit Quiz and See My Results
        </button>
        <div id="unanswered-msg">
          Please answer all questions before submitting.
        </div>
      </div>
    </div>

  </div>

  <!-- Violation overlay — inside quiz screen DOM so fullscreen contains it -->
  <div id="violation-overlay">
    <div class="vio-badge-large">Violation Detected</div>
    <div class="vio-title" id="vio-title-text">Rule Violation</div>
    <div class="vio-sub"   id="vio-sub-text"></div>
    <div class="vio-remaining" id="vio-remaining-text"></div>
    <button id="btn-resume" onclick="resumeTest()">
      I Understand — Resume Test
    </button>
  </div>

</div>

<!-- SCREEN 3 — TERMINATED -->
<div class="screen" id="screen-terminated">
  <div class="term-badge">Test Terminated</div>
  <div class="term-title">Maximum Violations Reached</div>
  <div class="term-sub">
    You have received 3 violations and your test has been permanently closed.
    Return to the Skill Input page and restart the process.
    Answer all questions honestly without switching tabs or leaving the camera frame.
  </div>
  <button id="btn-restart" onclick="handleRestart()">
    Return to Skill Input
  </button>
</div>

<canvas id="snap-canvas" width="320" height="240"></canvas>
<div id="sd-toast"></div>

<script>

// ════════════════════════════════════════
// CONSTANTS AND STATE
// ════════════════════════════════════════

const QUIZ_DATA      = {quiz_json};
const MAX_VIO        = 3;
const SNAP_INTERVAL  = 60000;
const FACE_CHK_INT   = 2000;
const NO_FACE_GRACE  = 5000;

let violations    = 0;
let terminated    = false;
let paused        = false;
let stream        = null;
let snapTimer     = null;
let clockTimer    = null;
let faceTimer     = null;
let noFaceTimeout = null;
let startTime     = null;
let answers       = {{}};
let totalQ        = 0;
let answeredQ     = 0;

// ════════════════════════════════════════
// STREAMLIT COMMUNICATION
// Sends a value back to Python via the official
// Streamlit component postMessage protocol.
// ════════════════════════════════════════

function sendToStreamlit(value) {{
  // Streamlit listens for this exact message shape from component iframes
  window.parent.postMessage({{
    isStreamlitMessage: true,
    type: 'streamlit:setComponentValue',
    value: value,
  }}, '*');
}}

// Tell Streamlit this component is ready (required handshake)
function notifyReady() {{
  window.parent.postMessage({{
    isStreamlitMessage: true,
    type: 'streamlit:componentReady',
    apiVersion: 1,
  }}, '*');
}}

// ════════════════════════════════════════
// SCREEN MANAGER
// ════════════════════════════════════════

function showScreen(id) {{
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}}

// ════════════════════════════════════════
// SCREEN 1 — CAMERA
// ════════════════════════════════════════

async function startCamera() {{
  const btn = document.getElementById('btn-allow-camera');
  const err = document.getElementById('cam-error-msg');

  btn.textContent  = 'Requesting camera access...';
  btn.disabled     = true;
  err.style.display = 'none';

  try {{
    stream = await navigator.mediaDevices.getUserMedia({{
      video: {{ width: 320, height: 240, facingMode: 'user' }},
      audio: false,
    }});

    const video     = document.getElementById('cam-video');
    video.srcObject = stream;
    await new Promise(r => video.onloadedmetadata = r);
    video.play();

    showScreen('screen-quiz');
    buildQuestions();
    initMonitoring();
    enterFullscreen();

  }} catch (e) {{
    err.style.display = 'block';
    err.textContent   =
      'Camera access failed: ' + e.message +
      '. Open your browser settings, allow camera access for this site, and refresh.';
    btn.textContent = 'Allow Camera and Begin Test';
    btn.disabled    = false;
  }}
}}

// ════════════════════════════════════════
// BUILD QUESTIONS
// ════════════════════════════════════════

function buildQuestions() {{
  const container = document.getElementById('questions-container');
  container.innerHTML = '';
  totalQ    = 0;
  answeredQ = 0;

  QUIZ_DATA.forEach((item, sIdx) => {{
    const block = document.createElement('div');
    block.className = 'skill-block';

    const header = document.createElement('div');
    header.className = 'skill-header';
    header.innerHTML =
      '<span class="skill-name">' + item.skill + '</span>' +
      '<span class="skill-level-tag">' + item.level + '</span>';
    block.appendChild(header);

    if (!item.questions || item.questions.length === 0) {{
      const note = document.createElement('div');
      note.className   = 'unverified-note';
      note.textContent =
        'Questions could not be generated for this skill. ' +
        'It will be accepted at your claimed level.';
      block.appendChild(note);
      container.appendChild(block);
      return;
    }}

    item.questions.forEach((q, qIdx) => {{
      totalQ++;
      const key = sIdx + '_' + qIdx;

      const qBlock = document.createElement('div');
      qBlock.className = 'q-block';

      const qNum = document.createElement('div');
      qNum.className   = 'q-number';
      qNum.textContent = 'Question ' + (qIdx + 1);
      qBlock.appendChild(qNum);

      const qText = document.createElement('div');
      qText.className   = 'q-text';
      qText.textContent = q.question;
      qBlock.appendChild(qText);

      const grid = document.createElement('div');
      grid.className = 'options-grid';

      [['A', q.option_a], ['B', q.option_b],
       ['C', q.option_c], ['D', q.option_d]].forEach(([letter, text]) => {{

        const btn = document.createElement('button');
        btn.className   = 'opt-btn';
        btn.dataset.key = key;
        btn.dataset.val = letter;
        btn.innerHTML   =
          '<span class="opt-letter">' + letter + '</span>' +
          '<span>' + text + '</span>';

        btn.onclick = function() {{
          if (terminated || paused) return;
          document.querySelectorAll('.opt-btn[data-key="' + key + '"]')
            .forEach(b => b.classList.remove('selected'));
          btn.classList.add('selected');
          const fresh = !(key in answers);
          answers[key] = letter;
          if (fresh) {{ answeredQ++; updateProgress(); }}
        }};

        grid.appendChild(btn);
      }});

      qBlock.appendChild(grid);
      block.appendChild(qBlock);
    }});

    container.appendChild(block);
  }});

  updateProgress();
}}

function updateProgress() {{
  const pct     = totalQ > 0 ? Math.round((answeredQ / totalQ) * 100) : 0;
  const btn     = document.getElementById('btn-submit');
  const bar     = document.getElementById('progress-bar');
  const progTxt = document.getElementById('submit-progress-text');

  bar.style.width = pct + '%';

  if (answeredQ >= totalQ && totalQ > 0) {{
    btn.disabled    = false;
    btn.textContent = 'Submit Quiz and See My Results';
    progTxt.textContent = 'All ' + totalQ + ' questions answered. Ready to submit.';
  }} else {{
    btn.disabled    = true;
    btn.textContent =
      'Submit Quiz and See My Results  (' + answeredQ + ' / ' + totalQ + ')';
    progTxt.textContent =
      answeredQ + ' of ' + totalQ + ' questions answered.';
  }}
}}

// ════════════════════════════════════════
// MONITORING
// ════════════════════════════════════════

function initMonitoring() {{
  startTime = Date.now();
  blockCopyPaste();
  watchTabSwitch();
  watchFace();
  scheduleSnapshots();
  runClock();
  watchFullscreenExit();
}}

function blockCopyPaste() {{
  document.addEventListener('keydown', e => {{
    if (terminated) return;
    const combo = (e.ctrlKey || e.metaKey) &&
      ['c','v','x','a','u','s','p'].includes(e.key.toLowerCase());
    if (combo) {{ e.preventDefault(); e.stopPropagation(); toast('Copy and paste is not allowed during the test.'); }}
    if (e.key === 'F11') e.preventDefault();
  }}, true);

  document.addEventListener('contextmenu', e => {{
    if (terminated) return;
    e.preventDefault();
    toast('Right-click is disabled during the test.');
  }});

  ['copy','cut','paste'].forEach(ev =>
    document.addEventListener(ev, e => {{ if (!terminated) e.preventDefault(); }})
  );
}}

function watchTabSwitch() {{
  document.addEventListener('visibilitychange', () => {{
    if (terminated || paused) return;
    if (document.hidden) {{
      setStatWarn('stat-tab', 'Left tab');
      triggerViolation('Tab Switch Detected',
        'You navigated away from the test window. ' +
        'Do not switch tabs or open other windows during the quiz.');
    }} else {{
      setStatOk('stat-tab', 'Active');
    }}
  }});

  window.addEventListener('blur', () => {{
    if (terminated || paused) return;
    triggerViolation('Window Focus Lost',
      'You switched to another application. ' +
      'Keep this window in focus throughout the test.');
  }});
}}

function watchFullscreenExit() {{
  document.addEventListener('fullscreenchange', () => {{
    if (terminated || paused) return;
    if (!document.fullscreenElement) {{
      triggerViolation('Fullscreen Exited',
        'You exited fullscreen mode. ' +
        'The test must remain in fullscreen at all times.');
    }}
  }});
  document.addEventListener('keydown', e => {{
    if (e.key === 'Escape' && !terminated) e.preventDefault();
  }}, true);
}}

function watchFace() {{
  const video  = document.getElementById('cam-video');
  const canvas = document.getElementById('snap-canvas');
  const ctx    = canvas.getContext('2d');

  faceTimer = setInterval(() => {{
    if (terminated || paused) return;
    try {{
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      const data = ctx.getImageData(0, 0, canvas.width, canvas.height);
      updateFaceUI(hasSkin(data));
    }} catch(e) {{}}
  }}, FACE_CHK_INT);
}}

function hasSkin(imageData) {{
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
  const dot = document.getElementById('face-indicator');
  if (found) {{
    dot.style.background = '#27ae60';
    setStatOk('stat-face', 'Detected');
    if (noFaceTimeout) {{ clearTimeout(noFaceTimeout); noFaceTimeout = null; }}
  }} else {{
    dot.style.background = '#e74c3c';
    setStatWarn('stat-face', 'Not detected');
    if (!noFaceTimeout && !paused) {{
      noFaceTimeout = setTimeout(() => {{
        if (!terminated && !paused) {{
          triggerViolation('Face Not Detected',
            'Your face is not visible in the camera. ' +
            'Remain within the camera frame at all times.');
        }}
        noFaceTimeout = null;
      }}, NO_FACE_GRACE);
    }}
  }}
}}

function scheduleSnapshots() {{
  setTimeout(takeSnap, 4000);
  snapTimer = setInterval(takeSnap, SNAP_INTERVAL);
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
    const t = new Date().toLocaleTimeString('en-IN', {{ hour: '2-digit', minute: '2-digit' }});
    setStatOk('stat-snap', t);
    flash.style.opacity = '1';
    setTimeout(() => flash.style.opacity = '0', 110);
  }} catch(e) {{}}
}}

function runClock() {{
  clockTimer = setInterval(() => {{
    if (terminated) return;
    const s  = Math.floor((Date.now() - startTime) / 1000);
    const mm = String(Math.floor(s / 60)).padStart(2,'0');
    const ss = String(s % 60).padStart(2,'0');
    document.getElementById('timer-display').textContent = mm + ':' + ss;
  }}, 1000);
}}

function setStatOk(id, text) {{
  const el = document.getElementById(id);
  el.textContent = text;
  el.className   = 'mstat-value mstat-ok';
}}

function setStatWarn(id, text) {{
  const el = document.getElementById(id);
  el.textContent = text;
  el.className   = 'mstat-value mstat-warn';
}}

// ════════════════════════════════════════
// FULLSCREEN
// ════════════════════════════════════════

function enterFullscreen() {{
  const el = document.getElementById('screen-quiz');
  if      (el.requestFullscreen)            el.requestFullscreen();
  else if (el.webkitRequestFullscreen)      el.webkitRequestFullscreen();
  else if (el.mozRequestFullScreen)         el.mozRequestFullScreen();
}}

function reEnterFullscreen() {{
  setTimeout(enterFullscreen, 350);
}}

// ════════════════════════════════════════
// VIOLATION SYSTEM
// ════════════════════════════════════════

function triggerViolation(title, message) {{
  if (terminated || paused) return;
  paused = true;
  violations++;
  document.getElementById('vio-count').textContent = violations;

  if (violations >= MAX_VIO) {{ terminateTest(); return; }}

  document.getElementById('vio-title-text').textContent   = title;
  document.getElementById('vio-sub-text').textContent     = message;
  document.getElementById('vio-remaining-text').textContent =
    'Violation ' + violations + ' of ' + MAX_VIO +
    '. ' + (MAX_VIO - violations) + ' more will permanently terminate the test.';

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
  clearInterval(clockTimer);
  clearInterval(faceTimer);
  if (noFaceTimeout) clearTimeout(noFaceTimeout);
  if (stream) stream.getTracks().forEach(t => t.stop());
  document.getElementById('violation-overlay').classList.remove('show');

  // ── FIX: send terminated signal directly to Python via postMessage ──
  sendToStreamlit(JSON.stringify({{ terminated: true }}));

  if (document.fullscreenElement) {{
    document.exitFullscreen().then(() => showScreen('screen-terminated'));
  }} else {{
    showScreen('screen-terminated');
  }}
}}

function handleRestart() {{
  // Signal Python to reset — it already received terminateTest() signal above,
  // but send again in case the user clicks Restart before Python processed it.
  sendToStreamlit(JSON.stringify({{ terminated: true }}));
}}

// ════════════════════════════════════════
// SUBMIT
// ════════════════════════════════════════

function submitQuiz() {{
  if (terminated) return;

  const warn = document.getElementById('unanswered-msg');
  if (answeredQ < totalQ) {{
    warn.style.display = 'block';
    return;
  }}
  warn.style.display = 'none';

  const btn = document.getElementById('btn-submit');
  btn.disabled    = true;
  btn.textContent = 'Submitting...';

  const payload = {{
    terminated: false,
    answers:    answers,
    quiz_data:  QUIZ_DATA,
  }};

  // ── FIX: send answers directly to Python via postMessage ──
  // No localStorage, no page reload needed.
  sendToStreamlit(JSON.stringify(payload));

  btn.textContent = 'Submitted — Processing your results...';
}}

// ════════════════════════════════════════
// TOAST
// ════════════════════════════════════════

function toast(msg) {{
  const t = document.getElementById('sd-toast');
  t.textContent   = msg;
  t.style.display = 'block';
  clearTimeout(t._to);
  t._to = setTimeout(() => t.style.display = 'none', 3200);
}}

// ════════════════════════════════════════
// INIT — tell Streamlit this component is ready
// ════════════════════════════════════════
notifyReady();

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
    1. Generate questions via Gemini and cache in session_state
    2. Check if quiz was already terminated (session_state flag)
    3. Render the proctored quiz HTML via components.html
       — components.html is bidirectional: the JS calls
         sendToStreamlit() which triggers a Streamlit rerun
         with the component value returned by components.html()
    4. If component value is present, parse and score answers
    5. Return verified_skills dict

    Parameters
    ----------
    selected_skills : dict  {{skill_name: claimed_level}}

    Returns
    -------
    verified_skills : dict  {{skill_name: verified_level}}
    """

    if not configure_gemini():
        st.error("Cannot run quiz — Gemini API not configured.")
        return {}

    student_name = st.session_state.get("student_name", "Student")

    # ── Generate questions — cached until skill selection changes ──
    selected_sig = tuple(sorted(selected_skills.items()))

    if (
        "quiz_data_sig" not in st.session_state
        or st.session_state["quiz_data_sig"] != selected_sig
    ):
        with st.spinner("Generating quiz questions. Please wait..."):
            quiz_data = []
            for skill, level in selected_skills.items():
                prompt    = build_quiz_prompt(skill, level)
                questions = call_gemini_with_retry(prompt, skill)
                quiz_data.append({
                    "skill":     skill,
                    "level":     level,
                    "questions": questions,
                })
                time.sleep(0.4)

            st.session_state["quiz_data"]     = quiz_data
            st.session_state["quiz_data_sig"] = selected_sig

    quiz_data = st.session_state["quiz_data"]

    # ── If terminated — show restart message ───────────────────
    if st.session_state.get("quiz_terminated"):
        st.markdown(
            "<div style='background:#fff5f5; border:1px solid #fecaca; "
            "border-radius:10px; padding:1rem 1.25rem; "
            "font-size:0.875rem; color:#7f1d1d; line-height:1.6;'>"
            "Your test was terminated after 3 violations. "
            "You must restart the skill input process to attempt the quiz again."
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        if st.button("Return to Skill Input", type="primary"):
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

    # ── Render quiz — component value is returned when JS calls sendToStreamlit ──
    st.markdown(
        "<div style='font-size:0.82rem; color:#515f74; "
        "margin-bottom:10px; line-height:1.55;'>"
        "Allow camera access when prompted. "
        "The quiz will begin after your camera is verified. "
        "Stay in fullscreen and do not switch tabs during the test."
        "</div>",
        unsafe_allow_html=True,
    )

    quiz_html = build_proctored_quiz_html(quiz_data, student_name)

    total_q_count = sum(
        len(item["questions"]) for item in quiz_data
        if item.get("questions")
    )
    component_height = min(
        max(700, 48 + (total_q_count * 185) + 140),
        920
    )

    # components.html returns None until JS calls sendToStreamlit(),
    # at which point Streamlit reruns and this returns the sent value.
    component_value = components.html(
        quiz_html,
        height=component_height,
        scrolling=False,
    )

    # ── Process returned value ─────────────────────────────────
    if component_value is None:
        return {}

    try:
        if isinstance(component_value, str):
            payload = json.loads(component_value)
        elif isinstance(component_value, dict):
            payload = component_value
        else:
            return {}
    except (json.JSONDecodeError, TypeError):
        return {}

    # Terminated signal
    if payload.get("terminated"):
        st.session_state["quiz_terminated"] = True
        st.markdown(
            "<div style='background:#fff5f5; border:1px solid #fecaca; "
            "border-radius:10px; padding:1rem 1.25rem; "
            "font-size:0.875rem; color:#7f1d1d; line-height:1.6;'>"
            "Your test was terminated after 3 violations. "
            "You must restart the skill input process."
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        if st.button("Return to Skill Input", type="primary"):
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

    # Submitted — score the answers
    raw_answers        = payload.get("answers", {})
    returned_quiz_data = payload.get("quiz_data", quiz_data)

    quiz_results    = []
    verified_skills = {}

    for skill_idx, item in enumerate(returned_quiz_data):
        skill     = item["skill"]
        level     = item["level"]
        questions = item.get("questions", [])

        student_answers = []
        for q_idx in range(len(questions)):
            key    = f"{skill_idx}_{q_idx}"
            letter = raw_answers.get(key, "")
            student_answers.append(letter)

        result = score_quiz_answers(skill, level, questions, student_answers)
        quiz_results.append(result)

        if result["verified_level"] != "Not Verified":
            verified_skills[skill] = result["verified_level"]

    # Fallback — if everything failed, use claimed levels
    if not verified_skills:
        for r in quiz_results:
            verified_skills[r["skill"]] = r["claimed_level"]

    st.session_state["quiz_results"]    = quiz_results
    st.session_state["verified_skills"] = verified_skills
    st.session_state["quiz_complete"]   = True

    st.success("Quiz submitted. Calculating your results...")
    return verified_skills