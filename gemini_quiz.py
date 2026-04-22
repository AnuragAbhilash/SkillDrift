# gemini_quiz.py — SkillDrift Gemini Quiz Engine

import json
import re
import time
import streamlit as st
from google import genai


def configure_gemini():
    try:
        api_key = st.secrets["gemini"]["api_key"]
        st.session_state["gemini_client"] = genai.Client(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"Gemini API configuration failed: {str(e)}")
        return False


def build_quiz_prompt(skill: str, level: str) -> str:
    prompt = f"""You are an expert technical interviewer for Indian CSE placement preparation.

Generate exactly 3 multiple choice questions to test a B.Tech CSE student's knowledge of {skill} at {level} level.

Rules:
- Questions must be practical and specific to {skill}
- Difficulty must match {level} level exactly
- Each question must have exactly 4 options: A, B, C, D
- Exactly one option must be correct
- The correct answers must be randomly distributed among A, B, C, and D
- Do NOT repeat the same correct option more than twice
- Output MUST contain exactly 3 questions (no more, no less)

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

Constraints:
- The "correct" field must be exactly one of: A, B, C, or D (uppercase only)
- Return ONLY the JSON array
- No explanation, no markdown, no code block, no trailing commas
"""
    return prompt


GEMINI_MODEL = "gemini-2.5-flash"


def call_gemini_with_retry(prompt: str, skill: str) -> list:
    try:
        api_key = st.secrets["gemini"]["api_key"]
    except Exception as e:
        st.error(f"Gemini API key missing or misconfigured. Check .streamlit/secrets.toml. Error: {e}")
        return []

    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"Could not create Gemini client: {e}")
        return []

    for attempt in range(2):
        try:
            response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
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
                st.warning(f"Gemini API error for {skill} ({type(e).__name__}): {e}. Skill accepted as Unverified.")
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
    required_keys = {"question", "option_a", "option_b", "option_c", "option_d", "correct"}
    for q in questions:
        if not isinstance(q, dict):
            return False
        if not required_keys.issubset(q.keys()):
            return False
        if str(q.get("correct", "")).upper() not in {"A", "B", "C", "D"}:
            return False
    return True


def score_quiz_answers(skill: str, claimed_level: str, questions: list, student_answers: list) -> dict:
    if not questions:
        return {
            "skill": skill, "claimed_level": claimed_level,
            "verified_level": claimed_level, "status": "Unverified",
            "correct_count": 0, "total_questions": 0,
        }

    total = len(questions)
    correct_count = 0

    for i, question in enumerate(questions):
        if i >= len(student_answers):
            break
        student_answer = str(student_answers[i]).upper().strip()
        correct_answer = str(question.get("correct", "")).upper().strip()
        if student_answer == correct_answer:
            correct_count += 1

    ratio = correct_count / total

    if ratio >= 0.67:
        status = "Confirmed"
        verified_level = claimed_level
    elif ratio >= 0.34:
        status = "Borderline"
        verified_level = claimed_level if claimed_level == "Beginner" else downgrade_level(claimed_level)
    else:
        status = "Not Verified"
        verified_level = "Not Verified"

    return {
        "skill": skill, "claimed_level": claimed_level,
        "verified_level": verified_level, "status": status,
        "correct_count": correct_count, "total_questions": total,
    }


def downgrade_level(level: str) -> str:
    return {"Advanced": "Intermediate", "Intermediate": "Beginner", "Beginner": "Beginner"}.get(level, "Beginner")


def run_skill_verification_quiz(selected_skills: dict) -> dict:

    if not configure_gemini():
        st.error("Cannot run quiz — Gemini API not configured.")
        return {}

    # Custom CSS for clean quiz UI
    st.markdown("""
    <style>
        div[data-testid="stForm"] {
            border: none !important;
            padding: 0 !important;
            background: transparent !important;
        }
        .quiz-skill-header {
            background: #FFFFFF;
            border: 1px solid #D2D2D7;
            border-left: 4px solid #6C63FF;
            border-radius: 10px;
            padding: 0.6rem 1rem;
            margin: 1rem 0 0.5rem 0;
        }
        .quiz-skill-name {
            font-weight: 700;
            font-size: 0.95rem;
            color: #1D1D1F;
        }
        .quiz-skill-level {
            font-size: 0.78rem;
            color: #86868B;
            margin-top: 0.1rem;
        }
        .quiz-q-label {
            font-size: 0.88rem;
            font-weight: 600;
            color: #1D1D1F;
            margin: 0.75rem 0 0.35rem 0;
            line-height: 1.45;
        }
        .stRadio > div { gap: 0.35rem !important; }
        .stRadio > div > label {
            background: #FFFFFF !important;
            border: 1px solid #E5E5EA !important;
            border-radius: 8px !important;
            padding: 0.5rem 0.85rem !important;
            font-size: 0.85rem !important;
            color: #1D1D1F !important;
            cursor: pointer !important;
            transition: border-color 0.1s ease !important;
        }
        .stRadio > div > label:hover {
            border-color: #6C63FF !important;
        }
        .stRadio > div > label[data-checked="true"] {
            border-color: #6C63FF !important;
            background: #F0EFFF !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom:1rem;">
        <div style="font-size:1rem; font-weight:600; color:#1D1D1F; margin-bottom:0.2rem;">
            Skill Verification Quiz
        </div>
        <div style="font-size:0.85rem; color:#86868B;">
            Answer honestly — your analysis depends on accurate results.
            This quiz verifies whether you actually know what you claimed.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Generate questions once
    selected_sig = tuple(sorted(selected_skills.items()))

    if "quiz_data_sig" not in st.session_state or st.session_state["quiz_data_sig"] != selected_sig:
        with st.spinner(f"Generating quiz questions via Gemini AI..."):
            st.session_state["quiz_data"] = []
            for skill, level in selected_skills.items():
                prompt    = build_quiz_prompt(skill, level)
                questions = call_gemini_with_retry(prompt, skill)
                st.session_state["quiz_data"].append({
                    "skill": skill, "level": level, "questions": questions,
                })
                time.sleep(0.5)
        st.session_state["quiz_data_sig"] = selected_sig

    all_quiz_data = st.session_state["quiz_data"]

    # ── Collect answers inside a form to prevent re-runs on radio click ──
    with st.form("quiz_form", clear_on_submit=False):
        student_responses = {}

        for quiz_item in all_quiz_data:
            skill     = quiz_item["skill"]
            level     = quiz_item["level"]
            questions = quiz_item["questions"]

            st.markdown(f"""
            <div class="quiz-skill-header">
                <div class="quiz-skill-name">{skill}</div>
                <div class="quiz-skill-level">{level} level</div>
            </div>
            """, unsafe_allow_html=True)

            if not questions:
                st.markdown(
                    f"<div style='color:#86868B; font-size:0.85rem; padding:0.35rem 0;'>"
                    f"No questions generated for {skill}. It will be accepted as Unverified.</div>",
                    unsafe_allow_html=True,
                )
                student_responses[skill] = []
                continue

            answers_for_skill = []
            for q_idx, q in enumerate(questions):
                st.markdown(f'<div class="quiz-q-label">Q{q_idx + 1}. {q["question"]}</div>',
                            unsafe_allow_html=True)

                options = {
                    "A": q["option_a"],
                    "B": q["option_b"],
                    "C": q["option_c"],
                    "D": q["option_d"],
                }
                option_labels = [f"{k}: {v}" for k, v in options.items()]

                selected = st.radio(
                    label=f"Answer for {skill} Q{q_idx + 1}",
                    options=option_labels,
                    key=f"quiz_{skill}_{q_idx}",
                    index=None,
                    label_visibility="collapsed",
                )
                answer_letter = selected[0] if selected else None
                answers_for_skill.append(answer_letter)

            student_responses[skill] = answers_for_skill
            st.markdown("<div style='height:0.25rem;'></div>", unsafe_allow_html=True)

        st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
        submit_quiz = st.form_submit_button(
            "Submit Quiz and See My Results",
            type="primary",
            use_container_width=True,
        )

    if not submit_quiz:
        return {}

    # Validate all answered
    unanswered = []
    for quiz_item in all_quiz_data:
        skill = quiz_item["skill"]
        if not quiz_item["questions"]:
            continue
        answers = student_responses.get(skill, [])
        if None in answers or len(answers) < len(quiz_item["questions"]):
            unanswered.append(skill)

    if unanswered:
        st.error(f"Please answer all questions before submitting. Unanswered: {', '.join(unanswered)}")
        return {}

    # Score
    quiz_results    = []
    verified_skills = {}

    for quiz_item in all_quiz_data:
        skill     = quiz_item["skill"]
        level     = quiz_item["level"]
        questions = quiz_item["questions"]
        answers   = student_responses.get(skill, [])

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

    st.success("Quiz submitted. Calculating your results...")
    return verified_skills
