from django.http import StreamingHttpResponse, HttpResponse
from django.conf import settings
import time

from apps.adapters.video_capture import VideoCaptureService

_service: VideoCaptureService | None = None

def _ensure_service():
    global _service
    if _service is None:
        _service = VideoCaptureService(getattr(settings, "VIDEO_JPEG_QUALITY", 70))
        _service.start()

def video_mjpeg(request):
    """
    GET /video → multipart/x-mixed-replace
    """
    _ensure_service()
    boundary = "frame"

    def gen():
        while True:
            buf = _service.last_jpeg()
            if not buf:
                time.sleep(0.1)
                continue
            yield (b"--" + boundary.encode() + b"\r\n" +
                   b"Content-Type: image/jpeg\r\n" +
                   f"Content-Length: {len(buf)}\r\n\r\n".encode() +
                   buf + b"\r\n")
            time.sleep(0.05)  # 최대 20fps

    resp = StreamingHttpResponse(gen(), content_type=f"multipart/x-mixed-replace; boundary={boundary}")
    return resp
