from __future__ import annotations
import json, time, logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

_default = {
    "battery": 0, "height": 0, "yaw": 0, "pitch": 0, "roll": 0,
    "pos": {"x": 0, "y": 0, "z": 0},
    "wifi": 0, "speed": 0, "traffic": "0 Mbps",
}

_mem: Dict[str, Any] = {"snapshot": _default.copy(), "ts": 0.0}

def _redis_client():
    try:
        import redis
        from urllib.parse import urlparse
        from django.conf import settings
        parsed = urlparse(settings.REDIS_URL)
        return redis.Redis(
            host=parsed.hostname, port=parsed.port,
            db=int((parsed.path or "/0").lstrip("/")),
            socket_connect_timeout=0.5, socket_timeout=0.5,
        )
    except Exception as e:
        logger.debug("[telemetry.store] Redis unavailable: %s", e)
        return None

KEY = "telemetry:snapshot"

def set_snapshot(data: Dict[str, Any]) -> None:
    # 키 이름 맞춤(없는 키는 기본값으로 보정)
    snap = {**_default, **data}
    if "pos" in data and isinstance(data["pos"], dict):
        snap["pos"] = {**_default["pos"], **data["pos"]}
    r = _redis_client()
    if r:
        try:
            r.set(KEY, json.dumps({"data": snap, "ts": time.time()}))
            return
        except Exception as e:
            logger.warning("[telemetry.store] Redis set failed: %s", e)
    # fallback: memory
    _mem["snapshot"] = snap
    _mem["ts"] = time.time()

def get_snapshot() -> Dict[str, Any]:
    r = _redis_client()
    if r:
        try:
            v = r.get(KEY)
            if v:
                payload = json.loads(v)
                return payload.get("data", _default.copy())
        except Exception as e:
            logger.warning("[telemetry.store] Redis get failed: %s", e)
    return _mem.get("snapshot", _default.copy())
