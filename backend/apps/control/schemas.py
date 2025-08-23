from typing import Dict, Any
from apps.common.errors import BadRequest

ACTIONS = {"move", "takeoff", "land", "emergency"}
DIRECTIONS = {"forward", "back", "left", "right", "up", "down", "cw", "ccw"}

def validate_control_message(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    입력 예:
      { "type":"control", "action":"move", "direction":"forward", "speed":50 }
      { "type":"control", "action":"takeoff" }
    반환: 정규화된 dict (불변 키 유지: action/direction/speed)
    """
    if not isinstance(data, dict):
        raise BadRequest("body must be JSON object")

    if data.get("type") != "control":
        raise BadRequest('invalid "type", expected "control"')

    action = data.get("action")
    if action not in ACTIONS:
        raise BadRequest(f'invalid "action": {action}')

    norm: Dict[str, Any] = {"type": "control", "action": action}

    if action == "move":
        direction = data.get("direction")
        if direction not in DIRECTIONS:
            raise BadRequest(f'invalid "direction": {direction}')
        speed = data.get("speed", 50)
        # Tello 통상 속도 범위(예시): 10~100
        try:
            speed = int(speed)
        except Exception:
            raise BadRequest('"speed" must be integer')
        if not (10 <= speed <= 100):
            raise BadRequest('"speed" must be between 10 and 100')

        norm["direction"] = direction
        norm["speed"] = speed

    return norm
