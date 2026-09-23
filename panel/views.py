"""Vistas del panel administrativo: resumen, estadísticas y gráficos."""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from pedidos.models import EstadoPedido, Pedido
from tienda.models import Producto

Usuario = get_user_model()


def _es_staff(usuario):
    return usuario.is_authenticated and usuario.is_staff


@user_passes_test(_es_staff, login_url="usuarios:iniciar_sesion")
def dashboard(request):
    """Resumen general de la tienda para el administrador."""
    desde = timezone.now() - timedelta(days=180)

    pedidos = Pedido.objects.exclude(estado__slug="cancelado")
    ventas_totales = pedidos.aggregate(total=Sum("total"))["total"] or 0
    total_pedidos = Pedido.objects.count()
    total_clientes = Usuario.objects.count()
    total_productos = Producto.objects.count()
    stock_bajo = Producto.objects.filter(activo=True, stock__lte=5).order_by("stock")[:10]
    ultimos_pedidos = (
        Pedido.objects.select_related("estado", "usuario").order_by("-creado")[:10]
    )

    resumen = {
        "ventas_totales": float(ventas_totales),
        "total_pedidos": total_pedidos,
        "total_clientes": total_clientes,
        "total_productos": total_productos,
        "pedidos_ultimos_30_dias": Pedido.objects.filter(
            creado__gte=timezone.now() - timedelta(days=30)
        ).count(),
    }
    return render(
        request,
        "panel/dashboard.html",
        {
            "resumen": resumen,
            "stock_bajo": stock_bajo,
            "ultimos_pedidos": ultimos_pedidos,
            "desde": desde,
        },
    )


@user_passes_test(_es_staff, login_url="usuarios:iniciar_sesion")
def api_estadisticas(request):
    """Datos en JSON para los gráficos del panel (Chart.js)."""
    desde = timezone.now() - timedelta(days=180)

    # Ingresos mensuales de los últimos 6 meses.
    ingresos = (
        Pedido.objects.filter(creado__gte=desde)
        .exclude(estado__slug="cancelado")
        .annotate(mes=TruncMonth("creado"))
        .values("mes")
        .annotate(total=Sum("total"))
        .order_by("mes")
    )
    series_ingresos = [
        {
            "mes": r["mes"].strftime("%Y-%m") if r["mes"] else "-",
            "total": float(r["total"] or 0),
        }
        for r in ingresos
    ]

    # Pedidos por estado.
    pedidos_por_estado = [
        {"nombre": e.nombre, "cantidad": e.pedidos.count()}
        for e in EstadoPedido.objects.all().order_by("orden")
    ]

    # Productos más vendidos.
    top_productos = list(
        Producto.objects.filter(activo=True, vendidos__gt=0)
        .order_by("-vendidos")[:6]
        .values("nombre", "vendidos")
    )

    return JsonResponse(
        {
            "ingresos_mensuales": series_ingresos,
            "pedidos_por_estado": pedidos_por_estado,
            "top_productos": top_productos,
        }
    )