from django.http import JsonResponse
def healthz(request):
    return JsonResponse({"ok": True})
