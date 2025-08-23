import logging
import threading
import time
from queue import PriorityQueue
from typing import Optional, Dict, Any, Tuple

from django.conf import settings

from apps.control.priority import PrioritizedItem, compute_priority
from apps.control.schemas import validate_control_message
from apps.adapters.tello_sdk import build_from_settings, TelloSDK

logger = logging.getLogger(__name__)

# 전역 싱글톤들
_queue: PriorityQueue[PrioritizedItem] = PriorityQueue()
_seq = 0
_worker_thread: Optional[threading.Thread] = None
_running = False
_sdk: Optional[TelloSDK] = None

# 레이트리밋(명령 과다 전송 방지)
MIN_INTERVAL_SEC = 0.04  # 40ms

def _next_seq() -> int:
    global _seq
    _seq += 1
    return _seq

def ensure_started():
    """외부(WS Consumer 등)에서 호출해 워커 시작 보장."""
    global _worker_thread, _running, _sdk
    if _worker_thread and _worker_thread.is_alive():
        return
    if _sdk is None:
        _sdk = build_from_settings(settings)
    _running = True
    _worker_thread = threading.Thread(target=_worker_loop, name="control-dispatcher", daemon=True)
    _worker_thread.start()
    logger.info("[dispatcher] started")

def stop():
    global _running
    _running = False
    logger.info("[dispatcher] stopping...")

def enqueue_control(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    클라이언트에서 받은 control 메시지 enqueue.
    반환: enqueued 정보(우선순위/시퀀스)
    """
    msg = validate_control_message(raw)
    prio = compute_priority(msg["action"], msg.get("direction"))
    item = PrioritizedItem(priority=prio, seq=_next_seq(), payload=msg)
    _queue.put(item)
    logger.info("[dispatcher] enqueued: %s (p=%d, seq=%d)", msg, prio, item.seq)
    ensure_started()
    return {"enqueued": True, "priority": prio, "seq": item.seq}

def _payload_to_sdk_command(payload: Dict[str, Any]) -> str:
    """
    간단 매핑: 실제 Tello SDK 명령 문자열로 변환.
    추후 세밀 튜닝 가능.
    """
    action = payload["action"]
    if action == "takeoff":
        return "takeoff"
    if action == "land":
        return "land"
    if action == "emergency":
        return "emergency"
    if action == "move":
        d = payload["direction"]
        s = payload["speed"]
        # 방향→SDK 문자열 매핑 예시
        if d == "forward": return f"forward {s}"
        if d == "back":    return f"back {s}"
        if d == "left":    return f"left {s}"
        if d == "right":   return f"right {s}"
        if d == "up":      return f"up {s}"
        if d == "down":    return f"down {s}"
        if d == "cw":      return f"cw {s*3}"    # 각속도→각도 변환은 임시(추후 교체)
        if d == "ccw":     return f"ccw {s*3}"
    return "command"  # fallback (SDK 활성화)

def _worker_loop():
    last_sent = 0.0
    assert _sdk is not None, "SDK must be initialized"
    # SDK 활성화(필요시): Tello는 첫 연결에 "command" 전송이 필요
    _sdk.send_command("command")

    while _running:
        try:
            item: PrioritizedItem = _queue.get(timeout=0.2)
        except Exception:
            continue

        # 레이트리밋
        now = time.time()
        wait = MIN_INTERVAL_SEC - (now - last_sent)
        if wait > 0:
            time.sleep(wait)

        payload = item.payload
        cmd = _payload_to_sdk_command(payload)
        ok, msg = _sdk.send_command(cmd, timeout=5.0)
        last_sent = time.time()

        status = {"type": "ack", "ok": bool(ok), "action": payload["action"], "seq": item.seq, "detail": msg}
        logger.info("[dispatcher] sent: %s -> %s", cmd, status)

        # TODO: 나중에 WS로 ACK 브로드캐스트(Consumer에서 hook) 연결

    logger.info("[dispatcher] exited")
