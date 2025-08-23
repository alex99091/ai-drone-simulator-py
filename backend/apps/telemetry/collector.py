import logging, threading, time, math, random
from typing import Optional, Dict, Any
from django.conf import settings
from .store import set_snapshot, get_snapshot
from .broadcaster import broadcast_snapshot

logger = logging.getLogger(__name__)

_running = False
_thread: Optional[threading.Thread] = None

def _mock_sample(prev: Dict[str, Any]) -> Dict[str, Any]:
    # 간단한 모의 텔레메트리(디버그용)
    t = time.time()
    return {
        "battery": max(0, prev.get("battery", 100) - 0.01),
        "height": abs(120 * math.sin(t/30)),
        "yaw": int((t*10) % 360),
        "pitch": 0,
        "roll": 0,
        "pos": {"x": round(math.cos(t/15)*5, 2), "y": round(math.sin(t/15)*5, 2), "z": 0},
        "wifi": 4,
        "speed": round(abs(2*math.sin(t/10)), 2),
        "traffic": f"{round(random.uniform(0.5, 2.0),2)} Mbps",
    }

def _loop():
    logger.info("[telemetry.collector] started")
    prev = get_snapshot()
    interval = max(1, int(getattr(settings, "STATUS_POLL_INTERVAL_SEC", 10)))
    while _running:
        try:
            # 실제 구현: Tello SDK 상태 읽기/파싱 → snap
            # 현재는 mock
            snap = _mock_sample(prev)
            set_snapshot(snap)
            broadcast_snapshot(snap)
            prev = snap
        except Exception as e:
            logger.warning("[telemetry.collector] loop err: %s", e)
        finally:
            time.sleep(interval)
    logger.info("[telemetry.collector] stopped")

def ensure_started():
    global _running, _thread
    if _thread and _thread.is_alive():
        return
    _running = True
    _thread = threading.Thread(target=_loop, name="telemetry-collector", daemon=True)
    _thread.start()

def stop():
    global _running
    _running = False
