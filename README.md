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

ai-drone-simulator-py/
├── backend/
│   ├── app/                        # 실행 스크립트 모음
│   │   ├── simulate_drone.py      # 실시간 YOLO + 드론 시뮬
│   │   ├── run_detector.py        # 감지기 단독 실행
│   │   ├── run_tracker.py         # 드론 추적기 테스트
│   │   └── run_api.py             # Flask API 실행 엔트리포인트
│   ├── api/                        # Flask API 구성
│   │   ├── __init__.py
│   │   ├── controller.py          # 라우터 정의
│   │   ├── dto.py                 # 요청/응답 모델 정의
│   │   └── service.py             # 드론 추적 로직 래퍼
│   ├── config/
│   │   └── settings.py            # 기본 설정값
│   ├── core/
│   │   ├── detector.py            # YOLO 기반 사람 감지
│   │   ├── drone.py               # 드론 객체 로직
│   │   ├── tracker.py             # 드론 위치 추적기
│   │   └── visualizer.py          # 시각화 로직 (OpenCV)
│   ├── utils/
│   │   └── helper.py              # 범용 함수들
│   ├── tests/                     # 단위 테스트
│   │   ├── test_detector.py
│   │   ├── test_drone.py
│   │   ├── test_tracker.py
│   │   ├── test_visualizer.py
│   │   └── test_api_service.py   # (작성 예정)
│   └── requirements.txt
├── README.md

```

## ⚙️ Requirements

- Python >= 3.8
- PyTorch
- torchvision
- OpenCV
- Flask>=2.0.0

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