"""
Alert Manager - combines EAR + MAR signals into a drowsiness score and alert level
"""
import time
from datetime import datetime


class AlertManager:
    def __init__(self):
        self.alert_history = []
        self.current_status = "Normal"
        self.last_alert_time = None
        self.alert_cooldown = 5        # seconds between logged alerts
        self.alert_hold = 3.0          # keep "Alert" on screen at least this long (so the UI/audio can't miss it)

        # Score thresholds (match the dashboard chart: yellow >= 30, red >= 70)
        self.WARNING_THRESHOLD = 30
        self.ALERT_THRESHOLD = 70
        self.EYE_CLOSED_ALERT_S = 1.5

        self._smoothed = 0.0
        self._last_t = None
        self._alert_until = 0.0

    def calculate_drowsiness_score(self, eye_data, yawn_data, no_face_detected=False):
        """
        Combine EAR-based and MAR-based evidence into a 0-100 score.
        Rises instantly, decays gradually (prevents flicker).
        """
        now = time.time()
        dt = 0.0 if self._last_t is None else min(now - self._last_t, 1.0)
        self._last_t = now

        if eye_data.get('calibrating', False):
            raw = 0.0
        else:
            raw = 0.0

            # --- Eyes (EAR): up to 70 points ---
            d = eye_data.get('closed_duration', 0.0)
            if eye_data.get('is_drowsy', False):
                raw += 70                                              # closed >= 1.5 s -> straight to Alert
            elif eye_data.get('eyes_closed', False):
                raw += 10 + 35 * min(d / self.EYE_CLOSED_ALERT_S, 1.0)  # grows the longer eyes stay shut

            # PERCLOS: share of last 30 s with eyes closed (up to 25 points)
            raw += min(eye_data.get('perclos', 0.0) / 0.4, 1.0) * 25

            # --- Mouth (MAR): yawning ---
            if yawn_data.get('yawn_detected', False):
                raw += 30
            elif yawn_data.get('is_yawning', False):
                raw += 10
            raw += min(yawn_data.get('recent_yawns', 0) * 10, 20)       # repeated yawns

            # --- Driver looking away ---
            if no_face_detected:
                raw += 10

        raw = min(raw, 100.0)
        if raw >= self._smoothed:
            self._smoothed = raw
        else:
            self._smoothed = max(raw, self._smoothed - 50.0 * dt)
        return int(round(self._smoothed))

    def determine_alert_level(self, drowsiness_score):
        if drowsiness_score >= self.ALERT_THRESHOLD:
            return "Alert"
        elif drowsiness_score >= self.WARNING_THRESHOLD:
            return "Warning"
        return "Normal"

    def should_trigger_alert(self):
        if self.last_alert_time is None:
            return True
        return time.time() - self.last_alert_time >= self.alert_cooldown

    def update_status(self, drowsiness_score):
        now = time.time()
        level = self.determine_alert_level(drowsiness_score)

        if level == "Alert":
            self._alert_until = now + self.alert_hold

        holding = now < self._alert_until
        new_status = "Alert" if holding else level
        reported_score = max(drowsiness_score, self.ALERT_THRESHOLD) if holding else drowsiness_score
        status_changed = new_status != self.current_status

        # Log alert (with cooldown)
        if new_status == "Alert" and self.should_trigger_alert():
            self.last_alert_time = now
            self.alert_history.append({
                'timestamp': datetime.now().isoformat(),
                'score': reported_score,
                'status': new_status
            })

        # Audio request stays true for the whole Alert period; the dashboard applies its own cooldown
        trigger_audio = (new_status == "Alert")

        self.current_status = new_status
        return {
            'status': new_status,
            'status_changed': status_changed,
            'trigger_audio': trigger_audio,
            'drowsiness_score': reported_score,
            'timestamp': datetime.now().isoformat()
        }

    def get_alert_stats(self):
        total_alerts = len(self.alert_history)
        return {
            'total_alerts': total_alerts,
            'current_status': self.current_status,
            'last_alert': self.alert_history[-1] if total_alerts > 0 else None,
            'alert_history': self.alert_history[-10:]
        }

    def reset(self):
        self.alert_history = []
        self.current_status = "Normal"
        self.last_alert_time = None
        self._smoothed = 0.0
        self._last_t = None
        self._alert_until = 0.0