"""Rutas de la tienda."""
from django.urls import path

from . import views

app_name = "tienda"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("productos/", views.productos, name="productos"),
    path("productos/categoria/<slug:categoria_slug>/", views.productos_por_categoria, name="productos_por_categoria"),
    path("producto/<slug:slug>/", views.detalle_producto, name="detalle_producto"),
    # Carrito
    path("carrito/", views.ver_carrito, name="carrito"),
    path("carrito/agregar/", views.agregar_al_carrito, name="agregar_carrito"),
    path("carrito/actualizar/<int:item_id>/", views.actualizar_carrito, name="actualizar_carrito"),
    path("carrito/eliminar/<int:item_id>/", views.eliminar_carrito, name="eliminar_carrito"),
    # Favoritos
    path("favoritos/", views.favoritos, name="favoritos"),
    path("favoritos/alternar/", views.alternar_favorito, name="alternar_favorito"),
]