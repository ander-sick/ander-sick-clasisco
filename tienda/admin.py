"""Registro de modelos de la tienda en el administrador de Django."""
from django.contrib import admin

from .models import (
    Carrito,
    Categoria,
    Color,
    Favorito,
    ImagenProducto,
    ItemCarrito,
    Marca,
    Producto,
    Talla,
)


class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 0


class ItemCarritoInline(admin.TabularInline):
    model = ItemCarrito
    extra = 0


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "orden", "activa", "creada")
    list_editable = ("orden", "activa")
    prepopulated_fields = {"slug": ("nombre",)}
    search_fields = ("nombre",)


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activa")
    list_editable = ("activa",)
    prepopulated_fields = {"slug": ("nombre",)}
    search_fields = ("nombre",)


@admin.register(Talla)
class TallaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "etiqueta", "orden")
    list_editable = ("etiqueta", "orden")
    search_fields = ("nombre",)


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "codigo", "orden")
    list_editable = ("codigo", "orden")
    search_fields = ("nombre",)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "categoria",
        "marca",
        "precio",
        "precio_anterior",
        "stock",
        "destacado",
        "en_oferta",
        "activo",
        "vendidos",
    )
    list_editable = ("precio", "precio_anterior", "stock", "destacado", "en_oferta", "activo")
    list_filter = ("categoria", "marca", "destacado", "en_oferta", "es_nuevo", "activo")
    search_fields = ("nombre", "descripcion")
    prepopulated_fields = {"slug": ("nombre",)}
    filter_horizontal = ("tallas", "colores")
    inlines = [ImagenProductoInline]
    readonly_fields = ("creado", "actualizado", "vendidos")


@admin.register(ImagenProducto)
class ImagenProductoAdmin(admin.ModelAdmin):
    list_display = ("producto", "alt", "orden")
    list_editable = ("alt", "orden")


@admin.register(Favorito)
class FavoritoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "producto", "creado")
    list_filter = ("usuario",)
    search_fields = ("usuario__username", "producto__nombre")


@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ("__str__", "usuario", "session_key", "cantidad_items", "creado")
    inlines = [ItemCarritoInline]


@admin.register(ItemCarrito)
class ItemCarritoAdmin(admin.ModelAdmin):
    list_display = ("producto", "carrito", "talla", "color", "cantidad", "subtotal")
    search_fields = ("producto__nombre",)