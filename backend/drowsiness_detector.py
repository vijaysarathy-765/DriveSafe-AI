"""
Drowsiness Detection Engine
Pipeline: Camera -> OpenCV -> MediaPipe Face Mesh landmarks -> EAR (eyes) + MAR (mouth)
          -> blink / eye-closure / yawn analysis -> drowsiness score -> alert
"""
import cv2
import numpy as np
import mediapipe as mp

from utils.alert_manager import AlertManager
from utils.eye_tracker import EyeTracker
from utils.yawn_detector import YawnDetector


class DrowsinessDetector:
    def __init__(self):
        """Initialize MediaPipe Face Mesh, EAR/MAR trackers and alert manager"""
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.eye_tracker = EyeTracker()
        self.yawn_detector = YawnDetector()
        self.alert_manager = AlertManager()
        self.frame_count = 0

    # ------------------------------------------------------------------
    def process_frame(self, frame):
        """
        Process one BGR frame.
        Returns: (annotated_frame, detection_results)
        """
        self.frame_count += 1
        frame_height, frame_width = frame.shape[:2]
        annotated_frame = frame.copy()

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        result = self.face_mesh.process(rgb)

        eye_data = {'avg_ear': 0.0, 'blink_count': self.eye_tracker.total_blinks, 'eyes_closed': False,
                    'closed_frames': 0, 'closed_duration': 0.0, 'is_drowsy': False,
                    'perclos': 0.0, 'calibrating': False}
        yawn_data = {'mar': 0.0, 'yawn_count': self.yawn_detector.total_yawns, 'is_yawning': False,
                     'yawn_detected': False, 'recent_yawns': 0}
        no_face_detected = not result.multi_face_landmarks

        if not no_face_detected:
            face_landmarks = result.multi_face_landmarks[0]

            eye_data = self.eye_tracker.process_frame(face_landmarks, frame_width, frame_height)
            yawn_data = self.yawn_detector.process_frame(face_landmarks, frame_width, frame_height)

            # Draw the landmarks actually used for EAR / MAR
            eye_color = (0, 0, 255) if eye_data['eyes_closed'] else (0, 255, 0)
            for pts in (eye_data['left_eye_landmarks'], eye_data['right_eye_landmarks']):
                for (px, py) in pts:
                    cv2.circle(annotated_frame, (int(px), int(py)), 2, eye_color, -1)
            mouth_color = (0, 165, 255) if yawn_data['is_yawning'] else (0, 255, 255)
            for (px, py) in yawn_data['mouth_landmarks']:
                cv2.circle(annotated_frame, (int(px), int(py)), 2, mouth_color, -1)

            cv2.putText(annotated_frame, f"EAR: {eye_data['avg_ear']:.2f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(annotated_frame, f"MAR: {yawn_data['mar']:.2f}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(annotated_frame, f"Eyes closed: {eye_data['closed_duration']:.1f}s", (10, 180),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        else:
            self.eye_tracker.on_no_face()
            self.yawn_detector.on_no_face()
            cv2.putText(annotated_frame, "NO FACE DETECTED", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Score + status
        raw_score = self.alert_manager.calculate_drowsiness_score(eye_data, yawn_data, no_face_detected)
        alert_info = self.alert_manager.update_status(raw_score)
        drowsiness_score = alert_info['drowsiness_score']

        status = alert_info['status']
        status_color = self._get_status_color(status)
        cv2.putText(annotated_frame, f"Status: {status}", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        cv2.putText(annotated_frame, f"Drowsiness: {drowsiness_score}%", (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)

        if eye_data.get('calibrating'):
            pct = int(eye_data.get('calibration_progress', 0) * 100)
            cv2.putText(annotated_frame, f"Calibrating {pct}% - keep eyes open, look at camera",
                        (10, frame_height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 0), 2)

        if status == "Alert":
            overlay = annotated_frame.copy()
            cv2.rectangle(overlay, (0, 0), (frame_width, frame_height), (0, 0, 255), -1)
            annotated_frame = cv2.addWeighted(annotated_frame, 0.7, overlay, 0.3, 0)
            warning_text = "DROWSINESS DETECTED!"
            text_size = cv2.getTextSize(warning_text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3)[0]
            cv2.putText(annotated_frame, warning_text,
                        ((frame_width - text_size[0]) // 2, (frame_height + text_size[1]) // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)

        # Keep the response light / JSON friendly
        eye_out = {k: v for k, v in eye_data.items() if not k.endswith('_landmarks')}
        yawn_out = {k: v for k, v in yawn_data.items() if not k.endswith('_landmarks')}

        detection_results = {
            'eye_data': eye_out,
            'yawn_data': yawn_out,
            'alert_info': alert_info,
            'no_face_detected': no_face_detected,
            'frame_count': self.frame_count
        }
        return annotated_frame, detection_results

    # ------------------------------------------------------------------
    def _get_status_color(self, status):
        return {'Normal': (0, 255, 0), 'Warning': (0, 255, 255), 'Alert': (0, 0, 255)}.get(status, (255, 255, 255))

    def get_current_status(self):
        return {
            'status': self.alert_manager.current_status,
            'blink_count': self.eye_tracker.total_blinks,
            'yawn_count': self.yawn_detector.total_yawns,
            'alert_stats': self.alert_manager.get_alert_stats()
        }

    def reset(self):
        """Reset session counters (keeps the eye calibration)"""
        self.alert_manager.reset()
        self.eye_tracker.reset(keep_calibration=True)
        self.yawn_detector.reset()
        self.frame_count = 0

    def cleanup(self):
        self.face_mesh.close()