from __future__ import annotations
import logging, threading, time, math, random
from typing import Optional, Dict, Any
from django.conf import settings
from apps.adapters.tello_sdk import build_from_settings, TelloSDK
from .store import set_snapshot, get_snapshot
from .broadcaster import broadcast_snapshot

logger = logging.getLogger(__name__)

_running = False
_thread: Optional[threading.Thread] = None
_sdk: Optional[TelloSDK] = None

# pos 적분 상태
_pos = {"x": 0.0, "y": 0.0, "z": 0.0}
_last_ts: Optional[float] = None

def _mock_sample(prev: Dict[str, Any]) -> Dict[str, Any]:
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

def _on_state_from_sdk(snap: Dict[str, Any]) -> None:
    global _pos, _last_ts
    # snap 예: {"battery":..,"height":..,"yaw":..,"pitch":..,"roll":..,"_vgx":..,"_vgy":..}
    now = time.time()
    if _last_ts is None: _last_ts = now
    dt = max(0.0, now - _last_ts)
    _last_ts = now

    # Dead reckoning: vgx/vgy(cm/s) -> m/s 로 변환하여 pos 적분
    vx = (snap.get("_vgx") or 0.0) / 100.0
    vy = (snap.get("_vgy") or 0.0) / 100.0
    _pos["x"] += vx * dt
    _pos["y"] += vy * dt

    out = {
        "battery": snap.get("battery", 0),
        "height": snap.get("height", 0.0),
        "yaw": snap.get("yaw", 0),
        "pitch": snap.get("pitch", 0),
        "roll": snap.get("roll", 0),
        "pos": {"x": round(_pos["x"], 2), "y": round(_pos["y"], 2), "z": 0},
        "wifi": 4,
        "speed": round((abs(vx) + abs(vy)) / 2.0, 2),
        "traffic": "—",
    }
    set_snapshot(out)
    broadcast_snapshot(out)

def _loop_mock():
    logger.info("[telemetry.collector] started (mock)")
    prev = get_snapshot()
    interval = max(1, int(getattr(settings, "STATUS_POLL_INTERVAL_SEC", 10)))
    while _running:
        try:
            snap = _mock_sample(prev)
            set_snapshot(snap)
            broadcast_snapshot(snap)
            prev = snap
        except Exception as e:
            logger.warning("[telemetry.collector] loop err: %s", e)
        finally:
            time.sleep(interval)
    logger.info("[telemetry.collector] stopped (mock)")

def _loop_real():
    logger.info("[telemetry.collector] started (real)")
    stop_state = _sdk.start_state_listener(_on_state_from_sdk)
    try:
        # 주기 호출은 상태 수신이 push이므로 가벼운 heartbeat 정도만
        while _running:
            time.sleep(1.0)
    finally:
        try: stop_state()
        except Exception: pass
        logger.info("[telemetry.collector] stopped (real)")

def ensure_started():
    global _running, _thread, _sdk
    if _thread and _thread.is_alive():
        return
    _sdk = build_from_settings(settings)
    _running = True
    target = _loop_mock if _sdk.cfg.mock else _loop_real
    _thread = threading.Thread(target=target, name="telemetry-collector", daemon=True)
    _thread.start()

def stop():
    global _running
    _running = False
