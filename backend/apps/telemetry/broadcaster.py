import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def broadcast_snapshot(snapshot: Dict[str, Any]) -> None:
    """
    Channels group 'tello_status'로 telemetry 전송.
    Redis/channel layer가 없어도 서버는 죽지 않도록 try/except 가드.
    """
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        layer = get_channel_layer()
        if not layer:
            return
        async_to_sync(layer.group_send)(
            "tello_status",
            {"type": "telemetry.message", "data": snapshot},
        )
    except Exception as e:
        logger.debug("[telemetry.broadcast] skip: %s", e)
