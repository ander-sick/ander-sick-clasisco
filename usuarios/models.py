"""Modelos de usuarios: perfil y direcciones de envío."""
from django.conf import settings
from django.db import models


class Perfil(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",
    )
    telefono = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to="perfiles/", blank=True, null=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"

    def __str__(self):
        return self.usuario.get_full_name() or self.usuario.username

    @property
    def nombre(self):
        return self.usuario.first_name

    @property
    def apellidos(self):
        return self.usuario.last_name


class Direccion(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="direcciones",
    )
    etiqueta = models.CharField(max_length=60, blank=True, help_text="Ej. Casa, Oficina")
    nombre_completo = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20)
    calle = models.CharField(max_length=200)
    ciudad = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=12)
    pais = models.CharField(max_length=80, default="México")
    referencias = models.CharField(max_length=250, blank=True)
    es_principal = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Dirección"
        verbose_name_plural = "Direcciones"
        ordering = ["-es_principal", "id"]

    def __str__(self):
        return (
            f"{self.nombre_completo} — {self.calle}, {self.ciudad}, "
            f"{self.estado} ({self.codigo_postal})"
        )

    def save(self, *args, **kwargs):
        if self.es_principal:
            Direccion.objects.filter(usuario=self.usuario).update(es_principal=False)
        super().save(*args, **kwargs)