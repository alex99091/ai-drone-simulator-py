# backend/backend/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import SessionMiddlewareStack

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

django_asgi_app = get_asgi_application()

# 라우팅은 에러를 숨기지 않고 직접 임포트 (오류 시 즉시 Trace)
from .routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": SessionMiddlewareStack(URLRouter(websocket_urlpatterns)),
})
