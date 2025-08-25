# apps/adapters/tello_sdk.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional, Tuple, Dict
import logging, os, socket, threading, time

logger = logging.getLogger(__name__)

@dataclass
class TelloConfig:
    ip: str = "192.168.10.1"
    cmd_port: int = 8889
    state_port: int = 8890
    video_port: int = 11111
    mock: bool = True  # DEBUG 기본 mock

class TelloSDK:
    """
    - send_command(): UDP 8889 전송/응답 대기
    - start_state_listener(): UDP 8890 수신 루프
    - ensure_state_bound(): 필요 시 런타임에 상태소켓 바인드
    """

    def __init__(self, config: TelloConfig, *, bind_state: bool = True):
        self.cfg = config
        self._cmd_sock: Optional[socket.socket] = None
        self._state_sock: Optional[socket.socket] = None
        self._state_running = False
        self._state_thread: Optional[threading.Thread] = None
        self._wants_state = bool(bind_state)
        logger.info("[TelloSDK] init mock=%s ip=%s", self.cfg.mock, self.cfg.ip)

        if not self.cfg.mock:
            # 명령 소켓 준비
            self._cmd_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._cmd_sock.settimeout(5.0)
            if self._wants_state:
                self._bind_state_socket()

    # ---- 내부: 상태 소켓 바인드 ----
    def _bind_state_socket(self):
        if self.cfg.mock or self._state_sock is not None:
            return
        self._state_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # SO_REUSEADDR는 macOS에서도 도움되지만, 동일 포트 중복 bind는 불가
        self._state_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._state_sock.bind(("", self.cfg.state_port))
        self._state_sock.settimeout(1.0)
        logger.info("[TelloSDK] state socket bound (udp:%d)", self.cfg.state_port)

    def ensure_state_bound(self):
        """나중에 필요해지면 동적으로 상태 소켓을 바인드"""
        try:
            self._wants_state = True
            self._bind_state_socket()
        except OSError as e:
            logger.warning("[TelloSDK] ensure_state_bound failed: %s", e)
            raise

    # --- Commands ---
    def send_command(self, command: str, timeout: float = 5.0) -> Tuple[bool, str]:
        if self.cfg.mock:
            logger.info("[MOCK] send_command: %s", command)
            return True, "ok(mock)"

        if not self._cmd_sock:
            return False, "cmd socket not ready"

        try:
            self._cmd_sock.settimeout(timeout)
            self._cmd_sock.sendto(command.encode("utf-8"), (self.cfg.ip, self.cfg.cmd_port))
            data, _ = self._cmd_sock.recvfrom(1024)
            resp = data.decode(errors="ignore").strip().lower()
            ok = (resp == "ok")
            return ok, resp
        except socket.timeout:
            return False, "timeout"
        except Exception as e:
            logger.warning("[TelloSDK] send_command error: %s", e)
            return False, str(e)

    # --- State listener ---
    def start_state_listener(self, on_state: Callable[[Dict], None]) -> Callable[[], None]:
        self._state_running = True
        if self.cfg.mock:
            def loop_mock():
                while self._state_running:
                    on_state({})
                    time.sleep(1.0)
            self._state_thread = threading.Thread(target=loop_mock, daemon=True)
            self._state_thread.start()
            logger.info("[TelloSDK] state listener started (mock)")
            def stop():
                self._state_running = False
            return stop

        # 필요 시 상태 소켓 바인드
        if self._state_sock is None:
            self.ensure_state_bound()

        def _parse(line: str) -> Dict:
            out: Dict[str, float] = {}
            for kv in line.strip().split(";"):
                if not kv or ":" not in kv: continue
                k, v = kv.split(":", 1)
                try: out[k] = float(v)
                except ValueError: pass
            return {
                "battery": int(out.get("bat", 0)),
                "height": round(out.get("h", 0.0) / 100.0, 2),
                "yaw": int(out.get("yaw", 0.0)),
                "pitch": int(out.get("pitch", 0.0)),
                "roll": int(out.get("roll", 0.0)),
                "_vgx": out.get("vgx", 0.0),
                "_vgy": out.get("vgy", 0.0),
                "_vgz": out.get("vgz", 0.0),
            }

        def loop():
            logger.info("[TelloSDK] state listener started (udp:%d)", self.cfg.state_port)
            while self._state_running:
                try:
                    data, _ = self._state_sock.recvfrom(2048)
                    txt = data.decode(errors="ignore")
                    on_state(_parse(txt))
                except socket.timeout:
                    continue
                except Exception as e:
                    logger.warning("[TelloSDK] state listener err: %s", e)
                    time.sleep(0.1)
            logger.info("[TelloSDK] state listener stopped")

        self._state_thread = threading.Thread(target=loop, daemon=True)
        self._state_thread.start()

        def stop():
            self._state_running = False
        return stop

    def close(self):
        self._state_running = False
        try:
            if self._state_thread and self._state_thread.is_alive():
                self._state_thread.join(timeout=1.0)
        except Exception:
            pass
        for s in (self._state_sock, self._cmd_sock):
            try: s and s.close()
            except Exception: pass
        logger.info("[TelloSDK] close() done")

# -------- 싱글턴 팩토리 --------
_singleton: Optional[TelloSDK] = None
def get_sdk_singleton(django_settings, *, bind_state: bool) -> TelloSDK:
    global _singleton
    mock_default = str(os.getenv("TELLO_MOCK", "true")).lower() == "true" or django_settings.DEBUG
    if _singleton is None:
        cfg = TelloConfig(
            ip=django_settings.TELLO["IP"],
            cmd_port=django_settings.TELLO["CMD_PORT"],
            state_port=django_settings.TELLO["STATE_PORT"],
            video_port=django_settings.TELLO["VIDEO_PORT"],
            mock=(mock_default is True and str(os.getenv("TELLO_MOCK","")).lower() != "false"),
        )
        _singleton = TelloSDK(cfg, bind_state=bind_state)
    else:
        if bind_state:
            _singleton.ensure_state_bound()
    return _singleton

# (이전과 호환용) — 새 코드는 get_sdk_singleton 사용 권장
def build_from_settings(django_settings) -> TelloSDK:
    return get_sdk_singleton(django_settings, bind_state=True)
