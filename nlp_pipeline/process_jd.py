"""
SkillDrift NLP Pipeline
=======================
Run this script ONCE from your project root:
    python nlp_pipeline/process_jd.py
What it generates:
    1. data/processed/required_skills_per_track.csv
    2. data/processed/skills_mapping.csv
    3. data/processed/city_job_counts.csv
Input:
    data/raw/raw_jd_data.csv  (your 794-row Naukri dataset)
"""
import pandas as pd
import numpy as np
from collections import Counter
import os
import re
# ============================================================
# STEP 0 — SKILL NORMALIZATION DICTIONARY
# Maps messy variations → clean standard names
# Add more entries here if you find new variations in your data
# ============================================================
SKILL_ALIASES = {
    # Python
    "python3": "Python",
    "python 3": "Python",
    "python programming": "Python",
    # SQL variants
    "sql": "SQL",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "ms sql": "SQL Server",
    "mssql": "SQL Server",
    "sql server": "SQL Server",
    "t-sql": "SQL",
    "pl/sql": "SQL",
    "plsql": "SQL",
    "nosql": "NoSQL",
    # Excel variants
    "ms excel": "Excel",
    "microsoft excel": "Excel",
    "ms-excel": "Excel",
    "advanced excel": "Advanced Excel",
    "ms office": "MS Office",
    "microsoft office": "MS Office",
    # Power BI variants
    "power bi": "Power BI",
    "powerbi": "Power BI",
    "power-bi": "Power BI",
    "power bi desktop": "Power BI",
    # Power Query
    "power query": "Power Query",
    "powerquery": "Power Query",
    "power query m": "Power Query",
    # Machine Learning
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "machinelearning": "Machine Learning",
    # Deep Learning
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",
    # NLP
    "nlp": "NLP",
    "natural language processing": "NLP",
    "natural language processing (nlp)": "NLP",
    # TensorFlow
    "tensorflow": "TensorFlow",
    "tensor flow": "TensorFlow",
    "tf": "TensorFlow",
    "tensorflow 2": "TensorFlow",
    # PyTorch
    "pytorch": "PyTorch",
    "py torch": "PyTorch",
    # Scikit-learn
    "scikit-learn": "Scikit-learn",
    "scikit learn": "Scikit-learn",
    "sklearn": "Scikit-learn",
    # JavaScript
    "javascript": "JavaScript",
    "js": "JavaScript",
    "java script": "JavaScript",
    "es6": "JavaScript",
    # TypeScript
    "typescript": "TypeScript",
    "ts": "TypeScript",
    # React
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "react js": "React",
    # Node.js
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "node js": "Node.js",
    "node": "Node.js",
    # Angular
    "angular": "Angular",
    "angularjs": "Angular",
    "angular.js": "Angular",
    "angular js": "Angular",
    # Vue
    "vue.js": "Vue.js",
    "vuejs": "Vue.js",
    "vue js": "Vue.js",
    "vue": "Vue.js",
    # Next.js
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "next js": "Next.js",
    # Django
    "django": "Django",
    "django rest framework": "Django",
    # Flask
    "flask": "Flask",
    # FastAPI
    "fastapi": "FastAPI",
    "fast api": "FastAPI",
    # Spring Boot
    "spring boot": "Spring Boot",
    "springboot": "Spring Boot",
    "spring": "Spring Boot",
    "spring framework": "Spring Boot",
    # Docker
    "docker": "Docker",
    "dockerfile": "Docker",
    "docker compose": "Docker",
    # Kubernetes
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "kube": "Kubernetes",
    # AWS
    "aws": "AWS",
    "amazon web services": "AWS",
    "amazon aws": "AWS",
    # Azure
    "azure": "Azure",
    "microsoft azure": "Azure",
    "ms azure": "Azure",
    # GCP
    "gcp": "GCP",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    # Git
    "git": "Git",
    "github": "Git",
    "gitlab": "Git",
    "git/github": "Git",
    "version control": "Git",
    # CI/CD
    "ci/cd": "CI/CD",
    "ci cd": "CI/CD",
    "cicd": "CI/CD",
    "continuous integration": "CI/CD",
    "continuous deployment": "CI/CD",
    # Jenkins
    "jenkins": "Jenkins",
    # Terraform
    "terraform": "Terraform",
    # Ansible
    "ansible": "Ansible",
    # Apache Spark
    "apache spark": "Apache Spark",
    "spark": "Apache Spark",
    "pyspark": "Apache Spark",
    # Kafka
    "kafka": "Kafka",
    "apache kafka": "Kafka",
    # Airflow
    "airflow": "Airflow",
    "apache airflow": "Airflow",
    # Hadoop
    "hadoop": "Hadoop",
    "apache hadoop": "Hadoop",
    # Hive
    "hive": "Hive",
    "apache hive": "Hive",
    # Snowflake
    "snowflake": "Snowflake",
    # BigQuery
    "bigquery": "BigQuery",
    "google bigquery": "BigQuery",
    "big query": "BigQuery",
    # dbt
    "dbt": "dbt",
    "data build tool": "dbt",
    # Scala
    "scala": "Scala",
    # Pandas
    "pandas": "Pandas",
    # NumPy
    "numpy": "NumPy",
    "num py": "NumPy",
    # Matplotlib/Visualization
    "matplotlib": "Matplotlib",
    "seaborn": "Seaborn",
    "plotly": "Plotly",
    # Tableau
    "tableau": "Tableau",
    # Looker
    "looker": "Looker",
    "looker studio": "Looker",
    "google data studio": "Looker",
    # Java
    "java": "Java",
    "core java": "Java",
    "java 8": "Java",
    "java ee": "Java",
    # C++
    "c++": "C++",
    "cpp": "C++",
    "c/c++": "C++",
    # C
    "c programming": "C",
    "c language": "C",
    # Linux
    "linux": "Linux",
    "unix": "Linux",
    "ubuntu": "Linux",
    "shell": "Shell Scripting",
    "shell scripting": "Shell Scripting",
    "bash": "Shell Scripting",
    "bash scripting": "Shell Scripting",
    # REST API
    "rest api": "REST API",
    "restful api": "REST API",
    "rest apis": "REST API",
    "api": "REST API",
    "restful": "REST API",
    # GraphQL
    "graphql": "GraphQL",
    # MongoDB
    "mongodb": "MongoDB",
    "mongo db": "MongoDB",
    "mongo": "MongoDB",
    # Redis
    "redis": "Redis",
    # Microservices
    "microservices": "Microservices",
    "micro services": "Microservices",
    "microservice": "Microservices",
    "microservice architecture": "Microservices",
    # Agile
    "agile": "Agile",
    "scrum": "Agile",
    "agile/scrum": "Agile",
    "kanban": "Agile",
    # Data Structures
    "data structures": "Data Structures",
    "dsa": "Data Structures",
    "data structure": "Data Structures",
    # Algorithms
    "algorithms": "Algorithms",
    "algorithm": "Algorithms",
    "data structures and algorithms": "Algorithms",
    # OOP
    "oop": "OOP",
    "object oriented programming": "OOP",
    "oops": "OOP",
    "object-oriented": "OOP",
    # Statistics
    "statistics": "Statistics",
    "statistical analysis": "Statistics",
    "stats": "Statistics",
    "statistical modeling": "Statistics",
    # Cybersecurity specific
    "network security": "Network Security",
    "ethical hacking": "Ethical Hacking",
    "penetration testing": "Penetration Testing",
    "pen testing": "Penetration Testing",
    "pentest": "Penetration Testing",
    "siem": "SIEM",
    "soc": "SOC",
    "firewalls": "Firewalls",
    "firewall": "Firewalls",
    "owasp": "OWASP",
    "kali linux": "Kali Linux",
    "kali": "Kali Linux",
    "incident response": "Incident Response",
    "vulnerability assessment": "Vulnerability Assessment",
    "vulnerability management": "Vulnerability Assessment",
    "cryptography": "Cryptography",
    "ceh": "CEH",
    "comptia security+": "CompTIA Security+",
    "comptia": "CompTIA Security+",
    "threat analysis": "Threat Analysis",
    "threat hunting": "Threat Analysis",
    # DevOps specific
    "prometheus": "Prometheus",
    "grafana": "Grafana",
    "monitoring": "Monitoring",
    "mlops": "MLOps",
    # Data Engineering
    "etl": "ETL",
    "data warehousing": "Data Warehousing",
    "data warehouse": "Data Warehousing",
    # ML Engineering
    "model deployment": "Model Deployment",
    "aws sagemaker": "AWS SageMaker",
    "sagemaker": "AWS SageMaker",
    "feature engineering": "Feature Engineering",
    "computer vision": "Computer Vision",
    "cv": "Computer Vision",
    "transformers": "Transformers",
    "hugging face": "Transformers",
    # Web specific
    "html": "HTML",
    "html5": "HTML",
    "css": "CSS",
    "css3": "CSS",
    "bootstrap": "Bootstrap",
    "jquery": "jQuery",
    "ajax": "AJAX",
    "php": "PHP",
    # Data Analysis specific
    "data analysis": "Data Analysis",
    "data analytics": "Data Analysis",
    "data visualization": "Data Visualization",
    "data viz": "Data Visualization",
    "dashboards": "Data Visualization",
    "dashboard": "Data Visualization",
    "business intelligence": "Business Intelligence",
    "bi": "Business Intelligence",
    "forecasting": "Forecasting",
    "data mining": "Data Mining",
    "predictive analytics": "Predictive Analytics",
    "sas": "SAS",
    "r": "R",
    "vba": "VBA",
    "power automate": "Power Automate",
    "google analytics": "Google Analytics",
    "looker studio": "Looker",
    "big data": "Big Data",
    "research": "Research",
    "networking": "Networking",
    "automation": "Automation",
    # Misc that appeared in your data
    "metadata": "Data Management",
    "data validation": "Data Management",
    "data management": "Data Management",
    "data processing": "Data Processing",
    "programming": "Programming",
    "backend development": "Backend Development",
    "full stack development": "Full Stack",
    "full stack": "Full Stack",
    "fullstack": "Full Stack",
    "c": "C",
    "sentinelone": "SIEM Tools",
    "crowdstrike": "SIEM Tools",
    "siem tools": "SIEM Tools",
    "mdr": "MDR",
    "sol": "SOC",
    "threat intelligence": "Threat Analysis",
}
# ============================================================
# STEP 1 — SKILL CLEANING FUNCTION
# ============================================================
def normalize_skill(raw_skill: str) -> str:
    """
    Clean a single skill string:
    - Strip whitespace
    - Lowercase for lookup
    - Return the standardized name
    """
    cleaned = raw_skill.strip()
    lookup = cleaned.lower()
    return SKILL_ALIASES.get(lookup, cleaned.title())
def extract_skills_from_row(skills_string: str) -> list:
    """
    Split a comma-separated skills string into individual skills
    and normalize each one.
    Skip blanks and very short tokens.
    """
    if pd.isna(skills_string) or str(skills_string).strip() == "":
        return []
    raw_skills = str(skills_string).split(",")
    normalized = []
    for s in raw_skills:
        s = s.strip()
        if len(s) < 2:
            continue
        norm = normalize_skill(s)
        if norm and len(norm) >= 2:
            normalized.append(norm)
    return normalized
# ============================================================
# STEP 2 — LOAD AND VALIDATE DATA
# ============================================================
def load_data(filepath: str) -> pd.DataFrame:
    print(f"\n{'='*60}")
    print(f"Loading data from: {filepath}")
    print(f"{'='*60}")
    df = pd.read_csv(filepath)
    print(f"Total rows loaded    : {len(df)}")
    print(f"Columns found        : {df.columns.tolist()}")
    required_cols = ["role", "company", "skills_required", "experience_level", "city"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    # Drop rows where skills_required is empty
    before = len(df)
    df = df.dropna(subset=["skills_required"])
    df = df[df["skills_required"].str.strip() != ""]
    after = len(df)
    print(f"Rows after removing empty skills: {after} (removed {before - after})")
    print(f"\nRole distribution:")
    print(df["role"].value_counts().to_string())
    return df
# ============================================================
# STEP 3 — GENERATE required_skills_per_track.csv
# ============================================================
def generate_required_skills(df: pd.DataFrame, top_n: int = 25) -> pd.DataFrame:
    """
    For each role, find the top N skills by frequency.
    Frequency = (count of JDs mentioning this skill) / (total JDs for this role) * 100
    """
    print(f"\n{'='*60}")
    print("Generating required_skills_per_track.csv")
    print(f"{'='*60}")
    results = []
    roles = df["role"].unique()
    for role in roles:
        role_df = df[df["role"] == role]
        total_jds = len(role_df)
        # Collect all skills for this role
        all_skills = []
        for _, row in role_df.iterrows():
            skills = extract_skills_from_row(row["skills_required"])
            all_skills.extend(skills)
        # Count frequency
        skill_counts = Counter(all_skills)
        total_skill_mentions = len(all_skills)
        print(f"\n  Role: {role}")
        print(f"  Total JDs: {total_jds}")
        print(f"  Unique skills found: {len(skill_counts)}")
        # Calculate frequency as percentage of JDs mentioning this skill
        skill_freq = {}
        for skill, count in skill_counts.items():
            # How many JDs mention this skill
            jd_count = sum(
                1 for _, row in role_df.iterrows()
                if skill in extract_skills_from_row(row["skills_required"])
            )
            freq_pct = round((jd_count / total_jds) * 100, 1)
            skill_freq[skill] = freq_pct
        # Sort by frequency, take top N
        sorted_skills = sorted(skill_freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
        print(f"  Top 5 skills: {sorted_skills[:5]}")
        for skill, freq in sorted_skills:
            results.append({
                "track": role,
                "skill": skill,
                "frequency_pct": freq
            })
    output_df = pd.DataFrame(results)
    return output_df
# ============================================================
# STEP 4 — GENERATE skills_mapping.csv
# ============================================================
def generate_skills_mapping(required_skills_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build skills_mapping.csv from required_skills_per_track.csv.
    A skill maps to a track if it appears in that track's required skills list.
    """
    print(f"\n{'='*60}")
    print("Generating skills_mapping.csv")
    print(f"{'='*60}")
    # Get all unique skills and all tracks
    all_skills = required_skills_df["skill"].unique().tolist()
    all_tracks = required_skills_df["track"].unique().tolist()
    # Create column names for tracks (safe Python names)
    track_col_map = {
        "Data Analyst": "data_analyst",
        "Data Scientist": "data_scientist",
        "Data Engineer": "data_engineer",
        "ML Engineer": "ml_engineer",
        "Web Developer": "web_developer",
        "DevOps Cloud": "devops_cloud",
        "Cybersecurity": "cybersecurity",
        "Software Dev": "software_dev",
    }
    track_cols = [track_col_map.get(t, t.lower().replace(" ", "_")) for t in all_tracks]
    # Build the mapping
    rows = []
    for skill in all_skills:
        row = {"skill": skill}
        for track, col in zip(all_tracks, track_cols):
            track_skills = required_skills_df[
                required_skills_df["track"] == track
            ]["skill"].tolist()
            row[col] = 1 if skill in track_skills else 0
        rows.append(row)
    mapping_df = pd.DataFrame(rows)
    # Sort by skill name for readability
    mapping_df = mapping_df.sort_values("skill").reset_index(drop=True)
    print(f"  Total skills in mapping: {len(mapping_df)}")
    print(f"  Tracks mapped: {track_cols}")
    return mapping_df
# ============================================================
# STEP 5 — GENERATE city_job_counts.csv
# ============================================================
# City coordinates for Indian cities
# Add more here if your data has cities not listed
CITY_COORDINATES = {
    "Bangalore": (12.9716, 77.5946),
    "Bengaluru": (12.9716, 77.5946),
    "Bengaluru/Bangalore": (12.9716, 77.5946),
    "Hyderabad": (17.3850, 78.4867),
    "Mumbai": (19.0760, 72.8777),
    "Pune": (18.5204, 73.8567),
    "Delhi": (28.7041, 77.1025),
    "New Delhi": (28.7041, 77.1025),
    "Chennai": (13.0827, 80.2707),
    "Gurugram": (28.4595, 77.0266),
    "Gurgaon": (28.4595, 77.0266),
    "Noida": (28.5355, 77.3910),
    "Kolkata": (22.5726, 88.3639),
    "Ahmedabad": (23.0225, 72.5714),
    "Jaipur": (26.9124, 75.7873),
    "Coimbatore": (11.0168, 76.9558),
    "Kochi": (9.9312, 76.2673),
    "Chandigarh": (30.7333, 76.7794),
    "Indore": (22.7196, 75.8577),
    "Nagpur": (21.1458, 79.0882),
    "Lucknow": (26.8467, 80.9462),
    "Bhubaneswar": (20.2961, 85.8245),
    "Thiruvananthapuram": (8.5241, 76.9366),
    "Vizag": (17.6868, 83.2185),
    "Visakhapatnam": (17.6868, 83.2185),
    "Kozhikode": (11.2588, 75.7804),
    "Atpadi": (17.4000, 74.7167),
    "Patna": (25.5941, 85.1376),
    "Bhopal": (23.2599, 77.4126),
    "Surat": (21.1702, 72.8311),
    "Vadodara": (22.3072, 73.1812),
    "Mysuru": (12.2958, 76.6394),
    "Mysore": (12.2958, 76.6394),
    "Mangaluru": (12.9141, 74.8560),
    "Mangalore": (12.9141, 74.8560),
    "Udaipur": (24.5854, 73.7125),
    "Ranchi": (23.3441, 85.3096),
    "Guwahati": (26.1445, 91.7362),
    "Remote": (20.5937, 78.9629),
    "Pan India": (20.5937, 78.9629),
    "Navi Mumbai": (19.0330, 73.0297),
    "Thane": (19.2183, 72.9781),
}
def normalize_city(city_str: str) -> str:
    """Normalize city names to standard form."""
    if pd.isna(city_str):
        return "Remote"
    city = str(city_str).strip()
    # Handle "Bengaluru" → "Bangalore" for display
    if city.lower() in ["bengaluru", "bengaluru/bangalore"]:
        return "Bangalore"
    if city.lower() in ["gurgaon"]:
        return "Gurugram"
    if city.lower() in ["new delhi"]:
        return "Delhi"
    if city.lower() in ["visakhapatnam"]:
        return "Vizag"
    if city.lower() in ["mysore"]:
        return "Mysuru"
    if city.lower() in ["mangalore"]:
        return "Mangaluru"
    return city
def generate_city_job_counts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Count job postings per city per role from real data.
    Only include cities that have coordinates.
    """
    print(f"\n{'='*60}")
    print("Generating city_job_counts.csv")
    print(f"{'='*60}")
    # Normalize city names in dataframe
    df = df.copy()
    df["city_normalized"] = df["city"].apply(normalize_city)
    # Get all roles
    roles = df["role"].unique().tolist()
    # Count per city per role
    city_role_counts = {}
    for city_raw in df["city_normalized"].unique():
        city_data = df[df["city_normalized"] == city_raw]
        role_counts = {}
        for role in roles:
            role_counts[role] = len(city_data[city_data["role"] == role])
        city_role_counts[city_raw] = role_counts
    # Build rows — only for cities we have coordinates for
    rows = []
    cities_missing_coords = []
    for city, role_counts in city_role_counts.items():
        # Skip cities with zero total postings
        total = sum(role_counts.values())
        if total == 0:
            continue
        # Get coordinates
        coords = CITY_COORDINATES.get(city)
        if coords is None:
            cities_missing_coords.append(city)
            continue
        row = {
            "city": city,
            "latitude": coords[0],
            "longitude": coords[1],
        }
        for role in roles:
            row[role] = role_counts.get(role, 0)
        rows.append(row)
    if cities_missing_coords:
        print(f"\n  WARNING: These cities had no coordinates and were skipped:")
        for c in cities_missing_coords:
            print(f"    - {c}")
        print(f"  Add them to CITY_COORDINATES dict in this script if needed.")
    city_df = pd.DataFrame(rows)
    # Sort by total jobs descending
    city_df["total"] = city_df[roles].sum(axis=1)
    city_df = city_df.sort_values("total", ascending=False).drop("total", axis=1)
    city_df = city_df.reset_index(drop=True)
    print(f"\n  Cities included in heatmap: {len(city_df)}")
    print(f"  Top 5 cities by total postings:")
    temp = city_df.copy()
    temp["total"] = city_df[roles].sum(axis=1)
    print(temp[["city", "total"]].head(5).to_string(index=False))
    return city_df
# ============================================================
# STEP 6 — SAVE ALL FILES
# ============================================================
def save_outputs(required_skills_df, skills_mapping_df, city_df):
    """Save all 3 generated CSV files to data/processed/"""
    os.makedirs("data/processed", exist_ok=True)
    # File 1
    path1 = "data/processed/required_skills_per_track.csv"
    required_skills_df.to_csv(path1, index=False)
    print(f"\n  Saved: {path1}  ({len(required_skills_df)} rows)")
    # File 2
    path2 = "data/processed/skills_mapping.csv"
    skills_mapping_df.to_csv(path2, index=False)
    print(f"  Saved: {path2}  ({len(skills_mapping_df)} rows)")
    # File 3
    path3 = "data/processed/city_job_counts.csv"
    city_df.to_csv(path3, index=False)
    print(f"  Saved: {path3}  ({len(city_df)} rows)")
# ============================================================
# STEP 7 — PRINT SUMMARY REPORT
# ============================================================
def print_summary(required_skills_df, skills_mapping_df, city_df):
    print(f"\n{'='*60}")
    print("PIPELINE COMPLETE — SUMMARY")
    print(f"{'='*60}")
    print(f"\nrequired_skills_per_track.csv:")
    for track in required_skills_df["track"].unique():
        track_df = required_skills_df[required_skills_df["track"] == track]
        top3 = track_df.head(3)[["skill", "frequency_pct"]].values.tolist()
        print(f"  {track:20s} → {len(track_df)} skills | Top 3: {top3}")
    print(f"\nskills_mapping.csv:")
    print(f"  Total unique skills mapped: {len(skills_mapping_df)}")
    print(f"\ncity_job_counts.csv:")
    roles = [c for c in city_df.columns if c not in ["city", "latitude", "longitude"]]
    city_df_temp = city_df.copy()
    city_df_temp["total"] = city_df_temp[roles].sum(axis=1)
    top5 = city_df_temp.nlargest(5, "total")[["city", "total"]]
    print(f"  Top 5 cities:\n{top5.to_string(index=False)}")
    print(f"\n{'='*60}")
    print("All files saved to data/processed/")
    print("You can now commit these files and move to Phase 2.")
    print(f"{'='*60}\n")
# ============================================================
# MAIN — Run everything
# ============================================================
if __name__ == "__main__":
    # Load raw data
    df = load_data("data/raw/raw_jd_data.csv")
    # Generate required skills per track
    required_skills_df = generate_required_skills(df, top_n=25)
    # Generate skills mapping from required skills
    skills_mapping_df = generate_skills_mapping(required_skills_df)
    # Generate city job counts
    city_df = generate_city_job_counts(df)
    # Save all outputs
    save_outputs(required_skills_df, skills_mapping_df, city_df)
    # Print summary
    print_summary(required_skills_df, skills_mapping_df, city_df)
