"""Registro de modelos de usuarios en el administrador de Django."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Direccion, Perfil

# Encabezados personalizados del sitio de administración.
admin.site.site_header = "Administración CLASISCO"
admin.site.site_title = "CLASISCO"
admin.site.index_title = "Panel de administración"


class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = "Perfil"
    fk_name = "usuario"


class UserAdmin(BaseUserAdmin):
    inlines = (PerfilInline,)
    list_display = ("username", "email", "first_name", "last_name", "is_staff")
    list_filter = ("is_staff", "is_superuser", "is_active")


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("usuario", "telefono", "actualizado")
    search_fields = ("usuario__username", "usuario__email", "telefono")


@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = (
        "nombre_completo",
        "usuario",
        "ciudad",
        "estado",
        "codigo_postal",
        "es_principal",
    )
    list_filter = ("pais", "estado", "es_principal")
    search_fields = (
        "usuario__username",
        "nombre_completo",
        "calle",
        "ciudad",
    )