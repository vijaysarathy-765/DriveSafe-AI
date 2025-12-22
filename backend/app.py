"""
Flask Backend for DriveSafe AI - Driver Drowsiness Detection
"""
import cv2
import time
from flask import Flask, Response, jsonify, send_from_directory
from flask_cors import CORS
from drowsiness_detector import DrowsinessDetector
import threading

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Initialize detector
detector = DrowsinessDetector()
camera = None
current_detection_results = {}
lock = threading.Lock()


def get_camera():
    """Initialize and return camera"""
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        camera.set(cv2.CAP_PROP_FPS, 30)
    return camera


def generate_frames():
    """Generate video frames with drowsiness detection"""
    global current_detection_results
    
    cam = get_camera()
    fps_start_time = time.time()
    fps_frame_count = 0
    fps = 0
    
    while True:
        success, frame = cam.read()
        if not success:
            break
        
        # Process frame for drowsiness detection
        processed_frame, detection_results = detector.process_frame(frame)
        
        # Update shared detection results
        with lock:
            current_detection_results = detection_results
        
        # Calculate FPS
        fps_frame_count += 1
        if fps_frame_count >= 10:
            fps = fps_frame_count / (time.time() - fps_start_time)
            fps_start_time = time.time()
            fps_frame_count = 0
        
        # Add FPS to frame
        cv2.putText(processed_frame, f"FPS: {fps:.1f}", (10, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        frame_bytes = buffer.tobytes()
        
        # Yield frame in multipart format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.route('/')
def index():
    """Serve the main dashboard"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/drowsiness_status')
def drowsiness_status():
    """Return current drowsiness detection status"""
    with lock:
        results = current_detection_results.copy()
    
    # Extract relevant data
    eye_data = results.get('eye_data', {})
    yawn_data = results.get('yawn_data', {})
    alert_info = results.get('alert_info', {})
    
    response = {
        'status': alert_info.get('status', 'Normal'),
        'drowsiness_score': alert_info.get('drowsiness_score', 0),
        'trigger_audio': alert_info.get('trigger_audio', False),
        'timestamp': alert_info.get('timestamp', ''),
        'metrics': {
            'ear': eye_data.get('avg_ear', 0),
            'mar': yawn_data.get('mar', 0),
            'blink_count': eye_data.get('blink_count', 0),
            'yawn_count': yawn_data.get('yawn_count', 0),
            'eyes_closed': eye_data.get('eyes_closed', False),
            'is_yawning': yawn_data.get('is_yawning', False)
        },
        'no_face_detected': results.get('no_face_detected', False)
    }
    
    return jsonify(response)


@app.route('/session_data')
def session_data():
    """Return session statistics"""
    stats = detector.get_current_status()
    
    return jsonify({
        'current_status': stats['status'],
        'total_blinks': stats['blink_count'],
        'total_yawns': stats['yawn_count'],
        'alert_history': stats['alert_stats']['alert_history'],
        'total_alerts': stats['alert_stats']['total_alerts']
    })


@app.route('/reset_session', methods=['POST'])
def reset_session():
    """Reset the current detection session"""
    detector.reset()
    return jsonify({'status': 'success', 'message': 'Session reset'})


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    try:
        print("=" * 60)
        print("[CAR ICON] DriveSafe AI - Driver Drowsiness Detection System")
        print("=" * 60)
        print("\n[OK] Starting Flask server...")
        print("[CAMERA] Initializing webcam...")
        print("\n[GLOBE] Access the dashboard at: http://127.0.0.1:5000")
        print("\nPress CTRL+C to stop the server\n")
        print("=" * 60)
        
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n\n[STOP] Shutting down...")
        detector.cleanup()
        if camera is not None:
            camera.release()
        print("[OK] Cleanup complete. Goodbye!")
