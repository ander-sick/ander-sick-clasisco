"""Vistas de pedidos: checkout, confirmación, historial, seguimiento y avisos."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from tienda.services import obtener_carrito, totales_carrito

from .forms import CheckoutForm
from .models import Notificacion, Pedido
from .services import (
    crear_pedido,
    marcar_notificaciones_leidas,
    pasos_seguimiento,
)


@login_required
def checkout(request):
    """Paso final de la compra: dirección + método de pago."""
    carrito = obtener_carrito(request)
    if not carrito or carrito.cantidad_items == 0:
        messages.warning(request, "Tu carrito está vacío. Agrega productos para continuar.")
        return redirect("tienda:carrito")

    totales = totales_carrito(carrito)
    form = CheckoutForm(request.POST or None, usuario=request.user)

    if request.method == "POST" and form.is_valid():
        direccion = form.obtener_direccion()
        pedido = crear_pedido(
            request,
            direccion=direccion,
            metodo_pago=form.cleaned_data["metodo_pago"],
            notas=form.cleaned_data.get("notas", ""),
        )
        return redirect("pedidos:confirmacion", numero=pedido.numero)

    return render(
        request,
        "checkout.html",
        {
            "form": form,
            "carrito": carrito,
            "totales": totales,
            "tiene_direcciones": request.user.direcciones.exists(),
            "metodos_pago": Pedido.METODOS_PAGO,
        },
    )


@login_required
def confirmacion_pedido(request, numero):
    """Página de éxito con el número de pedido generado."""
    pedido = get_object_or_404(
        Pedido.objects.prefetch_related("detalles"),
        numero=numero,
        usuario=request.user,
    )
    return render(request, "confirmacion_pedido.html", {"pedido": pedido})


@login_required
def lista_pedidos(request):
    """Historial de pedidos del cliente."""
    pedidos = (
        Pedido.objects.filter(usuario=request.user)
        .select_related("estado")
        .prefetch_related("detalles")
    )
    return render(request, "pedidos.html", {"pedidos": pedidos})


@login_required
def seguimiento_pedido(request, numero):
    """Seguimiento visual de un pedido."""
    pedido = get_object_or_404(
        Pedido.objects.select_related("estado", "envio_info", "pago").prefetch_related("detalles"),
        numero=numero,
        usuario=request.user,
    )
    pasos = pasos_seguimiento(pedido)
    return render(
        request,
        "seguimiento.html",
        {"pedido": pedido, "pasos": pasos},
    )


@login_required
def notificaciones(request):
    """Centro de notificaciones del cliente."""
    if request.method == "POST":
        marcar_notificaciones_leidas(request.user)
        messages.success(request, "Todas las notificaciones fueron marcadas como leídas.")
        return redirect("pedidos:notificaciones")

    avisos = request.user.notificaciones.all()[:50]
    return render(request, "notificaciones.html", {"avisos": avisos})