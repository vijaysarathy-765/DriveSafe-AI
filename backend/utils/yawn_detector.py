"""
Yawn Detection Module
Landmark-based Mouth Aspect Ratio (MAR). A yawn = MAR stays high for a sustained time.
"""
import time
from collections import deque

import numpy as np


def euclidean_distance(point1, point2):
    """Euclidean distance between two points"""
    return float(np.linalg.norm(np.asarray(point1, dtype=float) - np.asarray(point2, dtype=float)))


class YawnDetector:
    def __init__(self, mar_threshold=0.6, yawn_seconds=1.2, recent_window=120.0):
        """
        Args:
            mar_threshold: MAR above this = mouth wide open (default 0.6)
            yawn_seconds: MAR must stay high this long to count as a yawn
            recent_window: window (s) used to count 'recent yawns'
        """
        self.MAR_THRESHOLD = mar_threshold
        self.YAWN_SECONDS = yawn_seconds
        self.RECENT_WINDOW = recent_window

        # Inner-lip landmarks (MediaPipe Face Mesh)
        self.MOUTH_CORNERS = (78, 308)
        self.MOUTH_VERTICAL = [(82, 87), (13, 14), (312, 317)]
        self.reset()

    def calculate_mar(self, lm_px):
        """MAR = mean(vertical lip openings) / mouth width"""
        horizontal = euclidean_distance(lm_px[self.MOUTH_CORNERS[0]], lm_px[self.MOUTH_CORNERS[1]])
        vertical = np.mean([euclidean_distance(lm_px[a], lm_px[b]) for a, b in self.MOUTH_VERTICAL])
        return float(vertical / horizontal) if horizontal > 0 else 0.0

    def extract_mouth_landmarks(self, face_landmarks, frame_width, frame_height):
        """Pixel coordinates for every mouth landmark we use, keyed by index"""
        needed = set(self.MOUTH_CORNERS) | {i for pair in self.MOUTH_VERTICAL for i in pair}
        return {i: (face_landmarks.landmark[i].x * frame_width,
                    face_landmarks.landmark[i].y * frame_height) for i in needed}

    def process_frame(self, face_landmarks, frame_width, frame_height):
        now = time.time()
        pts = self.extract_mouth_landmarks(face_landmarks, frame_width, frame_height)
        mar = self.calculate_mar(pts)

        is_yawning = bool(mar > self.MAR_THRESHOLD)          # mouth open wide right now
        yawn_detected = False                                 # sustained => real yawn

        if is_yawning:
            if self._yawn_since is None:
                self._yawn_since = now
                self._counted = False
            if now - self._yawn_since >= self.YAWN_SECONDS:
                yawn_detected = True
                if not self._counted:                         # count once per yawn
                    self.total_yawns += 1
                    self._yawn_times.append(now)
                    self._counted = True
        else:
            self._yawn_since = None
            self._counted = False

        while self._yawn_times and now - self._yawn_times[0] > self.RECENT_WINDOW:
            self._yawn_times.popleft()

        return {
            'mar': round(mar, 3),
            'is_yawning': is_yawning,
            'yawn_count': int(self.total_yawns),
            'yawn_detected': bool(yawn_detected),
            'recent_yawns': len(self._yawn_times),
            'mouth_landmarks': list(pts.values()),
        }

    def on_no_face(self):
        self._yawn_since = None
        self._counted = False

    def reset(self):
        self.total_yawns = 0
        self._yawn_since = None
        self._counted = False
        self._yawn_times = deque()