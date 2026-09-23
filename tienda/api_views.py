"""Vistas de la API REST de la tienda (Django REST Framework)."""
from rest_framework import viewsets

from .models import Categoria, Producto
from .serializers import CategoriaSerializer, ProductoSerializer


class ProductoViewSet(viewsets.ReadOnlyModelViewSet):
    """API pública de productos."""

    queryset = Producto.objects.filter(activo=True).select_related(
        "categoria", "marca"
    )
    serializer_class = ProductoSerializer
    lookup_field = "slug"

    def get_queryset(self):
        qs = super().get_queryset()
        busqueda = self.request.query_params.get("q")
        categoria = self.request.query_params.get("categoria")
        if busqueda:
            qs = qs.filter(nombre__icontains=busqueda)
        if categoria:
            qs = qs.filter(categoria__slug=categoria)
        return qs


class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """API pública de categorías."""

    queryset = Categoria.objects.filter(activa=True)
    serializer_class = CategoriaSerializer
    lookup_field = "slug"