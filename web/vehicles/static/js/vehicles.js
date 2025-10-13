//  Manejar el modal del formulario de vehículos
const modal = document.getElementById("vehicle_modal");
const btnAdd = document.getElementById("btnAddVehicle");

btnAdd.onclick = () => {
    modal.style.display = "block";
    document.body.style.overflow = "hidden";
}

function closeModal() {
    modal.style.display = "none";
    document.body.style.overflow = "";
}

window.onclick = function (event) {
    if (event.target == modal) closeModal();
}

// Toast Control
document.addEventListener("DOMContentLoaded", function () {
    const toasts = document.querySelectorAll(".toast");
    const delay = 4000;
    const appearDelay = 500;

    toasts.forEach((toast, index) => {

        // Animación de entrada
        setTimeout(() => toast.classList.add("show"), appearDelay + (200 * index));

        // Animación de salida y eliminación
        setTimeout(() => {
            toast.classList.add("hide");
            setTimeout(() => toast.remove(), 500);
        }, delay + (index * 200));
    });
});

// Buscador API
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("vehicleSearchForm");
    const input = document.getElementById("vehicleSearchInput");
    const list = document.getElementById("vehicleList");
    const loader = document.getElementById("vehicleLoader");

    async function fetchVehicles(query) {

        loader.classList.remove("hidden");
        list.querySelectorAll(".vehicle-card, li").forEach(el => el.style.display = "none");

        try {
            const res = await fetch(`/vehiculos/search/?q=${encodeURIComponent(query)}`);
            const data = await res.json();
            renderVehicles(data.vehicles);
        } catch (error) {
            console.error("Error al buscar vehículos:", error);
        } finally {
            loader.classList.add("hidden");
            list.querySelectorAll(".vehicle-card, li").forEach(el => el.style.display = "");
        }
    }

    function renderVehicles(vehicles) {
        list.querySelectorAll(".vehicle-card, li").forEach(el => el.remove());

        if (!vehicles.length) {
            const li = document.createElement("li");
            li.textContent = "No hay vehículos registrados.";
            list.appendChild(li);
            return;
        }

        vehicles.forEach(v => {
            const article = document.createElement("article");
            article.className = "vehicle-card";
            article.innerHTML = `
        <img src="${v.imagen_url || '/static/img/img_not_found.jpg'}"
             class="vehicle-image" alt="${v.marca} ${v.modelo}">
        <div class="vehicle-info">
          <h2 class="vehicle-title">${v.patente}</h2>
          <p class="vehicle-description">${v.marca} - ${v.modelo}</p>
          <p class="vehicle-description">Año: ${v.anio}</p>
        </div>
        <svg xmlns="http://www.w3.org/2000/svg" class="vehicle-next-icon" viewBox="0 0 42 42">
          <path fill="currentColor" fill-rule="evenodd"
                d="M13.933 1L34 21.068L14.431 40.637l-4.933-4.933l14.638-14.636L9 5.933z" />
        </svg>
      `;
            list.appendChild(article);
        });
    }

    // Buscar al enviar el formulario
    form.addEventListener("submit", e => {
        e.preventDefault();
        fetchVehicles(input.value.trim());
    });

    // Buscar en vivo mientras se escribe (con retraso)
    let typingTimer;
    input.addEventListener("input", () => {
        clearTimeout(typingTimer);
        typingTimer = setTimeout(() => {
            fetchVehicles(input.value.trim());
        }, 400);
    });
});
