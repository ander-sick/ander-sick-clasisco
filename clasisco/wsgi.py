"""Configuración WSGI para el proyecto CLASISCO."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "clasisco.settings")

application = get_wsgi_application()