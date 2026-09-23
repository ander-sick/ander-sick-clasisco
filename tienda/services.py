"""Servicios de la tienda: lógica de carrito, totales y cantidades.

Esta capa aísla la lógica de negocio del carrito para que pueda reutilizarse
desde las vistas, los procesadores de contexto y el módulo de pedidos.
"""
from decimal import Decimal

from django.db.models import Q

from .models import Carrito, ItemCarrito

# Umbral para envío gratuito y costo de envío estándar (MXN).
ENVIO_GRATIS_DESDE = Decimal("1000.00")
COSTO_ENVIO = Decimal("99.99")


def obtener_carrito(request, crear=False):
    """Devuelve el carrito activo (usuario autenticado o sesión anónima).

    Con `crear=True` crea el carrito si no existe.
    """
    if request.user.is_authenticated:
        carrito = (
            Carrito.objects.filter(usuario=request.user)
            .order_by("-actualizado")
            .first()
        )
        if carrito is None and crear:
            carrito = Carrito.objects.create(usuario=request.user)
        return carrito

    session_key = request.session.session_key
    if session_key:
        carrito = (
            Carrito.objects.filter(session_key=session_key, usuario__isnull=True)
            .order_by("-actualizado")
            .first()
        )
        if carrito is None and crear:
            carrito = Carrito.objects.create(session_key=session_key)
        return carrito

    if crear:
        # Fuerza la creación de la clave de sesión antes de guardar el carrito.
        if not request.session.session_key:
            request.session["_carrito_init"] = True
            request.session.save()
        return Carrito.objects.create(session_key=request.session.session_key)

    return None


def transferir_carrito(request, usuario):
    """Asocia el carrito de una sesión anónima al usuario que inicia sesión."""
    session_key = request.session.session_key
    if not session_key:
        return

    carrito_anonimo = Carrito.objects.filter(
        session_key=session_key, usuario__isnull=True
    ).first()
    if not carrito_anonimo:
        return

    carrito_usuario = (
        Carrito.objects.filter(usuario=usuario).order_by("-actualizado").first()
    )
    if carrito_usuario and carrito_usuario.id != carrito_anonimo.id:
        # Fusiona los artículos en el carrito existente del usuario.
        for item in carrito_anonimo.items.all():
            existente = _buscar_item(carrito_usuario, item.producto, item.talla, item.color)
            if existente:
                existente.cantidad = min(
                    existente.cantidad + item.cantidad,
                    item.producto.stock or 1,
                )
                existente.save()
            else:
                item.carrito = carrito_usuario
                item.save()
        carrito_anonimo.delete()
    else:
        carrito_anonimo.usuario = usuario
        carrito_anonimo.save()


def _buscar_item(carrito, producto, talla, color):
    """Busca un artículo con la misma combinación producto/talla/color."""
    qs = ItemCarrito.objects.filter(carrito=carrito, producto=producto)
    qs = qs.filter(talla=talla) if talla else qs.filter(talla__isnull=True)
    qs = qs.filter(color=color) if color else qs.filter(color__isnull=True)
    return qs.first()


def agregar_item(request, producto, cantidad=1, talla=None, color=None):
    """Agrega (o acumula) un producto al carrito validando el stock."""
    if cantidad < 1:
        raise ValueError("La cantidad debe ser al menos 1.")

    if producto.stock <= 0:
        raise ValueError(f"{producto.nombre} está agotado.")

    carrito = obtener_carrito(request, crear=True)
    existente = _buscar_item(carrito, producto, talla, color)
    nueva_cantidad = (existente.cantidad if existente else 0) + cantidad

    if nueva_cantidad > producto.stock:
        raise ValueError(
            f"Stock insuficiente de {producto.nombre}: solo hay "
            f"{producto.stock} unidades."
        )

    if existente:
        existente.cantidad = nueva_cantidad
        existente.save()
        return existente

    return ItemCarrito.objects.create(
        carrito=carrito,
        producto=producto,
        talla=talla,
        color=color,
        cantidad=cantidad,
    )


def actualizar_cantidad(item_id, cantidad):
    """Actualiza la cantidad de un artículo, eliminándolo si llega a 0."""
    item = ItemCarrito.objects.get(pk=item_id)
    if cantidad <= 0:
        item.delete()
        return None
    item.cantidad = cantidad
    item.save()
    return item


def eliminar_item(item_id):
    """Elimina un artículo del carrito."""
    ItemCarrito.objects.filter(pk=item_id).delete()


def vaciar_carrito(carrito):
    """Elimina todos los artículos del carrito."""
    if carrito:
        carrito.items.all().delete()


def totales_carrito(carrito):
    """Calcula subtotal, descuento, envío y total del carrito."""
    if not carrito:
        return {
            "subtotal": Decimal("0"),
            "descuento": Decimal("0"),
            "envio": Decimal("0"),
            "total": Decimal("0"),
        }

    items = carrito.items.select_related("producto").all()
    subtotal = sum((i.producto.precio * i.cantidad for i in items), Decimal("0"))
    descuento = sum(
        (
            (i.producto.precio_anterior - i.producto.precio) * i.cantidad
            for i in items
            if i.producto.precio_anterior and i.producto.precio_anterior > i.producto.precio
        ),
        Decimal("0"),
    )
    envio = (
        Decimal("0")
        if subtotal >= ENVIO_GRATIS_DESDE or subtotal == 0
        else COSTO_ENVIO
    )
    total = max(subtotal - descuento + envio, Decimal("0"))

    return {
        "subtotal": subtotal,
        "descuento": descuento,
        "envio": envio,
        "total": total,
    }