from django.http import JsonResponse, HttpResponse

def ping(request):
    return JsonResponse({"ok": True, "service": "vision"})

def index(request):
    return HttpResponse("Vision service")