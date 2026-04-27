"""Proctoring module for SkillDrift quiz.

Tracks face presence, tab switches, and fullscreen exits.
Each violation is recorded with a reason and timestamp. The
quiz page polls get_proctor_snapshot() and shows a warning
overlay until the user acknowledges it. The test terminates
after MAX_VIOLATIONS unique violation events.
"""

import threading
import time

import av
import cv2
from streamlit_webrtc import webrtc_streamer, WebRtcMode


# =============================================================
# CONFIG
# =============================================================

MAX_VIOLATIONS              = 3
NO_FACE_VIOLATION_SECONDS   = 5.0
VIOLATION_COOLDOWN_SECONDS  = 8.0


# =============================================================
# SHARED STATE  (thread-safe between WebRTC callback and main)
# =============================================================

_LOCK = threading.Lock()

_STATE = {
    "no_face_streak":       0.0,
    "no_face_seconds":      0.0,
    "last_frame_time":      None,
    "violations":           0,
    "last_violation_at":    0.0,
    "face_present":         True,
    "running":              False,
    "tab_switches":         0,
    "face_misses":          0,
    "fs_exits":             0,
    "pending_warning":      "",
    "pending_warning_at":   0.0,
    "violation_log":        [],
}

_FACE_CASCADE = None


def _get_face_cascade():
    global _FACE_CASCADE
    if _FACE_CASCADE is None:
        path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        _FACE_CASCADE = cv2.CascadeClassifier(path)
    return _FACE_CASCADE


# =============================================================
# PUBLIC API
# =============================================================

def reset_proctor_state():
    """Wipe all in-memory proctor state."""
    with _LOCK:
        _STATE.update({
            "no_face_streak":       0.0,
            "no_face_seconds":      0.0,
            "last_frame_time":      None,
            "violations":           0,
            "last_violation_at":    0.0,
            "face_present":         True,
            "running":              False,
            "tab_switches":         0,
            "face_misses":          0,
            "fs_exits":             0,
            "pending_warning":      "",
            "pending_warning_at":   0.0,
        })
        _STATE["violation_log"] = []


def get_proctor_snapshot() -> dict:
    """Read-only copy of the current proctor state."""
    with _LOCK:
        snap = dict(_STATE)
        snap["violation_log"] = list(_STATE["violation_log"])
        return snap


def get_max_violations() -> int:
    return MAX_VIOLATIONS


def get_no_face_threshold() -> float:
    return NO_FACE_VIOLATION_SECONDS


def acknowledge_warning():
    """Clear the pending warning and reset the no-face streak."""
    with _LOCK:
        _STATE["pending_warning"]    = ""
        _STATE["pending_warning_at"] = 0.0
        # Reset streak so the timer starts fresh after acknowledging.
        _STATE["no_face_streak"]     = 0.0


def _record_violation(reason: str, counter_key: str):
    """Internal helper — caller must already hold _LOCK."""
    now = time.time()

    # Do not stack a violation on top of an unacknowledged warning.
    if _STATE.get("pending_warning"):
        return

    # Cooldown guard: ignore events within VIOLATION_COOLDOWN_SECONDS.
    if (now - _STATE["last_violation_at"]) < VIOLATION_COOLDOWN_SECONDS:
        return

    _STATE["violations"] += 1
    if counter_key in _STATE:
        _STATE[counter_key] += 1
    _STATE["last_violation_at"] = now

    remaining = max(0, MAX_VIOLATIONS - _STATE["violations"])

    if _STATE["violations"] >= MAX_VIOLATIONS:
        msg = (
            f"Violation {_STATE['violations']} of {MAX_VIOLATIONS}: {reason}. "
            f"You have reached the maximum number of violations. "
            f"The test will be terminated."
        )
    else:
        msg = (
            f"Warning {_STATE['violations']} of {MAX_VIOLATIONS}: {reason}. "
            f"You have {remaining} warning{'s' if remaining != 1 else ''} "
            f"remaining before the test is terminated."
        )

    _STATE["pending_warning"]    = msg
    _STATE["pending_warning_at"] = now
    _STATE["violation_log"].append({"reason": reason, "at": now})


def add_tab_switch_violation():
    with _LOCK:
        _record_violation(
            "you switched away from the test tab or window",
            "tab_switches",
        )


def add_fullscreen_exit_violation():
    with _LOCK:
        _record_violation(
            "you exited fullscreen mode",
            "fs_exits",
        )


# =============================================================
# WEBRTC FRAME CALLBACK
# =============================================================

def _video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")
    now = time.time()

    cascade = _get_face_cascade()
    gray    = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    small   = cv2.resize(gray, (320, 240))
    faces   = cascade.detectMultiScale(
        small,
        scaleFactor=1.15,
        minNeighbors=4,
        minSize=(30, 30),
    )
    face_count = len(faces) if hasattr(faces, "__len__") and len(faces) > 0 else 0

    with _LOCK:
        last = _STATE["last_frame_time"]
        dt   = (now - last) if last else 0.0
        if dt < 0 or dt > 3.0:
            dt = 0.0
        _STATE["last_frame_time"] = now
        _STATE["running"]         = True

        if face_count > 0:
            _STATE["face_present"]   = True
            _STATE["no_face_streak"] = 0.0
        else:
            _STATE["face_present"]    = False
            _STATE["no_face_streak"] += dt
            _STATE["no_face_seconds"] += dt

            if (
                _STATE["no_face_streak"] >= NO_FACE_VIOLATION_SECONDS
                and not _STATE.get("pending_warning")
                and (now - _STATE["last_violation_at"]) >= VIOLATION_COOLDOWN_SECONDS
            ):
                _record_violation(
                    f"your face was not detected for over "
                    f"{int(NO_FACE_VIOLATION_SECONDS)} seconds",
                    "face_misses",
                )
                # Reset streak so the next violation needs a new full window.
                _STATE["no_face_streak"] = 0.0

    h, w = img.shape[:2]
    sx = w / 320.0
    sy = h / 240.0

    if face_count > 0 and hasattr(faces, "__len__"):
        for (x, y, fw, fh) in faces:
            x1 = int(x * sx);  y1 = int(y * sy)
            x2 = int((x + fw) * sx); y2 = int((y + fh) * sy)
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 200, 80), 2)
        cv2.putText(img, "FACE OK", (10, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 200, 80), 2)
    else:
        cv2.putText(img, "NO FACE", (10, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 50, 220), 2)

    return av.VideoFrame.from_ndarray(img, format="bgr24")


# =============================================================
# CAMERA WIDGET
# =============================================================

def render_proctor_camera(key: str = "skilldrift-proctor"):
    """Render the WebRTC camera widget.

    desired_playing_state=True so the camera starts automatically
    without any Start button visible to the user.
    Returns the WebRTC context or None on failure.
    """
    try:
        return webrtc_streamer(
            key=key,
            mode=WebRtcMode.SENDRECV,
            media_stream_constraints={"video": True, "audio": False},
            video_frame_callback=_video_frame_callback,
            async_processing=True,
            desired_playing_state=True,
            rtc_configuration={
                "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
            },
        )
    except AttributeError:
        return None
    except Exception:
        return None
