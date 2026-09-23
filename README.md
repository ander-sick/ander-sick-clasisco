# 👔 CLASISCO — Tienda de ropa en línea

Plataforma web de venta de ropa tipo **tienda virtual profesional**, desarrollada con:

- **Backend:** Python + Django (con Django REST Framework para la API)
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, Font Awesome
- **Base de datos:** SQLite (desarrollo) / PostgreSQL (producción)

El cliente puede realizar el flujo completo:

> Ver producto → seleccionar talla/color → agregar al carrito → ingresar dirección → seleccionar pago → realizar pedido → recibir número de pedido → hacer seguimiento → recibir pedido.

Y el administrador controla toda la tienda desde **Django Admin** (`/admin/`) y un **panel de estadísticas** (`/panel-admin/`).

---

## 🚀 Puesta en marcha (desarrollo)

### 1. Requisitos

- **Python 3.10 o superior** (descárgalo de [python.org](https://www.python.org/downloads/); marca **"Add python.exe to PATH"** al instalarlo).

### 2. Crear el entorno virtual e instalar dependencias

Abre una terminal en la raíz del proyecto (`pro`) y ejecuta:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurar variables de entorno (opcional)

```powershell
copy .env.example .env
```

Ajusta `.env` si quieres usar PostgreSQL o cambiar el modo debug.

### 4. Crear la base de datos

```powershell
python manage.py makemigrations
python manage.py migrate
```

### 5. (Opcional) Cargar datos de demostración

```powershell
python manage.py crear_datos_demo
```

Esto crea categorías, marcas, tallas, colores, 14 productos, una dirección y un
pedido de ejemplo, además de dos cuentas de prueba:

| Cuenta        | Usuario  | Contraseña |
| ------------- | -------- | ---------- |
| Administrador | `admin`  | `admin123` |
| Cliente       | `cliente`| `cliente123`|

### 6. Crear el superusuario (si no usaste el comando anterior)

```powershell
python manage.py createsuperuser
```

### 7. ¡A ejecutar!

```powershell
python manage.py runserver
```

Abre **http://127.0.0.1:8000/**

---

## 🗺️ Mapa de rutas

| Ruta                         | Descripción                                    |
| ---------------------------- | ---------------------------------------------- |
| `/`                          | Página principal                               |
| `/productos/`                | Catálogo con buscador, filtros y ordenamiento |
| `/productos/categoria/<slug>/` | Productos por categoría                      |
| `/producto/<slug>/`          | Detalle de producto (talla, color, cantidad)  |
| `/carrito/`                  | Carrito de compras                             |
| `/usuario/registro/`         | Crear cuenta                                   |
| `/usuario/iniciar-sesion/`   | Iniciar sesión                                 |
| `/usuario/perfil/`           | Perfil del cliente                             |
| `/usuario/direcciones/`      | Administrar direcciones                        |
| `/pedidos/checkout/`         | Confirmar compra                               |
| `/pedidos/`                  | Historial de pedidos                           |
| `/pedidos/seguimiento/<num>/`| Seguimiento visual del pedido                  |
| `/pedidos/notificaciones/`   | Centro de notificaciones                       |
| `/favoritos/`                | Favoritos del cliente                          |
| `/admin/`                    | Panel administrativo de Django                 |
| `/panel-admin/`              | Panel de estadísticas con gráficos             |
| `/api/productos/`            | API REST de productos                          |
| `/api/categorias/`           | API REST de categorías                         |

---

## 🏗️ Estructura del proyecto

```text
pro/
│
├── manage.py
│
├── clasisco/            # Configuración del proyecto (settings, urls, wsgi, asgi)
├── tienda/              # Productos, categorías, marcas, tallas, colores,
│                        #   carrito, favoritos, API y datos de demostración
├── usuarios/            # Cuentas, perfil y direcciones
├── pedidos/             # Checkout, pedidos, pagos, envíos y notificaciones
├── panel/               # Panel administrativo con estadísticas (Chart.js)
│
├── templates/           # Plantillas HTML (base, inicio, productos, carrito,
│                        #   checkout, seguimiento, etc.)
├── static/
│   ├── css/             # style.css, responsive.css, admin.css
│   ├── js/              # main.js, carrito.js, checkout.js, admin.js
│   └── images/
├── media/productos/     # Imágenes subidas por el administrador
│
├── .env.example         # Variables de entorno de ejemplo
├── requirements.txt
└── README.md
```

---

## ⚙️ Pasar a producción

El proyecto está preparado para publicarse en Internet:

1. **PostgreSQL**

   En `.env`:
   ```env
   DB_ENGINE=postgresql
   DB_NAME=clasisco
   DB_USER=clasisco
   DB_PASSWORD=contraseña_segura
   DB_HOST=localhost
   DB_PORT=5432
   ```

   Luego:
   ```powershell
   python manage.py migrate
   ```

2. **Seguridad**

   ```env
   DJANGO_DEBUG=False
   DJANGO_HTTPS=True
   SECRET_KEY=<clave segura>
   DJANGO_ALLOWED_HOSTS=www.midominio.com
   CSRF_TRUSTED_ORIGINS=https://www.midominio.com
   ```

3. **Archivos estáticos y servidor**

   ```powershell
   python manage.py collectstatic
   pip install gunicorn whitenoise
   gunicorn clasisco.wsgi
   ```

   Sírvase con **Nginx + Gunicorn** (o cualquier PaaS). Cuando `DJANGO_HTTPS=True`
   se activan automáticamente: redirección HTTPS, cookies seguras y HSTS.
   `staticfiles/` es la carpeta de estáticos preparada para servir en producción.

---

## 🔌 Notas técnicas

- **Carrito en base de datos**: funciona con usuarios autenticados y con
  sesiones anónimas (se transfiere al iniciar sesión).
- **Descuento automático**: si `precio_anterior > precio`, el producto se marca
  como oferta y se calcula el porcentaje.
- **Estados del pedido**: `recibido → en_preparacion → enviado → entregado`
  (y `cancelado`), visibles como línea de tiempo en el seguimiento.
- **Notificaciones**: el cliente recibe avisos al confirmar el pedido y cuando
  cambia de estado (desde la administración).
- **API REST**: Django REST Framework expone `/api/productos/` y `/api/categorias/`.

---

## ❤️ Contribuciones

Este es el proyecto inicial de **CLASISCO**. Puedes ampliarlo con pasarelas de
pago reales (Stripe, PayPal), emails transaccionales o un sistema de cupones.