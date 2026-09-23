/* ============================================================
   CLASISCO — carrito.js
   Actualiza cantidades y totales del carrito sin recargar.
   ============================================================ */

(function () {
  "use strict";

  function actualizarTotales(datos) {
    const subtotal = document.getElementById("resumen-subtotal");
    const descuento = document.getElementById("resumen-descuento");
    const filaDescuento = document.getElementById("fila-descuento");
    const envio = document.getElementById("resumen-envio");
    const total = document.getElementById("resumen-total");

    if (subtotal) subtotal.textContent = Clasisco.formatearMoneda(datos.subtotal);
    if (descuento) descuento.textContent = "− " + Clasisco.formatearMoneda(datos.descuento);
    if (filaDescuento) {
      if (datos.descuento > 0) filaDescuento.classList.remove("d-none");
      else filaDescuento.classList.add("d-none");
    }
    if (envio) {
      envio.innerHTML =
        datos.envio > 0
          ? Clasisco.formatearMoneda(datos.envio)
          : '<span class="text-success">Gratis</span>';
    }
    if (total) total.textContent = Clasisco.formatearMoneda(datos.total);
  }

  function actualizarSubtotalFila(itemId, valor) {
    const celda = document.getElementById("subtotal-item-" + itemId);
    if (celda) celda.textContent = Clasisco.formatearMoneda(valor);
  }

  function eliminarFila(itemId) {
    const fila = document.getElementById("fila-item-" + itemId);
    if (fila) fila.remove();
    // Si ya no quedan artículos, recargar para mostrar el carrito vacío.
    if (document.querySelectorAll(".cart-row").length === 0) {
      window.location.reload();
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('[data-item]').forEach(function (entrada) {
      const itemId = entrada.dataset.item;
      const url = entrada.dataset.url;
      const maximo = parseInt(entrada.max, 10) || 999;

      // Botones + / − del control de cantidad
      const control = entrada.closest(".qty-control");
      if (control) {
        control.querySelectorAll(".qty-btn").forEach(function (boton) {
          boton.addEventListener("click", async function () {
            let valor = parseInt(entrada.value, 10) || 1;
            if (boton.dataset.accion === "+") valor = Math.min(valor + 1, maximo);
            else valor = Math.max(valor - 1, 1);
            await enviarCambio(url, itemId, valor, entrada);
          });
        });
      }

      // Cambio directo del campo numérico
      entrada.addEventListener("change", async function () {
        let valor = parseInt(entrada.value, 10) || 1;
        valor = Math.max(1, Math.min(valor, maximo));
        entrada.value = valor;
        await enviarCambio(url, itemId, valor, entrada);
      });
    });

    // Botones de eliminar: evitan el envío normal y usan AJAX.
    document.querySelectorAll(".cart-eliminar").forEach(function (boton) {
      boton.addEventListener("click", async function (evento) {
        evento.preventDefault();
        const formulario = boton.closest("form");
        const url = formulario.action;
        const fila = boton.closest(".cart-row");
        const itemId = fila ? fila.id.replace("fila-item-", "") : null;

        const respuesta = await Clasisco.enviarPOST(url, {}, false);
        if (respuesta.ok && respuesta.datos && respuesta.datos.ok) {
          Clasisco.actualizarContadorCarrito(respuesta.datos.carrito_count);
          Clasisco.mostrarToast(respuesta.datos.mensaje, "success");
          actualizarTotales(respuesta.datos);
          if (itemId) eliminarFila(itemId);
        } else if (respuesta.datos && respuesta.datos.error) {
          Clasisco.mostrarToast(respuesta.datos.error, "danger");
        }
      });
    });
  });

  async function enviarCambio(url, itemId, cantidad, entrada) {
    const cuerpo = new URLSearchParams();
    cuerpo.append("cantidad", cantidad);
    const respuesta = await Clasisco.enviarPOST(url, { cantidad: cantidad }, false);
    if (respuesta.ok && respuesta.datos && respuesta.datos.ok) {
      Clasisco.actualizarContadorCarrito(respuesta.datos.carrito_count);
      Clasisco.mostrarToast(respuesta.datos.mensaje, "success");
      actualizarTotales(respuesta.datos);
      actualizarSubtotalFila(itemId, respuesta.datos.item_subtotal);
      if (respuesta.datos.item_subtotal <= 0) eliminarFila(itemId);
    } else if (respuesta.datos && respuesta.datos.error) {
      Clasisco.mostrarToast(respuesta.datos.error, "danger");
      // Restaura el valor vigente.
      window.location.reload();
    }
  }
})();