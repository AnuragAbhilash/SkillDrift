# pages/02_skill_input.py

import streamlit as st
from datetime import datetime
from brain import (
    calculate_drift_score, calculate_entropy, calculate_career_match,
    calculate_readiness_score, get_next_skill, get_urgency_level,
    calculate_focus_debt, get_peer_placement_rate,
)
from gemini_quiz import run_skill_verification_quiz

st.set_page_config(
    page_title="SkillDrift — Skill Input",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    [data-testid="stSidebarNav"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    header[data-testid="stHeader"] { display: none !important; }
    .stDeployButton { display: none !important; }
    #MainMenu { display: none !important; }
    footer { display: none !important; }

    .stApp { background-color: #F5F5F7; }
    .block-container { padding-top: 1.75rem; padding-bottom: 3rem; max-width: 1000px; }

    h1 { font-size: 1.6rem !important; font-weight: 700 !important; color: #1D1D1F !important; }
    h2 { font-size: 1.2rem !important; font-weight: 600 !important; color: #1D1D1F !important; }
    h3 { font-size: 1rem !important; font-weight: 600 !important; color: #1D1D1F !important; }

    .stButton > button {
        border-radius: 8px;
        border: 1px solid #D2D2D7;
        background: #F5F5F7;
        color: #1D1D1F;
        font-weight: 500;
        font-size: 0.875rem;
        transition: all 0.12s ease;
    }
    .stButton > button:hover { background: #E8E8ED; }
    .stButton > button[kind="primary"] {
        background: #6C63FF;
        color: #FFFFFF;
        border-color: #6C63FF;
        font-weight: 600;
    }
    .stButton > button[kind="primary"]:hover { background: #5A52E0; }

    .stCheckbox label { color: #1D1D1F !important; font-size: 0.88rem !important; }
    .stRadio label { color: #1D1D1F !important; font-size: 0.85rem !important; }
    .stSelectbox label { color: #1D1D1F !important; font-size: 0.875rem !important; font-weight: 500 !important; }
    .stTextInput label { color: #1D1D1F !important; font-size: 0.875rem !important; font-weight: 500 !important; }
    .stTextInput input { font-size: 0.95rem !important; }

    div[data-baseweb="tab"] { color: #86868B; font-size: 0.875rem; }
    div[data-baseweb="tab"][aria-selected="true"] { color: #1D1D1F; font-weight: 600; }
    .stProgress > div > div { background-color: #6C63FF; }

    .section-box {
        background: #FFFFFF;
        border: 1px solid #D2D2D7;
        border-radius: 14px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
    }
    .section-tag {
        font-size: 0.68rem;
        font-weight: 600;
        color: #6C63FF;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

if st.button("Back to Home", key="back_home"):
    st.switch_page("pages/01_home.py")

st.markdown("""
<div style="margin-bottom:1.25rem;">
    <div style="font-size:1.6rem; font-weight:700; color:#1D1D1F;">Analyze My Career Focus</div>
    <div style="font-size:0.9rem; color:#86868B; margin-top:0.2rem;">
        Fill in your details, select your skills, and take a short quiz to verify what you know.
    </div>
</div>
""", unsafe_allow_html=True)

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
        "AR/VR", "AI", "Risk Management", "MDR",
    ],
}

LEVELS = ["Beginner", "Intermediate", "Advanced"]

# ── Part 1 — Name + Semester (compact, side by side) ──────────
st.markdown('<div class="section-tag">Step 1 — Your Details</div>', unsafe_allow_html=True)

col_name, col_sem = st.columns([3, 1], gap="medium")
with col_name:
    name_input = st.text_input(
        "Full Name",
        value=st.session_state.get("student_name", "") or "",
        placeholder="e.g. Priya Sharma",
        max_chars=80,
    )
with col_sem:
    semester = st.selectbox(
        "Semester",
        options=list(range(1, 9)),
        index=(st.session_state.get("semester", 4) or 4) - 1,
        format_func=lambda x: f"Sem {x}",
    )

st.markdown("<div style='height:0.75rem;'></div>", unsafe_allow_html=True)

# ── Part 2 — Skills ───────────────────────────────────────────
st.markdown('<div class="section-tag">Step 2 — Select Your Skills</div>', unsafe_allow_html=True)
st.markdown(
    "<div style='font-size:0.85rem; color:#86868B; margin-bottom:0.75rem;'>"
    "Select every technology you have studied. Rate your level honestly — "
    "the quiz in the next step will verify your claims."
    "</div>",
    unsafe_allow_html=True,
)

selected_skills = {}
tabs = st.tabs(list(ALL_SKILLS.keys()))

for tab, (category, skills) in zip(tabs, ALL_SKILLS.items()):
    with tab:
        st.markdown(
            f"<div style='font-size:0.8rem; color:#86868B; margin-bottom:0.5rem;'>"
            f"Select all that apply</div>",
            unsafe_allow_html=True,
        )
        cols = st.columns(2)
        for i, skill in enumerate(skills):
            with cols[i % 2]:
                already_selected = skill in st.session_state.get("selected_skills", {})
                checked = st.checkbox(skill, value=already_selected, key=f"skill_check_{skill}")
                if checked:
                    prev_level = st.session_state.get("selected_skills", {}).get(skill, "Beginner")
                    level_idx  = LEVELS.index(prev_level) if prev_level in LEVELS else 0
                    level = st.radio(
                        f"Level for {skill}",
                        options=LEVELS,
                        index=level_idx,
                        key=f"level_{skill}",
                        horizontal=True,
                        label_visibility="collapsed",
                    )
                    selected_skills[skill] = level

# ── Submit ────────────────────────────────────────────────────
st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
col_submit, col_info = st.columns([2, 3])

with col_submit:
    submit_skills = st.button(
        "Continue to Skill Verification Quiz",
        type="primary",
        use_container_width=True,
    )

with col_info:
    if selected_skills:
        skill_count = len(selected_skills)
        color = "#FF3B30" if skill_count > 40 else "#34C759"
        st.markdown(
            f"<div style='padding-top:0.5rem;'>"
            f"<span style='color:{color}; font-weight:600; font-size:0.9rem;'>"
            f"{skill_count} skills selected</span></div>",
            unsafe_allow_html=True,
        )
        if skill_count > 40:
            st.warning(f"{skill_count} skills selected — this may indicate skill drift. You can still continue.")

if submit_skills:
    name_clean = name_input.strip()
    if not name_clean:
        st.error("Please enter your name to continue.")
        st.stop()
    if len(selected_skills) < 3:
        st.error("Please select at least 3 skills to continue.")
        st.stop()

    st.session_state["student_name"]    = name_clean
    st.session_state["semester"]        = semester
    st.session_state["selected_skills"] = selected_skills
    st.session_state["session_start"]   = datetime.now().isoformat()
    st.session_state["quiz_complete"]   = False
    st.session_state["verified_skills"] = {}

    st.success(f"Hello {name_clean}. {len(selected_skills)} skills selected. Starting quiz...")
    st.rerun()

# ── Part 3 — Quiz ─────────────────────────────────────────────
if (
    st.session_state.get("student_name")
    and st.session_state.get("selected_skills")
    and not st.session_state.get("quiz_complete")
):
    st.markdown("<hr style='border:none; border-top:1px solid #D2D2D7; margin:1.5rem 0;'>",
                unsafe_allow_html=True)
    st.markdown(
        f"<div style='font-size:1rem; font-weight:600; color:#1D1D1F; margin-bottom:0.25rem;'>"
        f"Welcome, {st.session_state['student_name']}</div>"
        f"<div style='font-size:0.85rem; color:#86868B;'>"
        f"{len(st.session_state['selected_skills'])} skills selected — "
        f"now let us verify what you actually know.</div>",
        unsafe_allow_html=True,
    )

    verified = run_skill_verification_quiz(st.session_state["selected_skills"])

    if verified:
        st.session_state["verified_skills"] = verified
        st.session_state["quiz_complete"]   = True

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

        st.success("Analysis complete. Redirecting to your dashboard...")
        st.switch_page("pages/03_drift_score.py")

elif st.session_state.get("quiz_complete"):
    st.markdown("<hr style='border:none; border-top:1px solid #D2D2D7; margin:1.5rem 0;'>",
                unsafe_allow_html=True)
    st.success(f"Quiz already completed, {st.session_state['student_name']}. Navigate using the sidebar.")

    quiz_results = st.session_state.get("quiz_results", [])
    if quiz_results:
        st.subheader("Your Verified Skill Levels")
        import pandas as pd
        rows = []
        for r in quiz_results:
            rows.append({
                "Skill":          r["skill"],
                "Claimed Level":  r["claimed_level"],
                "Verified Level": r["verified_level"],
                "Status":         r["status"],
                "Score":          f"{r['correct_count']}/{r['total_questions']}"
                                  if r["total_questions"] > 0 else "N/A",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    if st.button("Go to Dashboard", type="primary"):
        st.switch_page("pages/03_drift_score.py")
