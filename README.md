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
├── backend/backend/
├─ manage.py
├─ pyproject.toml / requirements.txt
├─ .env                      # 백엔드 환경변수 (프론트 .env와 별도)
├─ backend/                  # Django 프로젝트 루트 (settings/asgi/urls)
│  ├─ __init__.py
│  ├─ settings.py            # Channels/Redis/CORS/INSTALLED_APPS 설정
│  ├─ urls.py                # HTTP 라우팅(/api, /video)
│  ├─ asgi.py                # ASGI + ProtocolTypeRouter
│  └─ routing.py             # Channels 라우팅(WebSocket URLConf)
├─ apps/
│  ├─ api/                   # HTTP API (status 등)
│  │  ├─ __init__.py
│  │  ├─ urls.py             # /api/ 하위 엔드포인트
│  │  └─ views.py            # GET /api/tello/status
│  ├─ stream/                # 영상 스트리밍(MJPEG 변환)
│  │  ├─ __init__.py
│  │  ├─ views.py            # GET /video (StreamingHttpResponse)
│  │  └─ services.py         # 프레임 그랩/인코딩(OpenCV/ffmpeg) 관리
│  ├─ ws/                    # WebSocket(명령/상태) Consumers
│  │  ├─ __init__.py
│  │  ├─ consumers.py        # CommandConsumer, StatusConsumer
│  │  └─ utils.py            # 메시지 검증/직렬화
│  ├─ control/               # 명령 처리(우선순위 큐, ack)
│  │  ├─ __init__.py
│  │  ├─ priority.py         # emergency/land 우선 처리 PQ
│  │  ├─ dispatcher.py       # 큐→Tello 전송 스레드/비동기 처리
│  │  └─ schemas.py          # {action,direction,speed} 검증 스키마
│  ├─ telemetry/             # 상태 수집/배포(폴링 10s + 캐시)
│  │  ├─ __init__.py
│  │  ├─ collector.py        # 10초마다 Tello 상태 수집
│  │  ├─ broadcaster.py      # WS 구독자에게 telemetry 푸시
│  │  └─ store.py            # Redis에 최신 스냅샷 저장/로드
│  ├─ adapters/              # 외부(Tello SDK/UDP) 어댑터
│  │  ├─ __init__.py
│  │  ├─ tello_sdk.py        # 명령 소켓, 상태 UDP(8890), 비디오 UDP(11111)
│  │  └─ video_capture.py    # 비디오 프레임 수신/디코드
│  └─ common/                # 공통 유틸/예외/로깅/헬스체크
│     ├─ __init__.py
│     ├─ errors.py
│     ├─ health.py           # /healthz, /readyz
│     └─ logging.py
└─ ops/
   ├─ docker/                # Dockerfile/compose(옵션)
   └─ scripts/               # 개발/운영 스크립트 (runserver, worker 등)
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