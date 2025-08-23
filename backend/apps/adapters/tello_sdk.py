"""
Tello SDK 어댑터 뼈대.
- 실제 UDP 통신은 추후 단계에서 구현.
- 지금은 인터페이스만 정의하고, DEBUG/MOCK일 땐 no-op 동작.
"""

from dataclasses import dataclass
from typing import Callable, Optional, Tuple
import logging
import os

logger = logging.getLogger(__name__)

@dataclass
class TelloConfig:
    ip: str = "192.168.10.1"
    cmd_port: int = 8889
    state_port: int = 8890
    video_port: int = 11111
    mock: bool = True  # DEBUG 단계 기본 mock

class TelloSDK:
    """Tello 명령/상태/영상 포트에 대한 최소 인터페이스 정의"""

    def __init__(self, config: TelloConfig):
        self.cfg = config
        self._running_state_listener = False
        logger.info("[TelloSDK] init mock=%s ip=%s", self.cfg.mock, self.cfg.ip)

    # --- Commands ---
    def send_command(self, command: str, timeout: float = 5.0) -> Tuple[bool, str]:
        """
        명령 전송. 실제 구현에서는 UDP 8889로 전송 후 응답 수신.
        반환: (ok, message)
        """
        if self.cfg.mock:
            logger.info("[MOCK] send_command: %s (timeout=%.1f)", command, timeout)
            return True, "ok(mock)"
        # TODO: 실제 UDP 송신/수신 구현
        logger.warning("[TelloSDK] real send_command not implemented")
        return False, "not-implemented"

    # --- State listener ---
    def start_state_listener(self, on_state: Callable[[dict], None]) -> Callable[[], None]:
        """
        상태(8890) 수신 루프 시작.
        반환: stop() 콜러블
        """
        self._running_state_listener = True
        logger.info("[TelloSDK] start_state_listener (mock=%s)", self.cfg.mock)

        def stop():
            self._running_state_listener = False
            logger.info("[TelloSDK] stop_state_listener")

        # TODO: 실제 소켓 루프(스레드) 구현
        return stop

    # --- Cleanup ---
    def close(self):
        logger.info("[TelloSDK] close()")
        # TODO: 소켓 정리
        pass


def build_from_settings(django_settings) -> TelloSDK:
    """Django settings로부터 기본 인스턴스 구성"""
    mock_default = str(os.getenv("TELLO_MOCK", "true")).lower() == "true" or django_settings.DEBUG
    cfg = TelloConfig(
        ip=django_settings.TELLO["IP"],
        cmd_port=django_settings.TELLO["CMD_PORT"],
        state_port=django_settings.TELLO["STATE_PORT"],
        video_port=django_settings.TELLO["VIDEO_PORT"],
        mock=mock_default,
    )
    return TelloSDK(cfg)
