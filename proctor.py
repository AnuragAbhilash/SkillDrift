"""
Proctoring module for SkillDrift quiz.

Uses streamlit-webrtc for live camera + server-side face detection.
Face-missing and tab-switch violations are accumulated in module-level
shared state (thread-safe). The quiz page polls this state on rerun
(triggered by streamlit-autorefresh) to enforce the 3-violation limit.

This is the standard pattern recommended in the streamlit-webrtc docs.
No fragile cross-origin URL hacks, no postMessage tricks.
"""

import threading
import time
from collections import deque

import av
import cv2
import numpy as np
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode


# Module-level shared state (one per python process / streamlit session)
# A real production system would scope this per-session via st.session_state,
# but the WebRTC callback runs in a separate thread that cannot read
# st.session_state safely. The module-level pattern is what the official
# tutorial recommends.
_LOCK = threading.Lock()
_STATE = {
    "no_face_seconds": 0.0,    # cumulative seconds without a detected face
    "no_face_streak":  0.0,    # current consecutive seconds without face
    "last_frame_time": None,
    "violations":      0,
    "last_violation_at": 0.0,
    "face_present":    True,
    "running":         False,
}

# How many consecutive seconds without a face counts as 1 violation
NO_FACE_VIOLATION_SECONDS = 8.0
# Cooldown between consecutive face-missing violations
VIOLATION_COOLDOWN_SECONDS = 5.0


# Load the Haar cascade once (it ships with opencv-python)
_FACE_CASCADE = None
def _get_face_cascade():
    global _FACE_CASCADE
    if _FACE_CASCADE is None:
        path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        _FACE_CASCADE = cv2.CascadeClassifier(path)
    return _FACE_CASCADE


def reset_proctor_state():
    """Wipe shared state. Called when starting a fresh quiz."""
    with _LOCK:
        _STATE["no_face_seconds"]    = 0.0
        _STATE["no_face_streak"]     = 0.0
        _STATE["last_frame_time"]    = None
        _STATE["violations"]         = 0
        _STATE["last_violation_at"]  = 0.0
        _STATE["face_present"]       = True
        _STATE["running"]            = False


def get_proctor_snapshot() -> dict:
    """Return a thread-safe snapshot of current proctor state."""
    with _LOCK:
        return dict(_STATE)


def add_tab_switch_violation():
    """Called by the page when a tab-switch is detected via JS bridge."""
    with _LOCK:
        _STATE["violations"] += 1
        _STATE["last_violation_at"] = time.time()


def _video_frame_callback(frame):
    """Runs in WebRTC's worker thread. Detect face presence per frame."""
    img = frame.to_ndarray(format="bgr24")
    now = time.time()

    cascade = _get_face_cascade()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # downscale for speed
    small = cv2.resize(gray, (320, 240))
    faces = cascade.detectMultiScale(
        small, scaleFactor=1.2, minNeighbors=4, minSize=(40, 40)
    )
    face_count = len(faces) if faces is not None else 0

    with _LOCK:
        last = _STATE["last_frame_time"]
        dt = (now - last) if last else 0.0
        if dt < 0 or dt > 5:
            dt = 0.0
        _STATE["last_frame_time"] = now
        _STATE["running"] = True

        if face_count > 0:
            _STATE["face_present"] = True
            _STATE["no_face_streak"] = 0.0
        else:
            _STATE["face_present"] = False
            _STATE["no_face_streak"] += dt
            _STATE["no_face_seconds"] += dt
            # Trigger a violation if face has been missing too long
            if (
                _STATE["no_face_streak"] >= NO_FACE_VIOLATION_SECONDS
                and (now - _STATE["last_violation_at"]) >= VIOLATION_COOLDOWN_SECONDS
            ):
                _STATE["violations"] += 1
                _STATE["last_violation_at"] = now
                _STATE["no_face_streak"] = 0.0  # reset streak after counting

    # Draw rectangles on the live feed for student feedback
    if face_count > 0:
        scale_x = img.shape[1] / 320.0
        scale_y = img.shape[0] / 240.0
        for (x, y, w, h) in faces:
            x1 = int(x * scale_x)
            y1 = int(y * scale_y)
            x2 = int((x + w) * scale_x)
            y2 = int((y + h) * scale_y)
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            img, "FACE OK", (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2,
        )
    else:
        cv2.putText(
            img, "NO FACE", (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2,
        )

    return av.VideoFrame.from_ndarray(img, format="bgr24")


def render_proctor_camera(key: str = "skilldrift-proctor"):
    """
    Render the WebRTC camera widget with face detection.
    Returns the WebRTC context. Caller should check ctx.state.playing.
    """
    return webrtc_streamer(
        key=key,
        mode=WebRtcMode.SENDRECV,
        media_stream_constraints={"video": True, "audio": False},
        video_frame_callback=_video_frame_callback,
        async_processing=True,
        rtc_configuration={
            "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
        },
    )
