document.addEventListener("DOMContentLoaded", () => {

    // Elementos DOM
    const UI = {
        modalCreacion: document.getElementById("vehicleModal"),
        modalDetalle: document.getElementById("vehicleDetailModal"),
        modalConfirmacion: document.getElementById("confirmationModal"),
        modalMensaje: document.getElementById("messageModal"),
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
    
    // Estado del modal de detalle
    let isEditMode = false;
    let originalVehicleData = null;
    let currentLicensePlate = null;
    let pendingEditMode = false; // Para saber si debe entrar en modo edición después de cargar

    // Manejo de Modales

    const creationModalInstance = UI.modalCreacion
        ? new bootstrap.Modal(UI.modalCreacion)
        : null;

    const detailModalInstance = UI.modalDetalle
        ? new bootstrap.Modal(UI.modalDetalle)
        : null;

    const confirmationModalInstance = UI.modalConfirmacion
        ? new bootstrap.Modal(UI.modalConfirmacion)
        : null;

    const messageModalInstance = UI.modalMensaje
        ? new bootstrap.Modal(UI.modalMensaje)
        : null;

    // Función para ocultar todos los botones del modal (durante carga)
    const hideModalButtons = () => {
        const viewModeButtons = document.getElementById('viewModeButtons');
        const editModeButtons = document.getElementById('editModeButtons');
        if (viewModeButtons) viewModeButtons.style.display = 'none';
        if (editModeButtons) editModeButtons.style.display = 'none';
    };

    // Resetear estado cuando se cierra el modal de detalle
    if (UI.modalDetalle) {
        UI.modalDetalle.addEventListener('hidden.bs.modal', () => {
            isEditMode = false;
            pendingEditMode = false;
            originalVehicleData = null;
            currentLicensePlate = null;
            // Ocultar botones al cerrar
            hideModalButtons();
        });
        
        // También resetear cuando se empieza a abrir el modal
        UI.modalDetalle.addEventListener('show.bs.modal', () => {
            // Si no hay un pendingEditMode activo, resetear el modo
            if (!pendingEditMode) {
                isEditMode = false;
            }
        });
    }

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

    // Manejo de Modales de Mensajes

    /**
     * Muestra un modal de confirmación y retorna una promesa que se resuelve con true/false
     * @param {string} title - Título del modal
     * @param {string} message - Mensaje del modal
     * @returns {Promise<boolean>} - true si se confirma, false si se cancela
     */
    const showConfirmation = (title, message) => {
        return new Promise((resolve) => {
            const titleElement = document.getElementById('confirmationModalTitle');
            const bodyElement = document.getElementById('confirmationModalBody');
            const confirmBtn = document.getElementById('confirmationModalConfirmBtn');

            if (titleElement) titleElement.textContent = title;
            if (bodyElement) bodyElement.textContent = message;

            // Remover listeners anteriores
            const newConfirmBtn = confirmBtn.cloneNode(true);
            confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);

            // Agregar nuevo listener
            newConfirmBtn.addEventListener('click', () => {
                confirmationModalInstance?.hide();
                resolve(true);
            }, { once: true });

            // Manejar el cierre del modal sin confirmar
            const handleCancel = () => {
                resolve(false);
                UI.modalConfirmacion.removeEventListener('hidden.bs.modal', handleCancel);
            };
            UI.modalConfirmacion.addEventListener('hidden.bs.modal', handleCancel, { once: true });

            confirmationModalInstance?.show();
        });
    };

    /**
     * Muestra un modal de mensaje (éxito o error)
     * @param {string} title - Título del modal
     * @param {string} message - Mensaje del modal
     * @param {string} type - Tipo de mensaje: 'success', 'error', 'info', 'warning'
     */
    const showMessage = (title, message, type = 'info') => {
        const titleElement = document.getElementById('messageModalTitle');
        const bodyElement = document.getElementById('messageModalBody');
        const iconElement = document.getElementById('messageModalIcon');
        const headerElement = document.getElementById('messageModalHeader');

        if (titleElement) titleElement.textContent = title;
        if (bodyElement) bodyElement.textContent = message;

        // Configurar icono y colores según el tipo
        if (iconElement && headerElement) {
            // Limpiar clases anteriores
            iconElement.className = 'bi me-2';
            headerElement.className = 'modal-header';

            switch (type) {
                case 'success':
                    iconElement.classList.add('bi-check-circle-fill', 'text-success');
                    headerElement.classList.add('bg-success', 'bg-opacity-10', 'border-success');
                    break;
                case 'error':
                    iconElement.classList.add('bi-x-circle-fill', 'text-danger');
                    headerElement.classList.add('bg-danger', 'bg-opacity-10', 'border-danger');
                    break;
                case 'warning':
                    iconElement.classList.add('bi-exclamation-triangle-fill', 'text-warning');
                    headerElement.classList.add('bg-warning', 'bg-opacity-10', 'border-warning');
                    break;
                default: // info
                    iconElement.classList.add('bi-info-circle-fill', 'text-info');
                    headerElement.classList.add('bg-info', 'bg-opacity-10', 'border-info');
            }
        }

        messageModalInstance?.show();
    };

    // Renderizado

    // Renderiza la lista de vehículos en el DOM.
    const renderVehicles = (vehicles) => {
        UI.vehicleList.innerHTML = "";

        if (!vehicles || vehicles.length === 0) {
            UI.vehicleList.innerHTML = `<div class="alert alert-info">No hay vehículos registrados.</div>`;
            return;
        }

        // Obtener el rol del usuario del atributo data
        const userRole = document.querySelector('[data-user-role]')?.dataset.userRole;
        const isAdmin = userRole === 'Administrador';

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
                                  ${isAdmin ? `<li><a class="dropdown-item edit-vehicle-btn" href="#" data-license-plate="${vehicle.license_plate}"><i class="bi bi-pencil-fill me-2"></i> Editar</a></li>` : ''}
                                  ${isAdmin ? `<li><a class="dropdown-item text-danger delete-vehicle-btn" href="#" data-license-plate="${vehicle.license_plate}"><i class="bi bi-trash-fill me-2"></i> Borrar</a></li>` : ''}
                                </ul>
                            </div>

                        </div>
                    </div>

                    </div>
            </div>
        `).join('');

        UI.vehicleList.innerHTML = vehicleHTML;
    };


    // Función para actualizar los botones del modal según el modo
    const updateModalButtons = () => {
        const viewModeButtons = document.getElementById('viewModeButtons');
        const editModeButtons = document.getElementById('editModeButtons');
        const modalDeleteBtn = document.getElementById('modalDeleteVehicleBtn');
        const modalEditBtn = document.getElementById('modalEditVehicleBtn');
        
        const userRole = document.querySelector('[data-user-role]')?.dataset.userRole;
        const isAdmin = userRole === 'Administrador';

        if (isEditMode) {
            // Modo edición: mostrar botones Cancelar y Guardar
            if (viewModeButtons) viewModeButtons.style.display = 'none';
            if (editModeButtons) editModeButtons.style.display = 'block';
        } else {
            // Modo visualización: mostrar botones Eliminar y Editar
            if (viewModeButtons) viewModeButtons.style.display = 'block';
            if (editModeButtons) editModeButtons.style.display = 'none';
            
            // Mostrar botones solo si es administrador
            if (modalDeleteBtn) modalDeleteBtn.style.display = isAdmin ? 'inline-block' : 'none';
            if (modalEditBtn) modalEditBtn.style.display = isAdmin ? 'inline-block' : 'none';
        }
    };

    // Función para habilitar/deshabilitar el formulario
    const toggleFormEdit = (enable) => {
        const fieldset = document.getElementById('vehicleDetailFieldset');
        if (fieldset) {
            fieldset.disabled = !enable;
        }
    };

    // Función para entrar en modo edición
    const enterEditMode = () => {
        isEditMode = true;
        toggleFormEdit(true);
        updateModalButtons();
    };

    // Función para salir del modo edición
    const exitEditMode = () => {
        isEditMode = false;
        toggleFormEdit(false);
        updateModalButtons();
    };

    // Función para cancelar edición y restaurar datos originales
    const cancelEdit = () => {
        if (originalVehicleData) {
            renderVehicleDetail(originalVehicleData, false);
            exitEditMode();
            // Vincular eventos nuevamente
            attachModalEventListeners();
        }
    };

    // Función para recolectar datos del formulario
    const collectFormData = () => {
        return {
            license_plate: currentLicensePlate,
            brand: document.getElementById('detail_brand')?.value || '',
            model: document.getElementById('detail_model')?.value || '',
            year: parseInt(document.getElementById('detail_year')?.value) || null,
            mileage: parseInt(document.getElementById('detail_mileage')?.value) || null,
            engine_number: document.getElementById('detail_engine_number')?.value || '',
            vin: document.getElementById('detail_vin')?.value || '',
            oil_capacity_liters: parseFloat(document.getElementById('detail_oil_capacity')?.value) || null,
            mileage_last_updated: document.getElementById('detail_mileage_last_updated')?.value || '',
            registration_date: document.getElementById('detail_registration_date')?.value || '',
            next_revision_date: document.getElementById('detail_next_revision_date')?.value || ''
        };
    };

    // Función para guardar cambios
    const saveVehicleChanges = async () => {
        if (!currentLicensePlate) {
            showMessage('Error', 'No se pudo identificar el vehículo a actualizar.', 'error');
            return;
        }

        const formData = collectFormData();

        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';

            const res = await fetch('/vehiculos/update/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(formData)
            });

            if (!res.ok) {
                const errorData = await res.json().catch(() => ({ message: 'Error desconocido' }));
                throw new Error(errorData.message || 'Error al actualizar el vehículo');
            }

            const data = await res.json();

            if (data.success) {
                // Actualizar datos originales con los nuevos
                originalVehicleData = data.vehicle;
                
                // Salir del modo edición
                exitEditMode();
                
                // Recargar los detalles con los datos actualizados
                renderVehicleDetail(data.vehicle, false);
                attachModalEventListeners();
                
                // Recargar la lista de vehículos
                fetchVehicles(UI.searchInput.value.trim());
                
                // Mostrar mensaje de éxito
                showMessage('Éxito', data.message || 'Vehículo actualizado correctamente', 'success');
            } else {
                throw new Error(data.message || 'No se pudo actualizar el vehículo');
            }
        } catch (err) {
            console.error("Error al actualizar vehículo:", err);
            showMessage('Error', `Error al actualizar el vehículo: ${err.message}`, 'error');
        }
    };

    // Rellena el contenido del modal de detalle del vehículo.
    const renderVehicleDetail = (vehicle, enterEditAfterRender = false) => {
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
        <input type="hidden" id="detail_current_license_plate" value="${vehicle.license_plate || ''}">
    `;
        
        // Actualizar estado
        currentLicensePlate = vehicle.license_plate;
        originalVehicleData = vehicle;
        
        // Si debe entrar en modo edición después de renderizar
        if (enterEditAfterRender || pendingEditMode) {
            isEditMode = false; // Resetear antes de entrar al modo edición
            pendingEditMode = false;
        } else {
            isEditMode = false;
        }
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
            // Re-vincular eventos de eliminación después de renderizar
            attachDeleteEventListeners();
        } catch (err) {
            console.error("Error al buscar vehículos:", err);
            renderVehicles([]);
        } finally {
            UI.loader.classList.add("d-none");
        }
    };

    // Función para eliminar un vehículo
    const deleteVehicle = async (licensePlate) => {
        if (!licensePlate) {
            showMessage('Error', 'No se pudo obtener la patente del vehículo.', 'error');
            return false;
        }

        // Confirmar eliminación
        const confirmMessage = `¿Estás seguro de que deseas eliminar el vehículo con patente "${licensePlate}"?\n\nEsta acción no se puede deshacer.`;
        const confirmed = await showConfirmation('Eliminar Vehículo', confirmMessage);
        
        if (!confirmed) {
            return false;
        }

        try {
            // Enviar petición de eliminación usando POST (más compatible que DELETE)
            const formData = new FormData();
            formData.append('license_plate', licensePlate);
            formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]')?.value || '');

            const res = await fetch('/vehiculos/delete/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                }
            });

            if (!res.ok) {
                const errorData = await res.json().catch(() => ({ message: 'Error desconocido' }));
                throw new Error(errorData.message || 'Error al eliminar el vehículo');
            }

            const data = await res.json();
            
            if (data.success) {
                // Cerrar el modal de detalle si está abierto
                detailModalInstance?.hide();
                
                // Recargar la lista de vehículos
                fetchVehicles(UI.searchInput.value.trim());
                
                // Mostrar mensaje de éxito
                showMessage('Éxito', data.message || 'Vehículo eliminado correctamente', 'success');
                return true;
            } else {
                throw new Error(data.message || 'No se pudo eliminar el vehículo');
            }
        } catch (err) {
            console.error("Error al eliminar vehículo:", err);
            showMessage('Error', `Error al eliminar el vehículo: ${err.message}`, 'error');
            return false;
        }
    };

    // Vincular eventos de eliminación y edición a los botones del dropdown
    const attachDeleteEventListeners = () => {
        // Eliminar listeners anteriores para evitar duplicados
        document.querySelectorAll('.delete-vehicle-btn').forEach(btn => {
            btn.removeEventListener('click', handleDeleteClick);
        });

        // Agregar nuevos listeners
        document.querySelectorAll('.delete-vehicle-btn').forEach(btn => {
            btn.addEventListener('click', handleDeleteClick);
        });

        // Vincular eventos de edición
        document.querySelectorAll('.edit-vehicle-btn').forEach(btn => {
            btn.removeEventListener('click', handleEditClick);
            btn.addEventListener('click', handleEditClick);
        });
    };

    // Manejador de clic en botón eliminar del dropdown
    const handleDeleteClick = async (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        const licensePlate = e.currentTarget.dataset.licensePlate || e.currentTarget.dataset.license_plate;
        if (licensePlate) {
            await deleteVehicle(licensePlate);
        }
    };

    // Manejador de clic en botón eliminar del modal
    const handleModalDeleteClick = async (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        const licensePlateInput = document.getElementById('detail_current_license_plate');
        const licensePlate = licensePlateInput?.value;
        
        if (licensePlate) {
            await deleteVehicle(licensePlate);
        } else {
            showMessage('Error', 'No se pudo obtener la patente del vehículo.', 'error');
        }
    };

    // Manejador de clic en botón editar del modal
    const handleModalEditClick = (e) => {
        e.preventDefault();
        e.stopPropagation();
        enterEditMode();
    };

    // Manejador de clic en botón cancelar edición
    const handleCancelEditClick = (e) => {
        e.preventDefault();
        e.stopPropagation();
        cancelEdit();
    };

    // Manejador de clic en botón guardar cambios
    const handleSaveVehicleClick = async (e) => {
        e.preventDefault();
        e.stopPropagation();
        await saveVehicleChanges();
    };

    // Manejador de clic en botón editar del dropdown
    const handleEditClick = async (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        const licensePlate = e.currentTarget.dataset.licensePlate || e.currentTarget.dataset.license_plate;
        if (!licensePlate) return;

        // Marcar que debe entrar en modo edición después de cargar
        pendingEditMode = true;

        // Abrir el modal de detalle
        detailModalInstance?.show();
        
        // Ocultar botones mientras carga
        hideModalButtons();
        
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

            // Renderizar con la bandera de entrar en modo edición
            renderVehicleDetail(vehicle, true);
            attachModalEventListeners();
            
            // Entrar directamente en modo edición
            enterEditMode();
        } catch (err) {
            console.error("Error cargando detalle del vehículo:", err);
            UI.vehicleDetailContent.innerHTML = `<div class="alert alert-danger">No se pudo cargar el detalle del vehículo.</div>`;
            showMessage('Error', 'No se pudo cargar el detalle del vehículo. Inténtalo nuevamente.', 'error');
            pendingEditMode = false; // Resetear en caso de error
            updateModalButtons(); // Actualizar botones después de error
        }
    };

    // Función para vincular todos los eventos del modal
    const attachModalEventListeners = () => {
        const modalDeleteBtn = document.getElementById('modalDeleteVehicleBtn');
        const modalEditBtn = document.getElementById('modalEditVehicleBtn');
        const modalCancelBtn = document.getElementById('modalCancelEditBtn');
        const modalSaveBtn = document.getElementById('modalSaveVehicleBtn');

        if (modalDeleteBtn) {
            modalDeleteBtn.removeEventListener('click', handleModalDeleteClick);
            modalDeleteBtn.addEventListener('click', handleModalDeleteClick);
        }

        if (modalEditBtn) {
            modalEditBtn.removeEventListener('click', handleModalEditClick);
            modalEditBtn.addEventListener('click', handleModalEditClick);
        }

        if (modalCancelBtn) {
            modalCancelBtn.removeEventListener('click', handleCancelEditClick);
            modalCancelBtn.addEventListener('click', handleCancelEditClick);
        }

        if (modalSaveBtn) {
            modalSaveBtn.removeEventListener('click', handleSaveVehicleClick);
            modalSaveBtn.addEventListener('click', handleSaveVehicleClick);
        }

        // Actualizar visibilidad de botones
        updateModalButtons();
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
        // Ignorar clics en botones de eliminar o editar
        if (e.target.closest('.delete-vehicle-btn') || e.target.closest('.edit-vehicle-btn')) {
            return;
        }

        const dropdown = e.target.closest(".dropdown");
        if (dropdown) {
            return;
        }

        const card = e.target.closest(".vehicle-card");
        if (!card) return;

        // Obtener la patente del nuevo atributo data
        const licensePlate = card.dataset.licensePlate || card.dataset.license_plate;

        // Asegurarse de no estar en modo edición pendiente
        pendingEditMode = false;
        isEditMode = false; // Resetear explícitamente

        detailModalInstance?.show();
        
        // Ocultar botones mientras carga
        hideModalButtons();
        
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

            renderVehicleDetail(vehicle, false);
            attachModalEventListeners();
        } catch (err) {
            console.error("Error cargando detalle del vehículo:", err);
            UI.vehicleDetailContent.innerHTML = `<div class="alert alert-danger">No se pudo cargar el detalle del vehículo.</div>`;
            showMessage('Error', 'No se pudo cargar el detalle del vehículo. Inténtalo nuevamente.', 'error');
            updateModalButtons(); // Actualizar botones después de error
        }
    };

    // Asignación de Eventos
    UI.btnAddVehicle?.addEventListener("click", () => creationModalInstance?.show());
    UI.searchForm.addEventListener("submit", handleSearchSubmit);
    UI.searchInput.addEventListener("input", handleSearchInput);
    UI.vehicleList.addEventListener("click", handleVehicleListClick);

    // Vincular eventos de eliminación inicialmente (para vehículos renderizados en el servidor)
    attachDeleteEventListeners();

    // Inicialización de Toast
    showToasts();
});