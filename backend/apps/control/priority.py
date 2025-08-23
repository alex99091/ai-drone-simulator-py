from dataclasses import dataclass
from typing import Dict, Optional

# 우선순위 테이블: 숫자가 작을수록 먼저 처리
ACTION_BASE: Dict[str, int] = {
    "emergency": 0,
    "land": 0,
    "takeoff": 1,
    "move": 5,         # 기본은 낮음
}

MOVE_ADJUST: Dict[str, int] = {
    "up": 3,
    "down": 3,
    "cw": 4,
    "ccw": 4,
    # forward/back/left/right 는 기본 5 유지
}

def compute_priority(action: str, direction: Optional[str] = None) -> int:
    base = ACTION_BASE.get(action, 5)
    if action == "move" and direction:
        base = MOVE_ADJUST.get(direction, base)
    return base

@dataclass(order=True)
class PrioritizedItem:
    priority: int
    seq: int
    payload: dict  # {type:"control", action, direction?, speed?}
