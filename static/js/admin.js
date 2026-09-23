/* ============================================================
   CLASISCO — admin.js
   Menú lateral móvil y gráficos del panel administrativo.
   ============================================================ */

(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    /* ---------- Menú lateral en móviles ---------- */
    const boton = document.getElementById("btn-toggle-sidebar");
    const sidebar = document.getElementById("admin-sidebar");
    if (boton && sidebar) {
      boton.addEventListener("click", function () {
        sidebar.classList.toggle("abierta");
      });
    }

    /* ---------- Gráficos ---------- */
    const contenedor = document.getElementById("datos-panel");
    if (!contenedor) return;
    const urlEstadisticas = contenedor.dataset.url;

    fetch(urlEstadisticas, { headers: { "X-Requested-With": "XMLHttpRequest" } })
      .then(function (respuesta) {
        if (!respuesta.ok) throw new Error("Sin datos");
        return respuesta.json();
      })
      .then(function (datos) {
        const colores = ["#c9a24b", "#2e8b57", "#2c6fbb", "#b03a2e", "#7d7e84", "#6a5510"];

        /* Ingresos mensuales (línea) */
        const lienzoIngresos = document.getElementById("chart-ingresos");
        if (lienzoIngresos && datos.ingresos_mensuales.length) {
          new Chart(lienzoIngresos, {
            type: "line",
            data: {
              labels: datos.ingresos_mensuales.map(function (r) { return r.mes; }),
              datasets: [{
                label: "Ventas (MXN)",
                data: datos.ingresos_mensuales.map(function (r) { return r.total; }),
                borderColor: "#c9a24b",
                backgroundColor: "rgba(201, 162, 75, 0.15)",
                fill: true,
                tension: 0.4,
                pointBackgroundColor: "#16171b",
              }],
            },
            options: {
              responsive: true,
              plugins: { legend: { display: false } },
              scales: {
                y: { beginAtZero: true, ticks: { callback: function (v) { return "$" + v; } } },
              },
            },
          });
        } else if (lienzoIngresos) {
          lienzoIngresos.parentElement.insertAdjacentHTML(
            "beforeend",
            '<p class="text-muted mb-0">Aún no hay ventas registradas.</p>'
          );
        }

        /* Pedidos por estado (dona) */
        const lienzoEstados = document.getElementById("chart-estados");
        if (lienzoEstados && datos.pedidos_por_estado.length) {
          new Chart(lienzoEstados, {
            type: "doughnut",
            data: {
              labels: datos.pedidos_por_estado.map(function (r) { return r.nombre; }),
              datasets: [{
                data: datos.pedidos_por_estado.map(function (r) { return r.cantidad; }),
                backgroundColor: colores,
                borderWidth: 2,
                borderColor: "#ffffff",
              }],
            },
            options: { responsive: true, plugins: { legend: { position: "bottom" } } },
          });
        }

        /* Top productos (barras) */
        const lienzoTop = document.getElementById("chart-top");
        if (lienzoTop && datos.top_productos.length) {
          new Chart(lienzoTop, {
            type: "bar",
            data: {
              labels: datos.top_productos.map(function (r) { return r.nombre; }),
              datasets: [{
                label: "Unidades vendidas",
                data: datos.top_productos.map(function (r) { return r.vendidos; }),
                backgroundColor: "#16171b",
                borderRadius: 3,
              }],
            },
            options: {
              responsive: true,
              indexAxis: "y",
              plugins: { legend: { display: false } },
              scales: { x: { beginAtZero: true, ticks: { precision: 0 } } },
            },
          });
        } else if (lienzoTop) {
          lienzoTop.parentElement.insertAdjacentHTML(
            "beforeend",
            '<p class="text-muted mb-0">Aún no hay ventas para mostrar.</p>'
          );
        }
      })
      .catch(function () {
        const cilindros = document.querySelectorAll(".panel-card canvas");
        cilindros.forEach(function (canvas) {
          canvas.parentElement.insertAdjacentHTML(
            "beforeend",
            '<p class="text-muted mb-0">No fue posible cargar los gráficos.</p>'
          );
        });
      });
  });
})();