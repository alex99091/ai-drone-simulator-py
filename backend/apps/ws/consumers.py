from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync
import logging

from apps.control.dispatcher import enqueue_control, ensure_started as ensure_dispatcher
from apps.telemetry.collector import ensure_started as ensure_collector

logger = logging.getLogger(__name__)

class CommandConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.accept()
        ensure_dispatcher()  # 워커 기동 보장
        self.send_json({"type": "hello", "role": "command"})

    def receive_json(self, content, **kwargs):
        # 공통 규격: { type:"control", action, direction?, speed? }
        try:
            res = enqueue_control(content)
            # 즉시 enqueue ACK (실제 송신 ACK은 dispatcher에서 후속 브로드캐스트로 확장 가능)
            self.send_json({"type": "ack", "ok": True, **res})
        except Exception as e:
            logger.warning("command error: %s", e)
            self.send_json({"type": "ack", "ok": False, "message": str(e)})

    def disconnect(self, code):
        pass

class StatusConsumer(JsonWebsocketConsumer):
    GROUP = "tello_status"

    def connect(self):
        self.accept()
        ensure_collector()  # 콜렉터 기동 보장
        try:
            async_to_sync(self.channel_layer.group_add)(self.GROUP, self.channel_name)
        except Exception as e:
            logger.debug("status group add failed: %s", e)
        self.send_json({"type": "hello", "role": "status"})

    def telemetry_message(self, event):
        # broadcaster가 보낸 이벤트를 그대로 전달
        data = event.get("data", {})
        self.send_json({"type": "telemetry", **data})

    def disconnect(self, code):
        try:
            async_to_sync(self.channel_layer.group_discard)(self.GROUP, self.channel_name)
        except Exception:
            pass
