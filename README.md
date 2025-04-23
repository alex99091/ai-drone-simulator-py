# 🛸 AI Drone Simulator

A high-level Python project that simulates drone movement  
based on AI-powered human detection.  
This project uses YOLOv5 and OpenCV to detect people through a webcam  
and moves a virtual drone accordingly  
— all without needing a physical drone.

---

## 🚀 Features

- 🤖 Real-time human detection using YOLOv5 (PyTorch-based)
- 🛰️ Simulates drone position updates based on object location
- 🖥️ Visualizes video feed and drone movement with OpenCV
- 🔌 Structured to allow future expansion with real drones or web APIs

---

## 🧱 Project Structure
```bash

ai-drone-simulator/
├── main.py                # Main application loop
├── config/
│   └── settings.py        # Drone speed and initial values
├── core/
│   ├── detector.py        # Human detection logic (YOLO)
│   ├── tracker.py         # Drone position tracking logic
│   └── visualizer.py      # Video feed rendering with overlays
├── utils/
│   └── helper.py          # Utility functions
├── models/                # (Optional) Model storage
├── venv/                  # Virtual environment (excluded from repo)
└── README.md
```

## ⚙️ Requirements

- Python >= 3.8
- PyTorch
- torchvision
- OpenCV

### Install with:

```bash

pip install torch torchvision opencv-python
```

### YOLOv5 Setup:

```bash

git clone https://github.com/ultralytics/yolov5
cd yolov5
pip install -r requirements.txt

```

## ▶️ How to Run

```bash

python main.py
```

- Launches webcam feed
- Detects people using YOLOv5
- Prints "Person detected!" in console
- Virtual drone (green box) moves left/right to follow detected target

## 🔧 Future Enhancements

- Add Flask-based REST API for status/command handling
- Real-time WebSocket communication
- Connect to real drone (e.g., DJI Tello)
- Unit testing with pytest

##  👤 Author

- Developer: ALEX KWAK
- GitHub: https://github.com/alex99091