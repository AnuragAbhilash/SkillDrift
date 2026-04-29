# pages/08_market_intel.py

import streamlit as st
from session_store import init_session
import plotly.graph_objects as go
import pandas as pd
from brain import load_city_job_counts, load_required_skills, CAREER_TRACKS, TRACK_TO_ROLE
from _sidebar import APPLE_CSS, render_sidebar

st.set_page_config(
    page_title="SkillDrift — Job Market",
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
    st.stop()

city_df    = load_city_job_counts()
req_df     = load_required_skills()
best_track = st.session_state.get("best_track", CAREER_TRACKS[0])

TRACK_TO_CITY_COL = {
    "Data Analyst":   "Data Analyst",
    "ML Engineer":    "ML Engineer",
    "Web Developer":  "Web Developer",
    "DevOps Cloud":   "DevOps Cloud",
    "Cybersecurity":  "Cybersecurity",
    "Software Dev":   "Software Dev",
    "QA Tester":      "QA Tester",
    "Full Stack Dev": "Full Stack Dev",
}

# ── Page Title ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:1.25rem;">
    <div style="font-size:1.5rem;font-weight:800;color:#171c1f;font-family:'Manrope',sans-serif;">
        Job Market
    </div>
    <div style="font-size:0.875rem;color:#515f74;margin-top:5px;">
        Real data from 1,600 Indian job postings on Naukri.com — where are the jobs and what do companies actually want?
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Jobs by City", "Skills Companies Want"])

# ── TAB 1 — City Map ───────────────────────────────────────────────────────────
with tab1:
    st.markdown("""
    <div style="font-size:0.88rem;font-weight:600;color:#171c1f;margin-bottom:4px;margin-top:8px;">
        Where are the jobs in India?
    </div>
    <div style="font-size:0.82rem;color:#515f74;margin-bottom:12px;">
        Bigger bubble = more job openings in that city. Pick a career track below to filter.
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
        st.warning(f"No city data found for {selected_track}.")
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
                    lambda r: f"<b>{r['city']}</b><br>{int(r['job_count'])} openings", axis=1
                ),
                hoverinfo="text",
                mode="markers",
                marker=dict(
                    size=map_df["bubble_size"],
                    color=map_df["job_count"],
                    colorscale="Blues",
                    showscale=True,
                    colorbar=dict(
                        title="Openings",
                        titlefont=dict(color="#171c1f"),
                        tickfont=dict(color="#171c1f"),
                        bgcolor="#FFFFFF",
                        bordercolor="#e2e8f0",
                    ),
                    line=dict(color="#FFFFFF", width=1),
                    opacity=0.85,
                ),
            ))
            fig_map.add_trace(go.Scattergeo(
                lat=map_df["latitude"],
                lon=map_df["longitude"],
                text=map_df["city"],
                mode="text",
                textfont=dict(size=9, color="#171c1f"),
                hoverinfo="skip",
            ))
            fig_map.update_geos(
                scope="asia",
                center=dict(lat=22.5, lon=80.0),
                projection_scale=6.5,
                showland=True, landcolor="#f8fafc",
                showocean=True, oceancolor="#e8eeff",
                showcoastlines=True, coastlinecolor="#e2e8f0",
                showcountries=True, countrycolor="#e2e8f0",
                showframe=False,
            )
            fig_map.update_layout(
                paper_bgcolor="#FFFFFF",
                geo_bgcolor="#FFFFFF",
                font=dict(color="#171c1f"),
                margin=dict(l=0, r=0, t=24, b=0),
                height=460,
                title=dict(
                    text=f"{selected_track} — Job Openings by City",
                    font=dict(color="#171c1f", size=13, family="Manrope"),
                    x=0.5,
                ),
            )
            st.plotly_chart(fig_map, use_container_width=True)

            # City rankings table
            st.markdown(f"""
            <div style="font-size:0.88rem;font-weight:700;color:#171c1f;margin-bottom:8px;">
                City Rankings for {selected_track}
            </div>
            """, unsafe_allow_html=True)

            rank_df = (
                map_df[["city", "job_count"]]
                .sort_values("job_count", ascending=False)
                .reset_index(drop=True)
            )
            rank_df.index += 1
            rank_df.columns = ["City", "Job Openings in Dataset"]
            st.dataframe(rank_df, use_container_width=True)

            if selected_track == best_track and not rank_df.empty:
                top_city = rank_df.iloc[0]["City"]
                st.markdown(
                    f"<div style='font-size:0.82rem;color:#515f74;margin-top:6px;'>"
                    f"<strong style='color:#171c1f;'>{top_city}</strong> has the most "
                    f"{best_track} openings in this dataset. If you are open to relocating, "
                    f"this is where the demand is highest.</div>",
                    unsafe_allow_html=True,
                )

# ── TAB 2 — Skill Demand ───────────────────────────────────────────────────────
with tab2:
    st.markdown("""
    <div style="font-size:0.88rem;font-weight:600;color:#171c1f;margin-bottom:4px;margin-top:8px;">
        What skills are companies actually asking for?
    </div>
    <div style="font-size:0.82rem;color:#515f74;margin-bottom:12px;">
        Green bar = you already have this skill. Red bar = you are missing it.
        The longer the bar, the more companies ask for that skill.
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

        track_skills_df["have_it"] = track_skills_df["skill"].apply(
            lambda s: s.lower() in verified_lower
        )
        bar_colors_t = ["#15803d" if h else "#ba1a1a" for h in track_skills_df["have_it"]]

        fig_trend = go.Figure(go.Bar(
            x=track_skills_df["frequency_pct"].tolist(),
            y=track_skills_df["skill"].tolist(),
            orientation="h",
            marker_color=bar_colors_t,
            text=[f"{v:.0f}%" for v in track_skills_df["frequency_pct"]],
            textposition="outside",
            textfont=dict(color="#171c1f", size=11),
        ))
        fig_trend.update_layout(
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#f8fafc",
            font=dict(color="#171c1f", size=11, family="Inter"),
            xaxis=dict(
                range=[0, 118],
                gridcolor="#e2e8f0",
                title="% of companies asking for this skill",
                color="#515f74",
            ),
            yaxis=dict(
                gridcolor="#e2e8f0",
                autorange="reversed",
                color="#171c1f",
            ),
            margin=dict(l=10, r=60, t=16, b=16),
            height=460,
        )
        st.plotly_chart(fig_trend, use_container_width=True)

        # Summary counts
        have_count    = int(track_skills_df["have_it"].sum())
        missing_count = len(track_skills_df) - have_count

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="sd-metric">
                <div class="sd-metric-label">Skills Shown</div>
                <div class="sd-metric-value" style="color:#171c1f;">{len(track_skills_df)}</div>
                <div class="sd-metric-sub">top skills for this track</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="sd-metric">
                <div class="sd-metric-label">You Already Have</div>
                <div class="sd-metric-value" style="color:#15803d;">{have_count}</div>
                <div class="sd-metric-sub">of these skills</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="sd-metric">
                <div class="sd-metric-label">You Are Missing</div>
                <div class="sd-metric-value" style="color:#ba1a1a;">{missing_count}</div>
                <div class="sd-metric-sub">skills to add</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;
                    padding:12px 16px;margin-top:16px;">
            <div style="font-size:0.8rem;color:#515f74;line-height:1.6;">
                <strong style="color:#171c1f;">Where does this data come from?</strong><br>
                Skills are extracted from 1,600 real Indian job descriptions scraped from Naukri.com
                and processed using NLP frequency analysis. The percentage shows how often each skill
                appears across all job postings for that role.
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:1.5rem 0;'>",
            unsafe_allow_html=True)

col_prev, col_next = st.columns(2)
with col_prev:
    if st.button("Back — Placement Odds", use_container_width=True):
        st.switch_page("pages/07_peer_mirror.py")
with col_next:
    if st.button("Next — My Report Card", type="primary", use_container_width=True):
        st.switch_page("pages/10_final_report.py")