# =============================================================
# test_brain.py — SkillDrift Brain Function Test Suite
# Run this file to verify all brain.py functions work correctly
# Usage: python test_brain.py
# =============================================================

import sys
import traceback

def run_test(test_name, func):
    """Helper to run a test and report pass/fail clearly."""
    try:
        result = func()
        print(f"  ✅ PASS — {test_name}")
        return result
    except Exception as e:
        print(f"  ❌ FAIL — {test_name}")
        print(f"     Error: {str(e)}")
        traceback.print_exc()
        return None

print()
print("=" * 60)
print("  SKILLDRIFT — brain.py TEST SUITE")
print("=" * 60)

# Import all functions
print()
print("[ STEP 1 ] Importing brain.py functions...")
try:
    from brain import (
        calculate_drift_score,
        calculate_entropy,
        calculate_career_match,
        calculate_readiness_score,
        get_next_skill,
        get_urgency_level,
        calculate_focus_debt,
        get_peer_placement_rate,
        verify_faculty_login,
        generate_student_report_csv,
        load_required_skills,
        load_skills_mapping,
        load_city_job_counts,
        load_faculty_credentials,
    )
    print("  ✅ All imports successful")
except ImportError as e:
    print(f"  ❌ Import failed: {e}")
    sys.exit(1)


# =============================================================
# TEST DATA — Priya's profile from the project story
# =============================================================
priya_skills = {
    "Python":    "Intermediate",
    "HTML":      "Beginner",
    "SQL":       "Advanced",
    "Excel":     "Beginner",
}

priya_semester = 4


# =============================================================
# TEST 1 — CSV DATA LOADING
# =============================================================
print()
print("[ STEP 2 ] Testing CSV data loading...")

def test_load_required_skills():
    df = load_required_skills()
    assert len(df) > 0, "required_skills_per_track.csv is empty"
    assert "track" in df.columns, "Missing column: track"
    assert "skill" in df.columns, "Missing column: skill"
    assert "frequency_pct" in df.columns, "Missing column: frequency_pct"
    print(f"           Loaded {len(df)} rows, {df['track'].nunique()} unique tracks")
    return df

def test_load_skills_mapping():
    df = load_skills_mapping()
    assert len(df) > 0, "skills_mapping.csv is empty"
    assert "skill" in df.columns, "Missing column: skill"
    assert "track" in df.columns, "Missing column: track"
    print(f"           Loaded {len(df)} skill-track mappings")
    return df

def test_load_city_job_counts():
    df = load_city_job_counts()
    assert len(df) > 0, "city_job_counts.csv is empty"
    print(f"           Loaded {len(df)} city-role rows")
    return df

def test_load_faculty_credentials():
    df = load_faculty_credentials()
    assert len(df) > 0, "faculty_credentials.csv is empty"
    assert "email" in df.columns, "Missing column: email"
    assert "hashed_password" in df.columns, "Missing column: hashed_password"
    print(f"           Loaded {len(df)} faculty accounts")
    return df

run_test("load_required_skills()", test_load_required_skills)
run_test("load_skills_mapping()", test_load_skills_mapping)
run_test("load_city_job_counts()", test_load_city_job_counts)
run_test("load_faculty_credentials()", test_load_faculty_credentials)


# =============================================================
# TEST 2 — DRIFT SCORE
# =============================================================
print()
print("[ STEP 3 ] Testing calculate_drift_score()...")

drift_score = None
track_counts = None

def test_drift_score():
    global drift_score, track_counts
    score, label, counts = calculate_drift_score(priya_skills)
    assert isinstance(score, float), "drift_score must be a float"
    assert 0.0 <= score <= 100.0, f"drift_score out of range: {score}"
    assert label in [
        "Highly Focused", "Moderately Focused",
        "Drifting", "Highly Scattered", "Insufficient Skills"
    ], f"Unexpected label: {label}"
    assert isinstance(counts, dict), "track_counts must be a dict"
    assert len(counts) == 8, f"Expected 8 tracks, got {len(counts)}"
    drift_score = score
    track_counts = counts
    print(f"           Score: {score} | Label: {label}")
    print(f"           Track counts: {counts}")
    return score

run_test("calculate_drift_score(priya_skills)", test_drift_score)

# Edge case — fewer than 3 skills
def test_drift_score_edge_case():
    score, label, counts = calculate_drift_score({"Python": "Beginner"})
    assert score == 0.0, "Score should be 0 for fewer than 3 skills"
    assert label == "Insufficient Skills"
    print(f"           Edge case (1 skill): Score={score}, Label={label} ✅")

run_test("calculate_drift_score() — edge case < 3 skills", test_drift_score_edge_case)


# =============================================================
# TEST 3 — ENTROPY SCORE
# =============================================================
print()
print("[ STEP 4 ] Testing calculate_entropy()...")

entropy_score = None

def test_entropy():
    global entropy_score
    assert track_counts is not None, "track_counts not set — drift score test failed"
    score, label = calculate_entropy(track_counts)
    assert isinstance(score, float), "entropy_score must be a float"
    assert score >= 0.0, f"entropy_score cannot be negative: {score}"
    entropy_score = score
    print(f"           Score: {score} bits | Label: {label}")
    return score

run_test("calculate_entropy(track_counts)", test_entropy)

# Edge case — empty track counts
def test_entropy_edge_case():
    score, label = calculate_entropy({t: 0 for t in [
        "Data Analyst", "Data Scientist", "Data Engineer", "ML Engineer",
        "Web Developer", "DevOps Cloud", "Cybersecurity", "Software Dev"
    ]})
    assert score == 0.0, "Entropy should be 0 for empty counts"
    assert label == "No Skills"
    print(f"           Edge case (zero skills): Score={score}, Label={label} ✅")

run_test("calculate_entropy() — edge case zero skills", test_entropy_edge_case)


# =============================================================
# TEST 4 — CAREER TRACK MATCH
# =============================================================
print()
print("[ STEP 5 ] Testing calculate_career_match()...")

best_track = None
best_match = None

def test_career_match():
    global best_track, best_match
    matches = calculate_career_match(priya_skills)
    assert isinstance(matches, list), "Result must be a list"
    assert len(matches) == 8, f"Expected 8 tracks, got {len(matches)}"
    for m in matches:
        assert "track" in m
        assert "match_pct" in m
        assert "matched_skills" in m
        assert "missing_skills" in m
        assert 0.0 <= m["match_pct"] <= 100.0
    best_match = matches[0]
    best_track = best_match["track"]
    print(f"           Best track: {best_track} at {best_match['match_pct']}%")
    print(f"           Matched skills: {best_match['matched_skills']}")
    print(f"           Missing (top 3): {[s['skill'] for s in best_match['missing_skills'][:3]]}")
    return matches

run_test("calculate_career_match(priya_skills)", test_career_match)


# =============================================================
# TEST 5 — READINESS SCORE
# =============================================================
print()
print("[ STEP 6 ] Testing calculate_readiness_score()...")

def test_readiness_score():
    assert best_track is not None, "best_track not set — career match test failed"
    score = calculate_readiness_score(priya_skills, best_track)
    assert isinstance(score, float), "readiness_score must be a float"
    assert 0.0 <= score <= 100.0, f"readiness_score out of range: {score}"
    print(f"           Readiness Score: {score}% for {best_track}")
    return score

run_test("calculate_readiness_score()", test_readiness_score)


# =============================================================
# TEST 6 — NEXT SKILL
# =============================================================
print()
print("[ STEP 7 ] Testing get_next_skill()...")

def test_next_skill():
    assert best_match is not None, "best_match not set — career match test failed"
    missing = best_match.get("missing_skills", [])
    result = get_next_skill(missing, best_track)
    assert isinstance(result, dict), "Result must be a dict"
    assert "skill" in result, "Missing key: skill"
    assert "frequency_pct" in result, "Missing key: frequency_pct"
    assert "reason" in result, "Missing key: reason"
    assert result["skill"] != "", "Skill name cannot be empty"
    print(f"           Next Skill: {result['skill']} ({result['frequency_pct']}% frequency)")
    print(f"           Reason: {result['reason'][:80]}...")
    return result

run_test("get_next_skill()", test_next_skill)

# Edge case — no missing skills
def test_next_skill_edge_case():
    result = get_next_skill([], "Data Analyst")
    assert result == {}, "Empty missing list should return empty dict"
    print(f"           Edge case (no missing skills): returns {{}} ✅")

run_test("get_next_skill() — edge case empty list", test_next_skill_edge_case)


# =============================================================
# TEST 7 — URGENCY ENGINE
# =============================================================
print()
print("[ STEP 8 ] Testing get_urgency_level()...")

def test_urgency_all_semesters():
    results = {}
    for sem in range(1, 9):
        result = get_urgency_level(sem)
        assert "urgency_level" in result
        assert "urgency_color" in result
        assert "urgency_message" in result
        assert "days_remaining" in result
        assert "weeks_remaining" in result
        assert result["urgency_level"] in ["Green", "Yellow", "Red"]
        results[sem] = result["urgency_level"]
    print(f"           Semester urgency map: {results}")
    print(f"           Days remaining (sem {priya_semester}): {get_urgency_level(priya_semester)['days_remaining']}")
    return results

run_test("get_urgency_level() — all 8 semesters", test_urgency_all_semesters)


# =============================================================
# TEST 8 — FOCUS DEBT
# =============================================================
print()
print("[ STEP 9 ] Testing calculate_focus_debt()...")

def test_focus_debt():
    assert best_track is not None, "best_track not set"
    result = calculate_focus_debt(priya_skills, best_track)
    assert "focus_debt_hours" in result
    assert "distraction_skills" in result
    assert "on_track_skills" in result
    assert "days_to_recover" in result
    assert result["focus_debt_hours"] >= 0
    print(f"           Focus Debt: {result['focus_debt_hours']} hours")
    print(f"           Distraction skills: {result['distraction_skills']}")
    print(f"           On-track skills: {result['on_track_skills']}")
    print(f"           Days to recover (at 2hr/day): {result['days_to_recover']}")
    return result

run_test("calculate_focus_debt()", test_focus_debt)


# =============================================================
# TEST 9 — PEER PLACEMENT RATE
# =============================================================
print()
print("[ STEP 10 ] Testing get_peer_placement_rate()...")

def test_peer_placement():
    assert drift_score is not None, "drift_score not set"
    assert best_track is not None, "best_track not set"
    result = get_peer_placement_rate(drift_score, best_track)
    assert "student_placement_rate" in result
    assert "focused_placement_rate" in result
    assert "survival_rates" in result
    assert "disclaimer" in result
    assert 0 <= result["student_placement_rate"] <= 100
    assert 0 <= result["focused_placement_rate"] <= 100
    assert len(result["survival_rates"]) == 8
    print(f"           Student est. placement rate: {result['student_placement_rate']}%")
    print(f"           Focused {best_track} rate: {result['focused_placement_rate']}%")
    print(f"           Disclaimer present: {'Yes' if result['disclaimer'] else 'No'}")
    return result

run_test("get_peer_placement_rate()", test_peer_placement)


# =============================================================
# TEST 10 — FACULTY LOGIN
# =============================================================
print()
print("[ STEP 11 ] Testing verify_faculty_login()...")

def test_faculty_login_success():
    success, name, error = verify_faculty_login("faculty1@college.edu", "Faculty@123")
    assert success is True, f"Login should succeed. Error: {error}"
    assert name == "Dr. Anita Sharma", f"Wrong name: {name}"
    assert error == ""
    print(f"           Login success: {name} ✅")

def test_faculty_login_wrong_password():
    success, name, error = verify_faculty_login("faculty1@college.edu", "wrongpassword")
    assert success is False, "Login should fail with wrong password"
    assert name == ""
    assert error != ""
    print(f"           Wrong password blocked: '{error}' ✅")

def test_faculty_login_wrong_email():
    success, name, error = verify_faculty_login("nobody@fake.com", "Faculty@123")
    assert success is False, "Login should fail with unknown email"
    assert name == ""
    print(f"           Unknown email blocked: '{error}' ✅")

run_test("verify_faculty_login() — correct credentials", test_faculty_login_success)
run_test("verify_faculty_login() — wrong password", test_faculty_login_wrong_password)
run_test("verify_faculty_login() — unknown email", test_faculty_login_wrong_email)


# =============================================================
# TEST 11 — REPORT CSV GENERATION
# =============================================================
print()
print("[ STEP 12 ] Testing generate_student_report_csv()...")

def test_report_csv():
    session_data = {
        "student_name":    "Priya Sharma",
        "semester":        4,
        "drift_score":     drift_score,
        "drift_label":     "Highly Scattered",
        "entropy_score":   entropy_score,
        "entropy_label":   "Disordered — Showing Drift",
        "best_track":      best_track or "Data Analyst",
        "match_pct":       52.0,
        "readiness_score": 22.0,
        "next_skill":      "SQL",
        "urgency_level":   "Yellow",
        "focus_debt_hours": 30,
        "verified_skills": priya_skills,
    }
    csv_string = generate_student_report_csv(session_data)
    assert isinstance(csv_string, str), "Output must be a string"
    assert len(csv_string) > 0, "CSV output is empty"
    assert "Priya Sharma" in csv_string, "Student name missing from CSV"
    assert "Python" in csv_string, "Skills missing from CSV"
    assert "verified_skills" in csv_string, "verified_skills row missing"
    print(f"           CSV generated: {len(csv_string)} characters")
    print(f"           First line: {csv_string.splitlines()[0]}")
    return csv_string

run_test("generate_student_report_csv()", test_report_csv)


# =============================================================
# FINAL SUMMARY
# =============================================================
print()
print("=" * 60)
print("  TEST SUITE COMPLETE")
print("=" * 60)
print()
print("  If all tests show ✅ PASS — brain.py is production ready.")
print("  If any test shows ❌ FAIL — paste the error here.")
print()