"""Vistas auxiliares del proyecto (páginas de error)."""
from django.shortcuts import render


def pagina_no_encontrada(request, exception=None):
    """Página 404 personalizada."""
    return render(request, "404.html", status=404)


def error_del_servidor(request):
    """Página 500 personalizada."""
    return render(request, "500.html", status=500)