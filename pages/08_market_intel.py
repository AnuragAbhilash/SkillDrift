# pages/08_market_intel.py

import streamlit as st
from session_store import init_session
import plotly.graph_objects as go
import pandas as pd
from brain import load_city_job_counts, load_required_skills, CAREER_TRACKS, TRACK_TO_ROLE
from _sidebar import APPLE_CSS, render_sidebar

st.set_page_config(
    page_title="SkillDrift — Market Intelligence",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session()
st.session_state["_current_page"] = "market"
st.markdown(APPLE_CSS, unsafe_allow_html=True)
render_sidebar()

if not st.session_state.get("student_name"):
    st.warning("Session not found. Please start from the beginning.")
    st.switch_page("pages/02_skill_input.py")


city_df    = load_city_job_counts()
req_df     = load_required_skills()
best_track = st.session_state.get("best_track", CAREER_TRACKS[0])

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

st.markdown("""
<div style="margin-bottom:1.25rem;">
    <div style="font-size:1.6rem; font-weight:700; color:#1D1D1F;">Market Intelligence</div>
    <div style="font-size:0.88rem; color:#86868B; margin-top:0.2rem;">
        Real data from 794 Indian job postings on Naukri.com — where are the jobs and what do employers want?
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["City Job Density", "Skill Demand by Track"])

# ── TAB 1 — City Map ──────────────────────────────────────────
with tab1:
    st.markdown("""
    <div style="font-size:0.88rem; font-weight:600; color:#1D1D1F; margin-bottom:0.4rem;">
        City-wise Job Density for Your Career Track
    </div>
    <div style="font-size:0.82rem; color:#86868B; margin-bottom:0.75rem;">
        Bubble size = number of job postings in that city. Larger = more opportunities.
    </div>
    """, unsafe_allow_html=True)

    col_sel, _ = st.columns([2, 3])
    with col_sel:
        selected_track = st.selectbox(
            "Career Track",
            options=CAREER_TRACKS,
            index=CAREER_TRACKS.index(best_track) if best_track in CAREER_TRACKS else 0,
            key="map_track_select",
        )

    track_col = TRACK_TO_CITY_COL.get(selected_track, selected_track)

    if track_col not in city_df.columns:
        st.warning(f"Column '{track_col}' not found. Available: {list(city_df.columns)}")
    else:
        map_df = city_df[["city", "latitude", "longitude", track_col]].copy()
        map_df = map_df.rename(columns={track_col: "job_count"})
        map_df = map_df[map_df["job_count"] > 0].dropna(subset=["latitude", "longitude"])

        if map_df.empty:
            st.info(f"No job postings found for {selected_track}. Try a different track.")
        else:
            max_count = map_df["job_count"].max()
            map_df["bubble_size"] = (map_df["job_count"] / max_count * 35 + 8).round(1)

            fig_map = go.Figure()
            fig_map.add_trace(go.Scattergeo(
                lat=map_df["latitude"],
                lon=map_df["longitude"],
                text=map_df.apply(
                    lambda r: f"<b>{r['city']}</b><br>{int(r['job_count'])} {selected_track} postings", axis=1
                ),
                hoverinfo="text", mode="markers",
                marker=dict(
                    size=map_df["bubble_size"],
                    color=map_df["job_count"],
                    colorscale="Blues",
                    showscale=True,
                    colorbar=dict(title="Job Postings", titlefont=dict(color="#1D1D1F"),
                                  tickfont=dict(color="#1D1D1F"), bgcolor="#FFFFFF", bordercolor="#D2D2D7"),
                    line=dict(color="#FFFFFF", width=1),
                    opacity=0.85,
                ),
            ))
            fig_map.add_trace(go.Scattergeo(
                lat=map_df["latitude"], lon=map_df["longitude"],
                text=map_df["city"], mode="text",
                textfont=dict(size=9, color="#1D1D1F"), hoverinfo="skip",
            ))
            fig_map.update_geos(
                scope="asia", center=dict(lat=20.5937, lon=78.9629),
                projection_scale=4.5,
                showland=True, landcolor="#F5F5F7",
                showocean=True, oceancolor="#E8E8ED",
                showcoastlines=True, coastlinecolor="#D2D2D7",
                showcountries=True, countrycolor="#D2D2D7",
                showframe=False,
            )
            fig_map.update_layout(
                paper_bgcolor="#FFFFFF", geo_bgcolor="#FFFFFF",
                font=dict(color="#1D1D1F"),
                margin=dict(l=0, r=0, t=20, b=0),
                height=480,
                title=dict(
                    text=f"{selected_track} — Job Density Across Indian Cities",
                    font=dict(color="#1D1D1F", size=13), x=0.5,
                ),
            )
            st.plotly_chart(fig_map, use_container_width=True)

            st.markdown(f"""
            <div style="font-size:0.85rem; font-weight:600; color:#1D1D1F; margin-bottom:0.5rem;">
                City Rankings — {selected_track}
            </div>
            """, unsafe_allow_html=True)
            rank_df = map_df[["city", "job_count"]].sort_values("job_count", ascending=False).reset_index(drop=True)
            rank_df.index += 1
            rank_df.columns = ["City", "Job Postings in Dataset"]
            st.dataframe(rank_df, use_container_width=True)

            if selected_track == best_track and not rank_df.empty:
                top_city = rank_df.iloc[0]["City"]
                st.markdown(
                    f"<div style='font-size:0.85rem; color:#86868B; margin-top:0.5rem;'>"
                    f"<strong style='color:#1D1D1F;'>{top_city}</strong> has the most "
                    f"{best_track} job postings in this dataset.</div>",
                    unsafe_allow_html=True,
                )

# ── TAB 2 — Skill Demand ──────────────────────────────────────
with tab2:
    st.markdown("""
    <div style="font-size:0.88rem; font-weight:600; color:#1D1D1F; margin-bottom:0.3rem;">
        Top Skills Demanded by Indian Employers
    </div>
    <div style="font-size:0.82rem; color:#86868B; margin-bottom:0.75rem;">
        Ranked by how often they appear in Naukri.com job postings.
        Green = you have it. Red = you are missing it.
    </div>
    """, unsafe_allow_html=True)

    col_sel2, _ = st.columns([2, 3])
    with col_sel2:
        selected_track2 = st.selectbox(
            "Career Track",
            options=CAREER_TRACKS,
            index=CAREER_TRACKS.index(best_track) if best_track in CAREER_TRACKS else 0,
            key="trend_track_select",
        )

    role_name2      = TRACK_TO_ROLE.get(selected_track2, selected_track2)
    track_skills_df = req_df[req_df["track"] == role_name2].copy()
    track_skills_df = track_skills_df.sort_values("frequency_pct", ascending=False).head(15)

    if track_skills_df.empty:
        st.warning(f"No skill data found for {selected_track2}.")
    else:
        verified_skills = st.session_state.get("verified_skills", {})
        verified_lower  = [s.lower() for s in verified_skills.keys()]

        track_skills_df["have_it"] = track_skills_df["skill"].apply(lambda s: s.lower() in verified_lower)
        bar_colors_t = ["#34C759" if h else "#FF3B30" for h in track_skills_df["have_it"]]

        fig_trend = go.Figure(go.Bar(
            x=track_skills_df["frequency_pct"].tolist(),
            y=track_skills_df["skill"].tolist(),
            orientation="h",
            marker_color=bar_colors_t,
            text=[f"{v:.1f}%" for v in track_skills_df["frequency_pct"]],
            textposition="outside",
            textfont=dict(color="#1D1D1F", size=11),
        ))
        fig_trend.update_layout(
            paper_bgcolor="#FFFFFF", plot_bgcolor="#F5F5F7",
            font=dict(color="#1D1D1F", size=11),
            xaxis=dict(range=[0, 115], gridcolor="#D2D2D7",
                       title="Appears in X% of Job Postings", color="#86868B"),
            yaxis=dict(gridcolor="#D2D2D7", autorange="reversed", color="#1D1D1F"),
            margin=dict(l=10, r=60, t=30, b=15),
            height=460,
            title=dict(
                text=f"Top Skills for {selected_track2} — Green = You Have It | Red = Missing",
                font=dict(color="#1D1D1F", size=12), x=0.5,
            ),
        )
        st.plotly_chart(fig_trend, use_container_width=True)

        have_count    = int(track_skills_df["have_it"].sum())
        missing_count = len(track_skills_df) - have_count

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Skills Shown", len(track_skills_df))
        with c2:
            st.metric("You Have", have_count)
        with c3:
            st.metric("You Are Missing", missing_count)

        st.markdown(
            "<div style='font-size:0.78rem; color:#86868B; margin-top:0.25rem;'>"
            "Source: Skills extracted from 794 real Indian job descriptions from Naukri.com, "
            "processed using NLP frequency analysis.</div>",
            unsafe_allow_html=True,
        )

st.markdown("<hr style='border:none; border-top:1px solid #D2D2D7; margin:1.5rem 0;'>",
            unsafe_allow_html=True)

col_prev, col_next = st.columns(2)
with col_prev:
    if st.button("Back — Peer Mirror", use_container_width=True):
        st.switch_page("pages/07_peer_mirror.py")
with col_next:
    if st.button("Next — Final Report", type="primary", use_container_width=True):
        st.switch_page("pages/10_final_report.py")
