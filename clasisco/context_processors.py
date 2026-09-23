"""Procesadores de contexto disponibles en todas las plantillas.

Proporcionan al frontend: categorías, marcas, contador del carrito y
notificaciones no leídas.
"""
from tienda.models import Categoria, Marca
from tienda.services import obtener_carrito


def globales(request):
    """Datos globales para todas las plantillas."""
    carrito = obtener_carrito(request)

    notificaciones_no_leidas = 0
    if request.user.is_authenticated:
        notificaciones_no_leidas = (
            request.user.notificaciones.filter(leida=False).count()
        )

    return {
        "clasisco_nombre": "CLASISCO",
        "carrito": carrito,
        "carrito_count": carrito.cantidad_items if carrito else 0,
        "categorias": Categoria.objects.filter(activa=True).order_by("orden", "nombre"),
        "marcas": Marca.objects.filter(activa=True).order_by("nombre"),
        "notificaciones_no_leidas": notificaciones_no_leidas,
    }