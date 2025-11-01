document.addEventListener("DOMContentLoaded", () => {

    // Elementos DOM
    const UI = {
        modalCreacion: document.getElementById("vehicleModal"),
        modalDetalle: document.getElementById("vehicleDetailModal"),
        btnAddVehicle: document.getElementById("btnAddVehicle"),
        searchForm: document.getElementById("vehicleSearchForm"),
        searchInput: document.getElementById("vehicleSearchInput"),
        vehicleList: document.getElementById("vehicleList"),
        loader: document.getElementById("vehicleLoader"),
        vehicleDetailContent: document.getElementById("vehicleDetailContent"),
        toasts: document.querySelectorAll(".toast"),
    };

    const TYPING_DELAY = 400;
    let typingTimer;

    // Manejo de Modales

    const creationModalInstance = UI.modalCreacion
        ? new bootstrap.Modal(UI.modalCreacion)
        : null;

    const detailModalInstance = UI.modalDetalle
        ? new bootstrap.Modal(UI.modalDetalle)
        : null;

    UI.vehicleList.addEventListener('show.bs.dropdown', (event) => {
        const card = event.target.closest('.vehicle-card');
        if (card) {
            // Eleva la tarjeta para que su dropdown se muestre por encima de las otras
            card.style.position = 'relative'; // Necesario para que z-index funcione
            card.style.zIndex = '100';        // Un z-index alto
        }
    });

    // Escucha cuando CUALQUIER dropdown en la lista se está cerrando
    UI.vehicleList.addEventListener('hide.bs.dropdown', (event) => {
        const card = event.target.closest('.vehicle-card');
        if (card) {
            // Devuelve la tarjeta a su estado normal
            card.style.zIndex = 'auto';
        }
    });

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

    // Renderizado

    // Renderiza la lista de vehículos en el DOM.
    const renderVehicles = (vehicles) => {
        UI.vehicleList.innerHTML = "";

        if (!vehicles || vehicles.length === 0) {
            UI.vehicleList.innerHTML = `<div class="alert alert-info">No hay vehículos registrados.</div>`;
            return;
        }

        const vehicleHTML = vehicles.map(vehicle => `
            <div class="card mb-3 vehicle-card" data-license-plate="${vehicle.license_plate}">
                <div class="row g-0">
                    <div class="col-md-2 d-flex align-items-center justify-content-center p-2">
                        <img src="${vehicle.imagen_url || '/static/img/img_not_found.jpg'}" 
                             class="img-fluid rounded" 
                             alt="${vehicle.brand} ${vehicle.model}">
                    </div>
                    <div class="col-md-10">
                        
                        <div class="card-body d-flex justify-content-between align-items-start">
                            
                            <div class="vehicle-card-content">
                                <h5 class="card-title mb-1">${vehicle.license_plate}</h5>
                                <p class="card-text mb-0"><small class="text-muted">${vehicle.brand} - ${vehicle.model} (${vehicle.year})</small></p>
                                <p class="card-text">
                                    ${vehicle.vehicle_type_name ? `<span class="badge bg-secondary">${vehicle.vehicle_type_name}</span>` : ''}
                                    ${vehicle.vehicle_status_name ? `<span class="badge bg-success">${vehicle.vehicle_status_name}</span>` : ''}
                                </p>
                            </div>
                            
                            <div class="dropdown">
                                <a href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false" class="text-secondary">
                                    <i class="bi bi-three-dots-vertical fs-5"></i>
                                </a>
                              
                                <ul class="dropdown-menu dropdown-menu-end">
                                  <li><a class="dropdown-item" href="#"><i class="bi bi-pencil-fill me-2"></i> Editar</a></li>
                                  <li><a class="dropdown-item text-danger" href="#"><i class="bi bi-trash-fill me-2"></i> Borrar</a></li>
                                </ul>
                            </div>

                        </div>
                    </div>

                    </div>
            </div>
        `).join('');

        UI.vehicleList.innerHTML = vehicleHTML;
    };


    // Rellena el contenido del modal de detalle del vehículo.
    const renderVehicleDetail = (vehicle) => {
        UI.vehicleDetailContent.innerHTML = `
        <div class="text-center mb-3">
            <img src="${vehicle.imagen_url || '/static/img/img_not_found.jpg'}" 
                 class="img-fluid rounded" 
                 alt="${vehicle.brand} ${vehicle.model}"
                 style="max-height: 200px; width: auto;">
        </div>

        <form id="vehicleDetailForm">
            <fieldset id="vehicleDetailFieldset" disabled>

                <div class="form-floating mb-3">
                    <input type="text" class="form-control" id="detail_license_plate" value="${vehicle.license_plate || ''}" placeholder=" " disabled>
                    <label for="detail_license_plate">Patente</label>
                </div>

                <div class="row g-2 mb-3">
                    <div class="col-md">
                        <div class="form-floating">
                            <input type="text" class="form-control" id="detail_brand" value="${vehicle.brand || ''}" placeholder=" ">
                            <label for="detail_brand">Marca</label>
                        </div>
                    </div>
                    <div class="col-md">
                        <div class="form-floating">
                            <input type="text" class="form-control" id="detail_model" value="${vehicle.model || ''}" placeholder=" ">
                            <label for="detail_model">Modelo</label>
                        </div>
                    </div>
                </div>

                <div class="row g-2 mb-3">
                    <div class="col-md">
                        <div class="form-floating">
                            <input type="number" class="form-control" id="detail_year" value="${vehicle.year || ''}" placeholder=" ">
                            <label for="detail_year">Año</label>
                        </div>
                    </div>
                    <div class="col-md">
                        <div class="form-floating">
                            <input type="number" class="form-control" id="detail_mileage" value="${vehicle.mileage || ''}" placeholder=" ">
                            <label for="detail_mileage">Kilometraje (km)</label>
                        </div>
                    </div>
                </div>

                <div class="row g-2 mb-3">
                    <div class="col-md">
                        <div class="form-floating">
                            <input type="text" class="form-control" id="detail_vehicle_type" value="${vehicle.vehicle_type_name || ''}" placeholder=" ">
                            <label for="detail_vehicle_type">Tipo</label>
                        </div>
                    </div>
                    <div class="col-md">
                        <div class="form-floating">
                            <input type="text" class="form-control" id="detail_vehicle_status" value="${vehicle.vehicle_status_name || ''}" placeholder=" ">
                            <label for="detail_vehicle_status">Estado</label>
                        </div>
                    </div>
                </div>

                <div class="form-floating mb-3">
                    <input type="text" class="form-control" id="detail_fire_station" value="${vehicle.fire_station_name || ''}" placeholder=" ">
                    <label for="detail_fire_station">Cuartel</label>
                </div>
                
                <div class="row g-2 mb-3">
                    <div class="col-md">
                        <div class="form-floating">
                            <input type="text" class="form-control" id="detail_engine_number" value="${vehicle.engine_number || ''}" placeholder=" ">
                            <label for="detail_engine_number">Número de Motor</label>
                        </div>
                    </div>
                    <div class="col-md">
                        <div class="form-floating">
                            <input type="text" class="form-control" id="detail_vin" value="${vehicle.vin || ''}" placeholder=" ">
                            <label for="detail_vin">VIN (Chasis)</label>
                        </div>
                    </div>
                </div>
                
                <div class="row g-2 mb-3">
                    <div class="col-md">
                        <div class="form-floating">
                            <input type="number" class="form-control" id="detail_oil_capacity" value="${vehicle.oil_capacity_liters || ''}" placeholder=" ">
                            <label for="detail_oil_capacity">Capacidad de Aceite (L)</label>
                        </div>
                    </div>
                    <div class="col-md">
                        <div class="form-floating">
                            <input type="text" class="form-control" id="detail_oil_type" value="${vehicle.oil_type_name || ''}" placeholder=" ">
                            <label for="detail_oil_type">Tipo de Aceite</label>
                        </div>
                    </div>
                </div>

                <div class="row g-2 mb-3">
                    <div class="col-md">
                        <div class="form-floating">
                            <input type="text" class="form-control" id="detail_fuel_type" value="${vehicle.fuel_type_name || ''}" placeholder=" ">
                            <label for="detail_fuel_type">Combustible</label>
                        </div>
                    </div>
                    <div class="col-md">
                        <div class="form-floating">
                            <input type="text" class="form-control" id="detail_transmission_type" value="${vehicle.transmission_type_name || ''}" placeholder=" ">
                            <label for="detail_transmission_type">Transmisión</label>
                        </div>
                    </div>
                </div>
                
                <div class="row g-2 mb-3">
                    <div class="col-md">
                        <div class="form-floating">
                            <input type="date" class="form-control" id="detail_mileage_last_updated" value="${vehicle.mileage_last_updated || ''}" placeholder=" ">
                            <label for="detail_mileage_last_updated">Último Kilometraje</glabel>
                        </div>
                    </div>
                    <div class="col-md">
                        <div class="form-floating">
                            <input type="date" class="form-control" id="detail_registration_date" value="${vehicle.registration_date || ''}" placeholder=" ">
                            <label for="detail_registration_date">Fecha Inscripción</label>
                        </div>
                    </div>
                </div>
                
                <div class="form-floating mb-3">
                    <input type="date" class="form-control" id="detail_next_revision_date" value="${vehicle.next_revision_date || ''}" placeholder=" ">
                    <label for="detail_next_revision_date">Próxima Revisión</label>
                </div>

            </fieldset>
        </form>
    `;
    };


    //Busca vehículos en el servidor.
    const fetchVehicles = async (query = "") => {
        UI.vehicleList.innerHTML = "";
        UI.loader.classList.remove("d-none");

        try {
            const res = await fetch(`/vehiculos/search/?q=${encodeURIComponent(query)}`);
            if (!res.ok) throw new Error("Error en la solicitud al servidor");

            const data = await res.json();
            renderVehicles(data.vehicles || []);
        } catch (err) {
            console.error("Error al buscar vehículos:", err);
            renderVehicles([]);
        } finally {
            UI.loader.classList.add("d-none");
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
        const dropdown = e.target.closest(".dropdown");
        if (dropdown) {
            return;
        }

        const card = e.target.closest(".vehicle-card");
        if (!card) return;

        // Obtener la patente del nuevo atributo data
        const licensePlate = card.dataset.licensePlate || card.dataset.license_plate;

        detailModalInstance?.show();
        UI.vehicleDetailContent.innerHTML = `
            <div class="d-flex justify-content-center align-items-center" style="min-height: 200px;">
                <div class="spinner-border text-danger" role="status">
                    <span class="visually-hidden">Cargando detalles...</span>
                </div>
            </div>
        `;

        try {
            const res = await fetch(`/vehiculos/detail/?license_plate=${encodeURIComponent(licensePlate)}`);
            if (!res.ok) throw new Error("No se pudo obtener la información del vehículo");

            const data = await res.json();
            const vehicle = data.vehicle || data;

            renderVehicleDetail(vehicle);
        } catch (err) {
            console.error("Error cargando detalle del vehículo:", err);
            UI.vehicleDetailContent.innerHTML = `<div class="alert alert-danger">No se pudo cargar el detalle del vehículo.</div>`;
            alert("No se pudo cargar el detalle del vehículo. Inténtalo nuevamente.");
        }
    };

    // Asignación de Eventos
    UI.btnAddVehicle?.addEventListener("click", () => creationModalInstance?.show());
    UI.searchForm.addEventListener("submit", handleSearchSubmit);
    UI.searchInput.addEventListener("input", handleSearchInput);
    UI.vehicleList.addEventListener("click", handleVehicleListClick);

    // Inicialización de Toast
    showToasts();
});