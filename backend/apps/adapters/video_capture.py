"""
영상 캡처 서비스 뼈대.
- 추후: UDP 11111 H.264 수신 → 디코드(OpenCV/ffmpeg) → JPEG
- 현재: 더미 프레임(검정 이미지) 생성해 last_jpeg()로 제공
"""

import logging
import threading
import time
from typing import Optional

import numpy as np
import cv2

logger = logging.getLogger(__name__)

class VideoCaptureService:
    def __init__(self, jpeg_quality: int = 70):
        self.jpeg_quality = int(jpeg_quality)
        self._lock = threading.Lock()
        self._last_jpeg: Optional[bytes] = None
        self._running = False
        self._th: Optional[threading.Thread] = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._th = threading.Thread(target=self._loop_dummy, daemon=True)
        self._th.start()
        logger.info("[VideoCaptureService] started (dummy frames)")

    def stop(self):
        self._running = False
        if self._th and self._th.is_alive():
            self._th.join(timeout=1.0)
        logger.info("[VideoCaptureService] stopped")

    def last_jpeg(self) -> Optional[bytes]:
        with self._lock:
            return self._last_jpeg

    # ---- dummy generator (검정 배경에 시간 텍스트) ----
    def _loop_dummy(self):
        while self._running:
            img = np.zeros((360, 640, 3), dtype=np.uint8)
            ts = time.strftime("%H:%M:%S")
            cv2.putText(img, f"NO STREAM (dummy) {ts}", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (180, 180, 180), 2, cv2.LINE_AA)
            ok, buf = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality])
            if ok:
                with self._lock:
                    self._last_jpeg = buf.tobytes()
            time.sleep(0.2)  # 5 FPS
