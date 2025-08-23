from django.urls import path
from apps.ws.consumers import CommandConsumer, StatusConsumer

websocket_urlpatterns = [
    path("ws/tello/command", CommandConsumer.as_asgi()),
    path("ws/tello/status",  StatusConsumer.as_asgi()),
]
