from django.contrib import admin
from django.urls import path
from apps.common.health import healthz

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz", healthz),
    # 이후 단계에서:
    # path("api/", include("apps.api.urls")),
    # path("video", video_stream_view),
]
