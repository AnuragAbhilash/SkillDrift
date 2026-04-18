# Window 8 - Market Intelligence 
# =============================================================
# pages/08_market_intel.py — Window 8: Market Intelligence
# City heatmap and skill demand trend from real Naukri data.
# =============================================================

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from brain import load_city_job_counts, load_required_skills, CAREER_TRACKS, TRACK_TO_ROLE

st.set_page_config(
    page_title="SkillDrift — Market Intelligence",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session Guard ─────────────────────────────────────────────
if not st.session_state.get("student_name"):
    st.warning("⚠️ Session not found. Please start from the beginning.")
    st.switch_page("pages/02_skill_input.py")

# =============================================================
# SIDEBAR
# =============================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0;">
      <svg width="80" height="80" viewBox="0 0 80 80"
           xmlns="http://www.w3.org/2000/svg">
        <circle cx="40" cy="40" r="40" fill="#2D3250"/>
        <circle cx="40" cy="30" r="15" fill="#6C63FF"/>
        <ellipse cx="40" cy="65" rx="22" ry="15" fill="#6C63FF"/>
      </svg>
    </div>
    """, unsafe_allow_html=True)

    student_name = st.session_state.get("student_name", "Student")
    st.markdown(
        f"<div style='text-align:center; font-weight:700; "
        f"font-size:1.1rem; color:#FAFAFA;'>{student_name}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='text-align:center; color:#7F8C8D; font-size:0.85rem;'>"
        f"Semester {st.session_state.get('semester', '?')}</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    drift_score   = st.session_state.get("drift_score")
    drift_label   = st.session_state.get("drift_label", "")
    entropy_score = st.session_state.get("entropy_score")
    entropy_label = st.session_state.get("entropy_label", "")

    if drift_score is not None:
        drift_color = (
            "#2ECC71" if drift_score >= 60
            else "#F39C12" if drift_score >= 40
            else "#E74C3C"
        )
        st.markdown(f"""
        <div style="background:#1A1D27; border:1px solid #2D3250;
                    border-radius:8px; padding:1rem; margin-bottom:0.75rem;">
            <div style="color:#7F8C8D; font-size:0.8rem;">DRIFT SCORE</div>
            <div style="font-size:2rem; font-weight:900; color:{drift_color};">
                {drift_score}
            </div>
            <div style="color:#BDC3C7; font-size:0.85rem;">{drift_label}</div>
        </div>
        """, unsafe_allow_html=True)

        entropy_color = (
            "#2ECC71" if entropy_score < 1.2
            else "#F39C12" if entropy_score < 2.0
            else "#E74C3C"
        )
        st.markdown(f"""
        <div style="background:#1A1D27; border:1px solid #2D3250;
                    border-radius:8px; padding:1rem; margin-bottom:0.75rem;">
            <div style="color:#7F8C8D; font-size:0.8rem;">ENTROPY SCORE</div>
            <div style="font-size:2rem; font-weight:900; color:{entropy_color};">
                {entropy_score}
                <span style="font-size:1rem;">bits</span>
            </div>
            <div style="color:#BDC3C7; font-size:0.85rem;">{entropy_label}</div>
        </div>
        """, unsafe_allow_html=True)

        track_counts = st.session_state.get("track_counts", {})
        if track_counts:
            tracks  = list(track_counts.keys())
            counts  = list(track_counts.values())
            counts_closed = counts + [counts[0]]
            tracks_closed = tracks + [tracks[0]]

            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=counts_closed,
                theta=tracks_closed,
                fill="toself",
                fillcolor="rgba(108, 99, 255, 0.3)",
                line=dict(color="#6C63FF", width=2),
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, showticklabels=False,
                                    gridcolor="#2D3250"),
                    angularaxis=dict(tickfont=dict(size=9, color="#BDC3C7"),
                                     gridcolor="#2D3250"),
                    bgcolor="#0E1117",
                ),
                paper_bgcolor="#0E1117",
                showlegend=False,
                margin=dict(l=20, r=20, t=20, b=20),
                height=280,
            )
            st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("---")
    st.markdown("📊 **Your Dashboard**")
    nav_pages = [
        ("🎯 Drift & Entropy Scores",   "pages/03_drift_score.py"),
        ("⏰ Urgency Engine",            "pages/04_urgency.py"),
        ("🏆 Career Track Match",        "pages/05_career_match.py"),
        ("📚 Next Skill & Readiness",    "pages/06_next_skill.py"),
        ("👥 Peer Mirror",               "pages/07_peer_mirror.py"),
        ("🗺️ Market Intelligence",       "pages/08_market_intel.py"),
        ("📄 Final Report",              "pages/10_final_report.py"),
    ]
    for label, page in nav_pages:
        if st.button(label, use_container_width=True, key=f"nav_{page}"):
            st.switch_page(page)

    st.markdown("---")
    if st.button("🚪 Log Out", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("pages/01_home.py")

# =============================================================
# MAIN CONTENT
# =============================================================

st.title("🗺️ Market Intelligence")
st.markdown(
    "Real data from **794 Indian job postings** collected from Naukri.com. "
    "Where are the jobs? What do employers actually want?"
)
st.markdown("---")

# Load data
city_df    = load_city_job_counts()
req_df     = load_required_skills()
best_track = st.session_state.get("best_track", CAREER_TRACKS[0])

# Build track column map from city_df
# city_job_counts.csv columns: city, latitude, longitude,
# Data Analyst, Data Scientist, Data Engineer, ML Engineer,
# Web Developer, DevOps Cloud, Cybersecurity, Software Dev

TRACK_TO_CITY_COL = {
    "Data Analyst":   "Data Analyst",
    "Data Scientist": "Data Scientist",
    "Data Engineer":  "Data Engineer",
    "ML Engineer":    "ML Engineer",
    "Web Developer":  "Web Developer",
    "DevOps Cloud":   "DevOps Cloud",
    "Cybersecurity":  "Cybersecurity",
    "Software Dev":   "Software Dev",
}

tab1, tab2 = st.tabs(["🗺️ City Job Density Map", "📊 Skill Demand Trend"])

# =============================================================
# TAB 1 — CITY JOB HEATMAP
# =============================================================
with tab1:
    st.subheader("City-wise Job Density for Your Career Track")
    st.markdown(
        "Circle size represents number of job postings in that city "
        "from the Naukri.com dataset. Larger circle = more opportunities."
    )

    col_track_select, col_info = st.columns([2, 3])
    with col_track_select:
        selected_track = st.selectbox(
            "Select Career Track",
            options=CAREER_TRACKS,
            index=CAREER_TRACKS.index(best_track) if best_track in CAREER_TRACKS else 0,
            key="map_track_select",
        )

    track_col = TRACK_TO_CITY_COL.get(selected_track, selected_track)

    if track_col not in city_df.columns:
        st.warning(
            f"⚠️ Column '{track_col}' not found in city_job_counts.csv. "
            f"Available columns: {list(city_df.columns)}"
        )
    else:
        map_df = city_df[["city", "latitude", "longitude", track_col]].copy()
        map_df = map_df.rename(columns={track_col: "job_count"})
        map_df = map_df[map_df["job_count"] > 0].copy()
        map_df = map_df.dropna(subset=["latitude", "longitude"])

        if map_df.empty:
            st.info(
                f"No job postings found for {selected_track} in the dataset. "
                "Try a different track."
            )
        else:
            # Scale bubble sizes — min 8, max 40
            max_count = map_df["job_count"].max()
            map_df["bubble_size"] = (
                map_df["job_count"] / max_count * 35 + 8
            ).round(1)

            fig_map = go.Figure()

            fig_map.add_trace(go.Scattergeo(
                lat=map_df["latitude"],
                lon=map_df["longitude"],
                text=map_df.apply(
                    lambda r: f"<b>{r['city']}</b><br>"
                              f"{int(r['job_count'])} {selected_track} postings",
                    axis=1,
                ),
                hoverinfo="text",
                mode="markers",
                marker=dict(
                    size=map_df["bubble_size"],
                    color=map_df["job_count"],
                    colorscale="Viridis",
                    showscale=True,
                    colorbar=dict(
                        title="Job Postings",
                        titlefont=dict(color="#BDC3C7"),
                        tickfont=dict(color="#BDC3C7"),
                        bgcolor="#1A1D27",
                        bordercolor="#2D3250",
                    ),
                    line=dict(color="#FAFAFA", width=1),
                    opacity=0.85,
                ),
            ))

            # Add city name labels
            fig_map.add_trace(go.Scattergeo(
                lat=map_df["latitude"],
                lon=map_df["longitude"],
                text=map_df["city"],
                mode="text",
                textfont=dict(size=9, color="#FAFAFA"),
                hoverinfo="skip",
            ))

            fig_map.update_geos(
                scope="asia",
                center=dict(lat=20.5937, lon=78.9629),
                projection_scale=4.5,
                showland=True,
                landcolor="#1A1D27",
                showocean=True,
                oceancolor="#0E1117",
                showcoastlines=True,
                coastlinecolor="#2D3250",
                showcountries=True,
                countrycolor="#2D3250",
                showframe=False,
            )

            fig_map.update_layout(
                paper_bgcolor="#0E1117",
                geo_bgcolor="#0E1117",
                font=dict(color="#BDC3C7"),
                margin=dict(l=0, r=0, t=30, b=0),
                height=520,
                title=dict(
                    text=f"{selected_track} — Job Density Across Indian Cities",
                    font=dict(color="#FAFAFA", size=14),
                    x=0.5,
                ),
            )

            st.plotly_chart(fig_map, use_container_width=True)

            # City ranking table below map
            st.subheader(f"🏙️ City Rankings — {selected_track}")
            rank_df = map_df[["city", "job_count"]].sort_values(
                "job_count", ascending=False
            ).reset_index(drop=True)
            rank_df.index = rank_df.index + 1
            rank_df.columns = ["City", "Job Postings in Dataset"]
            st.dataframe(rank_df, use_container_width=True)

            # Context note
            if selected_track == best_track:
                top_city = rank_df.iloc[0]["City"] if not rank_df.empty else "Unknown"
                st.markdown(
                    f"> 📌 **{top_city}** has the highest concentration of "
                    f"**{best_track}** job postings in this dataset. "
                    f"Students targeting this track may need to consider "
                    f"relocation or remote opportunities from smaller cities."
                )

# =============================================================
# TAB 2 — SKILL DEMAND TREND
# =============================================================
with tab2:
    st.subheader("Top Skills Demanded by Indian Employers")
    st.markdown(
        "Horizontal bar chart showing the top 10 skills for each career track, "
        "ranked by how frequently they appear in Naukri.com job postings. "
        "Data is from your 794-row Naukri dataset."
    )

    col_track_select2, _ = st.columns([2, 3])
    with col_track_select2:
        selected_track2 = st.selectbox(
            "Select Career Track",
            options=CAREER_TRACKS,
            index=CAREER_TRACKS.index(best_track) if best_track in CAREER_TRACKS else 0,
            key="trend_track_select",
        )

    role_name2 = TRACK_TO_ROLE.get(selected_track2, selected_track2)
    track_skills_df = req_df[req_df["track"] == role_name2].copy()
    track_skills_df = track_skills_df.sort_values("frequency_pct", ascending=False).head(15)

    if track_skills_df.empty:
        st.warning(f"No skill data found for {selected_track2}.")
    else:
        verified_skills = st.session_state.get("verified_skills", {})
        verified_lower  = [s.lower() for s in verified_skills.keys()]

        track_skills_df["have_it"] = track_skills_df["skill"].apply(
            lambda s: s.lower() in verified_lower
        )
        bar_colors_t = [
            "#2ECC71" if have else "#E74C3C"
            for have in track_skills_df["have_it"]
        ]

        fig_trend = go.Figure(go.Bar(
            x=track_skills_df["frequency_pct"].tolist(),
            y=track_skills_df["skill"].tolist(),
            orientation="h",
            marker_color=bar_colors_t,
            text=[f"{v:.1f}%" for v in track_skills_df["frequency_pct"]],
            textposition="outside",
            textfont=dict(color="#BDC3C7"),
        ))

        fig_trend.update_layout(
            paper_bgcolor="#0E1117",
            plot_bgcolor="#0E1117",
            font=dict(color="#BDC3C7"),
            xaxis=dict(
                range=[0, 110],
                gridcolor="#2D3250",
                title="Appears in X% of Job Postings",
            ),
            yaxis=dict(gridcolor="#2D3250", autorange="reversed"),
            margin=dict(l=10, r=60, t=30, b=20),
            height=500,
            title=dict(
                text=f"Top Skills for {selected_track2} — Green = You Have It | Red = Missing",
                font=dict(color="#FAFAFA", size=13),
                x=0.5,
            ),
        )

        st.plotly_chart(fig_trend, use_container_width=True)

        # Summary
        have_count    = track_skills_df["have_it"].sum()
        missing_count = len(track_skills_df) - have_count

        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.metric("Skills Shown", len(track_skills_df))
        with col_s2:
            st.metric("You Have", int(have_count), delta=None)
        with col_s3:
            st.metric("You're Missing", int(missing_count), delta=None)

        st.caption(
            "Source: Skills extracted from 794 real Indian job descriptions "
            "collected from Naukri.com and processed using NLP frequency analysis."
        )

st.markdown("---")

# ── Navigation ────────────────────────────────────────────────
col_prev, col_next = st.columns(2)
with col_prev:
    if st.button("← Back to Peer Mirror", use_container_width=True):
        st.switch_page("pages/07_peer_mirror.py")
with col_next:
    if st.button("Next → Final Report 📄", type="primary", use_container_width=True):
        st.switch_page("pages/10_final_report.py")