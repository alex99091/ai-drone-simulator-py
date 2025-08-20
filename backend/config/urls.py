from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/dash/", include("dash.urls")),
    path("api/control/", include("control.urls")),
    path("api/vision/", include("vision.urls")),
]