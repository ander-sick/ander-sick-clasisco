"""Vistas principales de la tienda (catálogo, carrito y favoritos)."""
import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, resolve_url

from .models import Categoria, Color, Favorito, ItemCarrito, Producto, Talla
from .services import (
    agregar_item,
    actualizar_cantidad,
    eliminar_item,
    obtener_carrito,
    totales_carrito,
)


def inicio(request):
    """Página principal de CLASISCO."""
    productos_destacados = Producto.objects.filter(activo=True, destacado=True)[:12]
    productos_nuevos = Producto.objects.filter(activo=True, es_nuevo=True)[:12]
    productos_oferta = Producto.objects.filter(activo=True, en_oferta=True)[:12]
    productos_recientes = Producto.objects.filter(activo=True)[:12]

    return render(
        request,
        "inicio.html",
        {
            "productos_destacados": productos_destacados,
            "productos_nuevos": productos_nuevos,
            "productos_oferta": productos_oferta,
            "productos_recientes": productos_recientes,
        },
    )


def productos(request):
    """Catálogo de productos con buscador, filtros, ordenamiento y paginación."""
    query = request.GET.get("q", "").strip()
    categoria_slug = request.GET.get("categoria", "")
    marca_slug = request.GET.get("marca", "")
    ordenar = request.GET.get("orden", "-creado")
    talla_id = request.GET.get("talla", "")
    color_id = request.GET.get("color", "")
    solo_oferta = request.GET.get("solo_oferta") == "1"
    solo_nuevo = request.GET.get("solo_nuevo") == "1"
    solo_destacado = request.GET.get("solo_destacado") == "1"

    qs = (
        Producto.objects.select_related("categoria", "marca")
        .prefetch_related("tallas", "colores")
        .filter(activo=True)
    )

    if query:
        qs = qs.filter(
            Q(nombre__icontains=query)
            | Q(descripcion__icontains=query)
            | Q(categoria__nombre__icontains=query)
            | Q(marca__nombre__icontains=query)
        )

    if categoria_slug:
        qs = qs.filter(categoria__slug=categoria_slug)

    if marca_slug:
        qs = qs.filter(marca__slug=marca_slug)

    if talla_id:
        qs = qs.filter(tallas__id=talla_id)

    if color_id:
        qs = qs.filter(colores__id=color_id)

    if solo_oferta:
        qs = qs.filter(en_oferta=True)

    if solo_nuevo:
        qs = qs.filter(es_nuevo=True)

    if solo_destacado:
        qs = qs.filter(destacado=True)

    ordenes_validas = {
        "-creado": "-creado",
        "creado": "creado",
        "precio": "precio",
        "-precio": "-precio",
        "-vendidos": "-vendidos",
        "nombre": "nombre",
    }
    qs = qs.order_by(ordenes_validas.get(ordenar, "-creado")).distinct()

    paginator = Paginator(qs, 12)
    page_number = request.GET.get("page")
    productos_paginados = paginator.get_page(page_number)

    return render(
        request,
        "productos.html",
        {
            "productos": productos_paginados,
            "query": query,
            "categoria_slug": categoria_slug,
            "marca_slug": marca_slug,
            "ordenar": ordenar,
            "talla_id": talla_id,
            "color_id": color_id,
            "solo_oferta": solo_oferta,
            "solo_nuevo": solo_nuevo,
            "solo_destacado": solo_destacado,
            "tallas": Talla.objects.all(),
            "colores": Color.objects.all(),
        },
    )


def productos_por_categoria(request, categoria_slug):
    categoria = get_object_or_404(Categoria, slug=categoria_slug, activa=True)
    qs = (
        Producto.objects.filter(activo=True, categoria=categoria)
        .select_related("marca")
        .prefetch_related("tallas", "colores")
        .order_by("-creado")
    )
    paginator = Paginator(qs, 12)
    page_number = request.GET.get("page")
    productos_paginados = paginator.get_page(page_number)

    return render(
        request,
        "productos.html",
        {
            "productos": productos_paginados,
            "categoria": categoria,
            "categoria_slug": categoria.slug,
            "tallas": Talla.objects.all(),
            "colores": Color.objects.all(),
        },
    )


def detalle_producto(request, slug):
    producto = get_object_or_404(Producto, slug=slug, activo=True)
    productos_relacionados = (
        Producto.objects.filter(activo=True, categoria=producto.categoria)
        .exclude(pk=producto.pk)
        .select_related("marca")
        .order_by("-vendidos")[:8]
    )

    en_favoritos = False
    if request.user.is_authenticated:
        en_favoritos = Favorito.objects.filter(
            usuario=request.user, producto=producto
        ).exists()

    return render(
        request,
        "detalle_producto.html",
        {
            "producto": producto,
            "productos_relacionados": productos_relacionados,
            "en_favoritos": en_favoritos,
        },
    )


# ---------------------------------------------------------------------------
# Carrito (AJAX + respaldo sin JavaScript)
# ---------------------------------------------------------------------------
def _es_xhr(request):
    return (
        request.headers.get("x-requested-with", "").lower() == "xmlhttprequest"
        or request.headers.get("accept", "").find("application/json") != -1
    )


def ver_carrito(request):
    carrito = obtener_carrito(request)
    totales = totales_carrito(carrito)
    return render(
        request, "carrito.html", {"carrito": carrito, "totales": totales}
    )


def agregar_al_carrito(request):
    """Agrega un producto al carrito. Responde JSON en AJAX."""
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        data = request.POST

    producto_id = data.get("producto") or request.POST.get("producto")
    try:
        cantidad = int(data.get("cantidad", 1) or 1)
    except (TypeError, ValueError):
        cantidad = 1

    talla_id = data.get("talla") or request.POST.get("talla")
    color_id = data.get("color") or request.POST.get("color")

    producto = get_object_or_404(Producto, pk=producto_id, activo=True)
    talla = Talla.objects.filter(pk=talla_id).first() if talla_id else None
    color = Color.objects.filter(pk=color_id).first() if color_id else None

    try:
        agregar_item(request, producto, cantidad=cantidad, talla=talla, color=color)
    except ValueError as error:
        if _es_xhr(request):
            return JsonResponse({"error": str(error)}, status=400)
        return redirect("tienda:productos")

    carrito = obtener_carrito(request)
    totales = totales_carrito(carrito)
    mensaje = f"{producto.nombre} agregado al carrito"

    if _es_xhr(request):
        return JsonResponse(
            {
                "ok": True,
                "mensaje": mensaje,
                "carrito_count": carrito.cantidad_items if carrito else 0,
                "total": float(totales["total"]),
            }
        )
    return redirect("tienda:carrito")


def actualizar_carrito(request, item_id):
    """Modifica la cantidad de un artículo del carrito."""
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    carrito = obtener_carrito(request)
    if not carrito:
        return JsonResponse({"error": "Carrito no encontrado"}, status=404)

    item = get_object_or_404(ItemCarrito, pk=item_id, carrito=carrito)

    try:
        cantidad = int(request.POST.get("cantidad", 1))
    except (TypeError, ValueError):
        cantidad = 1

    if cantidad <= 0:
        subtotal_antes = float(item.subtotal)
        eliminar_item(item.pk)
        mensaje = "Artículo eliminado del carrito"
        nuevo_subtotal = 0.0
    else:
        if cantidad > item.producto.stock:
            return JsonResponse(
                {"error": f"Stock insuficiente: solo hay {item.producto.stock} unidades."},
                status=400,
            )
        actualizar_cantidad(item.pk, cantidad)
        item.refresh_from_db()
        nuevo_subtotal = float(item.subtotal)
        mensaje = "Cantidad actualizada"

    carrito = obtener_carrito(request)
    totales = totales_carrito(carrito)

    if _es_xhr(request):
        return JsonResponse(
            {
                "ok": True,
                "mensaje": mensaje,
                "carrito_count": carrito.cantidad_items if carrito else 0,
                "item_subtotal": nuevo_subtotal,
                "item_subtotal_anterior": subtotal_antes if cantidad <= 0 else nuevo_subtotal,
                "subtotal": float(totales["subtotal"]),
                "descuento": float(totales["descuento"]),
                "envio": float(totales["envio"]),
                "total": float(totales["total"]),
            }
        )
    return redirect("tienda:carrito")


def eliminar_carrito(request, item_id):
    """Elimina un artículo del carrito."""
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    carrito = obtener_carrito(request)
    if not carrito:
        return JsonResponse({"error": "Carrito no encontrado"}, status=404)

    eliminar_item(item_id)
    carrito = obtener_carrito(request)
    totales = totales_carrito(carrito)

    if _es_xhr(request):
        return JsonResponse(
            {
                "ok": True,
                "mensaje": "Artículo eliminado del carrito",
                "carrito_count": carrito.cantidad_items if carrito else 0,
                "subtotal": float(totales["subtotal"]),
                "descuento": float(totales["descuento"]),
                "envio": float(totales["envio"]),
                "total": float(totales["total"]),
            }
        )
    return redirect("tienda:carrito")


# ---------------------------------------------------------------------------
# Favoritos
# ---------------------------------------------------------------------------
def alternar_favorito(request):
    """Agrega o quita un producto de favoritos (AJAX o tradicional)."""
    if not request.user.is_authenticated:
        if _es_xhr(request):
            return JsonResponse(
                {
                    "login": True,
                    "mensaje": "Inicia sesión para guardar favoritos.",
                    "url": resolve_url("usuarios:iniciar_sesion"),
                },
                status=401,
            )
        return redirect(f"{resolve_url('usuarios:iniciar_sesion')}?next={request.path}")

    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        data = request.POST

    producto_id = data.get("producto") or request.POST.get("producto")
    producto = get_object_or_404(Producto, pk=producto_id, activo=True)

    favorito, creado = Favorito.objects.get_or_create(
        usuario=request.user, producto=producto
    )
    if not creado:
        favorito.delete()

    mensaje = "Agregado a favoritos" if creado else "Eliminado de favoritos"

    if _es_xhr(request):
        return JsonResponse({"ok": True, "guardado": creado, "mensaje": mensaje})
    return redirect(request.META.get("HTTP_REFERER", "tienda:inicio"))


@login_required
def favoritos(request):
    favoritos = Favorito.objects.filter(usuario=request.user).select_related(
        "producto", "producto__categoria", "producto__marca"
    )
    return render(request, "favoritos.html", {"favoritos": favoritos})