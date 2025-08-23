from django.http import JsonResponse
from apps.telemetry.store import get_snapshot
from apps.telemetry.collector import ensure_started as ensure_collector

def tello_status(request):
    # 첫 접근 시 콜렉터 기동(중복 기동 안전)
    ensure_collector()
    snap = get_snapshot()
    return JsonResponse(snap)
