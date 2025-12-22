"""
Simplified Drowsiness Detection Engine using OpenCV Haar Cascades
This version works without MediaPipe/dlib for immediate demo
"""
import cv2
import numpy as np
from utils.alert_manager import AlertManager


class DrowsinessDetector:
    def __init__(self):
        """Initialize Simplified Drowsiness Detector with OpenCV"""
        # Load Haar Cascade classifiers
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # Initialize alert manager
        self.alert_manager = AlertManager()
        
        # Tracking variables
        self.frame_count = 0
        self.blink_counter = 0
        self.total_blinks = 0
        self.total_yawns = 0
        self.eyes_closed_frames = 0
        self.last_face_detected = True
        
    def process_frame(self, frame):
        """
        Process a single video frame for drowsiness detection.
        
        Args:
            frame: BGR image from webcam
        
        Returns:
            tuple: (processed_frame, detection_results)
        """
        self.frame_count += 1
        frame_height, frame_width = frame.shape[:2]
        
        # Convert to grayscale for detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        # Initialize results
        eye_data = {'avg_ear': 0.25, 'blink_count': self.total_blinks, 'eyes_closed': False, 'closed_frames': self.eyes_closed_frames, 'is_drowsy': False}
        yawn_data = {'mar': 0.0, 'yawn_count': self.total_yawns, 'yawn_detected': False}
        no_face_detected = len(faces) == 0
        
        # Draw on frame
        annotated_frame = frame.copy()
        
        if len(faces) > 0:
            self.last_face_detected = True
            # Get largest face
            (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
            
            # Draw face rectangle
            cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Get face ROI
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = annotated_frame[y:y+h, x:x+w]
            
            # Detect eyes in face region
            eyes = self.eye_cascade.detectMultiScale(roi_gray)
            
            # Simple eye closure detection
            if len(eyes) < 2:  # Both eyes not detected = possibly closed
                self.eyes_closed_frames += 1
                eye_data['eyes_closed'] = True
                eye_data['avg_ear'] = 0.15  # Simulated low EAR
                
                if self.eyes_closed_frames >= 30:  # ~2 seconds at 15 FPS
                    eye_data['is_drowsy'] = True
                    
            else:
                # Eyes detected = open
                if self.eyes_closed_frames >= 3:  # Was a blink
                    self.total_blinks += 1
                self.eyes_closed_frames = 0
                eye_data['avg_ear'] = 0.28  # Simulated normal EAR
                
                # Draw eye rectangles
                for (ex, ey, ew, eh) in eyes[:2]:  # Only first 2 eyes
                    cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 255), 2)
            
            # Update eye data
            eye_data['blink_count'] = self.total_blinks
            eye_data['closed_frames'] = self.eyes_closed_frames
            
            # Simple mouth detection (bottom half of face)
            mouth_region = roi_gray[int(h*0.6):, int(w*0.3):int(w*0.7)]
            if mouth_region.size > 0:
                mouth_brightness = np.mean(mouth_region)
                # Dark mouth region might indicate yawning (open mouth)
                if mouth_brightness < 50:  # Arbitrary threshold
                    yawn_data['mar'] = 0.65  # Simulated yawning
                    yawn_data['yawn_detected'] = True
                    self.total_yawns += 1
            
            yawn_data['yawn_count'] = self.total_yawns
            
            # Display EAR value on frame
            ear_text = f"EAR: {eye_data['avg_ear']:.2f}"
            cv2.putText(annotated_frame, ear_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Display MAR value on frame
            mar_text = f"MAR: {yawn_data['mar']:.2f}"
            cv2.putText(annotated_frame, mar_text, (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
        else:
            no_face_detected = True
            self.last_face_detected = False
            cv2.putText(annotated_frame, "NO FACE DETECTED", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Calculate drowsiness score
        drowsiness_score = self.alert_manager.calculate_drowsiness_score(
            eye_data, yawn_data, no_face_detected
        )
        
        # Update alert status
        alert_info = self.alert_manager.update_status(drowsiness_score)
        
        # Display status on frame
        status = alert_info['status']
        status_color = self._get_status_color(status)
        cv2.putText(annotated_frame, f"Status: {status}", (10, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        
        # Display drowsiness score
        score_text = f"Drowsiness: {drowsiness_score}%"
        cv2.putText(annotated_frame, score_text, (10, 120), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        
        # Add alert overlay if critical
        if status == "Alert":
            overlay = annotated_frame.copy()
            cv2.rectangle(overlay, (0, 0), (frame_width, frame_height), (0, 0, 255), -1)
            annotated_frame = cv2.addWeighted(annotated_frame, 0.7, overlay, 0.3, 0)
            
            # Add warning text
            warning_text = "DROWSINESS DETECTED!"
            text_size = cv2.getTextSize(warning_text, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)[0]
            text_x = (frame_width - text_size[0]) // 2
            text_y = (frame_height + text_size[1]) // 2
            cv2.putText(annotated_frame, warning_text, (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        
        # Compile detection results
        detection_results = {
            'eye_data': eye_data,
            'yawn_data': yawn_data,
            'alert_info': alert_info,
            'no_face_detected': no_face_detected,
            'frame_count': self.frame_count
        }
        
        return annotated_frame, detection_results
    
    def _get_status_color(self, status):
        """Get color for status text"""
        colors = {
            'Normal': (0, 255, 0),    # Green
            'Warning': (0, 255, 255),  # Yellow
            'Alert': (0, 0, 255)       # Red
        }
        return colors.get(status, (255, 255, 255))
    
    def get_current_status(self):
        """
        Get current drowsiness detection status.
        
        Returns:
            dict: Current status information
        """
        return {
            'status': self.alert_manager.current_status,
            'blink_count': self.total_blinks,
            'yawn_count': self.total_yawns,
            'alert_stats': self.alert_manager.get_alert_stats()
        }
    
    def reset(self):
        """Reset all trackers"""
        self.alert_manager.reset()
        self.frame_count = 0
        self.total_blinks = 0
        self.total_yawns = 0
        self.eyes_closed_frames = 0
    
    def cleanup(self):
        """Cleanup resources"""
        pass  # No resources to cleanup for Haar Cascades
