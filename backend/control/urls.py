from django.urls import path
from . import views

urlpatterns = [
    path("health", views.health),

    path("takeoff", views.takeoff),
    path("land", views.land),
    path("emergency", views.emergency),

    path("forward", views.move_forward),
    path("back", views.move_back),
    path("left", views.move_left),
    path("right", views.move_right),
    path("up", views.move_up),
    path("down", views.move_down),

    path("cw", views.rotate_cw),
    path("ccw", views.rotate_ccw),
]
