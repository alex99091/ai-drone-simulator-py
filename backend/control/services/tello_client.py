import os
import threading
from typing import Any, Dict

DEV_NO_DRONE = os.environ.get("DEV_NO_DRONE", "0") == "1"

try:
    if not DEV_NO_DRONE:
        from djitellopy import Tello  # type: ignore
    else:
        Tello = None  # Dev dummy mode
except Exception:
    # 안전장치: import 실패 시 더미로 전환
    Tello = None
    DEV_NO_DRONE = True


class _DummyTello:
    """드론이 없거나 라이브러리 미설치 시 개발용 더미."""
    def connect(self): return True
    def end(self): pass
    def get_battery(self): return 100
    def get_height(self): return 0
    def takeoff(self): return True
    def land(self): return True
    def emergency(self): return True
    def move_forward(self, x): return True
    def move_back(self, x): return True
    def move_left(self, x): return True
    def move_right(self, x): return True
    def move_up(self, x): return True
    def move_down(self, x): return True
    def rotate_clockwise(self, x): return True
    def rotate_counter_clockwise(self, x): return True


class TelloClient:
    """스레드 세이프 싱글톤 + 지연 연결."""
    _instance = None
    _class_lock = threading.Lock()

    def __init__(self):
        self._lock = threading.Lock()
        self._connected = False
        self._tello = _DummyTello() if (DEV_NO_DRONE or Tello is None) else Tello()

    @classmethod
    def instance(cls) -> "TelloClient":
        if cls._instance is None:
            with cls._class_lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    # 내부 공통 실행 헬퍼
    def _do(self, fn, *args, **kwargs):
        with self._lock:
            self.ensure()
            return fn(*args, **kwargs)

    # 외부 노출 API ---------------------------------------------------------
    def ensure(self):
        """연결 보장 (이미 연결되었다면 no-op)."""
        if not self._connected:
            try:
                self._tello.connect()
                self._connected = True
            except Exception as e:
                # 연결 실패 시 플래그를 유지해 다음 호출에서 재시도
                self._connected = False
                raise e

    def status(self) -> Dict[str, Any]:
        ok = False
        battery = None
        height = None
        try:
            self.ensure()
            battery = self._tello.get_battery()
            height = self._tello.get_height()
            ok = True
        except Exception:
            ok = False
        return {"connected": ok and self._connected, "battery": battery, "height": height}

    def takeoff(self): return self._do(self._tello.takeoff)
    def land(self): return self._do(self._tello.land)
    def emergency(self): return self._do(self._tello.emergency)

    def forward(self, cm: int): return self._do(self._tello.move_forward, int(cm))
    def back(self, cm: int): return self._do(self._tello.move_back, int(cm))
    def left(self, cm: int): return self._do(self._tello.move_left, int(cm))
    def right(self, cm: int): return self._do(self._tello.move_right, int(cm))
    def up(self, cm: int): return self._do(self._tello.move_up, int(cm))
    def down(self, cm: int): return self._do(self._tello.move_down, int(cm))

    def cw(self, deg: int): return self._do(self._tello.rotate_clockwise, int(deg))
    def ccw(self, deg: int): return self._do(self._tello.rotate_counter_clockwise, int(deg))

    def close(self):
        with self._lock:
            try:
                self._tello.end()
            finally:
                self._connected = False


tello = TelloClient.instance()