/* ============================================================
   CLASISCO — checkout.js
   Validación y envío del formulario de compra.
   ============================================================ */

(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    const formulario = document.getElementById("form-checkout");
    if (!formulario) return;

    const boton = document.getElementById("btn-confirmar");
    const selectDireccion = formulario.elements["direccion"];

    function validarNuevaDireccion() {
      const camposRequeridos = [
        "nombre_completo",
        "telefono",
        "calle",
        "ciudad",
        "estado",
        "codigo_postal",
        "pais",
      ];
      let validos = true;
      camposRequeridos.forEach(function (nombre) {
        const campo = formulario.elements[nombre];
        if (!campo) return;
        const grupo = campo.closest(".col-md-6, .col-md-4, .col-12") || campo.parentElement;
        if (!campo.value.trim()) {
          campo.classList.add("is-invalid");
          if (grupo) {
            let feedback = grupo.querySelector(".invalid-feedback");
            if (!feedback) {
              feedback = document.createElement("div");
              feedback.className = "invalid-feedback";
              feedback.textContent = "Este campo es obligatorio.";
              grupo.appendChild(feedback);
            }
          }
          validos = false;
        } else {
          campo.classList.remove("is-invalid");
        }
      });
      return validos;
    }

    const pagoInicial = formulario.querySelector("input[name=metodo_pago]:checked");
    const aviso = document.getElementById("aviso-pago");
    if (aviso) {
      formulario.querySelectorAll("input[name=metodo_pago]").forEach(function (radio) {
        radio.addEventListener("change", function () {
          aviso.textContent =
            "Pago elegido: " + radio.nextElementSibling.textContent.trim() +
            ". La confirmación se gestionará en el siguiente paso (simulado en desarrollo).";
        });
      });
    }

    formulario.addEventListener("submit", function (evento) {
      const usaGuardada = selectDireccion && selectDireccion.value;
      const nuevamente = !usaGuardada || true; // validar siempre que la dirección esté completa

      let validado = true;
      if (nuevamente) {
        // Si el cliente eligió una dirección guardada, no exigir los campos nuevos,
        // pero si solo rellenó los campos nuevos, sí validarlos.
        if (!usaGuardada) {
          validado = validarNuevaDireccion();
        }
      }

      if (!validado) {
        evento.preventDefault();
        Clasisco.mostrarToast("Completa los campos obligatorios de la dirección.", "warning");
        return;
      }

      if (boton) {
        boton.disabled = true;
        boton.innerHTML =
          '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Procesando…';
      }
    });
  });
})();