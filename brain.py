# brain.py — SkillDrift Core Calculation Engine
# All math, scoring, and analysis logic lives here.
# Page files only call these functions. No math in pages.

import pandas as pd
import numpy as np
from scipy.stats import entropy as scipy_entropy
import os
import csv
import io
import hashlib
from datetime import datetime
from collections import Counter

# =============================================================
# SECTION 1 — DATA LOADING
# =============================================================

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "processed")
AUTH_DIR = os.path.join(os.path.dirname(__file__), "data", "auth")


def load_required_skills() -> pd.DataFrame:
    path = os.path.join(DATA_DIR, "required_skills_per_track.csv")
    df = pd.read_csv(path)
    df["skill"] = df["skill"].str.strip()
    df["track"] = df["track"].str.strip()
    df["frequency_pct"] = pd.to_numeric(df["frequency_pct"], errors="coerce").fillna(0.0)
    return df


def load_skills_mapping() -> pd.DataFrame:
    path = os.path.join(DATA_DIR, "skills_mapping.csv")
    df = pd.read_csv(path)
    df["skill"] = df["skill"].str.strip()

    track_columns = [c for c in df.columns if c != "skill"]
    long_df = df.melt(id_vars=["skill"], value_vars=track_columns,
                      var_name="track_raw", value_name="belongs")
    long_df = long_df[long_df["belongs"] == 1].copy()

    TRACK_NAME_MAP = {
        "data_analyst":   "Data Analyst",
        "data_scientist": "Data Scientist",
        "data_engineer":  "Data Engineer",
        "ml_engineer":    "ML Engineer",
        "web_developer":  "Web Developer",
        "devops_cloud":   "DevOps Cloud",
        "cybersecurity":  "Cybersecurity",
        "software_dev":   "Software Dev",
    }
    long_df["track"] = long_df["track_raw"].map(TRACK_NAME_MAP)
    long_df = long_df[["skill", "track"]].reset_index(drop=True)
    return long_df


def load_city_job_counts() -> pd.DataFrame:
    path = os.path.join(DATA_DIR, "city_job_counts.csv")
    df = pd.read_csv(path)
    df["city"] = df["city"].str.strip()
    return df


def load_faculty_credentials() -> pd.DataFrame:
    path = os.path.join(AUTH_DIR, "faculty_credentials.csv")
    df = pd.read_csv(path)
    df["email"] = df["email"].str.strip().str.lower()
    df["hashed_password"] = df["hashed_password"].str.strip()
    df["faculty_name"] = df["faculty_name"].str.strip()
    return df


# =============================================================
# SECTION 2 — THE EIGHT CAREER TRACKS
# =============================================================

CAREER_TRACKS = [
    "Data Analyst",
    "Data Scientist",
    "Data Engineer",
    "ML Engineer",
    "Web Developer",
    "DevOps Cloud",
    "Cybersecurity",
    "Software Dev",
]

TRACK_TO_ROLE = {
    "Data Analyst":   "Data Analyst",
    "Data Scientist": "Data Scientist",
    "Data Engineer":  "Data Engineer",
    "ML Engineer":    "ML Engineer",
    "Web Developer":  "Web Developer",
    "DevOps Cloud":   "DevOps Cloud",
    "Cybersecurity":  "Cybersecurity",
    "Software Dev":   "Software Dev",
}


# =============================================================
# SECTION 3 — SKILL LEVEL WEIGHTS
# =============================================================

LEVEL_WEIGHTS = {
    "Advanced":     1.0,
    "Intermediate": 1.0,
    "Beginner":     0.5,
    "Not Verified": 0.0,
}


# =============================================================
# SECTION 4 — DRIFT SCORE
# =============================================================

def calculate_drift_score(verified_skills: dict) -> tuple:
    if len(verified_skills) < 3:
        return 0.0, "Insufficient Skills", {t: 0 for t in CAREER_TRACKS}

    skills_map_df = load_skills_mapping()
    track_counts = {track: 0 for track in CAREER_TRACKS}

    for skill in verified_skills.keys():
        matched_tracks = skills_map_df[
            skills_map_df["skill"].str.lower() == skill.lower()
        ]["track"].tolist()
        for track in matched_tracks:
            for career_track in CAREER_TRACKS:
                if track.lower().replace(" ", "") == career_track.lower().replace(" ", ""):
                    track_counts[career_track] += 1
                    break

    counts_array = np.array(list(track_counts.values()), dtype=float)
    actual_std = float(np.std(counts_array))
    n_skills = len(verified_skills)
    n_tracks = len(CAREER_TRACKS)
    max_counts = np.zeros(n_tracks)
    max_counts[0] = n_skills
    max_std = float(np.std(max_counts))
    min_std = 0.0

    if max_std == min_std:
        concentration_score = 0.0
    else:
        concentration_score = 100.0 * (actual_std - min_std) / (max_std - min_std)
        concentration_score = float(np.clip(concentration_score, 0.0, 100.0))

    drift_score = round(100.0 - concentration_score, 1)

    if drift_score <= 20:
        drift_label = "Highly Focused"
    elif drift_score <= 40:
        drift_label = "Moderately Focused"
    elif drift_score <= 60:
        drift_label = "Drifting"
    elif drift_score <= 80:
        drift_label = "Highly Scattered"
    else:
        drift_label = "Extremely Scattered"

    return drift_score, drift_label, track_counts


# =============================================================
# SECTION 5 — ENTROPY SCORE
# =============================================================

def calculate_entropy(track_counts: dict) -> tuple:
    counts = np.array(list(track_counts.values()), dtype=float)
    total = counts.sum()
    if total == 0:
        return 0.0, "No Skills"

    probs = counts / total
    entropy_score = float(scipy_entropy(probs, base=2))

    if entropy_score < 1.2:
        entropy_label = "Highly Ordered — Strong Focus"
    elif entropy_score < 2.0:
        entropy_label = "Moderately Ordered"
    elif entropy_score < 2.8:
        entropy_label = "Disordered — Showing Drift"
    else:
        entropy_label = "Highly Disordered — Strong Drift"

    return round(entropy_score, 2), entropy_label


# =============================================================
# SECTION 6 — CAREER TRACK MATCH
# =============================================================

def calculate_career_match(verified_skills: dict) -> list:
    required_df = load_required_skills()
    verified_skill_names_lower = [s.lower() for s in verified_skills.keys()]
    ranked_matches = []

    for track in CAREER_TRACKS:
        role_name = TRACK_TO_ROLE[track]
        track_skills_df = required_df[required_df["track"] == role_name].copy()

        if track_skills_df.empty:
            ranked_matches.append({
                "track": track, "match_pct": 0.0,
                "matched_skills": [], "missing_skills": [],
            })
            continue

        total_required = len(track_skills_df)
        matched_skills = []
        missing_skills = []

        for _, row in track_skills_df.iterrows():
            skill_name = row["skill"]
            freq_pct = row["frequency_pct"]
            if skill_name.lower() in verified_skill_names_lower:
                matched_skills.append(skill_name)
            else:
                missing_skills.append({"skill": skill_name, "frequency_pct": freq_pct})

        missing_skills.sort(key=lambda x: x["frequency_pct"], reverse=True)
        match_pct = (len(matched_skills) / total_required) * 100.0

        ranked_matches.append({
            "track": track, "match_pct": round(match_pct, 1),
            "matched_skills": matched_skills, "missing_skills": missing_skills,
        })

    ranked_matches.sort(key=lambda x: x["match_pct"], reverse=True)
    return ranked_matches


# =============================================================
# SECTION 7 — READINESS SCORE
# =============================================================

def calculate_readiness_score(verified_skills: dict, best_track: str) -> float:
    required_df = load_required_skills()
    role_name = TRACK_TO_ROLE.get(best_track, best_track)
    track_skills_df = required_df[required_df["track"] == role_name].copy()

    if track_skills_df.empty:
        return 0.0

    verified_lower = {k.lower(): v for k, v in verified_skills.items()}
    total_weight = 0.0
    earned_weight = 0.0

    for _, row in track_skills_df.iterrows():
        skill_name = row["skill"]
        freq_pct = row["frequency_pct"]
        total_weight += freq_pct
        level = verified_lower.get(skill_name.lower(), None)
        skill_weight = LEVEL_WEIGHTS.get(level, 0.0)
        earned_weight += freq_pct * skill_weight

    if total_weight == 0:
        return 0.0
    readiness_score = (earned_weight / total_weight) * 100.0
    return round(float(np.clip(readiness_score, 0.0, 100.0)), 1)


# =============================================================
# SECTION 8 — NEXT SKILL RECOMMENDATION
# =============================================================

FOUNDATIONAL_ORDER = [
    "SQL", "Python", "Excel", "Statistics", "Java",
    "HTML", "CSS", "JavaScript", "Linux", "Git",
    "Pandas", "NumPy", "Machine Learning", "Docker", "Kubernetes",
]


def get_next_skill(missing_skills: list, best_track: str) -> dict:
    if not missing_skills:
        return {}

    max_freq = missing_skills[0]["frequency_pct"]
    top_skills = [s for s in missing_skills if s["frequency_pct"] == max_freq]

    if len(top_skills) == 1:
        chosen = top_skills[0]
    else:
        for foundational in FOUNDATIONAL_ORDER:
            for candidate in top_skills:
                if candidate["skill"].lower() == foundational.lower():
                    chosen = candidate
                    break
            else:
                continue
            break
        else:
            chosen = top_skills[0]

    reason = (
        f"{chosen['skill']} appears in {chosen['frequency_pct']:.1f}% of "
        f"{best_track} job postings in the Indian job market dataset. "
        f"It is the single highest-impact skill you can add right now."
    )
    return {"skill": chosen["skill"], "frequency_pct": chosen["frequency_pct"], "reason": reason}


# =============================================================
# SECTION 9 — URGENCY ENGINE
# =============================================================

def get_urgency_level(semester: int) -> dict:
    today = datetime.now()
    current_year = today.year

    if today.month < 7:
        sem7_start = datetime(current_year, 7, 1)
    else:
        sem7_start = datetime(current_year + 1, 7, 1)

    if semester >= 7:
        delta_days = (today - sem7_start).days
        days_remaining = 0 if delta_days >= 0 else abs(delta_days)
    else:
        days_remaining = max(0, (sem7_start - today).days)

    weeks_remaining = days_remaining // 7

    if semester <= 2:
        urgency_level = "Green"
        urgency_color = "#2ECC71"
        urgency_message = (
            "You have enough time to build deep skills from scratch. "
            "Pick one career track and go deep — do not spread across multiple fields."
        )
    elif semester <= 4:
        urgency_level = "Yellow"
        urgency_color = "#F39C12"
        urgency_message = (
            "Time is limited. Any further drift is dangerous. "
            "You should be narrowing your focus to one track right now."
        )
    else:
        urgency_level = "Red"
        urgency_color = "#E74C3C"
        if semester == 8:
            urgency_message = (
                "Placement season is currently active or has already passed. "
                "Every day without focused preparation reduces placement probability."
            )
        else:
            urgency_message = (
                "Placement season is imminent. Focus on one track immediately. "
                "Stop learning new technologies and go deep on your best matching track."
            )

    return {
        "urgency_level": urgency_level,
        "urgency_color": urgency_color,
        "urgency_message": urgency_message,
        "days_remaining": days_remaining,
        "weeks_remaining": weeks_remaining,
    }


# =============================================================
# SECTION 10 — FOCUS DEBT
# =============================================================

HOURS_PER_DISTRACTION_SKILL = 30


def calculate_focus_debt(verified_skills: dict, best_track: str) -> dict:
    required_df = load_required_skills()
    role_name = TRACK_TO_ROLE.get(best_track, best_track)
    track_skills_df = required_df[required_df["track"] == role_name]
    required_skill_names_lower = [s.lower() for s in track_skills_df["skill"].tolist()]

    distraction_skills = []
    on_track_skills = []

    for skill in verified_skills.keys():
        if skill.lower() in required_skill_names_lower:
            on_track_skills.append(skill)
        else:
            distraction_skills.append(skill)

    focus_debt_hours = len(distraction_skills) * HOURS_PER_DISTRACTION_SKILL
    daily_hours = 2
    days_to_recover = focus_debt_hours // daily_hours if daily_hours > 0 else 0

    return {
        "focus_debt_hours": focus_debt_hours,
        "distraction_skills": distraction_skills,
        "on_track_skills": on_track_skills,
        "daily_hours": daily_hours,
        "days_to_recover": days_to_recover,
    }


# =============================================================
# SECTION 11 — PEER PLACEMENT RATE
# =============================================================

DRIFT_TO_PLACEMENT_RATE = [
    ( 0,  20, 78),
    (20,  40, 62),
    (40,  60, 44),
    (60,  80, 29),
    (80, 100, 18),
]

FOCUSED_PLACEMENT_RATES = {
    "Data Analyst": 77, "Data Scientist": 71, "Data Engineer": 68,
    "ML Engineer": 65, "Web Developer": 74, "DevOps Cloud": 72,
    "Cybersecurity": 69, "Software Dev": 76,
}

TRACK_SURVIVAL_RATES = {
    "Data Analyst": 72, "Data Scientist": 51, "Data Engineer": 58,
    "ML Engineer": 47, "Web Developer": 75, "DevOps Cloud": 63,
    "Cybersecurity": 60, "Software Dev": 70,
}


def get_peer_placement_rate(drift_score: float, best_track: str) -> dict:
    student_rate = 18
    for min_d, max_d, rate in DRIFT_TO_PLACEMENT_RATE:
        if min_d <= drift_score <= max_d:
            student_rate = rate
            break

    focused_rate = FOCUSED_PLACEMENT_RATES.get(best_track, 70)
    disclaimer = (
        "These placement rates are estimates based on NASSCOM annual reports "
        "and AICTE published outcome data."
    )
    return {
        "student_placement_rate": student_rate,
        "focused_placement_rate": focused_rate,
        "survival_rates": TRACK_SURVIVAL_RATES,
        "disclaimer": disclaimer,
    }


# =============================================================
# SECTION 12 — SKILL STRING PARSING
# =============================================================

def parse_skills_string(skills_str: str) -> dict:
    if not isinstance(skills_str, str) or skills_str.strip() == "":
        return {}
    skills_dict = {}
    pairs = skills_str.split(",")
    for pair in pairs:
        pair = pair.strip()
        if ":" in pair:
            parts = pair.split(":", 1)
            skill = parts[0].strip()
            level = parts[1].strip()
            if skill and level:
                skills_dict[skill] = level
    return skills_dict


# =============================================================
# SECTION 13 — FULL STUDENT ANALYSIS (single student dict)
# NEW: Used by faculty to compute everything for one student
# and return it in a shape that mirrors the student session_state.
# =============================================================

def compute_full_student_analysis(student_name: str, semester: int, verified_skills: dict) -> dict:
    """
    Runs all 8 calculations for one student and returns a dict
    that mirrors the keys used in student session_state.
    Safe to call in a loop for batch processing.
    """
    drift_score, drift_label, track_counts = calculate_drift_score(verified_skills)
    entropy_score, entropy_label = calculate_entropy(track_counts)
    career_matches = calculate_career_match(verified_skills)
    best_match = career_matches[0] if career_matches else {}
    best_track = best_match.get("track", "Unknown")
    match_pct = best_match.get("match_pct", 0.0)
    readiness_score = calculate_readiness_score(verified_skills, best_track)
    urgency_info = get_urgency_level(semester)
    focus_debt_info = calculate_focus_debt(verified_skills, best_track)
    next_skill_info = get_next_skill(best_match.get("missing_skills", []), best_track)
    peer_info = get_peer_placement_rate(drift_score, best_track)

    return {
        # identity
        "student_name":    student_name,
        "semester":        semester,
        "verified_skills": verified_skills,
        # drift & entropy
        "drift_score":     drift_score,
        "drift_label":     drift_label,
        "track_counts":    track_counts,
        "entropy_score":   entropy_score,
        "entropy_label":   entropy_label,
        # career match
        "career_matches":  career_matches,
        "best_track":      best_track,
        "match_pct":       match_pct,
        # readiness
        "readiness_score": readiness_score,
        # next skill
        "next_skill_info": next_skill_info,
        # urgency
        "urgency_info":    urgency_info,
        # focus debt
        "focus_debt_info": focus_debt_info,
        # peer
        "peer_info":       peer_info,
        # flat copies for table display
        "urgency_level":   urgency_info["urgency_level"],
        "focus_debt_hours": focus_debt_info["focus_debt_hours"],
        "next_skill":      next_skill_info.get("skill", ""),
        "skill_count":     len(verified_skills),
    }


# =============================================================
# SECTION 14 — BATCH PROCESSING (faculty upload)
# =============================================================

def parse_skilldrift_report_csv(file_obj) -> dict | None:
    """
    Parses a SkillDrift student report CSV.

    The report format is a multi-section key-value file (not a flat table):
        SkillDrift Report, Generated by SkillDrift Platform
        student_name, Anurag
        semester, 8
        ...
        verified_skills, "Python:Beginner,SQL:Beginner"

    Reads every row as key→value and extracts the three fields needed.
    Also handles plain flat CSVs that have student_name/semester/verified_skills
    as column headers (for backwards compatibility).

    Returns dict with student_name, semester, verified_skills  OR  None on failure.
    """
    try:
        # Reset file pointer in case it was read before
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)
        df = pd.read_csv(file_obj, header=None, dtype=str)
    except Exception:
        return None

    if df.empty:
        return None

    # ── Try multi-section key-value format (SkillDrift report) ──────────────
    kv = {}
    for _, row in df.iterrows():
        key = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
        val = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ""
        if key and key not in ("nan",) and val not in ("nan", ""):
            kv[key] = val

    student_name    = kv.get("student_name", "").strip()
    semester_str    = kv.get("semester", "").strip()
    verified_str    = kv.get("verified_skills", "").strip()

    if student_name and verified_str:
        try:
            semester = int(float(semester_str)) if semester_str else 4
            if semester < 1 or semester > 8:
                semester = 4
        except (ValueError, TypeError):
            semester = 4
        return {
            "student_name":    student_name,
            "semester":        semester,
            "verified_skills": verified_str,
        }

    # ── Fallback: try flat table format ──────────────────────────────────────
    if hasattr(file_obj, "seek"):
        file_obj.seek(0)
    try:
        flat_df = pd.read_csv(file_obj, dtype=str)
        flat_df.columns = [c.strip().lower() for c in flat_df.columns]
        if {"student_name", "semester", "verified_skills"}.issubset(flat_df.columns):
            row = flat_df.iloc[0]
            sname = str(row.get("student_name", "")).strip()
            vstr  = str(row.get("verified_skills", "")).strip()
            if sname and vstr:
                try:
                    sem = int(float(str(row.get("semester", "4"))))
                    if sem < 1 or sem > 8:
                        sem = 4
                except (ValueError, TypeError):
                    sem = 4
                return {"student_name": sname, "semester": sem, "verified_skills": vstr}
    except Exception:
        pass

    return None


def validate_and_process_batch(uploaded_files: list) -> dict:
    all_rows = []
    all_student_analyses = []
    skipped_files = []
    seen_names = set()
    duplicate_count = 0
    valid_count = 0

    files_to_process = uploaded_files[:100]
    if len(uploaded_files) > 100:
        skipped_files.append(f"WARNING: Only first 100 of {len(uploaded_files)} files processed.")

    for uploaded_file in files_to_process:
        fname = getattr(uploaded_file, "name", str(uploaded_file))

        parsed = parse_skilldrift_report_csv(uploaded_file)

        if parsed is None:
            skipped_files.append(
                f"{fname}: Could not extract student_name / semester / verified_skills. "
                f"Make sure this is a SkillDrift report CSV downloaded from the Final Report page."
            )
            continue

        student_name    = parsed["student_name"]
        semester        = parsed["semester"]
        verified_str    = parsed["verified_skills"]
        verified_skills = parse_skills_string(verified_str)

        if not verified_skills:
            skipped_files.append(f"{fname}: verified_skills field is empty or unreadable.")
            continue

        if student_name.lower() in seen_names:
            duplicate_count += 1
            continue
        seen_names.add(student_name.lower())

        valid_count += 1

        analysis = compute_full_student_analysis(student_name, semester, verified_skills)
        all_student_analyses.append(analysis)

        all_rows.append({
            "student_name":     student_name,
            "semester":         semester,
            "verified_skills":  verified_str,
            "skill_count":      analysis["skill_count"],
            "drift_score":      analysis["drift_score"],
            "drift_label":      analysis["drift_label"],
            "entropy_score":    analysis["entropy_score"],
            "best_track":       analysis["best_track"],
            "match_pct":        analysis["match_pct"],
            "readiness_score":  analysis["readiness_score"],
            "urgency_level":    analysis["urgency_level"],
            "focus_debt_hours": analysis["focus_debt_hours"],
            "next_skill":       analysis["next_skill"],
        })

    merged_df = pd.DataFrame(all_rows)
    summary = {}

    if not merged_df.empty:
        summary["total_students"]      = len(merged_df)
        summary["avg_drift_score"]     = round(merged_df["drift_score"].mean(), 1)
        summary["avg_readiness_score"] = round(merged_df["readiness_score"].mean(), 1)
        summary["avg_entropy_score"]   = round(merged_df["entropy_score"].mean(), 2)
        summary["red_count"]           = int((merged_df["urgency_level"] == "Red").sum())
        summary["yellow_count"]        = int((merged_df["urgency_level"] == "Yellow").sum())
        summary["green_count"]         = int((merged_df["urgency_level"] == "Green").sum())

        all_missing = []
        for analysis in all_student_analyses:
            if analysis["career_matches"]:
                for ms in analysis["career_matches"][0].get("missing_skills", [])[:5]:
                    all_missing.append(ms["skill"])

        summary["top_missing_skills"] = Counter(all_missing).most_common(5) if all_missing else []
        summary["track_distribution"] = merged_df["best_track"].value_counts().to_dict()

    return {
        "merged_df":              merged_df,
        "all_student_analyses":   all_student_analyses,   # NEW: list of full analysis dicts
        "valid_count":            valid_count,
        "skipped_files":          skipped_files,
        "duplicate_count":        duplicate_count,
        "summary":                summary,
    }


# =============================================================
# SECTION 15 — FACULTY AUTHENTICATION
# =============================================================

def verify_faculty_login(email: str, password: str) -> tuple:
    try:
        credentials_df = load_faculty_credentials()
    except FileNotFoundError:
        return False, "", "Faculty credentials file not found. Contact administrator."

    email_clean = email.strip().lower()
    hashed_input = hashlib.sha256(password.encode()).hexdigest()
    match = credentials_df[credentials_df["email"] == email_clean]

    if match.empty:
        return False, "", "No account found with this email address."

    stored_hash = match.iloc[0]["hashed_password"]
    faculty_name = match.iloc[0]["faculty_name"]

    if hashed_input == stored_hash:
        return True, faculty_name, ""
    else:
        return False, "", "Incorrect password. Please try again."


# =============================================================
# SECTION 16 — REPORT CSV GENERATION
# =============================================================

def generate_student_report_csv(session_data: dict) -> str:
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["SkillDrift Report", "Generated by SkillDrift Platform"])
    writer.writerow(["Generated On", datetime.now().strftime("%Y-%m-%d %H:%M")])
    writer.writerow([])
    writer.writerow(["STUDENT INFORMATION"])
    writer.writerow(["student_name", session_data.get("student_name", "")])
    writer.writerow(["semester",     session_data.get("semester", "")])
    writer.writerow([])
    writer.writerow(["SKILL ANALYSIS"])
    writer.writerow(["drift_score",   session_data.get("drift_score", "")])
    writer.writerow(["drift_label",   session_data.get("drift_label", "")])
    writer.writerow(["entropy_score", session_data.get("entropy_score", "")])
    writer.writerow(["entropy_label", session_data.get("entropy_label", "")])
    writer.writerow([])
    writer.writerow(["CAREER MATCH"])
    writer.writerow(["best_track",      session_data.get("best_track", "")])
    writer.writerow(["match_pct",       session_data.get("match_pct", "")])
    writer.writerow(["readiness_score", session_data.get("readiness_score", "")])
    writer.writerow([])
    writer.writerow(["ACTION PLAN"])
    writer.writerow(["next_skill",       session_data.get("next_skill", "")])
    writer.writerow(["urgency_level",    session_data.get("urgency_level", "")])
    writer.writerow(["focus_debt_hours", session_data.get("focus_debt_hours", "")])
    writer.writerow([])
    writer.writerow(["VERIFIED SKILLS"])
    writer.writerow(["skill", "verified_level"])

    verified_skills = session_data.get("verified_skills", {})
    for skill, level in verified_skills.items():
        writer.writerow([skill, level])

    writer.writerow([])
    skills_str = ",".join([f"{s}:{l}" for s, l in verified_skills.items()])
    writer.writerow(["verified_skills", skills_str])

    return output.getvalue()