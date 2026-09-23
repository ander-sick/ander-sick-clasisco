"""Rutas de la aplicación de usuarios."""
from django.urls import path

from . import views

app_name = "usuarios"

urlpatterns = [
    path("registro/", views.registro, name="registro"),
    path("iniciar-sesion/", views.iniciar_sesion, name="iniciar_sesion"),
    path("cerrar-sesion/", views.cerrar_sesion, name="cerrar_sesion"),
    path("perfil/", views.perfil, name="perfil"),
    path("perfil/editar/", views.editar_perfil, name="editar_perfil"),
    path("direcciones/", views.direcciones, name="direcciones"),
    path("direcciones/nueva/", views.nueva_direccion, name="nueva_direccion"),
    path("direcciones/<int:pk>/editar/", views.editar_direccion, name="editar_direccion"),
    path("direcciones/<int:pk>/eliminar/", views.eliminar_direccion, name="eliminar_direccion"),
]