import json
import re
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

    # Centered, professional loader card. Streamlit's default
    # st.spinner rendered against a wide layout produced an
    # off-center block on the Proctored Quiz page; we draw our
    # own centered card instead so it sits in the visual middle
    # of the page on every viewport.
    st.markdown(
        """
        <style>
        .sd-quiz-loader-wrap {
            min-height: 70vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 24px;
        }
        .sd-quiz-loader-card {
            width: 100%;
            max-width: 520px;
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 32px 32px 28px 32px;
            box-shadow: 0 8px 30px rgba(23,28,31,0.06);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            text-align: center;
        }
        .sd-quiz-loader-title {
            font-family: 'Manrope', sans-serif;
            font-size: 1.15rem;
            font-weight: 800;
            color: #002c98;
            margin-bottom: 6px;
            letter-spacing: -0.01em;
        }
        .sd-quiz-loader-sub {
            font-size: 0.88rem;
            color: #515f74;
            margin-bottom: 20px;
            line-height: 1.5;
        }
        .sd-quiz-loader-spin {
            width: 38px;
            height: 38px;
            border: 3px solid #e2e8f0;
            border-top-color: #002c98;
            border-radius: 50%;
            margin: 0 auto 18px auto;
            animation: sd-spin 0.85s linear infinite;
        }
        @keyframes sd-spin { to { transform: rotate(360deg); } }
        .sd-quiz-loader-card .stProgress > div > div {
            background-color: #002c98 !important;
        }
        .sd-quiz-loader-status {
            font-size: 0.82rem;
            color: #171c1f;
            font-weight: 600;
            margin-top: 12px;
            min-height: 1.2em;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    loader = st.empty()
    with loader.container():
        st.markdown(
            """
            <div class="sd-quiz-loader-wrap">
              <div class="sd-quiz-loader-card" id="sd-quiz-loader-card">
                <div class="sd-quiz-loader-spin"></div>
                <div class="sd-quiz-loader-title">Generating your personalized quiz</div>
                <div class="sd-quiz-loader-sub">
                  Our AI is preparing questions tailored to every skill
                  and level you selected. This usually takes a few seconds.
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        prog_placeholder = st.empty()
        status_placeholder = st.empty()

        with prog_placeholder.container():
            prog = st.progress(0)

        quiz_data = []
        total = max(len(selected_skills), 1)
        for i, (skill, level) in enumerate(selected_skills.items()):
            with prog_placeholder.container():
                prog = st.progress(
                    i / total,
                    text=f"Preparing questions for {skill} ({level})...",
                )
            status_placeholder.markdown(
                f"<div class='sd-quiz-loader-status'>"
                f"Skill {i+1} of {total} &middot; {skill}</div>",
                unsafe_allow_html=True,
            )
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
            time.sleep(0.25)

        with prog_placeholder.container():
            prog = st.progress(1.0, text="Questions ready.")
        status_placeholder.markdown(
            "<div class='sd-quiz-loader-status' style='color:#15803d;'>"
            "All questions generated successfully.</div>",
            unsafe_allow_html=True,
        )
        time.sleep(0.4)

    # Clear the loader card so the quiz UI can render cleanly
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
