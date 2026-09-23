"""Rutas principales del proyecto CLASISCO."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Administración de Django (gestión completa de productos, pedidos, etc.)
    path("admin/", admin.site.urls),
    # Panel administrativo personalizado con estadísticas
    path("panel-admin/", include("panel.urls")),
    # Cuentas de usuario
    path("usuario/", include("usuarios.urls")),
    # Pedidos, checkout y seguimiento
    path("pedidos/", include("pedidos.urls")),
    # API REST (Django REST Framework)
    path("api/", include("tienda.api_urls")),
    # Tienda (inicio, productos, carrito, favoritos)
    path("", include("tienda.urls")),
]

# En desarrollo se sirven los archivos multimedia desde Django.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Páginas de error personalizadas.
handler404 = "clasisco.views.pagina_no_encontrada"
handler500 = "clasisco.views.error_del_servidor"