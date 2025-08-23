from django.contrib import admin
from django.urls import path, include
from apps.common.health import healthz, readyz
from apps.stream.views import video_mjpeg

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz", healthz),
    path("readyz", readyz),

    path("api/", include("apps.api.urls")),
    path("video", video_mjpeg),
]
