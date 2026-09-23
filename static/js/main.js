/* ============================================================
   CLASISCO — main.js
   Utilidades globales, galería, cantidades, favoritos y carrito.
   ============================================================ */

(function () {
  "use strict";

  /* ---------- Utilidades ---------- */

  function getCookie(nombre) {
    let valor = null;
    document.cookie.split(";").forEach(function (c) {
      const par = c.trim().split("=");
      if (par[0] === nombre) valor = decodeURIComponent(par[1]);
    });
    return valor;
  }

  const CSRF = getCookie("csrftoken");

  function formatearMoneda(valor) {
    const numero = parseFloat(valor) || 0;
    return "$" + numero.toFixed(2);
  }

  function mostrarToast(mensaje, tipo) {
    tipo = tipo || "info";
    let contenedor = document.getElementById("toast-container");
    if (!contenedor) {
      contenedor = document.createElement("div");
      contenedor.id = "toast-container";
      contenedor.className = "toast-container position-fixed top-0 end-0 p-3";
      contenedor.style.zIndex = "1090";
      document.body.appendChild(contenedor);
    }
    const toast = document.createElement("div");
    toast.className = "toast align-items-center text-bg-" + tipo + " border-0 mb-2";
    toast.setAttribute("role", "alert");
    toast.innerHTML =
      '<div class="d-flex"><div class="toast-body"></div>' +
      '<button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Cerrar"></button></div>';
    toast.querySelector(".toast-body").textContent = mensaje;
    contenedor.appendChild(toast);
    const instancia = new bootstrap.Toast(toast, { delay: 3500 });
    instancia.show();
    toast.addEventListener("hidden.bs.toast", function () {
      toast.remove();
    });
  }

  async function enviarPOST(url, datos, comoJSON) {
    const opciones = {
      method: "POST",
      headers: { "X-Requested-With": "XMLHttpRequest" },
    };
    if (CSRF) opciones.headers["X-CSRFToken"] = CSRF;
    if (comoJSON) {
      opciones.headers["Content-Type"] = "application/json";
      opciones.body = JSON.stringify(datos);
    } else {
      const cuerpo = new URLSearchParams();
      Object.keys(datos || {}).forEach(function (clave) {
        cuerpo.append(clave, datos[clave]);
      });
      opciones.body = cuerpo;
    }
    const respuesta = await fetch(url, opciones);
    let json = null;
    try {
      json = await respuesta.json();
    } catch (e) {
      json = null;
    }
    return { ok: respuesta.ok, status: respuesta.status, datos: json };
  }

  function actualizarContadorCarrito(contador) {
    const badge = document.getElementById("carrito-contador");
    if (badge) badge.textContent = contador;
    // También actualiza el badge del menú móvil con clase badge-cart
    document.querySelectorAll(".badge-cart").forEach(function (b) {
      b.textContent = contador;
    });
  }

  function manejarSesionRequerida(respuesta, urlActual) {
    if (respuesta.status === 401 && respuesta.datos && respuesta.datos.login) {
      const destino = encodeURIComponent(urlActual);
      window.location.href = respuesta.datos.url + "?next=" + destino;
      return true;
    }
    return false;
  }

  // Hacer disponibles algunas utilidades para otros scripts
  window.Clasisco = {
    CSRF: CSRF,
    enviarPOST: enviarPOST,
    mostrarToast: mostrarToast,
    formatearMoneda: formatearMoneda,
    actualizarContadorCarrito: actualizarContadorCarrito,
    manejarSesionRequerida: manejarSesionRequerida,
  };

  document.addEventListener("DOMContentLoaded", function () {
    /* ---------- Ocultar toasts de Django automáticamente ---------- */
    document.querySelectorAll("#toast-container .toast").forEach(function (t) {
      t.classList.add("show");
      setTimeout(function () {
        const instancia = bootstrap.Toast.getOrCreateInstance(t, { delay: 3800 });
        instancia.hide();
      }, 250);
    });

    /* ---------- Galería de producto ---------- */
    const imagenPrincipal = document.getElementById("imagen-activa");
    document.querySelectorAll(".miniatura img").forEach(function (mina) {
      mina.addEventListener("click", function () {
        const lleno = mina.dataset.full;
        if (imagenPrincipal && lleno) {
          imagenPrincipal.src = lleno;
          document.querySelectorAll(".miniatura").forEach(function (m) {
            m.classList.remove("activa");
          });
          mina.parentElement.classList.add("activa");
        }
      });
    });

    /* ---------- Control de cantidad genérico (páginas que no son carrito) ---------- */
    document.querySelectorAll(".qty-control").forEach(function (control) {
      const entrada = control.querySelector(".qty-input");
      if (!entrada || entrada.dataset.item) return; // el carrito lo maneja carrito.js
      const maximo = parseInt(entrada.max, 10) || 999;
      control.querySelectorAll(".qty-btn").forEach(function (boton) {
        boton.addEventListener("click", function () {
          let valor = parseInt(entrada.value, 10) || 1;
          if (boton.dataset.accion === "+") valor = Math.min(valor + 1, maximo);
          else valor = Math.max(valor - 1, 1);
          entrada.value = valor;
          entrada.dispatchEvent(new Event("change", { bubbles: true }));
        });
      });
    });

    /* ---------- Filtros automáticos ---------- */
    document.querySelectorAll(".filtro-automatico input").forEach(function (input) {
      input.addEventListener("change", function () {
        const formulario = input.closest("form");
        if (formulario) formulario.submit();
      });
    });

    /* ---------- Agregar al carrito desde tarjetas ---------- */
    document.querySelectorAll(".btn-add-cart").forEach(function (boton) {
      boton.addEventListener("click", async function () {
        if (boton.dataset.tieneTallas) {
          // Requiere seleccionar talla: ir al detalle del producto.
          window.location.href = boton.dataset.urlProducto;
          return;
        }
        boton.disabled = true;
        const respuesta = await Clasisco.enviarPOST(
          boton.dataset.url,
          { producto: boton.dataset.producto, cantidad: 1 },
          false
        );
        boton.disabled = false;
        if (Clasisco.manejarSesionRequerida(respuesta, window.location.href)) return;
        if (respuesta.ok && respuesta.datos && respuesta.datos.ok) {
          Clasisco.actualizarContadorCarrito(respuesta.datos.carrito_count);
          Clasisco.mostrarToast(respuesta.datos.mensaje, "success");
        } else if (respuesta.datos && respuesta.datos.error) {
          Clasisco.mostrarToast(respuesta.datos.error, "danger");
        }
      });
    });

    /* ---------- Favoritos (tarjetas) ---------- */
    document.querySelectorAll(".btn-fav").forEach(function (boton) {
      boton.addEventListener("click", async function () {
        const respuesta = await Clasisco.enviarPOST(
          boton.dataset.url,
          { producto: boton.dataset.producto },
          false
        );
        if (Clasisco.manejarSesionRequerida(respuesta, window.location.href)) return;
        if (respuesta.ok && respuesta.datos && respuesta.datos.ok) {
          const icono = boton.querySelector("i");
          if (respuesta.datos.guardado) {
            icono.className = "fa-solid fa-heart";
            boton.classList.add("activo");
            Clasisco.mostrarToast("Agregado a favoritos", "success");
          } else {
            icono.className = "fa-regular fa-heart";
            boton.classList.remove("activo");
            Clasisco.mostrarToast("Eliminado de favoritos", "info");
          }
        } else if (respuesta.datos && respuesta.datos.error) {
          Clasisco.mostrarToast(respuesta.datos.error, "danger");
        }
      });
    });

    /* ---------- Detalle de producto ---------- */
    const grupoTallas = document.getElementById("grupo-tallas");
    const grupoColores = document.getElementById("grupo-colores");
    let tallaSeleccionada = "";
    let colorSeleccionado = "";

    if (grupoTallas) {
      grupoTallas.querySelectorAll(".talla-selector").forEach(function (t) {
        t.addEventListener("click", function () {
          grupoTallas.querySelectorAll(".talla-selector").forEach(function (x) {
            x.classList.remove("seleccionado");
          });
          t.classList.add("seleccionado");
          tallaSeleccionada = t.dataset.talla;
        });
      });
    }
    if (grupoColores) {
      grupoColores.querySelectorAll(".color-selector").forEach(function (c) {
        c.addEventListener("click", function () {
          grupoColores.querySelectorAll(".color-selector").forEach(function (x) {
            x.classList.remove("seleccionado");
          });
          c.classList.add("seleccionado");
          colorSeleccionado = c.dataset.color;
        });
      });
    }

    const botonDetalle = document.getElementById("btn-agregar-detalle");
    if (botonDetalle) {
      botonDetalle.addEventListener("click", async function () {
        if (grupoTallas && !tallaSeleccionada) {
          Clasisco.mostrarToast("Selecciona una talla primero.", "warning");
          return;
        }
        const entradaCantidad = document.querySelector("#qty-detalle .qty-input");
        const cantidad = parseInt(entradaCantidad.value, 10) || 1;
        botonDetalle.disabled = true;
        const respuesta = await Clasisco.enviarPOST(
          botonDetalle.dataset.url,
          {
            producto: botonDetalle.dataset.producto,
            cantidad: cantidad,
            talla: tallaSeleccionada || "",
            color: colorSeleccionado || "",
          },
          true
        );
        botonDetalle.disabled = false;
        if (respuesta.ok && respuesta.datos && respuesta.datos.ok) {
          Clasisco.actualizarContadorCarrito(respuesta.datos.carrito_count);
          Clasisco.mostrarToast(respuesta.datos.mensaje, "success");
        } else if (respuesta.datos && respuesta.datos.error) {
          Clasisco.mostrarToast(respuesta.datos.error, "danger");
        }
      });
    }

    const botonFavDetalle = document.getElementById("btn-favorito-detalle");
    if (botonFavDetalle) {
      botonFavDetalle.addEventListener("click", async function () {
        const respuesta = await Clasisco.enviarPOST(
          botonFavDetalle.dataset.url,
          { producto: botonFavDetalle.dataset.producto },
          false
        );
        if (Clasisco.manejarSesionRequerida(respuesta, window.location.href)) return;
        if (respuesta.ok && respuesta.datos && respuesta.datos.ok) {
          const icono = document.getElementById("icono-favorito");
          if (respuesta.datos.guardado) {
            icono.className = "fa-solid fa-heart";
            Clasisco.mostrarToast("Agregado a favoritos", "success");
          } else {
            icono.className = "fa-regular fa-heart";
            Clasisco.mostrarToast("Eliminado de favoritos", "info");
          }
        } else if (respuesta.datos && respuesta.datos.error) {
          Clasisco.mostrarToast(respuesta.datos.error, "danger");
        }
      });
    }
  });
})();