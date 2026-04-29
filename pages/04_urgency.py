# pages/04_urgency.py

import streamlit as st
import streamlit.components.v1 as components
from session_store import init_session
from _sidebar import APPLE_CSS, render_sidebar

st.set_page_config(
    page_title="SkillDrift — Time Left",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session()
st.session_state["_current_page"] = "urgency"
st.markdown(APPLE_CSS, unsafe_allow_html=True)
render_sidebar()

if not st.session_state.get("student_name"):
    st.warning("Session not found. Please start from the beginning.")
    st.switch_page("pages/02_skill_input.py")
    st.stop()

urgency_info = st.session_state.get("urgency_info", {})
semester     = st.session_state.get("semester", 4)
best_track   = st.session_state.get("best_track", "your best matching track")

if not urgency_info:
    st.warning("Data not found. Please complete the quiz first.")
    st.stop()

urgency_level   = urgency_info.get("urgency_level", "Red")
urgency_message = urgency_info.get("urgency_message", "")
weeks_remaining = urgency_info.get("weeks_remaining", 0)

URGENCY_COLOR_MAP = {"Green": "#15803d", "Yellow": "#d97706", "Red": "#ba1a1a"}
URGENCY_BG_MAP    = {"Green": "#f0fdf4", "Yellow": "#fffbeb", "Red": "#fff5f5"}
urgency_color = URGENCY_COLOR_MAP.get(urgency_level, "#ba1a1a")
urgency_bg    = URGENCY_BG_MAP.get(urgency_level, "#fff5f5")
level_labels  = {
    "Green":  "You Have Time — Stay Focused",
    "Yellow": "Time is Getting Short",
    "Red":    "High Alert — Act Now",
}
level_display = level_labels.get(urgency_level, urgency_level)

# ── Page Title ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:28px;">
    <div style="font-family:'Manrope',sans-serif;font-size:1.5rem;font-weight:800;color:#171c1f;">
        Time Left
    </div>
    <div style="font-size:0.875rem;color:#515f74;margin-top:5px;">
        How much time you have before placement season. Use it well.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Status Banner ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:{urgency_bg};border:1.5px solid {urgency_color};
            border-left:6px solid {urgency_color};
            border-radius:12px;padding:20px 24px;margin-bottom:28px;">
    <div style="font-family:'Manrope',sans-serif;font-size:1rem;font-weight:800;
                color:{urgency_color};margin-bottom:6px;">
        {level_display}
    </div>
    <div style="font-size:0.9rem;color:#171c1f;line-height:1.65;">
        {urgency_message}
    </div>
</div>
""", unsafe_allow_html=True)

# ── Two Metric Cards ────────────────────────────────────────────────────────────
c1, c2 = st.columns(2, gap="medium")

with c1:
    st.markdown(f"""
    <div class="sd-metric">
        <div class="sd-metric-label">Your Current Semester</div>
        <div class="sd-metric-value" style="color:#002c98;">{semester}</div>
        <div class="sd-metric-sub">out of 8 semesters total</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    if semester >= 7:
        countdown_text = "Now"
        countdown_sub  = "Placement season is active — interviews are happening"
    else:
        countdown_text = str(weeks_remaining)
        countdown_sub  = "weeks left until Semester 7 placements begin"

    st.markdown(f"""
    <div class="sd-metric">
        <div class="sd-metric-label">Time Remaining</div>
        <div class="sd-metric-value" style="color:{urgency_color};">{countdown_text}</div>
        <div class="sd-metric-sub">{countdown_sub}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)

# ── Semester Timeline — rendered via components.html to avoid Streamlit markdown escaping ──
st.markdown("""
<div style="font-family:'Manrope',sans-serif;font-size:1rem;font-weight:700;
            color:#171c1f;margin-bottom:12px;">
    Where You Are in Your Degree
</div>
""", unsafe_allow_html=True)

semesters_total = 8
placement_start = 7

# Build each dot + connector as a plain string — no f-string loops inside st.markdown
dot_items = []
for i in range(1, semesters_total + 1):
    is_current   = (i == semester)
    is_past      = (i < semester)
    is_placement = (i >= placement_start)
    is_last      = (i == semesters_total)

    if is_current:
        dot_bg     = urgency_color
        lbl_color  = urgency_color
        lbl_wt     = "800"
        shadow     = f"0 0 0 6px {urgency_color}28"
        dot_size   = "42"
        inner_fs   = "16"
    elif is_past:
        dot_bg     = "#94a3b8"
        lbl_color  = "#94a3b8"
        lbl_wt     = "500"
        shadow     = "none"
        dot_size   = "30"
        inner_fs   = "13"
    elif is_placement:
        dot_bg     = "#002c98"
        lbl_color  = "#002c98"
        lbl_wt     = "600"
        shadow     = "none"
        dot_size   = "30"
        inner_fs   = "13"
    else:
        dot_bg     = "#e2e8f0"
        lbl_color  = "#94a3b8"
        lbl_wt     = "500"
        shadow     = "none"
        dot_size   = "30"
        inner_fs   = "13"

    text_color = "#ffffff" if (is_current or is_past or is_placement) else "#94a3b8"

    you_label = (
        f'<div style="font-size:11px;color:{urgency_color};font-weight:800;'
        f'text-align:center;margin-top:4px;">YOU</div>'
        if is_current else '<div style="height:19px;"></div>'
    )
    # No per-dot job label anymore — handled as a banner above the timeline
    job_label = '<div style="height:19px;"></div>'

    dot_html = (
        f'<div style="display:flex;flex-direction:column;align-items:center;flex-shrink:0;">'
        f'  <div style="font-size:11px;color:{lbl_color};font-weight:{lbl_wt};'
        f'              margin-bottom:6px;">Sem {i}</div>'
        f'  <div style="width:{dot_size}px;height:{dot_size}px;border-radius:50%;'
        f'              background:{dot_bg};display:flex;align-items:center;'
        f'              justify-content:center;box-shadow:{shadow};">'
        f'    <span style="color:{text_color};font-size:{inner_fs}px;font-weight:700;">{i}</span>'
        f'  </div>'
        f'  {you_label}'
        f'  {job_label}'
        f'</div>'
    )

    connector_color = "#94a3b8" if i < semester else "#e2e8f0"
    connector_html = (
        f'<div style="flex:1;height:3px;background:{connector_color};'
        f'min-width:10px;margin-bottom:38px;"></div>'
        if not is_last else ""
    )

    dot_items.append(dot_html + connector_html)

dots_joined = "\n".join(dot_items)

timeline_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  body {{ margin:0; padding:0; font-family: 'Inter', sans-serif; background: transparent; }}
</style>
</head>
<body>
<div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:14px;
            padding:20px 28px 16px 28px;">

  <div style="display:flex;justify-content:flex-end;margin-bottom:6px;padding-right:2px;">
    <div style="background:#e8eeff;border:1px solid #002c98;border-radius:6px;
                padding:3px 10px;font-size:11px;font-weight:700;color:#002c98;">
      Campus Placements happen in Sem 7 and 8
    </div>
  </div>

  <div style="display:flex;align-items:center;gap:0;">
    {dots_joined}
  </div>

  <div style="display:flex;gap:20px;margin-top:16px;padding-top:12px;
              border-top:1px solid #f1f5f9;flex-wrap:wrap;">
    <div style="display:flex;align-items:center;gap:6px;">
      <div style="width:11px;height:11px;border-radius:50%;background:#94a3b8;"></div>
      <span style="font-size:12px;color:#515f74;">Done</span>
    </div>
    <div style="display:flex;align-items:center;gap:6px;">
      <div style="width:11px;height:11px;border-radius:50%;background:#e2e8f0;
                  border:1px solid #cbd5e1;"></div>
      <span style="font-size:12px;color:#515f74;">Upcoming</span>
    </div>
    <div style="display:flex;align-items:center;gap:6px;">
      <div style="width:11px;height:11px;border-radius:50%;background:#002c98;"></div>
      <span style="font-size:12px;color:#515f74;">Placement Semesters</span>
    </div>
  </div>
</div>
</body>
</html>
"""

components.html(timeline_html, height=215, scrolling=False)

# ── Plain-language context ──────────────────────────────────────────────────────
semesters_left = max(0, placement_start - semester)

if semester >= 7:
    time_context = (
        "You are in placement season right now. Focus only on what companies are asking for. "
        "Check the Job Market page for current skill demand."
    )
elif semesters_left == 1:
    time_context = (
        f"Only 1 semester left before placements start. This is your last real chance to add skills "
        f"for {best_track}. Be selective — only learn what companies actually need."
    )
else:
    time_context = (
        f"You have {semesters_left} semesters before placements begin. Enough time to build strong "
        f"skills for {best_track} if you start now and stay focused."
    )

st.markdown(f"""
<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;
            padding:16px 20px;margin-top:12px;">
    <div style="font-size:0.9rem;color:#171c1f;line-height:1.7;">{time_context}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:28px 0;'>",
            unsafe_allow_html=True)

col_prev, col_next = st.columns(2)
with col_prev:
    if st.button("Back — Drift Score", use_container_width=True):
        st.switch_page("pages/03_drift_score.py")
with col_next:
    if st.button("Next — Career Track Match", type="primary", use_container_width=True):
        st.switch_page("pages/05_career_match.py")