from __future__ import annotations

import time
import logging
import threading
from typing import Optional

from django.http import StreamingHttpResponse
from django.conf import settings

from apps.adapters.video_capture import VideoCaptureService
from apps.adapters.tello_sdk import get_sdk_singleton

logger = logging.getLogger(__name__)

_service: Optional[VideoCaptureService] = None
_service_lock = threading.Lock()

_streamon_lock = threading.Lock()
_streamon_sent = False


def _ensure_streamon_once():
    global _streamon_sent
    if _streamon_sent:
        return
    with _streamon_lock:
        if _streamon_sent:
            return
        try:
            sdk = get_sdk_singleton(settings, bind_state=False)
            if not getattr(sdk.cfg, "mock", False):
                sdk.send_command("command", timeout=2.0)
                ok, msg = sdk.send_command("streamon", timeout=3.0)
                if not ok:
                    raise RuntimeError(f"streamon not ok: {msg}")
                logger.info("[/video] streamon started (ok=True, msg=%s)", msg)
            else:
                logger.info("[/video] mock mode → streamon skip")
            _streamon_sent = True
        except Exception as e:
            # 여기서 실패해도 스트림 제너레이터는 살아있게
            logger.warning("[/video] streamon failed: %s", e)


def _ensure_service():
    global _service
    if _service is not None:
        return
    with _service_lock:
        if _service is None:
            quality = getattr(settings, "VIDEO_JPEG_QUALITY", 70)
            _service = VideoCaptureService(quality)
            _service.start()
            logger.info("[/video] VideoCaptureService started (quality=%s)", quality)


def _mjpeg_generator(boundary: str, target_fps: int):
    """
    - 프레임 없을 때도 연결 유지 (짧게 sleep)
    - 클라이언트 끊김/서버 셧다운 시 즉시 종료 (GeneratorExit/BrokenPipe/OSError)
    """
    global _service

    sleep_interval = 1.0 / max(1, target_fps)
    try:
        while True:
            if _service is None:
                time.sleep(0.05)
                continue

            t0 = time.perf_counter()
            try:
                buf = _service.last_jpeg()
            except Exception as e:
                logger.debug("[/video] last_jpeg error: %s", e)
                buf = None

            if not buf:
                # 프레임이 잠시 없더라도 연결 유지
                time.sleep(0.05)
                continue

            try:
                yield (
                    b"--" + boundary.encode() + b"\r\n"
                    + b"Content-Type: image/jpeg\r\n"
                    + f"Content-Length: {len(buf)}\r\n\r\n".encode()
                    + buf + b"\r\n"
                )
            except (BrokenPipeError, OSError):
                # 클라이언트가 먼저 끊었음 → 조용히 종료
                return

            # FPS 스로틀링
            elapsed = time.perf_counter() - t0
            if elapsed < sleep_interval:
                time.sleep(sleep_interval - elapsed)

    except GeneratorExit:
        # 서버가 커넥션 정리 중 → 즉시 종료
        return
    except Exception as e:
        # 그 외 에러는 경고만
        logger.warning("[/video] generator error: %s", e)
        return


def video_mjpeg(request):
    boundary = getattr(settings, "VIDEO_MJPEG_BOUNDARY", "frame")
    target_fps = int(getattr(settings, "VIDEO_STREAM_FPS", 20))

    _ensure_service()
    _ensure_streamon_once()

    resp = StreamingHttpResponse(
        _mjpeg_generator(boundary=boundary, target_fps=target_fps),
        content_type=f"multipart/x-mixed-replace; boundary={boundary}",
    )
    # 스트리밍/프록시 버퍼 방지
    resp["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp["Pragma"] = "no-cache"
    resp["Expires"] = "0"
    resp["X-Accel-Buffering"] = "no"  # nginx 사용 시
    return resp
