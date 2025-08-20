from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="vision_index"),
    path("health", views.ping, name="vision_health"),
]