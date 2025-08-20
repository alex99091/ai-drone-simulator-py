from django.http import JsonResponse, HttpResponse
import random

def index(request):
    return HttpResponse("Dashboard")

def metrics(request):
    data = {
        "battery": random.randint(60, 95),
        "wifi": random.randint(40, 100),
        "speed": round(random.uniform(0.0, 4.0), 1),
        "height": round(random.uniform(0.5, 2.0), 1),
        "traffic": f"{random.randint(1, 50)} Mbps",
    }
    return JsonResponse(data)
