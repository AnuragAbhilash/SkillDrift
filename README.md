# SkillDrift

SkillDrift is a simple project that helps students understand whether their skills are aligned with a specific career path or scattered across different domains.

The idea came from a common problem: many students keep learning random skills without knowing if they are actually building toward a job role.

---

## What this project does

* Takes user skills as input
* Compares them with real job requirements
* Suggests the most suitable career track
* Shows missing skills (gap analysis)
* Recommends what to learn next

---

## Features

* Drift score (how scattered your skills are)
* Career match percentage
* Next skill recommendation
* Basic dashboard with results
* Faculty section to analyze multiple students

---

## Tech used

* Python
* Streamlit
* Pandas
* NumPy
* Plotly

---

## Project structure

```id="27391a"
SkillDrift/
│
├── app.py
├── brain.py
├── data/
│   ├── raw/
│   ├── processed/
│   ├── auth/
│   └── demo/
│
├── assets/
├── reports/
├── .streamlit/
└── requirements.txt
```

---

## How to run

Install dependencies:

```id="8127af"
pip install -r requirements.txt
```

Run the app:

```id="c1c5b2"
python -m streamlit run app.py
```

---

## Data

The project uses manually collected job data (from sites like Naukri) and converts it into structured CSV files such as:

* skills_mapping.csv
* required_skills_per_track.csv
* city_job_counts.csv

---

## Why I built this

While preparing for placements, I noticed that it’s easy to learn many things but hard to stay focused on one role. This project is an attempt to make that clearer using simple data analysis.

---

## Future improvements

* Better UI
* More accurate recommendations
* Live job data instead of manual collection
* Resume-based analysis

---

## Author

Sahib Hussain
B.Tech CSE Final Year
