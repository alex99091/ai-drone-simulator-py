import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services.tello_client import tello

def ok(action=None, **extra):
    payload = {"ok": True}
    if action:
        payload["action"] = action
    payload.update(extra)
    return JsonResponse(payload)

def fail(msg, status=400, **extra):
    d = {"ok": False, "error": str(msg)}
    d.update(extra)
    return JsonResponse(d, status=status)

def _json(request):
    try:
        if not request.body:
            return {}
        return json.loads(request.body.decode("utf-8"))
    except Exception:
        return {}

def _distance(p, default=20, min_v=1, max_v=500):
    try:
        val = int(p.get("cm", default))
    except Exception:
        val = default
    return max(min_v, min(val, max_v))

def _degrees(p, default=90):
    try:
        val = int(p.get("deg", default))
    except Exception:
        val = default
    return max(1, min(val, 360))

@csrf_exempt
def health(request):
    try:
        status = tello.status()
        return ok("health", **status)
    except Exception as e:
        return fail(e, 500)

@csrf_exempt
def takeoff(request):
    if request.method != "POST": return fail("Method not allowed", 405)
    try:
        tello.takeoff()
        return ok("takeoff")
    except Exception as e:
        return fail(e, 500)

@csrf_exempt
def land(request):
    if request.method != "POST": return fail("Method not allowed", 405)
    try:
        tello.land()
        return ok("land")
    except Exception as e:
        return fail(e, 500)

@csrf_exempt
def emergency(request):
    if request.method != "POST": return fail("Method not allowed", 405)
    try:
        tello.emergency()
        return ok("emergency")
    except Exception as e:
        return fail(e, 500)

@csrf_exempt
def move_forward(request):
    if request.method != "POST": return fail("Method not allowed", 405)
    p = _json(request)
    try:
        cm = _distance(p)
        tello.forward(cm)
        return ok("forward", cm=cm)
    except Exception as e:
        return fail(e, 500)

@csrf_exempt
def move_back(request):
    if request.method != "POST": return fail("Method not allowed", 405)
    p = _json(request)
    try:
        cm = _distance(p)
        tello.back(cm)
        return ok("back", cm=cm)
    except Exception as e:
        return fail(e, 500)

@csrf_exempt
def move_left(request):
    if request.method != "POST": return fail("Method not allowed", 405)
    p = _json(request)
    try:
        cm = _distance(p)
        tello.left(cm)
        return ok("left", cm=cm)
    except Exception as e:
        return fail(e, 500)

@csrf_exempt
def move_right(request):
    if request.method != "POST": return fail("Method not allowed", 405)
    p = _json(request)
    try:
        cm = _distance(p)
        tello.right(cm)
        return ok("right", cm=cm)
    except Exception as e:
        return fail(e, 500)

@csrf_exempt
def move_up(request):
    if request.method != "POST": return fail("Method not allowed", 405)
    p = _json(request)
    try:
        cm = _distance(p)
        tello.up(cm)
        return ok("up", cm=cm)
    except Exception as e:
        return fail(e, 500)

@csrf_exempt
def move_down(request):
    if request.method != "POST": return fail("Method not allowed", 405)
    p = _json(request)
    try:
        cm = _distance(p)
        tello.down(cm)
        return ok("down", cm=cm)
    except Exception as e:
        return fail(e, 500)

@csrf_exempt
def rotate_cw(request):
    if request.method != "POST": return fail("Method not allowed", 405)
    p = _json(request)
    try:
        deg = _degrees(p)
        tello.cw(deg)
        return ok("cw", deg=deg)
    except Exception as e:
        return fail(e, 500)

@csrf_exempt
def rotate_ccw(request):
    if request.method != "POST": return fail("Method not allowed", 405)
    p = _json(request)
    try:
        deg = _degrees(p)
        tello.ccw(deg)
        return ok("ccw", deg=deg)
    except Exception as e:
        return fail(e, 500)
