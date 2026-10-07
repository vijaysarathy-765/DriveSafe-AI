"""
Eye Tracking Module
Landmark-based Eye Aspect Ratio (EAR), blink detection and eye-closure timing.
Uses MediaPipe Face Mesh landmarks. All timing is in seconds (frame-rate independent).
"""
import time
from collections import deque

import numpy as np


def euclidean_distance(point1, point2):
    """Euclidean distance between two points"""
    return float(np.linalg.norm(np.asarray(point1, dtype=float) - np.asarray(point2, dtype=float)))


class EyeTracker:
    def __init__(self, ear_threshold=0.21, closed_seconds=1.5, calibration_seconds=3.0,
                 threshold_ratio=0.75, perclos_window=30.0, blink_min=0.05, blink_max=0.5):
        """
        Args:
            ear_threshold: fallback EAR threshold (used until calibration finishes)
            closed_seconds: eyes closed this long => drowsy
            calibration_seconds: time to measure the driver's open-eye EAR at startup
            threshold_ratio: closed threshold = ratio * open-eye baseline EAR
            perclos_window: sliding window (s) for % of time eyes are closed
            blink_min / blink_max: closure duration range (s) counted as a blink
        """
        self.DEFAULT_EAR_THRESHOLD = ear_threshold
        self.EAR_THRESHOLD = ear_threshold
        self.CLOSED_SECONDS = closed_seconds
        self.CALIBRATION_SECONDS = calibration_seconds
        self.THRESHOLD_RATIO = threshold_ratio
        self.PERCLOS_WINDOW = perclos_window
        self.BLINK_MIN = blink_min
        self.BLINK_MAX = blink_max

        # MediaPipe Face Mesh landmark indices: p1(corner), p2, p3 (top), p4(corner), p5, p6 (bottom)
        self.LEFT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE_INDICES = [362, 385, 387, 263, 373, 380]

        self.baseline_ear = None
        self.reset(keep_calibration=False)

    # ------------------------------------------------------------------
    def calculate_ear(self, eye_landmarks):
        """EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)"""
        a = euclidean_distance(eye_landmarks[1], eye_landmarks[5])
        b = euclidean_distance(eye_landmarks[2], eye_landmarks[4])
        c = euclidean_distance(eye_landmarks[0], eye_landmarks[3])
        return (a + b) / (2.0 * c + 1e-6)

    def extract_eye_landmarks(self, face_landmarks, eye_indices, frame_width, frame_height):
        """Pixel (x, y) coordinates of the 6 eye landmarks"""
        pts = []
        for idx in eye_indices:
            lm = face_landmarks.landmark[idx]
            pts.append([lm.x * frame_width, lm.y * frame_height])
        return np.array(pts)

    # ------------------------------------------------------------------
    def process_frame(self, face_landmarks, frame_width, frame_height):
        now = time.time()

        left_eye = self.extract_eye_landmarks(face_landmarks, self.LEFT_EYE_INDICES, frame_width, frame_height)
        right_eye = self.extract_eye_landmarks(face_landmarks, self.RIGHT_EYE_INDICES, frame_width, frame_height)
        left_ear = self.calculate_ear(left_eye)
        right_ear = self.calculate_ear(right_eye)
        avg_ear = float((left_ear + right_ear) / 2.0)

        # ---- calibration: learn this driver's open-eye EAR ----
        calibrating = not self.calibrated
        progress = 1.0
        if calibrating:
            if self._calib_start is None:
                self._calib_start = now
            if avg_ear > 0.12:                       # ignore obvious closures
                self._calib_samples.append(avg_ear)
            elapsed = now - self._calib_start
            progress = min(elapsed / self.CALIBRATION_SECONDS, 1.0)
            if elapsed >= self.CALIBRATION_SECONDS:
                if len(self._calib_samples) >= 10:
                    self.baseline_ear = float(np.median(self._calib_samples))
                    self.EAR_THRESHOLD = float(np.clip(self.baseline_ear * self.THRESHOLD_RATIO, 0.15, 0.28))
                    self.calibrated = True
                    calibrating = False
                else:                                # not enough good samples, retry
                    self._calib_start = now
                    self._calib_samples = []

        # ---- eye closure / blink logic (time based) ----
        eyes_closed = (not calibrating) and avg_ear < self.EAR_THRESHOLD
        closed_duration = 0.0
        if eyes_closed:
            if self._closed_since is None:
                self._closed_since = now
            closed_duration = now - self._closed_since
            self.frame_counter += 1
        else:
            if self._closed_since is not None:
                d = now - self._closed_since
                if self.BLINK_MIN <= d <= self.BLINK_MAX:
                    self.total_blinks += 1
            self._closed_since = None
            self.frame_counter = 0

        is_drowsy = bool(eyes_closed and closed_duration >= self.CLOSED_SECONDS)

        # ---- PERCLOS: fraction of recent time with eyes closed ----
        if not calibrating:
            self._history.append((now, bool(eyes_closed)))
        while self._history and now - self._history[0][0] > self.PERCLOS_WINDOW:
            self._history.popleft()
        perclos = (sum(1 for _, c in self._history if c) / len(self._history)) if self._history else 0.0

        return {
            'left_ear': round(float(left_ear), 3),
            'right_ear': round(float(right_ear), 3),
            'avg_ear': round(avg_ear, 3),
            'eyes_closed': bool(eyes_closed),
            'blink_count': int(self.total_blinks),
            'closed_frames': int(self.frame_counter),
            'closed_duration': round(float(closed_duration), 2),
            'is_drowsy': is_drowsy,
            'perclos': round(float(perclos), 3),
            'ear_threshold': round(float(self.EAR_THRESHOLD), 3),
            'calibrating': bool(calibrating),
            'calibration_progress': round(float(progress), 2),
            'left_eye_landmarks': left_eye,
            'right_eye_landmarks': right_eye,
        }

    def on_no_face(self):
        """Call when no face is visible so closure timers don't carry over"""
        self._closed_since = None
        self.frame_counter = 0

    def reset(self, keep_calibration=True):
        """Reset counters (and optionally the calibration)"""
        self.total_blinks = 0
        self.frame_counter = 0
        self._closed_since = None
        self._history = deque()
        if not (keep_calibration and getattr(self, 'calibrated', False)):
            self.calibrated = False
            self._calib_samples = []
            self._calib_start = None
            self.EAR_THRESHOLD = self.DEFAULT_EAR_THRESHOLD