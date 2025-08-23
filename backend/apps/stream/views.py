from __future__ import annotations
from django.http import StreamingHttpResponse
from django.conf import settings
import time, logging

from apps.adapters.video_capture import VideoCaptureService
from apps.adapters.tello_sdk import build_from_settings

logger = logging.getLogger(__name__)

_service: VideoCaptureService | None = None
_streamon_sent = False

def _ensure_service():
    global _service, _streamon_sent
    if _service is None:
        _service = VideoCaptureService(getattr(settings, "VIDEO_JPEG_QUALITY", 70))
        _service.start()
    # 실기 모드면 streamon 1회 전송
    try:
        sdk = build_from_settings(settings)
        if not sdk.cfg.mock and not _streamon_sent:
            ok, msg = sdk.send_command("streamon", timeout=3.0)
            logger.info("[/video] streamon -> %s (%s)", ok, msg)
            _streamon_sent = True
    except Exception as e:
        logger.warning("[/video] streamon failed: %s", e)

def video_mjpeg(request):
    _ensure_service()
    boundary = "frame"
    def gen():
        while True:
            buf = _service.last_jpeg()
            if not buf:
                time.sleep(0.05); continue
            yield (b"--" + boundary.encode() + b"\r\n" +
                   b"Content-Type: image/jpeg\r\n" +
                   f"Content-Length: {len(buf)}\r\n\r\n".encode() +
                   buf + b"\r\n")
            time.sleep(0.05)
    return StreamingHttpResponse(gen(), content_type=f"multipart/x-mixed-replace; boundary={boundary}")
