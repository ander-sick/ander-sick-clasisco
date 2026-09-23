"""Rutas de la API REST (Django REST Framework)."""
from rest_framework.routers import DefaultRouter

from .api_views import CategoriaViewSet, ProductoViewSet

router = DefaultRouter()
router.register("productos", ProductoViewSet, basename="api-productos")
router.register("categorias", CategoriaViewSet, basename="api-categorias")

urlpatterns = router.urls