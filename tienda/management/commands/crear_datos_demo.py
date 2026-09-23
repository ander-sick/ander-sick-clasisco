"""Comando para cargar datos de demostración en CLASISCO.

Uso:
    python manage.py crear_datos_demo

Crea usuarios, categorías, marcas, tallas, colores, productos y un pedido
de ejemplo. Útil para probar la tienda durante el desarrollo.
"""
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from pedidos.models import DetallePedido, Envio, EstadoPedido, Notificacion, Pago, Pedido
from pedidos.services import inicializar_estados
from tienda.models import Carrito, Categoria, Color, ItemCarrito, Marca, Producto, Talla
from usuarios.models import Direccion, Perfil

# Usuarios de demostración (SOLO desarrollo).
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
CLIENTE_USERNAME = "cliente"
CLIENTE_PASSWORD = "cliente123"


class Command(BaseCommand):
    help = "Crea datos de demostración para CLASISCO (desarrollo)."

    def handle(self, *args, **options):
        self.stdout.write("Creando datos de demostración…")

        categorias = self._crear_categorias()
        marcas = self._crear_marcas()
        tallas = self._crear_tallas()
        colores = self._crear_colores()
        admin_user, cliente = self._crear_usuarios()
        self._crear_productos(categorias, marcas, tallas, colores)

        inicializar_estados()
        self._crear_pedido_ejemplo(cliente)
        self._crear_direccion_ejemplo(cliente)

        self.stdout.write(self.style.SUCCESS(
            "\nListo. Usuarios de prueba:\n"
            f"  Administrador: {ADMIN_USERNAME} / {ADMIN_PASSWORD}\n"
            f"  Cliente:       {CLIENTE_USERNAME} / {CLIENTE_PASSWORD}\n"
            "\nEntra a /admin/ con el administrador."
        ))

    # ---------------------------------------------------------------
    def _crear_categorias(self):
        datos = [
            ("Hombre", "Ropa para hombre"),
            ("Mujer", "Ropa para mujer"),
            ("Niños", "Ropa infantil"),
            ("Calzado", "Zapatos, tenis y botas"),
            ("Accesorios", "Gorras, cinturones y más"),
        ]
        creadas = []
        for nombre, descripcion in datos:
            categoria, _ = Categoria.objects.get_or_create(
                nombre=nombre,
                defaults={"descripcion": descripcion, "activa": True},
            )
            creadas.append(categoria)
        return {c.nombre.lower(): c for c in creadas}

    def _crear_marcas(self):
        nombres = ["CLASISCO", "Elegance", "UrbanFit", "Clásico & Co", "VogueStreet"]
        creadas = []
        for nombre in nombres:
            marca, _ = Marca.objects.get_or_create(
                nombre=nombre, defaults={"activa": True}
            )
            creadas.append(marca)
        return {m.nombre: m for m in creadas}

    def _crear_tallas(self):
        nombres = ["XS", "S", "M", "L", "XL", "XXL", "36", "38", "40", "42"]
        creadas = []
        for i, nombre in enumerate(nombres):
            talla, _ = Talla.objects.get_or_create(
                nombre=nombre, defaults={"orden": i}
            )
            creadas.append(talla)
        return {t.nombre: t for t in creadas}

    def _crear_colores(self):
        datos = [
            ("Negro", "#111111"),
            ("Blanco", "#ffffff"),
            ("Gris", "#8c8c8c"),
            ("Azul marino", "#1f3a5f"),
            ("Beige", "#d9c7a7"),
            ("Verde oliva", "#5b5941"),
            ("Burdeos", "#6d1a2c"),
        ]
        creados = []
        for i, (nombre, codigo) in enumerate(datos):
            color, _ = Color.objects.get_or_create(
                nombre=nombre, defaults={"codigo": codigo, "orden": i}
            )
            creados.append(color)
        return {c.nombre: c for c in creados}

    def _crear_usuarios(self):
        admin_user, _ = User.objects.get_or_create(
            username=ADMIN_USERNAME,
            defaults={"is_staff": True, "is_superuser": True, "email": "admin@clasisco.com"},
        )
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.set_password(ADMIN_PASSWORD)
        admin_user.save()
        Perfil.objects.get_or_create(usuario=admin_user)

        cliente, _ = User.objects.get_or_create(
            username=CLIENTE_USERNAME,
            defaults={"email": "cliente@clasisco.com", "first_name": "María", "last_name": "García"},
        )
        cliente.set_password(CLIENTE_PASSWORD)
        cliente.save()
        Perfil.objects.get_or_create(usuario=cliente)
        return admin_user, cliente

    def _crear_productos(self, categorias, marcas, tallas, colores):
        catalogo = [
            # (nombre, categoria, marca, precio, precio_anterior, stock, tallas, colores, destacado, nuevo, oferta)
            ("Camisa de lino premium", "hombre", "Clásico & Co", 899.00, 1099.00, 40,
             ["S", "M", "L", "XL"], ["Blanco", "Beige", "Azul marino"], True, False, True),
            ("Blazer sartorial", "hombre", "UrbanFit", 2499.00, None, 15,
             ["M", "L", "XL"], ["Negro", "Azul marino"], True, True, False),
            ("Chamarra de mezclilla", "hombre", "CLASISCO", 1299.00, 1599.00, 22,
             ["S", "M", "L", "XL", "XXL"], ["Azul marino"], False, False, True),
            ("Pantalón de vestir", "hombre", "Elegance", 1190.00, None, 30,
             ["38", "40", "42"], ["Negro", "Gris"], False, False, False),
            ("Vestido midi floral", "mujer", "VogueStreet", 999.00, 1299.00, 35,
             ["XS", "S", "M", "L"], ["Beige"], True, True, True),
            ("Blusa con lazo", "mujer", "Elegance", 649.00, None, 50,
             ["S", "M", "L"], ["Blanco", "Burdeos"], False, False, False),
            ("Abrigo de lana", "mujer", "CLASISCO", 2890.00, None, 12,
             ["S", "M", "L"], ["Beige", "Negro"], True, True, False),
            ("Falda plisada", "mujer", "VogueStreet", 749.00, 949.00, 28,
             ["XS", "S", "M"], ["Burdeos", "Negro"], False, False, True),
            ("Playera infantil algodón", "niños", "UrbanFit", 299.00, None, 60,
             ["XS", "S", "M"], ["Blanco", "Gris"], False, True, False),
            ("Pants casual", "niños", "UrbanFit", 429.00, 549.00, 45,
             ["XS", "S", "M"], ["Verde oliva", "Negro"], False, False, True),
            ("Tenis urbanos", "calzado", "CLASISCO", 1599.00, 1899.00, 18,
             ["36", "38", "40", "42"], ["Blanco", "Negro"], True, True, True),
            ("Zapatos de vestir", "calzado", "Elegance", 1890.00, None, 10,
             ["40", "42"], ["Negro"], False, False, False),
            ("Gorra clásica", "accesorios", "CLASISCO", 349.00, None, 80,
             [], ["Negro", "Beige"], False, False, False),
            ("Cinturón de piel", "accesorios", "Clásico & Co", 549.00, 699.00, 25,
             [], ["Negro", "Burdeos"], False, False, True),
        ]

        # Índices numéricos de las tallas de calzado descartables: se quitan
        # si la talla no aplica al tipo de producto.
        for i, (nombre, cat, marca, precio, anterior, stock, ts, cs, dest, nuevo, oferta) in enumerate(catalogo):
            if Producto.objects.filter(nombre=nombre).exists():
                continue
            producto = Producto.objects.create(
                categoria=categorias[cat],
                marca=marcas[marca],
                nombre=nombre,
                descripcion=(
                    f"{nombre} — prenda seleccionada por nuestro equipo de estilo "
                    f"para la colección CLASISCO. Materiales de alta calidad, "
                    f"corte cuidado y acabados duraderos."
                ),
                precio=precio,
                precio_anterior=anterior,
                stock=stock,
                destacado=dest,
                es_nuevo=nuevo,
                en_oferta=oferta,
                activo=True,
            )
            producto.tallas.set([tallas[t] for t in ts])
            producto.colores.set([colores[c] for c in cs])
            producto.save()

        self.stdout.write(f"  Productos creados: {len(catalogo)}")

    def _crear_direccion_ejemplo(self, cliente):
        Direccion.objects.get_or_create(
            usuario=cliente,
            nombre_completo="María García",
            defaults={
                "etiqueta": "Casa",
                "telefono": "5512345678",
                "calle": "Av. Reforma 123, Col. Centro",
                "ciudad": "Ciudad de México",
                "estado": "CDMX",
                "codigo_postal": "06600",
                "pais": "México",
                "es_principal": True,
            },
        )

    def _crear_pedido_ejemplo(self, cliente):
        if Pedido.objects.filter(usuario=cliente).exists():
            return

        productos = list(Producto.objects.filter(activo=True).order_by("-destacado")[:3])
        if len(productos) < 2:
            return

        subtotal = sum(p.precio for p in productos[:2])
        descuento = sum(
            (p.precio_anterior - p.precio) for p in productos[:2]
            if p.precio_anterior and p.precio_anterior > p.precio
        )
        envio = 0 if subtotal >= 1000 else 99.99
        total = subtotal - descuento + envio

        estado = EstadoPedido.objects.get(slug="en_preparacion")
        pedido = Pedido.objects.create(
            numero=f"CLS-DEMO-{timezone.now():%Y%m%d}-000001",
            usuario=cliente,
            estado=estado,
            estado_pago="procesado",
            metodo_pago="tarjeta",
            subtotal=subtotal,
            descuento=descuento,
            envio=envio,
            total=total,
            direccion_envio=(
                "María García — Av. Reforma 123, Col. Centro, "
                "Ciudad de México, CDMX (06600)"
            ),
            creado=timezone.now() - timedelta(days=3),
        )
        Pedido.objects.filter(pk=pedido.pk).update(creado=timezone.now() - timedelta(days=3))

        for producto in productos[:2]:
            talla = producto.tallas.first()
            DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                nombre=producto.nombre,
                precio=producto.precio,
                cantidad=1,
                talla=talla.nombre if talla else "",
                color=producto.colores.first().nombre if producto.colores.first() else "",
                subtotal=producto.precio,
            )

        Pago.objects.create(
            pedido=pedido, metodo="tarjeta", estado="procesado",
            monto=total, referencia="PAY-DEMO-0001",
        )
        Envio.objects.create(
            pedido=pedido,
            empresa="Correos de México",
            numero_seguimiento="CLS-DEMO-GUIA-001",
            costo=envio,
            enviado=True,
            fecha_envio=timezone.now() - timedelta(days=1),
        )
        Notificacion.objects.create(
            usuario=cliente,
            titulo=f"Tu pedido {pedido.numero} va en camino",
            mensaje="Tu pedido fue enviado; espera el paquete en la dirección indicada.",
        )
        self.stdout.write("  Pedido de ejemplo creado.")