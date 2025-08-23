from __future__ import annotations
import logging, threading, time, shutil, subprocess
from typing import Optional

import numpy as np
import cv2

logger = logging.getLogger(__name__)

class VideoCaptureService:
    """
    - ffmpeg 존재하면: udp://@:11111 수신 → mjpeg → stdout 파이프 → last_jpeg 버퍼
    - 없으면: 더미 프레임 생성으로 폴백
    """
    def __init__(self, jpeg_quality: int = 70):
        self.jpeg_quality = int(jpeg_quality)
        self._lock = threading.Lock()
        self._last_jpeg: Optional[bytes] = None
        self._running = False
        self._th: Optional[threading.Thread] = None
        self._mode = "dummy"
        self._proc: Optional[subprocess.Popen] = None

    def start(self):
        if self._running:
            return
        self._running = True

        if shutil.which("ffmpeg"):
            self._mode = "ffmpeg"
            self._th = threading.Thread(target=self._loop_ffmpeg, daemon=True)
        else:
            self._mode = "dummy"
            self._th = threading.Thread(target=self._loop_dummy, daemon=True)

        self._th.start()
        logger.info("[VideoCaptureService] started mode=%s", self._mode)

    def stop(self):
        self._running = False
        if self._proc and self._proc.poll() is None:
            try: self._proc.terminate()
            except Exception: pass
        if self._th and self._th.is_alive():
            self._th.join(timeout=1.0)
        logger.info("[VideoCaptureService] stopped")

    def last_jpeg(self) -> Optional[bytes]:
        with self._lock:
            return self._last_jpeg

    # -------- loops --------
    def _loop_ffmpeg(self):
        cmd = [
            "ffmpeg",
            "-hwaccel", "auto",
            "-fflags", "nobuffer",
            "-flags", "low_delay",
            "-i", "udp://@:11111?overrun_nonfatal=1&fifo_size=50000000",
            "-f", "mjpeg",
            "-q:v", str(max(2, min(31, int(31 - (self.jpeg_quality/100)*29)))),
            "pipe:1",
        ]
        logger.info("[VideoCaptureService] spawn: %s", " ".join(cmd))
        try:
            self._proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0)
        except Exception as e:
            logger.warning("[VideoCaptureService] ffmpeg spawn failed: %s -> fallback to dummy", e)
            return self._loop_dummy()

        # 간단한 JPEG 프레임 경계 파서(MJPEG 스트림)
        buf = b""
        while self._running and self._proc and self._proc.stdout:
            chunk = self._proc.stdout.read(4096)
            if not chunk:
                time.sleep(0.01); continue
            buf += chunk
            while True:
                soi = buf.find(b"\xff\xd8")
                eoi = buf.find(b"\xff\xd9", soi + 2) if soi != -1 else -1
                if soi != -1 and eoi != -1:
                    frame = buf[soi:eoi+2]
                    buf = buf[eoi+2:]
                    with self._lock:
                        self._last_jpeg = frame
                else:
                    break

        logger.info("[VideoCaptureService] ffmpeg loop ended")

    def _loop_dummy(self):
        import numpy as np, cv2, time
        while self._running:
            img = np.zeros((360, 640, 3), dtype=np.uint8)
            ts = time.strftime("%H:%M:%S")
            cv2.putText(img, f"NO STREAM (dummy) {ts}", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (180, 180, 180), 2, cv2.LINE_AA)
            ok, buf = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality])
            if ok:
                with self._lock:
                    self._last_jpeg = buf.tobytes()
            time.sleep(0.2)  # ~5fps
