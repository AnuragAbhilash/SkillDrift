# =============================================================
# gemini_quiz.py — SkillDrift Gemini Quiz Engine
# Handles all Gemini API interaction for skill verification.
# Called only from pages/02_skill_input.py
# =============================================================

import json
import re
import time
import streamlit as st
from google import genai
from google.genai import types

# =============================================================
# SECTION 1 — CONFIGURE GEMINI API
# API key is read from Streamlit secrets (secrets.toml)
# Never hardcoded in this file.
# =============================================================

def configure_gemini():
    """
    Configures the Gemini API client using the key from secrets.
    Call this once at the start of the quiz flow.
    Returns True if configured successfully, False otherwise.
    """
    try:
        api_key = st.secrets["gemini"]["api_key"]
        st.session_state["gemini_client"] = genai.Client(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"Gemini API configuration failed: {str(e)}")
        return False


# =============================================================
# SECTION 2 — PROMPT BUILDER
# Builds the exact prompt sent to Gemini for each skill.
# =============================================================

def build_quiz_prompt(skill: str, level: str) -> str:
    """
    Builds a clean, specific prompt for Gemini to generate
    2 multiple choice questions for a given skill and level.

    Parameters
    ----------
    skill : str   e.g. "SQL"
    level : str   e.g. "Intermediate"

    Returns
    -------
    prompt : str
    """
    prompt = f"""You are an expert technical interviewer for Indian CSE placement preparation.

Generate exactly 2 multiple choice questions to test a B.Tech CSE student's knowledge of {skill} at {level} level.

Rules:
- Questions must be practical and specific to {skill}
- Difficulty must match {level} level exactly
- Each question must have exactly 4 options: A, B, C, D
- Exactly one option must be correct
- Return ONLY a valid JSON array with no extra text before or after

Required JSON format:
[
  {{
    "question": "Your question text here?",
    "option_a": "First option",
    "option_b": "Second option",
    "option_c": "Third option",
    "option_d": "Fourth option",
    "correct": "A"
  }},
  {{
    "question": "Your second question text here?",
    "option_a": "First option",
    "option_b": "Second option",
    "option_c": "Third option",
    "option_d": "Fourth option",
    "correct": "B"
  }}
]

The "correct" field must be exactly one of: A, B, C, or D (uppercase only).
Return only the JSON array. No explanation. No markdown. No code blocks."""

    return prompt


# =============================================================
# SECTION 3 — GEMINI API CALLER WITH SAFETY WRAPPER
# Tries twice before marking skill as Unverified.
# Never crashes the app on bad Gemini response.
# =============================================================

def call_gemini_with_retry(prompt: str, skill: str) -> list:
    """
    Calls Gemini API and attempts to parse the JSON response.
    Retries once if the first response is malformed.
    Returns empty list if both attempts fail.

    Parameters
    ----------
    prompt : str   The prompt to send to Gemini
    skill  : str   Skill name (used only for error messages)

    Returns
    -------
    questions : list of dicts  (empty list = both attempts failed)
    """

   

    try:
        api_key = st.secrets["gemini"]["api_key"]
        client = genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"DEBUG — Gemini error on attempt {attempt+1} for {skill}: {type(e).__name__}: {str(e)}")
        if attempt == 0:
            time.sleep(2)
        else:
            return []

    for attempt in range(2):
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
            )
            raw_text = response.text.strip()

            # Try to extract JSON even if Gemini added extra text
            questions = parse_gemini_response(raw_text, skill, attempt + 1)

            if questions:
                return questions

            # If parsing failed and this is attempt 1, wait briefly and retry
            if attempt == 0:
                time.sleep(1)

        except Exception as e:
            if attempt == 0:
                time.sleep(2)
            else:
                # Both attempts failed — return empty list
                return []

    return []


def parse_gemini_response(raw_text: str, skill: str, attempt: int) -> list:
    """
    Attempts to parse Gemini's response as a JSON array.
    Handles common issues like markdown code blocks and extra text.

    Parameters
    ----------
    raw_text : str    Raw text from Gemini response
    skill    : str    Used for error display only
    attempt  : int    1 or 2 (for logging)

    Returns
    -------
    questions : list  (empty list if parsing fails)
    """

    # Step 1 — Remove markdown code fences if present
    # Gemini sometimes wraps JSON in ```json ... ```
    cleaned = re.sub(r"```(?:json)?\s*", "", raw_text)
    cleaned = re.sub(r"```", "", cleaned)
    cleaned = cleaned.strip()

    # Step 2 — Try direct JSON parse
    try:
        questions = json.loads(cleaned)
        if validate_questions(questions):
            return questions
    except json.JSONDecodeError:
        pass

    # Step 3 — Try to extract JSON array using regex
    # Find the first [ ... ] block in the response
    array_match = re.search(r"\[.*?\]", cleaned, re.DOTALL)
    if array_match:
        try:
            questions = json.loads(array_match.group())
            if validate_questions(questions):
                return questions
        except json.JSONDecodeError:
            pass

    # Both parsing strategies failed
    return []


def validate_questions(questions: list) -> bool:
    """
    Validates that the parsed JSON has the correct structure.
    Returns True if valid, False if any required field is missing.
    """
    if not isinstance(questions, list):
        return False

    if len(questions) == 0:
        return False

    required_keys = {"question", "option_a", "option_b", "option_c", "option_d", "correct"}

    for q in questions:
        if not isinstance(q, dict):
            return False
        if not required_keys.issubset(q.keys()):
            return False
        # correct must be A, B, C, or D
        if str(q.get("correct", "")).upper() not in {"A", "B", "C", "D"}:
            return False

    return True


# =============================================================
# SECTION 4 — QUIZ SCORER
# Determines verified level for each skill based on quiz results.
# =============================================================

def score_quiz_answers(skill: str, claimed_level: str,
                       questions: list, student_answers: list) -> dict:
    """
    Scores the student's answers for one skill's quiz questions.

    Scoring rules:
    - More than half correct → level Confirmed at claimed level
    - Exactly half correct   → level Downgraded by one step
    - Fewer than half correct → Not Verified (excluded from analysis)

    Parameters
    ----------
    skill           : str   e.g. "SQL"
    claimed_level   : str   e.g. "Intermediate"
    questions       : list  List of question dicts from Gemini
    student_answers : list  List of student's answers e.g. ["A", "C"]

    Returns
    -------
    dict with keys:
        skill           : str
        claimed_level   : str
        verified_level  : str  (confirmed level, downgraded, or "Not Verified")
        status          : str  ("Confirmed", "Downgraded", "Not Verified")
        correct_count   : int
        total_questions : int
    """

    if not questions:
        # Gemini failed to generate questions — accept without verification
        return {
            "skill":           skill,
            "claimed_level":   claimed_level,
            "verified_level":  claimed_level,
            "status":          "Unverified",
            "correct_count":   0,
            "total_questions": 0,
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

    # Determine result based on score
    if correct_count > total / 2:
        # More than half correct — confirmed
        status = "Confirmed"
        verified_level = claimed_level

    elif correct_count == total / 2:
        # Exactly half correct — downgrade one step
        status = "Downgraded"
        verified_level = downgrade_level(claimed_level)

    else:
        # Fewer than half correct — not verified
        status = "Not Verified"
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
    """
    Downgrades a skill level by one step.
    Advanced -> Intermediate -> Beginner -> Not Verified
    """
    downgrade_map = {
        "Advanced":     "Intermediate",
        "Intermediate": "Beginner",
        "Beginner":     "Not Verified",
    }
    return downgrade_map.get(level, "Not Verified")


# =============================================================
# SECTION 5 — FULL QUIZ RUNNER
# Orchestrates the complete quiz for all selected skills.
# This is the main function called from 02_skill_input.py
# =============================================================

def run_skill_verification_quiz(selected_skills: dict) -> dict:
    """
    Runs the complete verification quiz for all selected skills.
    Displays questions in Streamlit UI and collects answers.

    This function is called ONCE from 02_skill_input.py after
    the student submits their skill selections.

    Parameters
    ----------
    selected_skills : dict
        {skill_name: claimed_level}
        e.g. {"Python": "Intermediate", "SQL": "Advanced"}

    Returns
    -------
    verified_skills : dict
        {skill_name: verified_level}
        Only includes skills that are Confirmed, Downgraded, or Unverified.
        Not Verified skills are EXCLUDED from this dict.

    Also stores in st.session_state:
        quiz_results      : list of result dicts (for display in Window 2)
        verified_skills   : dict (same as return value)
    """

    if not configure_gemini():
        st.error("Cannot run quiz — Gemini API not configured.")
        return {}

    st.markdown("---")
    st.subheader("🎯 Skill Verification Quiz")
    st.markdown(
        "Answer these questions honestly. Your analysis depends on accurate results. "
        "**This quiz verifies whether you actually know what you claimed.**"
    )

    # Generate all questions first so student sees all at once
    all_quiz_data = []

    with st.spinner("Generating quiz questions using Gemini AI..."):
        for skill, level in selected_skills.items():
            prompt = build_quiz_prompt(skill, level)
            questions = call_gemini_with_retry(prompt, skill)
            all_quiz_data.append({
                "skill":    skill,
                "level":    level,
                "questions": questions,
            })
            # Small delay between API calls to respect rate limits
            time.sleep(0.5)

    # Display questions and collect answers
    st.markdown("---")
    student_responses = {}  # skill -> list of answers

    for quiz_item in all_quiz_data:
        skill = quiz_item["skill"]
        level = quiz_item["level"]
        questions = quiz_item["questions"]

        if not questions:
            st.warning(
                f"⚠️ Could not generate questions for **{skill}**. "
                f"It will be accepted as **Unverified**."
            )
            student_responses[skill] = []
            continue

        st.markdown(f"### {skill} — {level} Level")

        answers_for_skill = []
        for q_idx, q in enumerate(questions):
            st.markdown(f"**Q{q_idx + 1}. {q['question']}**")

            options = {
                "A": q["option_a"],
                "B": q["option_b"],
                "C": q["option_c"],
                "D": q["option_d"],
            }

            # Display as radio buttons
            option_labels = [f"{k}: {v}" for k, v in options.items()]
            selected = st.radio(
                label=f"Select your answer:",
                options=option_labels,
                key=f"quiz_{skill}_{q_idx}",
                index=None,
            )

            # Extract just the letter (A/B/C/D) from the selected option
            if selected:
                answer_letter = selected[0]
            else:
                answer_letter = None

            answers_for_skill.append(answer_letter)
            st.markdown("")  # spacing

        student_responses[skill] = answers_for_skill
        st.markdown("---")

    # Submit button
    submit_quiz = st.button(
        "✅ Submit Quiz and See My Results",
        type="primary",
        use_container_width=True,
    )

    if not submit_quiz:
        return {}

    # Check all questions answered
    unanswered = []
    for quiz_item in all_quiz_data:
        skill = quiz_item["skill"]
        if not quiz_item["questions"]:
            continue
        answers = student_responses.get(skill, [])
        if None in answers or len(answers) < len(quiz_item["questions"]):
            unanswered.append(skill)

    if unanswered:
        st.error(
            f"Please answer all questions before submitting. "
            f"Unanswered skills: {', '.join(unanswered)}"
        )
        return {}

    # Score all answers
    quiz_results = []
    verified_skills = {}

    for quiz_item in all_quiz_data:
        skill    = quiz_item["skill"]
        level    = quiz_item["level"]
        questions = quiz_item["questions"]
        answers  = student_responses.get(skill, [])

        result = score_quiz_answers(skill, level, questions, answers)
        quiz_results.append(result)

        # Only include skills that are not "Not Verified"
        if result["verified_level"] != "Not Verified":
            verified_skills[skill] = result["verified_level"]

    # Save to session state
    st.session_state["quiz_results"]    = quiz_results
    st.session_state["verified_skills"] = verified_skills

    return verified_skills