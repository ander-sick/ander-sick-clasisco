"""Rutas del panel administrativo."""
from django.urls import path

from . import views

app_name = "panel"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("api/estadisticas/", views.api_estadisticas, name="api_estadisticas"),
]