# session_store.py
# =============================================================
# Persistent session storage that survives page refreshes.
#
# Streamlit's session_state is in-memory and is wiped on a hard
# browser refresh. We work around that by:
#   1. Generating a UUID session_id and putting it in the URL
#      query params (?sid=...). The browser keeps URL params
#      across refreshes for free.
#   2. Persisting a whitelist of session_state keys to a JSON
#      file on disk, keyed by that session_id.
#   3. On every page load, calling init_session() which restores
#      missing keys from the file before any page logic runs.
#
# Session lives until the user clicks Sign Out (which calls
# clear_session()) — refresh, re-open tab, even close+reopen
# the app all keep the session alive.
# =============================================================

import json
import os
import time
import uuid
from pathlib import Path

import streamlit as st


# Directory where session blobs live. Survives across runs.
_SESS_DIR = Path(__file__).parent / "data" / "sessions"
_SESS_DIR.mkdir(parents=True, exist_ok=True)

# Sessions older than this are garbage-collected on next access.
# 7 days is generous for an exam workflow.
_MAX_AGE_SECONDS = 7 * 24 * 3600

# Keys we persist. Anything not in this list is treated as
# transient (UI flags, internal counters, large blobs we don't
# want on disk like Gemini clients, etc.)
_PERSIST_KEYS = [
    # User identity / inputs
    "student_name",
    "semester",
    "selected_skills",
    "session_start",

    # Quiz state
    "quiz_data",
    "quiz_data_sig",
    "quiz_started",
    "quiz_complete",
    "quiz_terminated",
    "quiz_results",
    "verified_skills",

    # Proctor counters mirrored from the python-side proctor
    # module (so a refresh doesn't reset the violation count
    # on the displayed score but the underlying webrtc state
    # naturally resets — that's fine, we only persist what
    # the user has seen).
    "proctor_violations",
    "proctor_warning_message",
    "proctor_last_warning_at",

    # Computed dashboard data
    "drift_score", "drift_label", "track_counts",
    "entropy_score", "entropy_label",
    "career_matches", "best_track", "match_pct",
    "readiness_score", "next_skill_info", "urgency_info",
    "focus_debt_info", "peer_info",

    # Quiz answer keys (q_X_Y) are added dynamically below.

    # Faculty
    "faculty_logged_in", "faculty_name",
]


def _session_file(sid: str) -> Path:
    return _SESS_DIR / f"{sid}.json"


def _gc_old():
    """Best-effort cleanup of sessions older than MAX_AGE_SECONDS."""
    now = time.time()
    try:
        for f in _SESS_DIR.glob("*.json"):
            try:
                if now - f.stat().st_mtime > _MAX_AGE_SECONDS:
                    f.unlink(missing_ok=True)
            except Exception:
                pass
    except Exception:
        pass


def _load_from_disk(sid: str) -> dict:
    f = _session_file(sid)
    if not f.exists():
        return {}
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_to_disk(sid: str, data: dict) -> None:
    try:
        tmp = _session_file(sid).with_suffix(".tmp")
        tmp.write_text(json.dumps(data, default=str), encoding="utf-8")
        tmp.replace(_session_file(sid))
    except Exception:
        # Persistence is best-effort. We never want disk errors
        # to crash the UI.
        pass


def _delete_disk(sid: str) -> None:
    try:
        _session_file(sid).unlink(missing_ok=True)
    except Exception:
        pass


def _get_or_create_sid() -> str:
    """Return a stable session_id, creating one in the URL if needed."""
    # 1. Already in session_state? use it.
    sid = st.session_state.get("_sid")
    if sid:
        # Make sure it's reflected in the URL (in case the URL was
        # navigated to without ?sid=)
        try:
            qp = st.query_params
            if qp.get("sid") != sid:
                qp["sid"] = sid
        except Exception:
            pass
        return sid

    # 2. Try the URL query params.
    try:
        sid = st.query_params.get("sid")
    except Exception:
        sid = None

    # 3. Otherwise mint a new one and write it to the URL so a
    #    browser refresh keeps it.
    if not sid:
        sid = uuid.uuid4().hex
        try:
            st.query_params["sid"] = sid
        except Exception:
            pass

    st.session_state["_sid"] = sid
    return sid


def init_session():
    """Call at the top of every page (after st.set_page_config).

    1. Ensures we have a stable session_id in the URL.
    2. Restores persisted keys from disk into st.session_state
       if they're not already populated.
    3. Sets up sane defaults for keys the rest of the app
       expects to exist.
    """
    _gc_old()
    sid = _get_or_create_sid()
    persisted = _load_from_disk(sid)

    # Restore everything we have on disk. We don't overwrite
    # values already set in this run (in case the page set
    # something before init was called).
    for k, v in persisted.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # Defaults — only set if missing.
    defaults = {
        "student_name":       None,
        "semester":           None,
        "selected_skills":    {},
        "verified_skills":    {},
        "quiz_results":       [],
        "quiz_complete":      False,
        "quiz_terminated":    False,
        "quiz_started":       False,
        "drift_score":        None,
        "drift_label":        None,
        "track_counts":       None,
        "entropy_score":      None,
        "entropy_label":      None,
        "career_matches":     None,
        "best_track":         None,
        "match_pct":          None,
        "readiness_score":    None,
        "next_skill_info":    None,
        "urgency_info":       None,
        "focus_debt_info":    None,
        "peer_info":          None,
        "session_start":      None,
        "faculty_logged_in":  False,
        "faculty_name":       None,
        "proctor_violations":     0,
        "proctor_warning_message": "",
        "proctor_last_warning_at": 0.0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def save_session():
    """Persist the whitelisted keys to disk for the current sid."""
    sid = st.session_state.get("_sid")
    if not sid:
        return

    blob = {}
    # Whitelisted top-level keys
    for k in _PERSIST_KEYS:
        if k in st.session_state:
            try:
                json.dumps(st.session_state[k], default=str)
                blob[k] = st.session_state[k]
            except Exception:
                # Skip un-serializable objects (e.g. live clients)
                pass

    # Persist all q_X_Y answer keys so a refresh mid-quiz
    # doesn't lose answered radio buttons.
    for k in list(st.session_state.keys()):
        if isinstance(k, str) and k.startswith("q_"):
            try:
                json.dumps(st.session_state[k], default=str)
                blob[k] = st.session_state[k]
            except Exception:
                pass

    _save_to_disk(sid, blob)


def clear_session():
    """Wipe persisted state and the in-memory session_state.

    Called on Sign Out. The next page load will mint a fresh sid.
    """
    sid = st.session_state.get("_sid")
    if sid:
        _delete_disk(sid)

    for k in list(st.session_state.keys()):
        try:
            del st.session_state[k]
        except Exception:
            pass

    try:
        # Clear the URL ?sid= so the user truly starts fresh.
        st.query_params.clear()
    except Exception:
        pass
