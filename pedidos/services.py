"""Servicios de pedidos: creación de pedidos, pagos, envíos y seguimiento."""
import uuid

from django.db import transaction
from django.utils import timezone

from tienda.services import obtener_carrito, totales_carrito, vaciar_carrito

from .models import DetallePedido, Envio, EstadoPedido, Notificacion, Pago, Pedido


def generar_numero_pedido():
    """Genera un número de pedido legible y único: CLS-20260922-XXXXXX."""
    return f"CLS-{timezone.now():%Y%m%d}-{uuid.uuid4().hex[:6].upper()}"


def _estado_inicial():
    estado, _ = EstadoPedido.objects.get_or_create(
        slug="recibido",
        defaults={
            "nombre": "Pedido recibido",
            "orden": 1,
            "descripcion": "Hemos recibido tu pedido y estamos validándolo.",
        },
    )
    return estado


def inicializar_estados():
    """Crea los estados por defecto del flujo de pedidos si no existen."""
    estados = [
        ("recibido", "Pedido recibido", 1, "Hemos recibido tu pedido."),
        ("en_preparacion", "En preparación", 2, "Estamos preparando tu pedido."),
        ("enviado", "Enviado", 3, "Tu pedido está en camino."),
        ("entregado", "Entregado", 4, "Tu pedido fue entregado."),
        ("cancelado", "Cancelado", 99, "El pedido fue cancelado."),
    ]
    for slug, nombre, orden, descripcion in estados:
        EstadoPedido.objects.get_or_create(
            slug=slug,
            defaults={
                "nombre": nombre,
                "orden": orden,
                "descripcion": descripcion,
            },
        )


def crear_notificacion(usuario, titulo, mensaje):
    """Crea una notificación para el usuario."""
    return Notificacion.objects.create(
        usuario=usuario, titulo=titulo, mensaje=mensaje
    )


@transaction.atomic
def crear_pedido(request, *, direccion, metodo_pago, notas=""):
    """Convierte el carrito en un pedido confirmado.

    Descuenta stock, crea el pago y el envío, notifica al cliente y
    vacía el carrito. Devuelve el pedido creado.
    """
    carrito = obtener_carrito(request)
    if not carrito or carrito.cantidad_items == 0:
        raise ValueError("El carrito está vacío.")

    items = list(carrito.items.select_related("producto", "talla", "color"))
    totales = totales_carrito(carrito)

    pedido = Pedido.objects.create(
        numero=generar_numero_pedido(),
        usuario=request.user,
        estado=_estado_inicial(),
        estado_pago="pendiente",
        metodo_pago=metodo_pago,
        subtotal=totales["subtotal"],
        descuento=totales["descuento"],
        envio=totales["envio"],
        total=totales["total"],
        direccion_envio=str(direccion),
        notas=notas,
    )

    for item in items:
        DetallePedido.objects.create(
            pedido=pedido,
            producto=item.producto,
            nombre=item.producto.nombre,
            precio=item.producto.precio,
            cantidad=item.cantidad,
            talla=item.talla.nombre if item.talla else "",
            color=item.color.nombre if item.color else "",
            subtotal=item.producto.precio * item.cantidad,
        )
        producto = item.producto
        producto.stock = max(producto.stock - item.cantidad, 0)
        producto.vendidos += item.cantidad
        producto.save(update_fields=["stock", "vendidos"])

    Pago.objects.create(
        pedido=pedido,
        metodo=metodo_pago,
        estado="pendiente",
        monto=totales["total"],
    )
    Envio.objects.create(
        pedido=pedido,
        costo=totales["envio"],
        fecha_entrega_estimada=timezone.now().date() + timezone.timedelta(days=5),
    )

    crear_notificacion(
        request.user,
        f"Pedido {pedido.numero} confirmado",
        "Gracias por tu compra. Estamos preparando tu pedido para enviarlo.",
    )

    vaciar_carrito(carrito)
    return pedido


def actualizar_estado_pedido(pedido, estado_slug, notificar=True):
    """Cambia el estado de un pedido y opcionalmente notifica al cliente."""
    estado = EstadoPedido.objects.get(slug=estado_slug)
    pedido.estado = estado
    pedido.save(update_fields=["estado", "actualizado"])

    if notificar:
        crear_notificacion(
            pedido.usuario,
            f"Tu pedido {pedido.numero} {estado.nombre.lower()}",
            estado.descripcion or f"El estado de tu pedido cambió a: {estado.nombre}.",
        )
    return pedido


def registrar_envio(pedido, empresa, numero_seguimiento):
    """Guarda los datos del envío y marca el pedido como enviado."""
    envio, _ = Envio.objects.get_or_create(pedido=pedido)
    envio.empresa = empresa
    envio.numero_seguimiento = numero_seguimiento
    envio.enviado = True
    envio.fecha_envio = timezone.now()
    envio.save()
    pedido.estado_pago = "pagado"
    pedido.save(update_fields=["estado_pago"])
    return actualizar_estado_pedido(pedido, "enviado", notificar=True)


def pasos_seguimiento(pedido):
    """Devuelve la línea de tiempo visual del pedido según su estado."""
    pasos = list(
        EstadoPedido.objects.filter(slug__in=[
            "recibido", "en_preparacion", "enviado", "entregado",
        ]).order_by("orden")
    )
    actual_orden = pedido.estado.orden if not pedido.es_cancelado else 0
    resultado = []
    for paso in pasos:
        resultado.append(
            {
                "estado": paso,
                "completado": paso.orden <= actual_orden,
                "actual": paso.orden == actual_orden,
            }
        )
    return resultado


def marcar_notificaciones_leidas(usuario):
    """Marca como leídas todas las notificaciones del usuario."""
    return usuario.notificaciones.filter(leida=False).update(leida=True)