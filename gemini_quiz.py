import json
import re
import textwrap
import time
import streamlit as st
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
        st.warning(f"Gemini API key missing for {skill}. Using fallback. ({e})")
        return []

    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        st.warning(f"Gemini client error for {skill}: {e}")
        return []

    last_err = None
    for attempt in range(3):
        try:
            response  = client.models.generate_content(
                model=GEMINI_MODEL, contents=prompt
            )
            raw_text  = (response.text or "").strip()
            questions = parse_gemini_response(raw_text)
            if questions:
                return questions[:3]
            last_err = "empty/invalid response"
            time.sleep(0.8)
        except Exception as e:
            last_err = str(e)
            time.sleep(1.2)

    st.warning(
        f"Could not generate Gemini questions for {skill} ({last_err}). "
        "A self-assessment fallback question will be used."
    )
    return []


def parse_gemini_response(raw_text: str) -> list:
    if not raw_text:
        return []
    cleaned = re.sub(r"```(?:json)?\s*", "", raw_text)
    cleaned = re.sub(r"```", "", cleaned).strip()

    try:
        questions = json.loads(cleaned)
        if validate_questions(questions):
            return questions
    except json.JSONDecodeError:
        pass

    array_match = re.search(r"\[.*\]", cleaned, re.DOTALL)
    if array_match:
        try:
            questions = json.loads(array_match.group())
            if validate_questions(questions):
                return questions
        except json.JSONDecodeError:
            pass

    return []


def validate_questions(questions) -> bool:
    if not isinstance(questions, list) or len(questions) == 0:
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
# SECTION 4 — FALLBACK QUESTION BANK
# =============================================================

def fallback_questions(skill: str, level: str) -> list:
    s = skill
    return [
        {
            "question": f"Which statement best describes how you would handle a real {s} task at the {level} level?",
            "option_a": f"I can independently design and implement {s} solutions for production use.",
            "option_b": f"I can build standard {s} components with documentation and minor guidance.",
            "option_c": f"I have completed exercises in {s} but need a reference for most real tasks.",
            "option_d": f"I have only read about {s} and have not used it on any project.",
            "correct": "A" if level == "Advanced" else ("B" if level == "Intermediate" else "C"),
        },
        {
            "question": f"In {s}, what is the most reliable way to debug an unexpected runtime issue?",
            "option_a": "Guess and rewrite the code from scratch.",
            "option_b": "Read the error message, reproduce minimally, then inspect inputs and state.",
            "option_c": "Restart the machine and try again.",
            "option_d": "Avoid the operation that caused the issue.",
            "correct": "B",
        },
        {
            "question": f"Which practice most clearly indicates someone is genuinely working at the {level} level in {s}?",
            "option_a": "Copying full solutions from forums without understanding them.",
            "option_b": "Memorizing syntax with no project experience.",
            "option_c": f"Designing, implementing, testing, and explaining their work in {s} on real tasks.",
            "option_d": f"Talking about {s} without writing any code.",
            "correct": "C",
        },
    ]


# =============================================================
# SECTION 5 — ANSWER SCORER
# =============================================================

def score_quiz_answers(skill, claimed_level, questions, student_answers):
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
# SECTION 6 — QUIZ DATA GENERATION (cached per skill set)
# =============================================================

def ensure_quiz_data(selected_skills: dict):
    selected_sig = tuple(sorted(selected_skills.items()))
    if (
        "quiz_data_sig" in st.session_state
        and st.session_state.get("quiz_data_sig") == selected_sig
        and st.session_state.get("quiz_data")
    ):
        return st.session_state["quiz_data"]

    if not configure_gemini():
        st.error("Cannot generate quiz - Gemini not configured.")
        return None

    # ALL loader UI lives inside ONE st.empty() placeholder rendered
    # as pure HTML. No st.progress, no st.spinner. That means a
    # single .empty() call removes every trace of the loader -
    # no leftover progress bar or status line above the next page.
    loader = st.empty()

    def _render_loader(progress_pct: float, current_skill: str | None,
                       current_idx: int, total_count: int,
                       done: bool = False):
        # progress_pct is 0..1
        bar_width = max(0.0, min(1.0, progress_pct)) * 100.0
        if done:
            status_html = (
                "<div class='sd-quiz-loader-status' style='color:#15803d;'>"
                "All questions generated successfully.</div>"
            )
            spin_html = ""
            sub_text  = "Loading your test..."
        else:
            spin_html = "<div class='sd-quiz-loader-spin'></div>"
            sub_text  = ("Our AI is preparing questions tailored to every "
                         "skill and level you selected. This usually takes "
                         "a few seconds.")
            if current_skill:
                status_html = (
                    f"<div class='sd-quiz-loader-status'>"
                    f"Skill {current_idx} of {total_count} &middot; "
                    f"{current_skill}</div>"
                )
            else:
                status_html = (
                    "<div class='sd-quiz-loader-status'>Starting...</div>"
                )

        loader_html = textwrap.dedent(f"""
            <style>
            .sd-loader-fixed {{
                position: fixed;
                inset: 0;
                background: #f6fafe;
                z-index: 9000;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 24px;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            }}
            .sd-quiz-loader-card {{
                width: 100%;
                max-width: 520px;
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 14px;
                padding: 32px 32px 26px 32px;
                box-shadow: 0 8px 30px rgba(23,28,31,0.06);
                text-align: center;
            }}
            .sd-quiz-loader-title {{
                font-family: 'Manrope', sans-serif;
                font-size: 1.15rem;
                font-weight: 800;
                color: #002c98;
                margin-bottom: 6px;
            }}
            .sd-quiz-loader-sub {{
                font-size: 0.88rem;
                color: #515f74;
                margin-bottom: 20px;
                line-height: 1.5;
            }}
            .sd-quiz-loader-spin {{
                width: 38px; height: 38px;
                border: 3px solid #e2e8f0;
                border-top-color: #002c98;
                border-radius: 50%;
                margin: 0 auto 18px auto;
                animation: sd-spin 0.85s linear infinite;
            }}
            @keyframes sd-spin {{ to {{ transform: rotate(360deg); }} }}
            .sd-quiz-bar-track {{
                width: 100%;
                height: 8px;
                background: #e2e8f0;
                border-radius: 4px;
                overflow: hidden;
                margin-top: 4px;
            }}
            .sd-quiz-bar-fill {{
                height: 100%;
                background: #002c98;
                border-radius: 4px;
                transition: width 0.3s ease;
            }}
            .sd-quiz-loader-status {{
                font-size: 0.82rem;
                color: #171c1f;
                font-weight: 600;
                margin-top: 14px;
                min-height: 1.2em;
            }}
            </style>
            <div class="sd-loader-fixed">
              <div class="sd-quiz-loader-card">
                {spin_html}
                <div class="sd-quiz-loader-title">Generating your personalized quiz</div>
                <div class="sd-quiz-loader-sub">{sub_text}</div>
                <div class="sd-quiz-bar-track">
                  <div class="sd-quiz-bar-fill" style="width:{bar_width:.1f}%;"></div>
                </div>
                {status_html}
              </div>
            </div>
        """).strip()
        # IMPORTANT: dedent + strip removes the leading-whitespace
        # that was tricking Streamlit's markdown processor into
        # rendering the entire HTML body as an indented code block
        # (which is what produced the "raw HTML in a code box"
        # flash the user reported).
        loader.markdown(loader_html, unsafe_allow_html=True)

    _render_loader(0.0, None, 0, max(len(selected_skills), 1))

    quiz_data = []
    total = max(len(selected_skills), 1)
    for i, (skill, level) in enumerate(selected_skills.items()):
        _render_loader(i / total, skill, i + 1, total)
        prompt    = build_quiz_prompt(skill, level)
        questions = call_gemini_with_retry(prompt, skill)
        source = "gemini"
        if not questions:
            questions = fallback_questions(skill, level)
            source = "fallback"
        quiz_data.append({
            "skill":     skill,
            "level":     level,
            "questions": questions[:3],
            "source":    source,
        })
        time.sleep(0.2)

    # Skip the done=True final render - it was prone to a Streamlit
    # markdown bug where blank lines inside the f-string caused the
    # entire HTML body to be re-interpreted as an indented code block,
    # showing raw HTML to the user for ~400 ms. Clearing the loader
    # directly is a clean and instant transition into the in-test view.
    loader.empty()

    st.session_state["quiz_data"]     = quiz_data
    st.session_state["quiz_data_sig"] = selected_sig
    return quiz_data


# =============================================================
# SECTION 7 — RESET HELPERS
# =============================================================

QUIZ_KEYS = [
    "quiz_data", "quiz_data_sig", "quiz_terminated", "quiz_complete",
    "quiz_results", "verified_skills", "quiz_violations",
    "quiz_started_at", "quiz_face_misses", "quiz_tab_switches",
]


def reset_quiz_state(full=False):
    for k in QUIZ_KEYS:
        if k in st.session_state:
            del st.session_state[k]
    # Also delete any q_X_Y answer keys
    for k in [k for k in list(st.session_state.keys()) if str(k).startswith("q_")]:
        del st.session_state[k]
    if full:
        for k in (
            "student_name", "semester", "selected_skills",
            "drift_score", "drift_label", "track_counts",
            "entropy_score", "entropy_label", "career_matches",
            "best_track", "match_pct", "readiness_score",
            "next_skill_info", "urgency_info", "focus_debt_info",
            "peer_info", "session_start",
        ):
            if k in st.session_state:
                del st.session_state[k]


# =============================================================
# SECTION 8 — SCORING ENTRY POINT
# Called by the quiz page after Submit.
# =============================================================

def score_all(quiz_data: list) -> dict:
    quiz_results    = []
    verified_skills = {}
    for skill_idx, item in enumerate(quiz_data):
        skill     = item["skill"]
        level     = item["level"]
        questions = item.get("questions", [])

        answers = []
        for q_idx in range(len(questions)):
            sel = st.session_state.get(f"q_{skill_idx}_{q_idx}")
            letter = ""
            if isinstance(sel, str) and len(sel) > 0:
                letter = sel[0].upper()
            answers.append(letter)

        result = score_quiz_answers(skill, level, questions, answers)
        quiz_results.append(result)
        if result["verified_level"] != "Not Verified":
            verified_skills[skill] = result["verified_level"]

    if not verified_skills:
        for r in quiz_results:
            verified_skills[r["skill"]] = r["claimed_level"]

    st.session_state["quiz_results"]    = quiz_results
    st.session_state["verified_skills"] = verified_skills
    st.session_state["quiz_complete"]   = True
    return verified_skills