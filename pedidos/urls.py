"""Rutas de la aplicación de pedidos."""
from django.urls import path

from . import views

app_name = "pedidos"

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("confirmacion/<str:numero>/", views.confirmacion_pedido, name="confirmacion"),
    path("seguimiento/<str:numero>/", views.seguimiento_pedido, name="seguimiento"),
    path("notificaciones/", views.notificaciones, name="notificaciones"),
    path("", views.lista_pedidos, name="pedidos"),
]