from django.http import JsonResponse

class APIError(Exception):
    status = 500
    code = "internal_error"
    def __init__(self, message="Internal error", *, status=None, code=None, extra=None):
        super().__init__(message)
        if status is not None: self.status = int(status)
        if code is not None: self.code = str(code)
        self.extra = extra or {}

def error_response(exc: Exception):
    if isinstance(exc, APIError):
        payload = {"ok": False, "error": exc.code, "message": str(exc), **exc.extra}
        return JsonResponse(payload, status=exc.status)
    # fallback
    return JsonResponse({"ok": False, "error": "internal_error", "message": str(exc)}, status=500)

class BadRequest(APIError):
    status = 400
    code = "bad_request"

class NotFound(APIError):
    status = 404
    code = "not_found"

class Conflict(APIError):
    status = 409
    code = "conflict"

class ServiceUnavailable(APIError):
    status = 503
    code = "unavailable"
