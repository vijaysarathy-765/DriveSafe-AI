# 🚗 DriveSafe AI - Driver Drowsiness Detection System

<div align="center">

![DriveSafe AI](https://img.shields.io/badge/DriveSafe-AI-00f5a0?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-black?style=for-the-badge&logo=flask)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8-red?style=for-the-badge&logo=opencv)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A real-time AI-powered system to detect driver drowsiness and prevent accidents**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Demo](#-demo-flow) • [Technology](#-technology-stack)

</div>

---

## 📋 Overview

**DriveSafe AI** is an intelligent driver drowsiness detection system that uses computer vision and machine learning to monitor drivers in real-time. By analyzing facial features, eye movements, and yawning patterns, the system can detect early signs of fatigue and alert drivers before accidents occur.

### 🎯 Problem Statement

- **1.35 million** people die in road accidents globally each year
- **20%** of fatal crashes are caused by drowsy driving
- Drivers are often unaware of early drowsiness signs

### 💡 Solution

Real-time monitoring using:
- **Eye Aspect Ratio (EAR)** to detect eye closure
- **Mouth Aspect Ratio (MAR)** to detect yawning
- **MediaPipe Face Mesh** for precise facial landmark detection
- **Instant alerts** with audio and visual warnings

---

## 👨‍💻 Developer

<div align="center">

<img src="https://media.licdn.com/dms/image/v2/D5603AQELUBtsnsHSMw/profile-displayphoto-scale_200_200/B56ZqWa3UMH8AY-/0/1763460223180?e=1767830400&v=beta&t=lGB_KA1SJ_qQaB9ujBDbQ9AVeKxBElfglpPMAtAaTRE" alt="Ajith Kumar Murugan" width="150" height="150" style="border-radius: 50%; border: 3px solid #00f5a0;">

### **Ajith Kumar Murugan**
**AI Research Engineer/Scientist**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077b5?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/ajitharunai/)
[![GitHub](https://img.shields.io/badge/GitHub-arunaiajith-181717?style=for-the-badge&logo=github)](https://github.com/arunaiajith)

*Passionate about creating AI solutions that make a real-world impact*

</div>

---

## ✨ Features

### Core Functionality
- ✅ **Real-time face detection** using MediaPipe Face Mesh (468 landmarks)
- ✅ **Eye tracking** with EAR calculation to detect prolonged eye closure
- ✅ **Blink detection** to identify excessive blinking patterns
- ✅ **Yawn detection** using mouth aspect ratio analysis
- ✅ **Drowsiness scoring** algorithm (0-100 scale)
- ✅ **Multi-level alerts** (Normal/Warning/Alert)

### Dashboard Features
- 📹 **Live video feed** with facial landmark overlay
- 📊 **Real-time statistics** (blink count, yawn count, EAR/MAR values)
- 📈 **Interactive Chart.js graph** showing drowsiness timeline
- 🎨 **Premium dark mode UI** with glassmorphism effects
- ⚡ **Responsive design** for all screen sizes
- 🔊 **Audio alerts** when drowsiness detected
- 🚨 **Visual alerts** with red screen flash

### Technical Highlights
- ⚡ **15+ FPS** real-time processing
- 💻 **Offline capability** - no cloud dependency
- 🎯 **High accuracy** facial landmark detection
- 🔄 **Auto pause/resume** when tab hidden
- 📱 **Responsive** across devices

---

## 🛠️ Technology Stack

### Backend
- **Python 3.8+** - Core language
- **Flask** - Web framework
- **OpenCV** - Computer vision
- **MediaPipe** - Face mesh detection
- **NumPy** - Numerical computing
- **SciPy** - Distance calculations

### Frontend
- **HTML5** - Structure
- **CSS3** - Premium dark mode styling
- **JavaScript (ES6+)** - Interactivity
- **Chart.js** - Real-time visualization

---

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Webcam (built-in or external)
- Modern web browser (Chrome, Firefox, Edge)
- Windows/Mac/Linux operating system

### Step 1: Clone or Download

```bash
cd "AI-Based Driver Drowsiness Detection"
```

### Step 2: Create Virtual Environment

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask & Flask-CORS
- OpenCV
- MediaPipe
- NumPy
- SciPy

### Step 4: Verify Installation

```bash
python -c "import cv2, mediapipe; print('✅ All dependencies installed successfully!')"
```

---

## 🚀 Usage

### Start the Application

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Run the Flask server:**
   ```bash
   python app.py
   ```

3. **Open your browser:**
   - Navigate to: `http://127.0.0.1:5000`
   - Allow webcam permissions when prompted

4. **Start monitoring:**
   - The dashboard will load automatically
   - Live video feed will appear on the left
   - Statistics and graph on the right

### Stopping the Application

- Press `Ctrl+C` in the terminal to stop the server
- The camera will be released automatically

---

## 🎬 Demo Flow

Perfect for hackathon presentations:

### 1️⃣ **Opening (30 seconds)**
- Show the professional dashboard
- Explain the problem (drowsy driving statistics)
- Introduce DriveSafe AI

### 2️⃣ **Normal Operation (20 seconds)**
- Demonstrate live webcam feed with face mesh
- Point out real-time EAR and MAR values
- Show the drowsiness graph updating

### 3️⃣ **Drowsiness Detection (30 seconds)**
- Close eyes for 3+ seconds
- **Alert triggers!** 🚨
  - Audio beep plays
  - Screen flashes red
  - Status changes to "ALERT"
  - Graph spikes above threshold
- Emphasize instant response time

### 4️⃣ **Technical Explanation (20 seconds)**
- Explain EAR algorithm briefly
- Mention MediaPipe's 468 facial landmarks
- Highlight offline capability

### 5️⃣ **Impact Statement (20 seconds)**
- "This system can save lives"
- Mention real-world applications
- Discuss future enhancements

**Total Demo: ~2 minutes** ⏱️

---

## 📊 How It Works

### Eye Aspect Ratio (EAR)

```
EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
```

- **EAR > 0.25** → Eyes open
- **EAR < 0.25** → Eyes closed
- **Prolonged closure (>2 seconds)** → Drowsiness detected

### Mouth Aspect Ratio (MAR)

```
MAR = (vertical distance) / (horizontal distance)
```

- **MAR > 0.6** → Yawning detected
- Frequent yawning indicates fatigue

### Drowsiness Score Calculation

```python
score = 0
if eye_closed_duration > 2_seconds: score += 40
if blink_rate_excessive: score += 20
if yawn_detected: score += 30
if no_face_detected: score += 10

# Final score: 0-100
```

**Alert Levels:**
- 🟢 **0-30**: Normal
- 🟡 **31-69**: Warning
- 🔴 **70-100**: Alert (triggers audio/visual alarm)

---

## 🎨 Dashboard Features

### Video Panel
- Live webcam stream with face mesh overlay
- Real-time EAR and MAR display
- FPS counter
- Status badge (Normal/Warning/Alert)

### Statistics Panel
- **Current Status**: Visual indicator with emoji
- **Drowsiness Meter**: Progress bar (0-100%)
- **Live Metrics**:
  - Eye blink count 👁️
  - Yawn count 🥱
  - EAR value ⚡
  - MAR value 😮
- **Alert History**: Total alerts and last alert time

### Timeline Chart
- Rolling 60-second drowsiness graph
- Color-coded line (green/yellow/red)
- Alert threshold line at 70%
- Interactive tooltips

---

## 🔧 Configuration

### Adjusting Sensitivity

Edit `backend/utils/eye_tracker.py`:
```python
self.EAR_THRESHOLD = 0.25  # Lower = more sensitive
self.CONSECUTIVE_FRAMES = 20  # Higher = less sensitive
```

Edit `backend/utils/yawn_detector.py`:
```python
self.MAR_THRESHOLD = 0.6  # Lower = more sensitive
self.CONSECUTIVE_FRAMES = 15  # Higher = less sensitive
```

### Alert Cooldown

Edit `backend/utils/alert_manager.py`:
```python
self.alert_cooldown = 5  # seconds between alerts
```

---

## 🧪 Testing

### Test Normal State
1. Start the application
2. Look at the camera normally
3. Verify status shows "Normal" (green)
4. Check EAR value is around 0.25-0.30

### Test Drowsiness Detection
1. Close your eyes for 3+ seconds
2. Verify:
   - ✅ Status changes to "Alert" (red)
   - ✅ Audio beep plays
   - ✅ Screen flashes red
   - ✅ Drowsiness score jumps to 70+
   - ✅ Graph shows spike

### Test Yawn Detection
1. Simulate a yawn (wide mouth opening)
2. Verify:
   - ✅ MAR value increases above 0.6
   - ✅ Yawn count increments
   - ✅ Drowsiness score increases

---

## 📁 Project Structure

```
AI-Based Driver Drowsiness Detection/
├── backend/
│   ├── app.py                    # Flask application
│   ├── drowsiness_detector.py    # Core detection engine
│   └── utils/
│       ├── __init__.py
│       ├── eye_tracker.py        # EAR calculation
│       ├── yawn_detector.py      # MAR calculation
│       └── alert_manager.py      # Alert logic
├── frontend/
│   ├── index.html                # Dashboard
│   ├── css/
│   │   └── style.css            # Dark mode styling
│   ├── js/
│   │   ├── main.js              # Core JavaScript
│   │   └── chart-config.js      # Chart.js setup
│   └── assets/
│       └── alert-sound.mp3      # Audio alert
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## 🚀 Future Enhancements

### Phase 2 (Short-term)
- [ ] SQLite session logging
- [ ] Export session data to CSV
- [ ] Head pose detection (tilting/nodding)
- [ ] Multiple camera support
- [ ] Custom alert sounds

### Phase 3 (Medium-term)
- [ ] SMS/Email alerts to emergency contacts
- [ ] Mobile app (React Native)
- [ ] Cloud dashboard for fleet management
- [ ] Historical analytics and reports
- [ ] Multi-language support

### Phase 4 (Long-term)
- [ ] Integration with car systems (OBD-II)
- [ ] Steering pattern analysis
- [ ] Heart rate monitoring (with wearables)
- [ ] AI model fine-tuning with custom dataset
- [ ] Edge device deployment (Raspberry Pi, Jetson)

---

## 🐛 Troubleshooting

### Webcam Not Detected
```python
# Check available cameras
import cv2
for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Camera {i} available")
        cap.release()
```

### Low FPS
- Close other applications using the webcam
- Reduce video resolution in `app.py`:
  ```python
  camera.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
  camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
  ```

### Audio Not Playing
- Check browser permissions
- Click anywhere on the page to enable audio
- Try different browser (Chrome recommended)

### MediaPipe Errors
```bash
pip uninstall mediapipe
pip install mediapipe==0.10.8
```

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2025 DriveSafe AI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgments

- **MediaPipe** by Google for facial landmark detection
- **OpenCV** community for computer vision tools
- **Chart.js** for beautiful visualizations
- Research papers on drowsiness detection algorithms

---

## 📧 Contact & Support

For questions, suggestions, or contributions:

- 👨‍💻 **Developer**: [Ajith Kumar Murugan](https://www.linkedin.com/in/ajitharunai/)
- 🐛 **Report Issues**: [GitHub Issues](https://github.com/arunaiajith)
- 💡 **Feature Requests**: Open a discussion on GitHub

---

<div align="center">

**Made with ❤️ for safer roads by [Ajith Kumar Murugan](https://www.linkedin.com/in/ajitharunai/)**

⭐ Star this project if you find it useful!

[Back to Top](#-drivesafe-ai---driver-drowsiness-detection-system)

</div>
