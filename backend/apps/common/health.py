from django.http import JsonResponse

def healthz(request):
    return JsonResponse({"ok": True})

def readyz(request):
    """
    최소 준비 상태 체크:
      - Redis PING (channels layer 백엔드)
    """
    try:
        from urllib.parse import urlparse
        import redis  # pip install redis
        from django.conf import settings

        parsed = urlparse(settings.REDIS_URL)
        r = redis.Redis(
            host=parsed.hostname,
            port=parsed.port,
            db=int((parsed.path or "/0").lstrip("/")),
            socket_connect_timeout=1.0,
        )
        r.ping()
        return JsonResponse({"ok": True, "redis": "up"})
    except Exception as e:
        return JsonResponse({"ok": False, "redis": "down", "message": str(e)}, status=503)
