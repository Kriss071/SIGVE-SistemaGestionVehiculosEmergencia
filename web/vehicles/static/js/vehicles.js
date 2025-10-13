document.addEventListener("DOMContentLoaded", () => {

    // Elementos DOM
    const modal = document.getElementById("vehicle_modal");
    const btnAdd = document.getElementById("btnAddVehicle");
    const toasts = document.querySelectorAll(".toast");
    const vehicleSearchForm = document.getElementById("vehicleSearchForm");
    const vehicleSearchInput = document.getElementById("vehicleSearchInput");
    const vehicleList = document.getElementById("vehicleList");
    const vehicleLoader = document.getElementById("vehicleLoader");
    const vehicleDetailModal = document.getElementById("vehicleDetailModal");
    const vehicleDetailContent = document.getElementById("vehicleDetailContent");
    const closeVehicleDetailModal = document.getElementById("closeVehicleDetailModal");

    // Modal Formulario Creación Vehiculo

    const openModal = () => {
        modal.style.display = "block";
        document.body.style.overflow = "hidden";
    };

    const closeModal = () => {
        modal.style.display = "none";
        document.body.style.overflow = "";
    };

    btnAdd.addEventListener("click", openModal);
    window.addEventListener("click", e => {
        if (e.target === modal) closeModal();
    });

    // Modal detalle vehiculo
    const openVehicleDetailModal = (vehicle) => {
        vehicleDetailContent.innerHTML = `
        <img src="${vehicle.imagen_url || '/static/img/img_not_found.jpg'}" 
             alt="${vehicle.marca} ${vehicle.modelo}">
        <h2>${vehicle.patente}</h2>
        <p><strong>Marca:</strong> ${vehicle.marca}</p>
        <p><strong>Modelo:</strong> ${vehicle.modelo}</p>
        <p><strong>Año:</strong> ${vehicle.anio}</p>
        <p><strong>Tipo:</strong> ${vehicle.tipo_vehiculo || '-'}</p>
        <p><strong>Estado mantención:</strong> ${vehicle.estado_mantencion || '-'}</p>`;
        vehicleDetailModal.style.display = "block";
        document.body.style.overflow = "hidden";
    };

    const closeVehicleDetail = () => {
        vehicleDetailModal.style.display = "none";
        document.body.style.overflow = "";
    };

    closeVehicleDetailModal.addEventListener("click", closeVehicleDetail);
    window.addEventListener("click", e => {
        if (e.target === vehicleDetailModal) closeVehicleDetail();
    });

    vehicleList.addEventListener("click", (e) => {
        const card = e.target.closest(".vehicle-card");
        if (!card) return;

        // Extraer datos del card (puedes usar dataset para cada campo)
        const patente = card.querySelector(".vehicle-title").textContent;
        const marcaModelo = card.querySelectorAll(".vehicle-description");
        const marcaModeloText = marcaModelo[0]?.textContent.split(" - ") || ["", ""];
        const anioText = marcaModelo[1]?.textContent.replace("Año: ", "") || "";
        

        const vehicleData = {
            patente: patente,
            marca: marcaModeloText[0],
            modelo: marcaModeloText[1],
            anio: anioText,
            imagen_url: card.querySelector("img")?.src,
            tipo_vehiculo: card.dataset.tipo_vehiculo || "",
            estado_mantencion: card.dataset.estado_mantencion || ""
        };

        openVehicleDetailModal(vehicleData);
    });

    // Toast

    const showToasts = () => {
        const appearDelay = 500;
        const displayTime = 4000;
        toasts.forEach((toast, i) => {
            setTimeout(() => toast.classList.add("show"), appearDelay + i * 200);
            setTimeout(() => {
                toast.classList.add("hide");
                setTimeout(() => toast.remove(), 500);
            }, displayTime + i * 200);
        });
    };
    showToasts();

    // Buscador

    let typingTimer;
    const TYPING_DELAY = 400;

    const hideElements = (selector) => vehicleList.querySelectorAll(selector).forEach(el => el.style.display = "none");
    const showElements = (selector) => vehicleList.querySelectorAll(selector).forEach(el => el.style.display = "");

    const clearList = () => vehicleList.querySelectorAll(".vehicle-card, li").forEach(el => el.remove());


    const renderVehicles = (vehicles) => {
        clearList();
        if (!vehicles.length) {
            const li = document.createElement("li");
            li.textContent = "No hay vehículos registrados.";
            vehicleList.appendChild(li);
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
            vehicleList.appendChild(article);
        });
    };

    const fetchVehicles = async (query) => {
        vehicleLoader.classList.remove("hidden");
        hideElements(".vehicle-card, li");
        try {
            const res = await fetch(`/vehiculos/search/?q=${encodeURIComponent(query)}`);
            const data = await res.json();
            renderVehicles(data.vehicles);
        } catch (err) {
            console.error("Error al buscar vehículos:", err);
        } finally {
            vehicleLoader.classList.add("hidden");
            showElements(".vehicle-card, li");
        }
    };

    vehicleSearchForm.addEventListener("submit", e => {
        e.preventDefault();
        fetchVehicles(vehicleSearchInput.value.trim());
    });

    vehicleSearchInput.addEventListener("input", () => {
        clearTimeout(typingTimer);
        typingTimer = setTimeout(() => fetchVehicles(vehicleSearchInput.value.trim()), TYPING_DELAY);
    });
})