# Window 2 - Skill Input 
# =============================================================
# pages/02_skill_input.py — Window 2: Name + Skills + Quiz
# Three parts: Name collection → Skill selection → Gemini quiz
# =============================================================

import streamlit as st
from datetime import datetime
from brain import (
    calculate_drift_score,
    calculate_entropy,
    calculate_career_match,
    calculate_readiness_score,
    get_next_skill,
    get_urgency_level,
    calculate_focus_debt,
    get_peer_placement_rate,
)
from gemini_quiz import run_skill_verification_quiz

st.set_page_config(
    page_title="SkillDrift — Skill Input",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide default sidebar nav
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)

# Back to home button
if st.button("← Back to Home"):
    st.switch_page("pages/01_home.py")

st.title("🎯 Analyze My Career Focus")
st.markdown("---")

# =============================================================
# PART A — NAME COLLECTION
# =============================================================

# All skills organized into 6 tabs
ALL_SKILLS = {
    "Programming Languages": [
        "Python", "Java", "C", "C++", "JavaScript", "TypeScript",
        "R", "Go", "Rust", "Scala", "Kotlin", "Swift", "MATLAB",
        "Bash", "Shell Scripting", "PHP", "Ruby", "Dart", "Julia",
        "Perl", "Groovy", "Assembly", "Haskell", "Elixir",
    ],
    "Databases": [
        "SQL", "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Oracle DB",
        "Microsoft SQL Server", "Redis", "Cassandra", "DynamoDB",
        "Elasticsearch", "Neo4j", "Firebase", "InfluxDB", "MariaDB",
        "CockroachDB", "Snowflake", "BigQuery", "Redshift", "Hive",
        "HBase", "Teradata", "Db2", "Supabase",
    ],
    "Frameworks & Libraries": [
        "React", "Angular", "Vue.js", "Node.js", "Express.js",
        "Django", "Flask", "FastAPI", "Spring Boot", "Laravel",
        "Next.js", "Nuxt.js", "Bootstrap", "Tailwind CSS",
        "TensorFlow", "PyTorch", "Keras", "Scikit-learn",
        "Pandas", "NumPy", "Matplotlib", "Seaborn", "Plotly",
        "OpenCV", "NLTK", "SpaCy", "Hugging Face", "LangChain",
        "AJAX", ".Net", "jQuery",
    ],
    "Data Tools": [
        "Power BI", "Tableau", "Excel", "Google Sheets",
        "Apache Spark", "Apache Kafka", "Apache Airflow",
        "dbt", "Looker", "Metabase", "KNIME", "RapidMiner",
        "Jupyter Notebook", "Google Colab", "Apache Hadoop",
        "Databricks", "Alteryx", "SAS", "SPSS", "Qlik",
        "Data Analysis", "Data Management", "ETL", "Data Warehousing",
    ],
    "Cloud Platforms": [
        "AWS", "Azure", "GCP", "Heroku", "DigitalOcean",
        "Docker", "Kubernetes", "Terraform", "Ansible", "Jenkins",
        "GitHub Actions", "CircleCI", "Linux", "Nginx", "Apache",
        "Cloudflare", "Vercel", "Netlify", "Pulumi", "Helm",
    ],
    "Web & Other Technologies": [
        "HTML", "CSS", "REST API", "GraphQL", "WebSockets",
        "Git", "GitHub", "Postman", "Swagger", "gRPC",
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
        "Reinforcement Learning", "Statistics", "Probability",
        "Data Structures", "Algorithms", "System Design",
        "Cybersecurity", "Ethical Hacking", "SIEM", "SOC",
        "Penetration Testing", "Backend", "Frontend", "Full Stack",
        "Microservices", "DevOps", "MLOps", "Blockchain", "IoT",
        "AR/VR", "Ai", "Risk Management", "MDR",
    ],
}

LEVELS = ["Beginner", "Intermediate", "Advanced"]

# ── PART A: Name Input ────────────────────────────────────────
st.subheader("Part 1 — Tell Us Your Name")
st.markdown("*Your name will appear on your dashboard and your downloadable report.*")

name_input = st.text_input(
    "Your Full Name",
    value=st.session_state.get("student_name", "") or "",
    placeholder="e.g. Priya Sharma",
    max_chars=80,
)

# ── PART B: Skill Input Form ──────────────────────────────────
st.markdown("---")
st.subheader("Part 2 — Select Your Skills and Self-Rate Your Level")
st.markdown(
    "Select every technology you have studied. Rate your level **honestly**. "
    "The quiz in the next step will verify your claims."
)

# Semester selector
semester = st.selectbox(
    "Your Current Semester",
    options=list(range(1, 9)),
    index=(st.session_state.get("semester", 4) or 4) - 1,
    format_func=lambda x: f"Semester {x}",
)

st.markdown("#### Select Your Skills")
st.markdown("*Use the tabs below. Select a skill, then choose your level.*")

selected_skills = {}

tabs = st.tabs(list(ALL_SKILLS.keys()))

for tab, (category, skills) in zip(tabs, ALL_SKILLS.items()):
    with tab:
        st.markdown(f"**{category}** — select all that apply")
        cols = st.columns(2)
        for i, skill in enumerate(skills):
            with cols[i % 2]:
                already_selected = skill in st.session_state.get("selected_skills", {})
                checked = st.checkbox(
                    skill,
                    value=already_selected,
                    key=f"skill_check_{skill}",
                )
                if checked:
                    prev_level = st.session_state.get(
                        "selected_skills", {}
                    ).get(skill, "Beginner")
                    level_idx = LEVELS.index(prev_level) if prev_level in LEVELS else 0
                    level = st.radio(
                        f"Level for {skill}",
                        options=LEVELS,
                        index=level_idx,
                        key=f"level_{skill}",
                        horizontal=True,
                        label_visibility="collapsed",
                    )
                    selected_skills[skill] = level

# ── Validation ────────────────────────────────────────────────
st.markdown("---")

col_submit, col_info = st.columns([2, 3])

with col_submit:
    submit_skills = st.button(
        "▶ Continue to Skill Verification Quiz",
        type="primary",
        use_container_width=True,
    )

with col_info:
    if selected_skills:
        skill_count = len(selected_skills)
        color = "#E74C3C" if skill_count > 40 else "#2ECC71"
        st.markdown(
            f"<span style='color:{color}; font-weight:700;'>"
            f"{skill_count} skills selected</span>",
            unsafe_allow_html=True,
        )
        if skill_count > 40:
            st.warning(
                f"⚠️ You have selected {skill_count} skills. "
                "This may indicate skill drift. You can still continue."
            )

if submit_skills:
    # Validate name
    name_clean = name_input.strip()
    if not name_clean:
        st.error("❌ Please enter your name to continue.")
        st.stop()

    # Validate skill count
    if len(selected_skills) < 3:
        st.error("❌ Please select at least 3 skills to continue.")
        st.stop()

    # Save name and semester to session state
    st.session_state["student_name"]    = name_clean
    st.session_state["semester"]        = semester
    st.session_state["selected_skills"] = selected_skills
    st.session_state["session_start"]   = datetime.now().isoformat()
    st.session_state["quiz_complete"]   = False
    st.session_state["verified_skills"] = {}

    st.success(
        f"✅ Hello {name_clean}! You selected {len(selected_skills)} skills. "
        "Starting verification quiz..."
    )
    st.rerun()

# =============================================================
# PART C — GEMINI QUIZ (only shows after skills submitted)
# =============================================================

if (
    st.session_state.get("student_name")
    and st.session_state.get("selected_skills")
    and not st.session_state.get("quiz_complete")
):
    st.markdown("---")
    st.markdown(
        f"### Welcome, {st.session_state['student_name']}! 👋\n"
        f"You selected **{len(st.session_state['selected_skills'])} skills**. "
        f"Now let's verify what you actually know."
    )

    verified = run_skill_verification_quiz(st.session_state["selected_skills"])

    if verified:
        st.session_state["verified_skills"] = verified
        st.session_state["quiz_complete"]   = True

        # Run all calculations immediately and cache in session_state
        with st.spinner("Running full career analysis..."):
            drift_score, drift_label, track_counts = calculate_drift_score(verified)
            entropy_score, entropy_label = calculate_entropy(track_counts)
            career_matches = calculate_career_match(verified)
            best_match = career_matches[0] if career_matches else {}
            best_track = best_match.get("track", "Unknown")
            match_pct  = best_match.get("match_pct", 0.0)
            readiness  = calculate_readiness_score(verified, best_track)
            next_skill = get_next_skill(best_match.get("missing_skills", []), best_track)
            urgency    = get_urgency_level(st.session_state["semester"])
            debt       = calculate_focus_debt(verified, best_track)
            peer       = get_peer_placement_rate(drift_score, best_track)

            # Store everything in session_state
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

        st.success("✅ Analysis complete! Redirecting to your dashboard...")
        st.balloons()
        st.switch_page("pages/03_drift_score.py")

# Show quiz results table if quiz is already complete
elif st.session_state.get("quiz_complete"):
    st.markdown("---")
    st.success(
        f"✅ Quiz already completed, {st.session_state['student_name']}. "
        "Navigate using the sidebar."
    )

    quiz_results = st.session_state.get("quiz_results", [])
    if quiz_results:
        st.subheader("Your Verified Skill Levels")
        import pandas as pd

        rows = []
        for r in quiz_results:
            status_icon = {"Confirmed": "✅", "Downgraded": "⚠️",
                           "Not Verified": "❌", "Unverified": "🔶"}.get(r["status"], "")
            rows.append({
                "Skill": r["skill"],
                "Claimed Level": r["claimed_level"],
                "Verified Level": r["verified_level"],
                "Status": f"{status_icon} {r['status']}",
                "Score": f"{r['correct_count']}/{r['total_questions']}" if r["total_questions"] > 0 else "N/A",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    if st.button("🎯 Go to Dashboard", type="primary"):
        st.switch_page("pages/03_drift_score.py")