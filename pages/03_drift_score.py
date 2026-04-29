# pages/03_drift_score.py
# =============================================================
# Dashboard — first page after quiz completion.
# =============================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from session_store import init_session, clear_session
from brain import CAREER_TRACKS
from _sidebar import APPLE_CSS, render_sidebar

st.set_page_config(
    page_title="SkillDrift - Dashboard",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session()

st.session_state["_current_page"] = "drift"
st.markdown(APPLE_CSS, unsafe_allow_html=True)
render_sidebar()

if not st.session_state.get("student_name"):
    st.warning("Session not found. Please start from the beginning.")
    st.stop()

drift_score     = st.session_state.get("drift_score")   or 0
drift_label     = st.session_state.get("drift_label")   or ""
entropy_score   = st.session_state.get("entropy_score") or 0
entropy_label   = st.session_state.get("entropy_label") or ""
track_counts    = st.session_state.get("track_counts")  or {}
verified_skills = st.session_state.get("verified_skills", {})
quiz_results    = st.session_state.get("quiz_results", [])

if not verified_skills and not quiz_results:
    st.warning("No verified skills found. Please complete the quiz first.")
    st.stop()

# If quiz done but ALL skills failed, fall back to claimed skills for display
if quiz_results and not verified_skills:
    for r in quiz_results:
        verified_skills[r["skill"]] = r["claimed_level"]


# =============================================================
# FAILURE GATE
# =============================================================

semester_val = st.session_state.get("semester", 0)
try:
    sem_int = int(str(semester_val).split()[0]) if semester_val else 0
except Exception:
    sem_int = 0

# Count truly_verified using ACCURATE rule:
# Confirmed always counts.
# Borderline + Beginner claimed = counts (honest claim, showed something).
# Borderline + Intermediate/Advanced claimed = does NOT count (overclaimed).
# Not Verified = never counts.
total_claimed = len(quiz_results)

truly_verified = 0
for r in quiz_results:
    status  = r.get("status", "")
    claimed = r.get("claimed_level", "")
    if status == "Confirmed":
        truly_verified += 1
    elif status == "Borderline" and claimed == "Beginner":
        truly_verified += 1
    # Borderline + Intermediate/Advanced = 0 (did not earn it)

# Display count for UI (Confirmed + any Borderline shown in table)
truly_verified_display = sum(
    1 for r in quiz_results
    if r.get("status") in ("Confirmed", "Borderline")
)

# Beginner (sem 1-2): need 2+; Intermediate/Advanced (sem 3-8): need 3+
min_required = 2 if sem_int <= 2 else 3

quiz_done = st.session_state.get("quiz_complete", False)

# 5+ skills with 4+ truly_verified: proceed normally
enough_of_many = (total_claimed >= 5 and truly_verified >= 4)
gate_passed = (not quiz_done) or (truly_verified >= min_required) or enough_of_many

if quiz_done and not gate_passed:
    # ── FAILURE SCREEN ────────────────────────────────────────────────
    student_name = st.session_state.get("student_name", "")
    level_label  = "Beginner" if sem_int <= 2 else "Intermediate/Advanced"

    st.markdown(f"""
<div style="margin-bottom:24px;">
    <div style="font-family:'Manrope',sans-serif;font-size:1.5rem;font-weight:800;color:#171c1f;">
        Dashboard
    </div>
    <div style="font-size:0.875rem;color:#515f74;margin-top:5px;">
        Skill verification results for {student_name}.
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown(f"""
<div style="background:#fff5f5;border:1.5px solid #fca5a5;border-radius:14px;
            padding:32px 36px;margin-bottom:28px;text-align:center;">
    <div style="font-family:'Manrope',sans-serif;font-size:1.4rem;font-weight:800;
                color:#ba1a1a;margin-bottom:10px;">Verification Not Passed</div>
    <div style="font-size:0.95rem;color:#515f74;line-height:1.65;max-width:520px;margin:0 auto;">
        You passed <strong>{truly_verified} of {total_claimed}</strong> skills at the required standard.
        {level_label} students need at least <strong>{min_required} skills confirmed</strong> to access the full dashboard.
        Borderline on Intermediate or Advanced level does not count — you need 2/3 or 3/3 correct.
        Retake the quiz to unlock all pages.
    </div>
</div>
""", unsafe_allow_html=True)

    # Per-skill results table
    st.markdown("""
<div style="font-family:'Manrope',sans-serif;font-size:1rem;font-weight:700;
            color:#171c1f;margin:0 0 12px 0;">Per-Skill Results</div>
""", unsafe_allow_html=True)

    if quiz_results:
        rows = []
        for r in quiz_results:
            correct = int(r.get("correct_count", 0))
            total   = int(r.get("total_questions", 0))
            score_str = f"{correct}/{total}" if total > 0 else "-"
            rows.append({
                "Skill":         r.get("skill", ""),
                "Claimed Level": r.get("claimed_level", ""),
                "Score":         score_str,
                "Needed to Pass": "2/3 minimum",
                "Status":        r.get("status", ""),
            })
        df_fail = pd.DataFrame(rows)

        def _style_status_fail(val: str):
            if val == "Confirmed":    return "color: #15803d; font-weight: 700;"
            if val == "Borderline":   return "color: #d97706; font-weight: 700;"
            if val == "Not Verified": return "color: #ba1a1a; font-weight: 700;"
            return ""

        styled_fail = df_fail.style.map(_style_status_fail, subset=["Status"])
        st.dataframe(styled_fail, use_container_width=True, hide_index=True)

    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    if st.button("Start Quiz Again", type="primary"):
        clear_session()
        st.switch_page("pages/01_home.py")

    st.stop()


# =============================================================
# FINAL SCORE
# =============================================================

total_correct   = sum(int(r.get("correct_count", 0))   for r in quiz_results)
total_questions = sum(int(r.get("total_questions", 0)) for r in quiz_results)
final_pct = round((total_correct / total_questions) * 100, 1) if total_questions else 0.0

if   final_pct >= 70: score_label, score_color = "Strong",     "#15803d"
elif final_pct >= 40: score_label, score_color = "Borderline", "#d97706"
else:                 score_label, score_color = "Needs Work", "#ba1a1a"

not_verified_count = total_claimed - truly_verified


# =============================================================
# PAGE TITLE
# =============================================================

st.markdown(f"""
<div style="margin-bottom:24px;">
    <div style="font-family:'Manrope',sans-serif;font-size:1.5rem;font-weight:800;color:#171c1f;">
        Dashboard
    </div>
    <div style="font-size:0.875rem;color:#515f74;margin-top:5px;">
        Skill verification and analytics for {st.session_state.get('student_name','')}.
    </div>
</div>
""", unsafe_allow_html=True)


# =============================================================
# FINAL SCORE CARD
# =============================================================

st.markdown(f"""
<div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:14px;
            padding:28px 32px;margin-bottom:24px;
            border-top:4px solid {score_color};
            display:flex;align-items:center;justify-content:space-between;
            flex-wrap:wrap;gap:16px;">
  <div>
    <div style="font-size:0.78rem;font-weight:700;color:#515f74;
                text-transform:uppercase;letter-spacing:0.06em;">Final Score</div>
    <div style="font-family:'Manrope',sans-serif;font-size:2.6rem;font-weight:800;
                color:{score_color};line-height:1.1;margin-top:6px;">{final_pct}%</div>
    <div style="font-size:0.85rem;color:#515f74;margin-top:4px;">
      Based on {total_questions} question{'s' if total_questions != 1 else ''}
      across {len(quiz_results)} skill{'s' if len(quiz_results) != 1 else ''}.
    </div>
  </div>
  <div style="text-align:right;">
    <div style="font-size:0.78rem;font-weight:700;color:#515f74;
                text-transform:uppercase;letter-spacing:0.06em;">Evaluation</div>
    <div style="font-family:'Manrope',sans-serif;font-size:1.4rem;font-weight:800;
                color:{score_color};margin-top:6px;">{score_label}</div>
    <div style="font-size:0.82rem;color:#515f74;margin-top:4px;">
      Verified skills: <b>{truly_verified_display}</b> of {total_claimed} passed
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# =============================================================
# SKILL EVALUATION
# =============================================================

st.markdown("""
<div style="font-family:'Manrope',sans-serif;font-size:1.05rem;font-weight:700;
            color:#171c1f;margin:8px 0 6px 0;">Skill Evaluation</div>
<div style="font-size:0.86rem;color:#515f74;margin-bottom:14px;">
    Status of each skill you claimed.
</div>
""", unsafe_allow_html=True)

if quiz_results:
    rows = []
    for r in quiz_results:
        correct = int(r.get("correct_count", 0))
        total   = int(r.get("total_questions", 0))
        score_str = f"{correct}/{total}" if total > 0 else "-"
        rows.append({
            "Skill":          r.get("skill", ""),
            "Claimed Level":  r.get("claimed_level", ""),
            "Score":          score_str,
            "Verified Level": r.get("verified_level", ""),
            "Status":         r.get("status", ""),
        })
    df = pd.DataFrame(rows)

    def style_status(val: str):
        if val == "Confirmed":    return "color: #15803d; font-weight: 700;"
        if val == "Borderline":   return "color: #d97706; font-weight: 700;"
        if val == "Not Verified": return "color: #ba1a1a; font-weight: 700;"
        if val == "Unverified":   return "color: #94a3b8;"
        return ""

    def style_score(val: str):
        if "/" not in val:
            return ""
        parts = val.split("/")
        try:
            c, t = int(parts[0]), int(parts[1])
            ratio = c / t if t > 0 else 0
            if ratio >= 0.67:   return "color: #15803d; font-weight: 700;"
            elif ratio >= 0.34: return "color: #d97706; font-weight: 700;"
            else:               return "color: #ba1a1a; font-weight: 700;"
        except Exception:
            return ""

    styled = df.style.map(style_status, subset=["Status"]).map(style_score, subset=["Score"])
    st.dataframe(styled, use_container_width=True, hide_index=True)

    st.markdown("""
    <div style="font-size:0.82rem;color:#515f74;background:#f6fafe;border-radius:8px;
                padding:10px 14px;border-left:3px solid #002c98;margin-top:8px;line-height:1.6;">
        <b>How scoring works:</b> Each skill has 3 questions.
        <span style="color:#15803d;font-weight:700;">2/3 or 3/3 = Confirmed</span> &nbsp;|&nbsp;
        <span style="color:#d97706;font-weight:700;">1/3 = Borderline</span> (level downgraded) &nbsp;|&nbsp;
        <span style="color:#ba1a1a;font-weight:700;">0/3 = Not Verified</span> (excluded from analysis)
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("No skill evaluation data available.")

st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:28px 0;'>", unsafe_allow_html=True)


# =============================================================
# DRIFT + ENTROPY CARDS
# =============================================================

st.markdown("""
<div style="font-family:'Manrope',sans-serif;font-size:1.05rem;font-weight:700;
            color:#171c1f;margin:0 0 14px 0;">
    Drift Score and Entropy Score
</div>
""", unsafe_allow_html=True)

drift_color = (
    "#15803d" if drift_score <= 20
    else "#d97706" if drift_score <= 60
    else "#ba1a1a"
)
entropy_color = (
    "#15803d" if entropy_score < 1.2
    else "#d97706" if entropy_score < 2.0
    else "#ba1a1a"
)

c1, c2, c3 = st.columns(3, gap="medium")

with c1:
    st.markdown(f"""
    <div class="sd-metric" style="border-top:3px solid {drift_color};">
        <div class="sd-metric-label">Drift Score</div>
        <div class="sd-metric-value" style="color:{drift_color};">{drift_score}</div>
        <div style="font-size:0.9rem;font-weight:700;color:#171c1f;margin-top:8px;">{drift_label}</div>
        <div class="sd-metric-sub">0 = Focused &nbsp;|&nbsp; 100 = Scattered</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="sd-metric" style="border-top:3px solid {entropy_color};">
        <div class="sd-metric-label">Entropy Score</div>
        <div class="sd-metric-value" style="color:{entropy_color};">{entropy_score}</div>
        <div style="font-size:0.9rem;font-weight:700;color:#171c1f;margin-top:8px;">{entropy_label}</div>
        <div class="sd-metric-sub">0 bits = Focused &nbsp;|&nbsp; 3 bits = Max Scatter</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="sd-metric" style="border-top:3px solid #002c98;">
        <div class="sd-metric-label">Verified Skills</div>
        <div class="sd-metric-value" style="color:#002c98;">{truly_verified_display}</div>
        <div style="font-size:0.9rem;font-weight:700;color:#171c1f;margin-top:8px;">of {total_claimed} claimed</div>
        <div class="sd-metric-sub" style="color:#ba1a1a;">{total_claimed - truly_verified_display} not verified</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)


# =============================================================
# INTERPRETATION — short plain English only
# =============================================================

if drift_score <= 20:
    drift_interpretation = "Your skills are concentrated in very few tracks. This is the ideal pattern."
elif drift_score <= 40:
    drift_interpretation = "Mostly concentrated with some spread. Manageable if you stay focused."
elif drift_score <= 60:
    drift_interpretation = "Visible spread across multiple tracks. Needs correction before placement season."
else:
    drift_interpretation = "Broadly scattered across many unrelated tracks. This is a placement risk."

ca, cb = st.columns(2, gap="large")

with ca:
    st.markdown(f"""
    <div class="sd-card">
        <div style="font-family:'Manrope',sans-serif;font-size:1rem;font-weight:700;color:#171c1f;margin-bottom:12px;">
            Drift Score
        </div>
        <div style="font-size:0.9rem;color:#171c1f;line-height:1.7;">
            Measures how unevenly your verified skills are distributed across 8 CSE career tracks.<br><br>
            <strong>Low score (near 0)</strong> — skills concentrated in one track. Focused.<br>
            <strong>High score (near 100)</strong> — skills spread across many tracks. Scattered.
        </div>
        <div style="background:#f6fafe;border-radius:8px;padding:12px 14px;
                    border-left:3px solid {drift_color};margin-top:16px;
                    font-size:0.88rem;color:#515f74;line-height:1.55;">
            {drift_interpretation}
        </div>
    </div>
    """, unsafe_allow_html=True)

with cb:
    st.markdown(f"""
    <div class="sd-card">
        <div style="font-family:'Manrope',sans-serif;font-size:1rem;font-weight:700;color:#171c1f;margin-bottom:12px;">
            Entropy Score
        </div>
        <div style="font-size:0.9rem;color:#171c1f;line-height:1.7;">
            Measures how many career tracks your skills touch, regardless of which one leads.<br><br>
            <strong>0 bits</strong> — all skills in one track.<br>
            <strong>3 bits</strong> — skills spread equally across all 8 tracks.<br><br>
            Your current score is <strong>{entropy_score} bits</strong>.<br><br>
            {
                "You are well-ordered. Keep adding skills in your primary track to maintain this."
                if entropy_score < 0.9 else
                "Reasonably ordered. A few more focused skills will bring this closer to zero."
                if entropy_score < 1.8 else
                "Your skills are spreading across too many tracks. Focus on one domain."
                if entropy_score < 2.4 else
                "High disorder. Your skills are scattered across almost all tracks. Pick one track and go deep."
            }
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:28px 0;'>", unsafe_allow_html=True)


# =============================================================
# TRACK BREAKDOWN
# =============================================================

st.markdown("""
<div style="font-family:'Manrope',sans-serif;font-size:1rem;font-weight:700;color:#171c1f;margin-bottom:5px;">
    Your Skills Across All 8 Career Tracks
</div>
<div style="font-size:0.875rem;color:#515f74;margin-bottom:16px;">
    More skills in one track = less drift = better placement readiness.
</div>
""", unsafe_allow_html=True)

total_skill_count = max(len(verified_skills), 1)

if track_counts:
    track_df = pd.DataFrame([
        {
            "Career Track":     track,
            "Skills You Have":  int(count) if count == int(count) else round(count, 1),
            "Share of Profile": f"{round(count / total_skill_count * 100, 1)}%",
            "Focus Signal":     (
                "Primary Track" if count == max(track_counts.values()) and count > 0
                else "Secondary" if count > 0
                else "None"
            ),
        }
        for track, count in track_counts.items()
    ])

    if not track_df.empty:
        track_df = track_df.sort_values("Skills You Have", ascending=False).reset_index(drop=True)

    # Bar chart — ascending order (highest at top), color gradient by value, hover tooltips
    chart_df = track_df[track_df["Skills You Have"] > 0].copy()
    if not chart_df.empty:
        # Sort ascending so highest bar is at the TOP (plotly renders bottom-up)
        chart_df = chart_df.sort_values("Skills You Have", ascending=True)
        max_val = chart_df["Skills You Have"].max()
        min_val = chart_df["Skills You Have"].min()

        # Color scale: darker blue = more skills, lighter = fewer
        def _bar_color(v):
            if v == max_val:
                return "#002c98"   # primary — darkest blue
            elif max_val > min_val:
                ratio = (v - min_val) / (max_val - min_val)
                if ratio >= 0.6:
                    return "#1a52c9"   # strong blue
                elif ratio >= 0.3:
                    return "#6b8fd6"   # mid blue
                else:
                    return "#c2cef0"   # lightest blue
            return "#c2cef0"

        bar_colors = [_bar_color(v) for v in chart_df["Skills You Have"]]

        # Clean integer display — no .000000
        skill_vals = chart_df["Skills You Have"].tolist()
        text_labels = [str(int(v)) if v == int(v) else str(round(v, 1)) for v in skill_vals]

        # Hover tooltip
        hover_texts = [
            f"<b>{row['Career Track']}</b><br>"
            f"Skills: {int(row['Skills You Have']) if row['Skills You Have'] == int(row['Skills You Have']) else round(row['Skills You Have'], 1)}<br>"
            f"Share: {row['Share of Profile']}<br>"
            f"Signal: {row['Focus Signal']}"
            for _, row in chart_df.iterrows()
        ]

        fig_track = go.Figure(go.Bar(
            x=skill_vals,
            y=chart_df["Career Track"].tolist(),
            orientation="h",
            marker_color=bar_colors,
            marker=dict(
                color=bar_colors,
                line=dict(color="rgba(0,0,0,0.05)", width=1),
            ),
            text=text_labels,
            textposition="inside",
            textfont=dict(color="#ffffff", size=12, family="Inter"),
            hovertext=hover_texts,
            hoverinfo="text",
        ))
        fig_track.update_layout(
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#f8fafc",
            font=dict(color="#171c1f", size=11, family="Inter"),
            xaxis=dict(
                gridcolor="#e2e8f0",
                title="Skills You Have",
                color="#515f74",
                tickformat="d",
                dtick=1,
            ),
            yaxis=dict(
                gridcolor="#e2e8f0",
                color="#171c1f",
                tickfont=dict(size=12),
            ),
            margin=dict(l=10, r=20, t=16, b=10),
            height=max(220, len(chart_df) * 44),
            showlegend=False,
            hoverlabel=dict(
                bgcolor="#171c1f",
                font_size=12,
                font_family="Inter",
                font_color="#ffffff",
                bordercolor="#002c98",
            ),
        )
        st.plotly_chart(fig_track, use_container_width=True)

    def color_focus(val):
        if val == "Primary Track":
            return "color: #002c98; font-weight: 700"
        elif val == "Secondary":
            return "color: #d97706"
        return "color: #94a3b8"

    styled_track = track_df.style.map(color_focus, subset=["Focus Signal"])
    st.dataframe(styled_track, use_container_width=True, hide_index=True)
else:
    st.info("No track data available. Please complete the quiz first.")

st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:28px 0;'>", unsafe_allow_html=True)


# =============================================================
# NAV
# =============================================================

col_nav1, col_nav2 = st.columns(2)
with col_nav2:
    if st.button("Next - Urgency Engine", type="primary", use_container_width=True):
        st.switch_page("pages/04_urgency.py")