document.addEventListener("DOMContentLoaded", () => {

    // Elementos DOM
    const UI = {
        modalCreacion: document.getElementById("vehicle_modal"),
        modalDetalle: document.getElementById("vehicleDetailModal"),
        btnAddVehicle: document.getElementById("btnAddVehicle"),
        searchForm: document.getElementById("vehicleSearchForm"),
        searchInput: document.getElementById("vehicleSearchInput"),
        vehicleList: document.getElementById("vehicleList"),
        loader: document.getElementById("vehicleLoader"),
        vehicleDetailContent: document.getElementById("vehicleDetailContent"),
        closeDetailModalBtn: document.getElementById("closeVehicleDetailModal"),
        toasts: document.querySelectorAll(".toast"),
    };

    const TYPING_DELAY = 400;
    let typingTimer;

    // Manejo de Modales

    const toggleModal = (modal, show) => {
        if (!modal) return;
        modal.style.display = show ? "block" : "none";
        document.body.style.overflow = show ? "hidden" : "";
    };

    // Manejo de Toast

    const showToasts = () => {
        if (!UI.toasts.length) return;
        const appearDelay = 500;
        const displayTime = 4000;
        UI.toasts.forEach((toast, i) => {
            setTimeout(() => toast.classList.add("show"), appearDelay + i * 200);
            setTimeout(() => {
                toast.classList.add("hide");
                toast.addEventListener('transitionend', () => toast.remove(), { once: true });
            }, displayTime + i * 200);
        });
    };

    // Renderizad

    // Renderiza la lista de vehículos en el DOM.
    const renderVehicles = (vehicles) => {
        UI.vehicleList.innerHTML = "";

        if (!vehicles || vehicles.length === 0) {
            UI.vehicleList.innerHTML = `<div class="empty-list-message">No se encontraron vehículos.</div>`;
            return;
        }

        const vehicleHTML = vehicles.map(v => `
            <article class="vehicle-card" data-patente="${v.patente}">
                <img src="${v.imagen_url || '/static/img/img_not_found.jpg'}" class="vehicle-image" alt="${v.marca} ${v.modelo}">
                <div class="vehicle-info">
                    <h2 class="vehicle-title">${v.patente}</h2>
                    <p class="vehicle-description">${v.marca} - ${v.modelo}</p>
                    <p class="vehicle-description">Año: ${v.anio}</p>
                </div>
                <svg xmlns="http://www.w3.org/2000/svg" class="vehicle-next-icon" viewBox="0 0 42 42">
                    <path fill="currentColor" fill-rule="evenodd" d="M13.933 1L34 21.068L14.431 40.637l-4.933-4.933l14.638-14.636L9 5.933z" />
                </svg>
            </article>
        `).join('');

        UI.vehicleList.innerHTML = vehicleHTML;
    };


    // Rellena el contenido del modal de detalle del vehículo.
    const renderVehicleDetail = (vehicle) => {
        UI.vehicleDetailContent.innerHTML = `
            <img src="${vehicle.imagen_url || '/static/img/img_not_found.jpg'}" alt="${vehicle.marca} ${vehicle.modelo}">
            <h2>${vehicle.patente}</h2>
            <p><strong>Marca:</strong> ${vehicle.marca}</p>
            <p><strong>Modelo:</strong> ${vehicle.modelo}</p>
            <p><strong>Año:</strong> ${vehicle.anio}</p>
            <p><strong>Tipo:</strong> ${vehicle.tipo_vehiculo || '-'}</p>
            <p><strong>Estado mantención:</strong> ${vehicle.estado_mantencion || '-'}</p>
            <p><strong>Kilometraje:</strong> ${vehicle.kilometraje_actual || '0'} km</p>
            <p><strong>Observaciones:</strong> ${vehicle.observaciones || '-'}</p>
        `;
    };


    //Busca vehículos en el servidor.
    const fetchVehicles = async (query = "") => {
        UI.vehicleList.innerHTML = "";
        UI.loader.classList.remove("hidden");

        try {
            const res = await fetch(`/vehiculos/search/?q=${encodeURIComponent(query)}`);
            if (!res.ok) throw new Error("Error en la solicitud al servidor");

            const data = await res.json();
            renderVehicles(data.vehicles || []);
        } catch (err) {
            console.error("Error al buscar vehículos:", err);
            renderVehicles([]);
        } finally {
            UI.loader.classList.add("hidden");
        }
    };

    // Manejo de Eventos
    const handleSearchSubmit = (e) => {
        e.preventDefault();
        clearTimeout(typingTimer);
        fetchVehicles(UI.searchInput.value.trim());
    };

    const handleSearchInput = () => {
        clearTimeout(typingTimer);
        typingTimer = setTimeout(() => fetchVehicles(UI.searchInput.value.trim()), TYPING_DELAY);
    };

    const handleVehicleListClick = async (e) => {
        const card = e.target.closest(".vehicle-card");
        if (!card) return;

        const patente = card.dataset.patente;

        toggleModal(UI.modalDetalle, true);
        UI.vehicleDetailContent.innerHTML = `
            <div class="modal-loader">
                <div class="spinner"></div>
                <p>Cargando detalles...</p>
            </div>
        `;

        try {
            const res = await fetch(`/vehiculos/detail/?patente=${encodeURIComponent(patente)}`);
            if (!res.ok) throw new Error("No se pudo obtener la información del vehículo");

            const data = await res.json();
            const vehicle = data.vehicle || data;

            renderVehicleDetail(vehicle);
            toggleModal(UI.modalDetalle, true);
        } catch (err) {
            console.error("Error cargando detalle del vehículo:", err);
            alert("No se pudo cargar el detalle del vehículo. Inténtalo nuevamente.");
        }
    };

    // Asignación de Eventos
    UI.btnAddVehicle?.addEventListener("click", () => toggleModal(UI.modalCreacion, true));
    UI.searchForm.addEventListener("submit", handleSearchSubmit);
    UI.searchInput.addEventListener("input", handleSearchInput);
    UI.vehicleList.addEventListener("click", handleVehicleListClick);
    UI.closeDetailModalBtn?.addEventListener("click", () => toggleModal(UI.modalDetalle, false));

    // Evento para cerrar modales al hacer clic fuera de ellos
    window.addEventListener("click", e => {
        if (e.target === UI.modalCreacion) toggleModal(UI.modalCreacion, false);
        if (e.target === UI.modalDetalle) toggleModal(UI.modalDetalle, false);
    });

    // Inicialización de Toast
    showToasts();
});