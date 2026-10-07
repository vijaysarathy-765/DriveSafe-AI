# DriveSafe AI - Driver Drowsiness Detection and Alert System

## Overview

DriveSafe AI is a real-time driver drowsiness detection and alert system designed to improve driving safety by monitoring facial features through a webcam.

The system uses computer vision and facial landmark detection to analyze the driver's eyes and mouth. It calculates the **Eye Aspect Ratio (EAR)** to identify prolonged eye closure and the **Mouth Aspect Ratio (MAR)** to detect yawning. These signals are combined to estimate the driver's drowsiness level.

When a high level of drowsiness is detected, the system provides a visual warning and an audible alert to attract the driver's attention.

## Key Features

- Real-time driver face monitoring
- Facial landmark detection using MediaPipe
- Eye Aspect Ratio (EAR) calculation
- Mouth Aspect Ratio (MAR) calculation
- Eye closure and blink detection
- Yawning detection
- Real-time drowsiness score
- Normal, Warning, and Alert status levels
- Audible drowsiness alert
- Visual warning on the monitoring interface
- Real-time eye and mouth landmark visualization
- Alert history
- Drowsiness timeline visualization
- Flask-based backend
- Browser-based monitoring interface

## How It Works

The system processes the driver's webcam video continuously.

### Detection Pipeline

```text
Webcam
   ↓
Video Capture
   ↓
Face Detection
   ↓
Facial Landmark Detection
   ↓
Eye Landmarks        Mouth Landmarks
      ↓                    ↓
EAR Calculation      MAR Calculation
      ↓                    ↓
      └──────────┬─────────┘
                 ↓
        Drowsiness Analysis
                 ↓
         Drowsiness Score
                 ↓
       Normal / Warning / Alert
                 ↓
        Visual + Audio Alert
```

## Detection Methods

### 1. Eye Aspect Ratio (EAR)

The Eye Aspect Ratio (EAR) is used to determine whether the driver's eyes are open or closed.

Facial landmarks around the eye are detected using MediaPipe. The distances between the vertical and horizontal eye landmarks are used to calculate EAR.

The general EAR calculation is:

```text
EAR = (||p2 - p6|| + ||p3 - p5||) / (2 × ||p1 - p4||)
```

Where:

- `p1` and `p4` represent the horizontal eye points.
- `p2`, `p3`, `p5`, and `p6` represent vertical eye points.

A lower EAR indicates that the eye is becoming closed.

The system also monitors how long the eyes remain closed. Prolonged eye closure is treated as an important indication of possible drowsiness.

### 2. Mouth Aspect Ratio (MAR)

The Mouth Aspect Ratio (MAR) is used to detect yawning.

Facial landmarks around the mouth are analyzed, and the vertical and horizontal distances are used to calculate the mouth aspect ratio.

A higher MAR value indicates that the mouth is open.

If the mouth remains open for a sustained period, the system considers it a possible yawn.

### 3. Drowsiness Score

The system combines multiple signals instead of depending on only one measurement.

The drowsiness score considers factors such as:

- Eye closure
- Duration of eye closure
- Eye drowsiness detection
- Percentage of time eyes remain closed
- Yawning
- Recent yawns
- Face detection status

The resulting value is limited to a range of 0 to 100.

The score is converted into three status levels:

| Score    | Status  |
|----------|---------|
| 0 - 29   | Normal  |
| 30 - 69  | Warning |
| 70 - 100 | Alert   |

## Alert System

When the driver's drowsiness level reaches the alert threshold, the system activates the warning mechanism.

The alert system provides:

- Visual alert on the monitoring screen
- Audible warning
- Alert history
- Alert timestamp
- Recorded drowsiness score

A short alert hold period is used so that an alert does not disappear immediately when the measured score fluctuates between frames.

The system also uses an alert cooldown to avoid continuously triggering new alert events.

## Technology Stack

### Backend

- Python
- Flask
- OpenCV
- MediaPipe
- NumPy

### Frontend

- HTML5
- CSS3
- JavaScript
- Chart.js

### Development Tools

- Visual Studio Code
- Git
- GitHub
- Python Virtual Environment

## Project Structure

```text
DriveSafe-AI/
│
├── backend/
│   ├── app.py
│   ├── drowsiness_detector.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── alert_manager.py
│       ├── eye_tracker.py
│       └── yawn_detector.py
│
├── frontend/
│   ├── index.html
│   │
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       ├── main.js
│       └── chart-config.js
│
├── generate_alert_sound.py
├── requirements.txt
├── setup.bat
├── start_application.bat
├── .gitignore
└── README.md
```

## System Components

### `backend/app.py`

The Flask application provides the backend services required by the monitoring interface.

It handles:

- Starting the Flask server
- Video stream processing
- Drowsiness status requests
- Alert information
- Communication with the frontend

The application runs on port **5001**.

### `backend/drowsiness_detector.py`

This is the main detection component. It:

1. Receives video frames.
2. Converts frames for MediaPipe processing.
3. Detects facial landmarks.
4. Processes eye landmarks.
5. Calculates EAR.
6. Processes mouth landmarks.
7. Calculates MAR.
8. Determines eye closure and yawning conditions.
9. Calculates the drowsiness score.
10. Determines the current alert status.
11. Displays detection information on the video frame.

### `backend/utils/eye_tracker.py`

The eye tracker handles eye-related measurements. It is responsible for:

- Extracting eye landmarks
- Calculating EAR
- Detecting eye closure
- Tracking consecutive closed-eye frames
- Tracking blink information
- Maintaining eye-related detection data

### `backend/utils/yawn_detector.py`

The yawn detector handles mouth-related measurements. It is responsible for:

- Extracting mouth landmarks
- Calculating MAR
- Detecting sustained mouth opening
- Detecting yawning
- Tracking recent yawns

### `backend/utils/alert_manager.py`

The alert manager combines the eye and mouth detection results. It is responsible for:

- Calculating the drowsiness score
- Determining Normal, Warning, and Alert states
- Maintaining alert history
- Applying alert cooldown
- Maintaining a short alert hold period
- Providing the current alert status

## User Interface

The monitoring interface provides real-time information including:

- Live camera feed
- Current driver status
- Drowsiness score
- Eye blink count
- Yawn count
- EAR value
- MAR value
- Alert history
- Drowsiness timeline

## Installation

### Requirements

- Python 3.10 or a compatible version
- Webcam
- Internet connection for installing dependencies
- Computer capable of running real-time video processing

### 1. Clone the Repository

```bash
git clone https://github.com/vijaysarathy-765/DriveSafe-AI.git
cd DriveSafe-AI
```

### 2. Create a Virtual Environment

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the Application

Start the Flask application:

```bash
python backend/app.py
```

The application runs on:

```text
http://localhost:5001
```

Open the address in a web browser and allow camera access when requested.

## Using the System

1. Start the Flask application.
2. Open the application in a web browser.
3. Allow camera access.
4. Position your face clearly in front of the camera.
5. The system detects facial landmarks.
6. EAR and MAR values are calculated continuously.
7. Eye closure and yawning are monitored.
8. The drowsiness score is updated in real time.
9. If drowsiness reaches the alert level, the system activates a visual and audible warning.

For reliable detection, the driver's face should remain reasonably visible to the camera.

## Drowsiness Detection Logic

The system considers the driver's facial behavior over time rather than relying on a single frame.

### Eye Closure

```text
Eyes Open
   ↓
Normal EAR
   ↓
Normal Status
```

If the eyes remain closed:

```text
Low EAR
   ↓
Eyes Remain Closed
   ↓
Drowsiness Indicators Increase
   ↓
Warning / Alert
```

### Yawning

```text
High MAR
   ↓
Sustained Mouth Opening
   ↓
Possible Yawn
   ↓
Drowsiness Indicators Increase
```

The final drowsiness score combines these indicators.

## Advantages

- Real-time monitoring
- Non-contact detection
- Uses a standard webcam
- Does not require specialized wearable hardware
- Combines eye and mouth behavior
- Provides immediate warnings
- Easy to run on a personal computer
- Web-based monitoring interface

## Limitations

The current system is a computer-vision prototype and its accuracy can be affected by environmental and user conditions.

Possible limitations include:

- Poor lighting
- Face partially hidden from the camera
- Extreme head movement
- Camera quality
- Incorrect camera positioning
- Sunglasses or other objects covering the eyes
- Multiple people appearing in the camera frame
- Differences in individual facial features

The system should therefore be considered an **assistive safety prototype** rather than a replacement for responsible driving or professional vehicle safety systems.

## Future Enhancements

Possible future improvements include:

- Improved head-pose estimation
- Better performance under low-light conditions
- Driver-specific calibration
- More advanced drowsiness classification
- Machine-learning-based fatigue prediction
- Mobile application support
- Cloud-based session monitoring
- Driver session reports
- GPS integration
- Vehicle integration
- Improved audio alert customization
- Performance optimization for embedded devices