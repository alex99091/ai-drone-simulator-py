# 🛸 AI Drone Simulator — Django + DJI Tello + OpenCV

**Python 기반 실시간 관제 프로토타입**   
DJI Tello 드론 실기기에서 영상을 수집하고, **OpenCV + YOLOv8**로 사람인식.   
백엔드는 **Django**로, **Control / Status / Stream** API를 **분리하고 우선순위를 부여**해 영상 부하 상황에서도 제어 안정성 확보   
프론트는 **Vite + React 단일 대쉬보드**로 상태 지표(FPS/배터리/지연)와 제어등 표시   

> 이 프로젝트는 **Python 생태계(Django·OpenCV·YOLO)**로 **드론–AI–서버를 통합한 E2E 시스템**을 구현.   

---

## 🚀 Features

- **실기기 연동**: DJI Tello 제어/상태/영상 수집 (djitellopy/SDK)
- **사람 인식 AI**: OpenCV + YOLOv8n(가볍고 빠른 추론), ROI/지속조건으로 오탐·중복 알림 억제
- **API 분리 & 우선순위**
  - **Control** — 최우선(즉시 반응), 비상/착륙 우선 처리
  - **Status** — 기본 10분 주기(배터리/고도/FPS/지연 스냅샷)
  - **Stream** — 낮은 우선(끊김 시 자동 제외, 서비스 지속성 보장)
- **실시간 대시보드**: WebSocket으로 이벤트/지표 반영, 텔레그램 알림(쿨다운)
- **확장성 고려**: Django 기반 → 향후 **마이크로서비스** 단위로 도메인 분리 용이

---

## 🧱 Project Structure

```
ai-drone-simulator-py/
├─ backend/
│  ├─ manage.py
│  ├─ pyproject.toml / requirements.txt
│  ├─ .env                      # 백엔드 환경변수
│  ├─ backend/                  # Django 프로젝트 루트
│  │  ├─ __init__.py
│  │  ├─ settings.py            # Channels/CORS/INSTALLED_APPS
│  │  ├─ urls.py                # /api, /video, /healthz, /readyz
│  │  ├─ asgi.py                # ASGI + ProtocolTypeRouter(WS)
│  │  └─ routing.py             # Channels WebSocket URLConf
│  ├─ apps/
│  │  ├─ api/                   # HTTP API (health, status)
│  │  │  ├─ urls.py             # /api/*
│  │  │  └─ views.py            # GET /api/tello/status
│  │  ├─ stream/                # 영상 스트리밍(MJPEG/RTSP 변환)
│  │  │  ├─ views.py            # GET /video
│  │  │  └─ services.py         # OpenCV/ffmpeg 캡처/인코딩
│  │  ├─ ws/                    # WebSocket(명령/상태)
│  │  │  ├─ consumers.py        # CommandConsumer, StatusConsumer
│  │  │  └─ utils.py            # 메시지 검증/직렬화
│  │  ├─ control/               # 명령 처리(우선순위 큐, ack)
│  │  │  ├─ priority.py         # emergency/land 최우선
│  │  │  └─ dispatcher.py       # 큐→Tello 전송 스레드
│  │  ├─ telemetry/             # 상태 수집/배포
│  │  │  ├─ collector.py        # 기본 10분 주기 수집(배터리/고도/FPS/지연)
│  │  │  └─ broadcaster.py      # WS 구독자에게 푸시
│  │  ├─ ai/                    # OpenCV/YOLO 파이프라인
│  │  │  ├─ detector.py         # YOLOv8n 추론, ROI/지속조건
│  │  │  └─ tracker.py          # ByteTrack 등(옵션)
│  │  └─ common/                # 헬스체크/예외/로깅
│  │     ├─ health.py           # /healthz, /readyz
│  │     └─ logging.py
│  └─ ops/
│     ├─ docker/                # Dockerfile/compose(옵션)
│     └─ scripts/               # runserver, worker 등
└─ frontend/                    # Vite + React 단일 대시보드
   ├─ src/
   │  ├─ App.jsx                # Header/Sidebar/Dashboard 통합
   │  ├─ components/
   │  │  ├─ Header.jsx
   │  │  ├─ Sidebar.jsx
   │  │  ├─ Dashboard.jsx       # 스트림/지표/컨트롤 UI
   │  │  └─ StatusCard.jsx
   │  └─ lib/ws.js              # WebSocket 헬퍼
   ├─ index.html
   ├─ package.json
   └─ vite.config.js
```

---

## ⚙️ Requirements

**Backend**
- Python 3.10+
- Django, Django Channels, djangorestframework
- opencv-python
- ultralytics (YOLOv8)
- djitellopy
- (옵션) Redis (Channels layer)

**Frontend**
- Node 18+ / 20+
- Vite + React

**System**
- ffmpeg (Tello UDP 11111 → OpenCV 프레임 안정화)
- 동일 Wi‑Fi에서 Tello 연결

설치 예:
```bash
pip install -r requirements.txt
# 또는
pip install django djangorestframework channels opencv-python ultralytics djitellopy python-dotenv
```

---

## 🔐 Configuration (.env)

```dotenv
# Django
DJANGO_SECRET_KEY=your-secret
DJANGO_DEBUG=true
ALLOWED_HOSTS=127.0.0.1,localhost

# CORS/WS
CORS_ALLOW_ORIGINS=http://localhost:5173

# Tello
TELLO_CMD_ADDR=192.168.10.1:8889
TELLO_STATE_UDP_PORT=8890
TELLO_VIDEO_UDP=udp://0.0.0.0:11111

# Stream/Telemetry
STATUS_POLL_INTERVAL_MIN=10
STREAM_FPS_TARGET=30
ROI_XYWH=0,0,640,480
DETECTION_PERSIST_FRAMES=5

# Alert (optional)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
COOLDOWN_SECONDS=30
```

---

## ▶️ How to Run

### 1) Backend
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
- `GET /readyz` / `GET /healthz` 로 서버 상태 확인  
- `GET /video` 로 MJPEG 스트림(브라우저 미리보기)  
- `GET /api/tello/status` 로 상태 스냅샷(JSON)

### 2) Frontend (Dashboard)
```bash
cd frontend
npm i
npm run dev
```
- `.env` 예: `VITE_API_BASE=http://127.0.0.1:8000`  
- 대시보드에서 **스트림, 상태 지표(FPS/배터리/지연), 컨트롤 버튼** 확인

---

## 🔌 API Guide

### Health
- `GET /healthz` — liveness  
- `GET /readyz` — readiness

### Status (우선순위: 중)
- `GET /api/tello/status`
```json
{
  "battery": 87,
  "height_cm": 120,
  "fps": 28,
  "latency_ms": 640,
  "updated_at": "2025-08-23T12:34:56Z"
}
```
> 기본 **10분 주기**로 수집/캐시. 대시보드에 즉시 반영.

### Control (우선순위: 최상)
- WebSocket: `ws://<host>/ws/control`
```json
{ "action": "move", "direction": "left", "speed": 20 }
```
- 우선순위: `emergency` > `land` > 기타  
- 서버는 **ACK** 및 실패 사유를 WS로 회신

### Stream (우선순위: 낮음)
- `GET /video` (MJPEG)  
- 스트림 끊김/지연 시 **자동 제외**, 제어/상태는 지속 동작

---

## 🧠 OpenCV Human Detection (YOLOv8)

- 모델: **YOLOv8n**(ultralytics) — 빠른 추론에 적합  
- 오탐/중복 방지:
  - **ROI 제한**: 화면 내 관심 영역만 감시
  - **지속조건**: N 프레임 이상 연속 검출 시 이벤트 확정
  - **쿨다운**: 동일 대상 반복 알림 억제(텔레그램)

설치/테스트:
```bash
pip install ultralytics opencv-python
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')('sample.jpg')"
```

---

## 🧭 Architecture at a Glance

```
[Tello] ==> (UDP11111 Video) ==> [ffmpeg/OpenCV] ==> [AI Detector(YOLOv8)]
   |             |                                       |
   |             +--(8890 State)--> [Telemetry Collector]+--> [WebSocket] --> Frontend
   +--(8889 Cmd)<------------------[Control Dispatcher]<--(WS Control)
```

- **분리/우선순위**로 **제어 즉시성**과 **서비스 안정성** 보장
- Django 기반으로 **마이크로서비스 분리**에 유리한 경계 도출

---

## 🔭 Roadmap

- [ ] Stream 별도 서비스 분리(마이크로서비스화)
- [ ] Control/Status 스키마 OpenAPI 명세화
- [ ] 이벤트 리플레이/감사 로그(Ops)
- [ ] 모델 경량화 & 하드웨어 가속(TensorRT 등)

---

## 👤 Author

- **Developer**: ALEX KWAK (곽규빈)  
- **GitHub**: https://github.com/alex99091
