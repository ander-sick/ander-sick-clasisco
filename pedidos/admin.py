"""Registro de modelos de pedidos en el administrador de Django."""
from django.contrib import admin

from .models import DetallePedido, Envio, EstadoPedido, Notificacion, Pago, Pedido
from .services import actualizar_estado_pedido


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ("nombre", "precio", "cantidad", "talla", "color", "subtotal")


@admin.register(EstadoPedido)
class EstadoPedidoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "slug", "orden", "descripcion")
    list_editable = ("orden", "descripcion")
    prepopulated_fields = {"slug": ("nombre",)}


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        "numero",
        "usuario",
        "estado",
        "estado_pago",
        "metodo_pago",
        "total",
        "creado",
    )
    list_filter = ("estado", "estado_pago", "metodo_pago")
    search_fields = ("numero", "usuario__username", "usuario__email")
    date_hierarchy = "creado"
    readonly_fields = ("numero", "creado", "actualizado")
    inlines = [DetallePedidoInline]
    actions = [
        "marcar_como_recibido",
        "marcar_como_en_preparacion",
        "marcar_como_enviado",
        "marcar_como_entregado",
        "marcar_como_cancelado",
        "marcar_pago_recibido",
    ]

    def _cambiar_estado(self, request, queryset, slug, nombre_accion):
        for pedido in queryset:
            actualizar_estado_pedido(pedido, slug, notificar=True)
        self.message_user(request, f"{queryset.count()} pedido(s) {nombre_accion}.")

    @admin.action(description="Marcar como recibido")
    def marcar_como_recibido(self, request, queryset):
        self._cambiar_estado(request, queryset, "recibido", "marcados como recibidos")

    @admin.action(description="Marcar como en preparación")
    def marcar_como_en_preparacion(self, request, queryset):
        self._cambiar_estado(request, queryset, "en_preparacion", "marcados en preparación")

    @admin.action(description="Marcar como enviado")
    def marcar_como_enviado(self, request, queryset):
        self._cambiar_estado(request, queryset, "enviado", "marcados como enviados")

    @admin.action(description="Marcar como entregado")
    def marcar_como_entregado(self, request, queryset):
        self._cambiar_estado(request, queryset, "entregado", "marcados como entregados")

    @admin.action(description="Marcar como cancelado")
    def marcar_como_cancelado(self, request, queryset):
        self._cambiar_estado(request, queryset, "cancelado", "marcados como cancelados")

    @admin.action(description="Marcar pago como recibido")
    def marcar_pago_recibido(self, request, queryset):
        for pedido in queryset:
            pedido.estado_pago = "pagado"
            pedido.save(update_fields=["estado_pago"])
            pago = getattr(pedido, "pago", None)
            if pago:
                pago.estado = "pagado"
                pago.save(update_fields=["estado"])
        self.message_user(request, f"{queryset.count()} pago(s) marcados como recibidos.")


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ("pedido", "nombre", "precio", "cantidad", "talla", "color", "subtotal")
    search_fields = ("nombre", "pedido__numero")


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("pedido", "metodo", "estado", "monto", "creado")
    list_filter = ("metodo", "estado")
    search_fields = ("pedido__numero", "referencia")


@admin.register(Envio)
class EnvioAdmin(admin.ModelAdmin):
    list_display = (
        "pedido",
        "empresa",
        "numero_seguimiento",
        "enviado",
        "fecha_entrega_estimada",
    )
    list_editable = ("enviado",)
    search_fields = ("pedido__numero", "numero_seguimiento")


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ("usuario", "titulo", "leida", "creado")
    list_filter = ("leida",)
    search_fields = ("usuario__username", "titulo")