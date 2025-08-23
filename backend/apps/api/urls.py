from django.urls import path
from .views import tello_status

urlpatterns = [
    path("tello/status", tello_status),
]
