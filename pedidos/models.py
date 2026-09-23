"""Modelos de pedidos: pedidos, detalles, pagos, envíos y notificaciones."""
from django.conf import settings
from django.db import models
from django.urls import reverse


class EstadoPedido(models.Model):
    """Estados por los que pasa un pedido (usados en el seguimiento visual)."""

    nombre = models.CharField(max_length=120)
    slug = models.SlugField(max_length=60, unique=True)
    orden = models.PositiveIntegerField(
        default=0, help_text="Orden en el que aparece en el seguimiento"
    )
    descripcion = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Estado de pedido"
        verbose_name_plural = "Estados de pedidos"
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre


class Pedido(models.Model):
    """Cabecera del pedido realizado por el cliente."""

    METODOS_PAGO = [
        ("tarjeta", "Tarjeta de crédito / débito"),
        ("transferencia", "Transferencia bancaria"),
        ("contraentrega", "Pago contra entrega"),
        ("paypal", "PayPal"),
    ]
    ESTADOS_PAGO = [
        ("pendiente", "Pendiente"),
        ("procesado", "Procesado"),
        ("pagado", "Pagado"),
        ("reembolsado", "Reembolsado"),
        ("fallido", "Fallido"),
    ]

    numero = models.CharField(max_length=24, unique=True, editable=False)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pedidos"
    )
    estado = models.ForeignKey(
        EstadoPedido, on_delete=models.PROTECT, related_name="pedidos"
    )
    estado_pago = models.CharField(
        max_length=20, choices=ESTADOS_PAGO, default="pendiente"
    )
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    envio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    direccion_envio = models.TextField()
    notas = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ["-creado"]

    def __str__(self):
        return f"Pedido {self.numero}"

    def get_absolute_url(self):
        return reverse("pedidos:seguimiento", args=[self.numero])

    @property
    def es_cancelado(self):
        return self.estado.slug == "cancelado"


class DetallePedido(models.Model):
    """Copia inmutable de cada producto comprado en el pedido."""

    pedido = models.ForeignKey(
        Pedido, on_delete=models.CASCADE, related_name="detalles"
    )
    producto = models.ForeignKey(
        "tienda.Producto", on_delete=models.SET_NULL, null=True, related_name="detalles_pedido"
    )
    nombre = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField()
    talla = models.CharField(max_length=30, blank=True)
    color = models.CharField(max_length=60, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Detalle de pedido"
        verbose_name_plural = "Detalles de pedidos"

    def __str__(self):
        return f"{self.cantidad} × {self.nombre}"


class Pago(models.Model):
    """Registro del pago asociado a un pedido."""

    pedido = models.OneToOneField(
        Pedido, on_delete=models.CASCADE, related_name="pago"
    )
    metodo = models.CharField(max_length=20)
    estado = models.CharField(max_length=20, default="pendiente")
    referencia = models.CharField(max_length=120, blank=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"

    def __str__(self):
        return f"Pago de {self.pedido.numero} — {self.monto}"


class Envio(models.Model):
    """Información del envío y seguimiento del pedido."""

    pedido = models.OneToOneField(
        Pedido, on_delete=models.CASCADE, related_name="envio_info"
    )
    empresa = models.CharField(max_length=120, blank=True)
    numero_seguimiento = models.CharField(max_length=120, blank=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    fecha_entrega_estimada = models.DateField(null=True, blank=True)
    enviado = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Envío"
        verbose_name_plural = "Envíos"

    def __str__(self):
        return f"Envío de {self.pedido.numero}"


class Notificacion(models.Model):
    """Notificaciones dirigidas al cliente."""

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notificaciones",
    )
    titulo = models.CharField(max_length=120)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ["-creado"]

    def __str__(self):
        return self.titulo