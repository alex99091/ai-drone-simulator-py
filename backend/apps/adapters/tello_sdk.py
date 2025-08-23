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
    """

    def __init__(self, config: TelloConfig):
        self.cfg = config
        self._cmd_sock: Optional[socket.socket] = None
        self._state_sock: Optional[socket.socket] = None
        self._state_running = False
        self._state_thread: Optional[threading.Thread] = None
        logger.info("[TelloSDK] init mock=%s ip=%s", self.cfg.mock, self.cfg.ip)

        if not self.cfg.mock:
            # 명령 소켓: 바인드 없이 송신만, 응답은 recvfrom
            self._cmd_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._cmd_sock.settimeout(5.0)
            # 상태 소켓: 8890 수신 대기
            self._state_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._state_sock.bind(("", self.cfg.state_port))
            self._state_sock.settimeout(1.0)

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
            # 모의: 주기적으로 빈 dict 콜백(collector가 mock 처리)
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

        if not self._state_sock:
            raise RuntimeError("state socket not ready")

        def _parse(line: str) -> Dict:
            # 예시: "pitch:0;roll:0;yaw:5;vgx:0;vgy:0;vgz:0;templ:68;temph:70;tof:10;h:10;bat:87;baro:30.49;time:0;agx:0.00;agy:0.00;agz:-999.00;"
            out: Dict[str, float] = {}
            for kv in line.strip().split(";"):
                if not kv: continue
                if ":" not in kv: continue
                k, v = kv.split(":", 1)
                try:
                    out[k] = float(v)
                except ValueError:
                    pass
            # 필요한 키만 변환/정규화
            snap = {
                "battery": int(out.get("bat", 0)),
                "height": round(out.get("h", 0.0) / 100.0, 2),  # cm -> m
                "yaw": int(out.get("yaw", 0.0)),
                "pitch": int(out.get("pitch", 0.0)),
                "roll": int(out.get("roll", 0.0)),
                # 속도(cm/s) 그대로 전달(collector에서 m/s 적분용)
                "_vgx": out.get("vgx", 0.0),
                "_vgy": out.get("vgy", 0.0),
                "_vgz": out.get("vgz", 0.0),
            }
            return snap

        def loop():
            logger.info("[TelloSDK] state listener started (udp:%d)", self.cfg.state_port)
            while self._state_running:
                try:
                    data, _ = self._state_sock.recvfrom(2048)
                    txt = data.decode(errors="ignore")
                    snap = _parse(txt)
                    on_state(snap)
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
            try:
                s and s.close()
            except Exception:
                pass
        logger.info("[TelloSDK] close() done")

def build_from_settings(django_settings) -> TelloSDK:
    mock_default = str(os.getenv("TELLO_MOCK", "true")).lower() == "true" or django_settings.DEBUG
    cfg = TelloConfig(
        ip=django_settings.TELLO["IP"],
        cmd_port=django_settings.TELLO["CMD_PORT"],
        state_port=django_settings.TELLO["STATE_PORT"],
        video_port=django_settings.TELLO["VIDEO_PORT"],
        mock=mock_default is True and str(os.getenv("TELLO_MOCK", "")).lower() != "false",
    )
    return TelloSDK(cfg)
