from __future__ import annotations
import json
import logging
from typing import Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

# 고정 키 (프론트 API 스키마 영향 없음)
_SNAPSHOT_KEY = "telemetry:snapshot"

# 런타임 백엔드 선택 (settings로부터)
_use_redis = (
    getattr(settings, "TELEMETRY_CACHE_BACKEND", "memory") == "redis"
    and bool(getattr(settings, "TELEMETRY_REDIS_URL", "").strip())
)

_r = None
if _use_redis:
    try:
        import redis  # redis-py
        _r = redis.from_url(
            settings.TELEMETRY_REDIS_URL,
            decode_responses=True,  # str로 입출력
        )
        _r.ping()
        logger.info("[telemetry.store] redis connected: %s", settings.TELEMETRY_REDIS_URL)
    except Exception as e:
        logger.warning("[telemetry.store] redis init failed -> fallback to memory: %s", e)
        _r = None

# 메모리 캐시(프로세스 로컬)
_mem: dict[str, Any] = {}

def _serialize(data: dict[str, Any]) -> str:
    try:
        return json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    except Exception as e:
        logger.warning("[telemetry.store] serialize failed: %s", e)
        return "{}"

def _deserialize(s: Optional[str]) -> dict[str, Any]:
    if not s:
        return {}
    try:
        return json.loads(s)
    except Exception as e:
        logger.warning("[telemetry.store] deserialize failed: %s", e)
        return {}

def set(data: dict[str, Any], ttl: Optional[int] = None) -> None:
    """
    텔레메트리 스냅샷 저장.
    ttl=None 허용. Redis일 때만 ex=int(ttl) 전달, None이면 ex 미전달.
    """
    if _r is not None:
        try:
            payload = _serialize(data)
            if ttl is not None:
                _r.set(_SNAPSHOT_KEY, payload, ex=int(ttl))
            else:
                _r.set(_SNAPSHOT_KEY, payload)  # ex 미전달
            return
        except Exception as e:
            logger.warning("[telemetry.store] Redis set failed: %s", e)

    # 메모리 폴백
    _mem[_SNAPSHOT_KEY] = data

def get(default: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """
    텔레메트리 스냅샷 읽기. 없으면 default 또는 {}.
    """
    if _r is not None:
        try:
            s = _r.get(_SNAPSHOT_KEY)
            data = _deserialize(s)
            if data:
                return data
        except Exception as e:
            logger.warning("[telemetry.store] Redis get failed: %s", e)

    return (_mem.get(_SNAPSHOT_KEY) or default or {}).copy()

def ping() -> bool:
    if _r is None:
        return True
    try:
        _r.ping()
        return True
    except Exception:
        return False

# --- 호환 별칭 (과거 코드와 100% 호환) ---
write_snapshot = set
read_snapshot = get
set_status_snapshot = set
get_status_snapshot = get
# collector가 기대하는 이름(당신 로그의 ImportError 원인)
set_snapshot = set
get_snapshot = get

__all__ = [
    "set", "get", "ping",
    "write_snapshot", "read_snapshot",
    "set_status_snapshot", "get_status_snapshot",
    "set_snapshot", "get_snapshot",
]
