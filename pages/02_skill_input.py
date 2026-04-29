# pages/02_skill_input.py

import streamlit as st
from datetime import datetime
from gemini_quiz import reset_quiz_state
from session_store import init_session, save_session

st.set_page_config(
    page_title="SkillDrift - Skill Input",
    page_icon="assets/logo.png",
    layout="centered",
    initial_sidebar_state="collapsed",
)

init_session()

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800;900&family=Inter:wght@400;500;600;700&display=swap');

    [data-testid="stSidebarNav"]            { display: none !important; }
    [data-testid="collapsedControl"]        { display: none !important; }
    [data-testid="stExpandSidebar"]         { display: none !important; }
    [data-testid="stSidebarCollapseButton"] { display: none !important; }
    section[data-testid="stSidebar"]        { display: none !important; }
    header[data-testid="stHeader"]          { display: none !important; }
    .stDeployButton  { display: none !important; }
    #MainMenu        { display: none !important; }
    footer           { display: none !important; }

    :root {
        --blue:    #002c98;
        --blue-lt: #eef2ff;
        --text:    #171c1f;
        --muted:   #515f74;
        --border:  #e2e8f0;
        --surface: #f6fafe;
        --card:    #ffffff;
    }

    html, body, .stApp { background-color: var(--surface) !important; font-family: 'Inter', sans-serif; }

    .block-container {
        padding-top:    0         !important;
        padding-bottom: 3rem      !important;
        max-width:      900px     !important;
        margin-left:    auto      !important;
        margin-right:   auto      !important;
        padding-left:   2rem      !important;
        padding-right:  2rem      !important;
    }

    /* Top bar */
    .p2-topbar {
        display:         flex;
        justify-content: space-between;
        align-items:     center;
        padding:         18px 0;
        border-bottom:   1px solid var(--border);
        margin-bottom:   40px;
    }
    .p2-logo {
        font-family:    'Manrope', sans-serif;
        font-size:      1.2rem;
        font-weight:    800;
        color:          var(--blue);
        letter-spacing: -0.02em;
    }
    .p2-step-badge {
        font-size:      0.78rem;
        font-weight:    700;
        color:          var(--muted);
        background:     #eaeff4;
        padding:        5px 14px;
        border-radius:  20px;
        font-family:    'Inter', sans-serif;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        border:        1.5px solid var(--border);
        background:    var(--card);
        color:         var(--text);
        font-weight:   600;
        font-size:     0.9rem;
        font-family:   'Inter', sans-serif;
        padding:       0.5rem 1.25rem;
        transition:    all 0.12s ease;
    }
    .stButton > button:hover { background: #f0f4f8; }
    .stButton > button[kind="primary"] {
        background:   var(--blue);
        color:        #fff;
        border-color: var(--blue);
        font-weight:  700;
    }
    .stButton > button[kind="primary"]:hover {
        background: #0038bf; border-color: #0038bf;
    }

    /* Typography */
    .p2-title {
        font-family:   'Manrope', sans-serif;
        font-size:     1.6rem;
        font-weight:   800;
        color:         var(--text);
        margin-bottom: 6px;
    }
    .p2-sub {
        font-size:     0.9rem;
        color:         var(--muted);
        margin-bottom: 32px;
        line-height:   1.55;
    }

    /* Step labels */
    .step-label {
        font-size:      0.72rem;
        font-weight:    700;
        color:          var(--blue);
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom:  10px;
        font-family:    'Inter', sans-serif;
    }

    /* Form card */
    .form-card {
        background:    var(--card);
        border:        1px solid var(--border);
        border-radius: 14px;
        padding:       28px;
        margin-bottom: 20px;
        box-shadow:    0 2px 12px rgba(23,28,31,.04);
    }

    /* Tabs */
    div[data-baseweb="tab"] {
        font-size:   0.875rem;
        color:       var(--muted);
        font-family: 'Inter', sans-serif;
    }
    div[data-baseweb="tab"][aria-selected="true"] {
        color: var(--text); font-weight: 700;
    }

    /* Checkbox / radio */
    .stCheckbox label { color: var(--text) !important; font-size: 0.9rem !important; font-family: 'Inter', sans-serif !important; }
    .stRadio   label  { color: var(--text) !important; font-size: 0.875rem !important; font-family: 'Inter', sans-serif !important; }

    /* Form inputs */
    .stTextInput label  { color: var(--text) !important; font-size: 0.9rem !important; font-weight: 600 !important; font-family: 'Inter', sans-serif !important; }
    .stSelectbox label  { color: var(--text) !important; font-size: 0.9rem !important; font-weight: 600 !important; font-family: 'Inter', sans-serif !important; }
    .stTextInput input  { font-size: 1rem !important; font-family: 'Inter', sans-serif !important; }

    /* Progress */
    .stProgress > div > div { background-color: var(--blue); }

    /* Divider */
    .sd-divider { border: none; border-top: 1px solid var(--border); margin: 2rem 0; }

    /* Min-skills hint card */
    .min-skills-hint {
        background:    var(--blue-lt);
        border-left:   3px solid var(--blue);
        border-radius: 8px;
        padding:       10px 14px;
        font-size:     0.85rem;
        color:         var(--text);
        margin:        4px 0 16px 0;
        font-family:   'Inter', sans-serif;
    }
    .min-skills-hint b { color: var(--blue); }
</style>
""", unsafe_allow_html=True)

# ── Top bar ───────────────────────────────────────────────────────────────────
st.markdown("<div style='padding-top:20px;'><span style='font-family:Manrope,sans-serif;font-size:1.2rem;font-weight:800;color:#002c98;letter-spacing:-0.02em;'>SkillDrift</span></div>", unsafe_allow_html=True)

st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:0 0 36px 0;'>", unsafe_allow_html=True)

# Back button
if st.button("Back to Home", key="back_home"):
    st.switch_page("pages/01_home.py")

st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

# Page title
st.markdown("""
<div class="p2-title">Analyze My Career Focus</div>
<div class="p2-sub">Fill in your details, select your skills, and take a short quiz to verify what you know.</div>
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


def required_min_skills(sem: int) -> int:
    """Sem 1 -> 1 skill, Sem 2 -> 2 skills, Sem 3..8 -> 3 skills."""
    if sem == 1:
        return 1
    if sem == 2:
        return 2
    return 3


# ── Step 1 — Details ──────────────────────────────────────────────────────────
st.markdown('<div class="step-label">Step 1 — Your Details</div>', unsafe_allow_html=True)

col_name, col_sem = st.columns([3, 1], gap="medium")
with col_name:
    name_input = st.text_input(
        "Full Name",
        value=st.session_state.get("student_name", "") or "",
        placeholder="e.g. Priya Sharma",
        max_chars=80,
    )
with col_sem:
    # No automatic default - student must explicitly pick a semester.
    # We use a placeholder option whose value is None and disable any
    # restoration of a numeric default unless the student previously
    # saved one in this same session.
    saved_sem = st.session_state.get("semester")
    sem_options = [None] + list(range(1, 9))

    def _sem_label(x):
        return "Select semester" if x is None else f"Sem {x}"

    if saved_sem in range(1, 9):
        # Returning to the page after they already chose one - keep it.
        sem_index = sem_options.index(saved_sem)
    else:
        sem_index = 0  # placeholder

    semester = st.selectbox(
        "Semester",
        options=sem_options,
        index=sem_index,
        format_func=_sem_label,
    )

# Live hint on minimum skills required for this semester
if semester is not None:
    min_required = required_min_skills(semester)
    skill_word = "skill" if min_required == 1 else "skills"
    st.markdown(
        f"<div class='min-skills-hint'>"
        f"For <b>Sem {semester}</b>, you must select at least "
        f"<b>{min_required} {skill_word}</b> to continue.</div>",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        "<div class='min-skills-hint'>"
        "Select your semester above &mdash; the minimum number of skills "
        "required depends on it.</div>",
        unsafe_allow_html=True,
    )

# ── Step 2 — Skills ────────────────────────────────────────────────────────────
st.markdown('<div class="step-label" style="margin-top:8px;">Step 2 — Select Your Skills</div>', unsafe_allow_html=True)
st.markdown(
    "<div style='font-size:0.88rem; color:#515f74; margin-bottom:14px;'>"
    "Select every technology you have studied. Rate your level honestly — "
    "the quiz will verify your claims."
    "</div>",
    unsafe_allow_html=True,
)

selected_skills = {}
tab_labels = [
    f"{cat} ({sum(1 for s in skills if st.session_state.get(f'skill_check_{s}'))})"
    for cat, skills in ALL_SKILLS.items()
]
tabs = st.tabs(tab_labels)

for tab, (category, skills) in zip(tabs, ALL_SKILLS.items()):
    with tab:
        st.markdown(
            "<div style='font-size:0.82rem;color:#515f74;margin:10px 0 12px 0;'>"
            "Select all that apply, then set your level.</div>",
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

# ── Submit ─────────────────────────────────────────────────────────────────────
st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
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
        color = "#ba1a1a" if skill_count > 40 else "#15803d"
        st.markdown(
            f"<div style='padding-top:0.5rem;font-size:0.9rem;font-weight:700;color:{color};'>"
            f"{skill_count} skills selected</div>",
            unsafe_allow_html=True,
        )
        if skill_count > 40:
            st.warning(f"{skill_count} skills selected — this may indicate skill drift. You can still continue.")

if submit_skills:
    name_clean = name_input.strip()
    if not name_clean:
        st.error("Please enter your name to continue.")
        st.stop()
    if semester is None:
        st.error("Please select your semester to continue.")
        st.stop()

    min_required = required_min_skills(semester)
    if len(selected_skills) < min_required:
        skill_word = "skill" if min_required == 1 else "skills"
        st.error(
            f"Sem {semester} requires at least {min_required} {skill_word}. "
            f"You have selected {len(selected_skills)}."
        )
        st.stop()

    # Wipe any stale quiz / proctor state from previous attempts so the
    # new quiz starts fresh.
    reset_quiz_state(full=False)

    st.session_state["student_name"]    = name_clean
    st.session_state["semester"]        = semester
    st.session_state["selected_skills"] = selected_skills
    st.session_state["session_start"]   = datetime.now().isoformat()
    st.session_state["quiz_complete"]   = False
    st.session_state["verified_skills"] = {}

    save_session()
    st.switch_page("pages/02b_quiz.py")

# Already completed? give a way back to the dashboard
if st.session_state.get("quiz_complete"):
    st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:2rem 0;'>", unsafe_allow_html=True)
    st.success(
        f"Quiz already completed, {st.session_state['student_name']}. "
        "Your results are ready on the dashboard."
    )

    if st.button("Go to Dashboard", type="primary"):
        st.switch_page("pages/03_drift_score.py")