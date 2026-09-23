"""Modelos de la tienda CLASISCO:
Categorías, marcas, tallas, colores, productos, imágenes, favoritos y carrito.
"""
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to="categorias/", blank=True, null=True)
    orden = models.PositiveIntegerField(default=0)
    activa = models.BooleanField(default=True, verbose_name="Activa")
    creada = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("tienda:productos_por_categoria", args=[self.slug])


class Marca(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    logo = models.ImageField(upload_to="marcas/", blank=True, null=True)
    activa = models.BooleanField(default=True, verbose_name="Activa")

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)


class Talla(models.Model):
    nombre = models.CharField(max_length=20, unique=True, verbose_name="Talla")
    etiqueta = models.CharField(max_length=30, blank=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Talla"
        verbose_name_plural = "Tallas"
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre


class Color(models.Model):
    nombre = models.CharField(max_length=60)
    codigo = models.CharField(max_length=7, default="#000000", help_text="Código hexadecimal del color")
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Color"
        verbose_name_plural = "Colores"
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name="productos"
    )
    marca = models.ForeignKey(
        Marca, on_delete=models.SET_NULL, null=True, blank=True, related_name="productos"
    )
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_anterior = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Precio anterior (para descuento)",
    )
    stock = models.PositiveIntegerField(default=0, verbose_name="Existencias")
    imagen = models.ImageField(upload_to="productos/", blank=True, null=True)
    tallas = models.ManyToManyField(Talla, blank=True, related_name="productos")
    colores = models.ManyToManyField(Color, blank=True, related_name="productos")
    destacado = models.BooleanField(default=False, verbose_name="Destacado")
    es_nuevo = models.BooleanField(default=False, verbose_name="Nuevo")
    en_oferta = models.BooleanField(default=False, verbose_name="En oferta")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    vendidos = models.PositiveIntegerField(default=0)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["-creado"]

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        if (
            self.precio_anterior
            and self.precio_anterior > self.precio
            and not self.en_oferta
        ):
            self.en_oferta = True
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("tienda:detalle_producto", args=[self.slug])

    @property
    def descuento_porcentaje(self):
        """Porcentaje de descuento frente al precio anterior."""
        if self.precio_anterior and self.precio_anterior > self.precio:
            return int(
                round((1 - float(self.precio) / float(self.precio_anterior)) * 100)
            )
        return 0


class ImagenProducto(models.Model):
    producto = models.ForeignKey(
        Producto, on_delete=models.CASCADE, related_name="imagenes"
    )
    imagen = models.ImageField(upload_to="productos/galeria/")
    alt = models.CharField(max_length=150, blank=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Imagen de producto"
        verbose_name_plural = "Imágenes de productos"
        ordering = ["orden"]

    def __str__(self):
        return f"Imagen de {self.producto.nombre}"


class Favorito(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favoritos"
    )
    producto = models.ForeignKey(
        Producto, on_delete=models.CASCADE, related_name="favoritos"
    )
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Favorito"
        verbose_name_plural = "Favoritos"
        unique_together = ("usuario", "producto")
        ordering = ["-creado"]

    def __str__(self):
        return f"{self.usuario.username} → {self.producto.nombre}"


class Carrito(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="carritos",
    )
    session_key = models.CharField(max_length=60, blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Carrito"
        verbose_name_plural = "Carritos"

    def __str__(self):
        destino = self.usuario.username if self.usuario else self.session_key
        return f"Carrito de {destino}"

    @property
    def cantidad_items(self):
        return sum(item.cantidad for item in self.items.all())

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())


class ItemCarrito(models.Model):
    carrito = models.ForeignKey(
        Carrito, on_delete=models.CASCADE, related_name="items"
    )
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    talla = models.ForeignKey(
        Talla, on_delete=models.SET_NULL, null=True, blank=True
    )
    color = models.ForeignKey(
        Color, on_delete=models.SET_NULL, null=True, blank=True
    )
    cantidad = models.PositiveIntegerField(default=1)
    agregado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Artículo del carrito"
        verbose_name_plural = "Artículos del carrito"

    def __str__(self):
        return f"{self.cantidad} × {self.producto.nombre}"

    @property
    def subtotal(self):
        return self.producto.precio * self.cantidad