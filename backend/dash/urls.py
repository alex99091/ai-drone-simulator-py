from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="dash_index"),
    path("metrics", views.metrics, name="dash_metrics"),
]
