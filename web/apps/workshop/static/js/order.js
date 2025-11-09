/**
 * SIGVE - Lógica del Modal de Creación de Órdenes
 *
 * Maneja el flujo de múltiples pasos:
 * 1. Cargar contexto (dropdowns)
 * 2. Buscar vehículo (live search)
 * 3. (Opcional) Crear vehículo
 * 4. Crear orden
 */
(function() {
    'use strict';

    // (Asegúrate de tener 'sigve.js' cargado para las utilidades)
    if (!window.SIGVE) {
        console.error("sigve.js no está cargado. El modal no funcionará.");
        window.SIGVE = { 
            showNotification: (msg, type) => console.log(type, msg),
            showButtonLoading: btn => btn.disabled = true,
            hideButtonLoading: btn => btn.disabled = false
        };
    }

    // URLs (necesarias para el JS)
    const CONTEXT_URL = '/taller/api/order/context/';
    const SEARCH_URL = '/taller/api/vehicles/search/';
    const CREATE_VEHICLE_URL = '/taller/api/vehicle/create/';
    const CREATE_ORDER_URL = '/taller/api/order/create/';

    // Elementos del DOM
    let modalEl, modalInstance, loadingEl, contentEl, footerEl;
    let step1, step2, step3;
    let searchInput, searchResultsContainer, searchResultsList, searchNotFound;
    let orderForm, vehicleForm;
    let selectedVehiclePlate, newVehiclePlate, orderVehicleId, newVehicleLicensePlateInput;

    // Estado
    let currentStep = 'loading';
    let formDataContext = {};
    let selectedVehicle = null;
    let searchTimer = null;

    /**
     * Controlador principal del Modal
     */
    window.OrderModal = (function() {

        function init() {
            modalEl = document.getElementById('orderModal');
            if (!modalEl) return;
            
            modalInstance = new bootstrap.Modal(modalEl);
            
            // Elementos principales
            loadingEl = document.getElementById('orderModalLoading');
            contentEl = document.getElementById('orderModalContent');
            footerEl = document.getElementById('orderModalFooter');

            // Pasos
            step1 = document.getElementById('step1SearchVehicle');
            step2 = document.getElementById('step2CreateOrder');
            step3 = document.getElementById('step3CreateVehicle');

            // Búsqueda (Paso 1)
            searchInput = document.getElementById('vehicleSearchInput');
            searchResultsContainer = document.getElementById('vehicleSearchResultsContainer');
            searchResultsList = document.getElementById('vehicleSearchResults');
            searchNotFound = document.getElementById('vehicleSearchNotFound');
            document.getElementById('showCreateVehicleBtn').addEventListener('click', () => showStep('create_vehicle'));

            // Formularios
            orderForm = document.getElementById('createOrderForm');
            vehicleForm = document.getElementById('createVehicleForm');

            // Campos dinámicos
            selectedVehiclePlate = document.getElementById('selectedVehiclePlate');
            newVehiclePlate = document.getElementById('newVehiclePlate');
            orderVehicleId = document.getElementById('orderVehicleId');
            newVehicleLicensePlateInput = document.getElementById('newVehicleLicensePlateInput');
            
            // Eventos
            modalEl.addEventListener('hidden.bs.modal', resetModal);
            searchInput.addEventListener('keyup', handleSearchInput);
        }

        /**
         * Abre el modal y comienza la carga de contexto
         */
        function open() {
            modalInstance.show();
            showStep('loading');
            loadContext();
        }

        /**
         * Carga los datos (mecánicos, tipos, etc.) para los dropdowns
         */
        async function loadContext() {
            try {
                const response = await fetch(CONTEXT_URL);
                if (!response.ok) throw new Error('Error de red');
                
                const data = await response.json();
                if (!data.success) throw new Error(data.error || 'Error cargando datos');

                formDataContext = data;
                
                // Poblar todos los <select>
                populateSelect('selectMaintenanceType', data.maintenance_types);
                populateSelect('selectMechanic', data.mechanics, true, 'id', 'full_name');
                populateSelect('selectStatus', data.order_statuses);
                populateSelect('selectVehicleType', data.vehicle_catalog_data.vehicle_types);
                populateSelect('selectFireStation', data.fire_stations);

                // Setear fecha de hoy
                document.getElementById('orderEntryDate').valueAsDate = new Date();
                
                showStep('search');

            } catch (error) {
                console.error('Error:', error);
                SIGVE.showNotification(error.message, 'error');
                modalInstance.hide();
            }
        }

        /**
         * Utilidad para poblar un <select>
         */
        function populateSelect(selectId, items, allowEmpty = false, valueKey = 'id', nameKey = 'name') {
            const select = document.getElementById(selectId);
            select.innerHTML = ''; // Limpiar
            
            if (allowEmpty) {
                select.add(new Option('Sin asignar', ''));
            }
            
            items.forEach(item => {
                select.add(new Option(item[nameKey], item[valueKey]));
            });
        }

        /**
         * Maneja el tipeo en el input de búsqueda (con debounce)
         */
        function handleSearchInput() {
            clearTimeout(searchTimer);
            searchTimer = setTimeout(() => {
                performSearch(searchInput.value.trim().toUpperCase());
            }, 300); // 300ms debounce
        }

        /**
         * Ejecuta la búsqueda AJAX
         */
        async function performSearch(query) {
            if (query.length < 1) {
                searchResultsContainer.style.display = 'none';
                searchNotFound.style.display = 'none';
                return;
            }

            try {
                const response = await fetch(`${SEARCH_URL}?q=${encodeURIComponent(query)}`);
                const data = await response.json();

                if (data.success && data.vehicles.length > 0) {
                    renderResults(data.vehicles);
                } else {
                    searchResultsContainer.style.display = 'none';
                    searchNotFound.style.display = 'block';
                }
            } catch (error) {
                SIGVE.showNotification('Error al buscar vehículo', 'error');
            }
        }

        /**
         * Dibuja los resultados de la búsqueda
         */
        function renderResults(vehicles) {
            searchResultsList.innerHTML = '';
            vehicles.forEach(v => {
                const li = document.createElement('li');
                li.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center';
                li.style.cursor = 'pointer';
                
                const statusName = v.vehicle_status_name || (v.vehicle_status && v.vehicle_status.name) || 'N/A';
                const statusBadgeClass = getVehicleStatusBadgeClass(statusName);
                const activeBadge = v.has_active_order ? `<span class="badge bg-danger ms-2">Orden activa</span>` : '';
                
                if (v.has_active_order) {
                    li.classList.add('list-group-item-warning');
                }
                
                li.innerHTML = `
                    <div>
                        <strong class="badge bg-dark">${v.license_plate}</strong>
                        <span class="ms-2">${v.brand} ${v.model} (${v.year})</span>
                        <span class="ms-2 badge ${statusBadgeClass}">${statusName}</span>
                        ${activeBadge}
                    </div>
                    <i class="bi bi-chevron-right"></i>
                `;
                li.onclick = () => handleVehicleSelection(v);
                searchResultsList.appendChild(li);
            });
            searchResultsContainer.style.display = 'block';
            searchNotFound.style.display = 'none';
        }

        /**
         * Acción al seleccionar un vehículo de la lista
         */
        function handleVehicleSelection(vehicle) {
            if (vehicle.has_active_order) {
                const statusLabel = vehicle.active_order_status || 'activa';
                SIGVE.showNotification(`El vehículo ${vehicle.license_plate} ya tiene una orden ${statusLabel.toLowerCase()}.`, 'warning');
                return;
            }
            selectVehicle(vehicle);
        }
        
        function selectVehicle(vehicle) {
            selectedVehicle = vehicle;
            selectedVehiclePlate.textContent = vehicle.license_plate;
            orderVehicleId.value = vehicle.id;
            showStep('create_order');
        }

        /**
         * Muestra el paso solicitado y oculta los demás
         */
        function showStep(stepName) {
            currentStep = stepName;
            
            // Ocultar todo
            loadingEl.style.display = 'none';
            contentEl.style.display = 'none';
            step1.style.display = 'none';
            step2.style.display = 'none';
            step3.style.display = 'none';
            
            // Mostrar el paso actual
            if (stepName === 'loading') {
                loadingEl.style.display = 'block';
                renderFooter('loading');
            } else {
                contentEl.style.display = 'block';
                if (stepName === 'search') {
                    step1.style.display = 'block';
                    searchInput.focus();
                    renderFooter('search');
                } else if (stepName === 'create_order') {
                    step2.style.display = 'block';
                    renderFooter('create_order');
                } else if (stepName === 'create_vehicle') {
                    // Pre-llenar patente desde la búsqueda
                    const plate = searchInput.value.trim().toUpperCase();
                    newVehiclePlate.textContent = plate;
                    newVehicleLicensePlateInput.value = plate;
                    step3.style.display = 'block';
                    renderFooter('create_vehicle');
                }
            }
        }

        /**
         * Dibuja los botones del footer según el paso
         */
        function renderFooter(stepName) {
            footerEl.innerHTML = '';
            let backBtn = `<button type="button" class="btn btn-secondary" onclick="OrderModal.goBack()">
                                <i class="bi bi-arrow-left"></i> Atrás
                           </button>`;
            let cancelBtn = `<button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Cancelar</button>`;

            if (stepName === 'search') {
                footerEl.innerHTML = cancelBtn;
            } else if (stepName === 'create_vehicle') {
                footerEl.innerHTML = `
                    ${backBtn}
                    <button type="button" class="btn btn-warning" id="submitVehicleBtn">
                        Guardar Vehículo y Continuar <i class="bi bi-arrow-right"></i>
                    </button>`;
                document.getElementById('submitVehicleBtn').addEventListener('click', handleSubmitVehicle);
            } else if (stepName === 'create_order') {
                footerEl.innerHTML = `
                    ${backBtn}
                    <button type="button" class="btn btn-primary" id="submitOrderBtn">
                        <i class="bi bi-check-lg"></i> Crear Orden
                    </button>`;
                document.getElementById('submitOrderBtn').addEventListener('click', handleSubmitOrder);
            }
        }

        /**
         * Lógica del botón "Atrás"
         */
        function goBack() {
            if (currentStep === 'create_order' || currentStep === 'create_vehicle') {
                showStep('search');
            }
        }

        /**
         * Envía el formulario de NUEVO VEHÍCULO
         */
        async function handleSubmitVehicle(e) {
            const submitBtn = e.target;
            if (!vehicleForm.checkValidity()) {
                vehicleForm.classList.add('was-validated');
                SIGVE.showNotification('Por favor completa los campos obligatorios del vehículo.', 'warning');
                return;
            }
            
            SIGVE.showButtonLoading(submitBtn);
            const formData = new FormData(vehicleForm);

            try {
                const response = await fetch(CREATE_VEHICLE_URL, {
                    method: 'POST',
                    body: formData,
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });
                const data = await response.json();

                if (data.success) {
                    SIGVE.showNotification('Vehículo registrado. Ahora crea la orden.', 'success');
                    selectVehicle(data.vehicle); // ¡Pasa al siguiente paso!
                } else {
                    const error = data.errors
                        ? Object.values(data.errors)[0][0]
                        : (data.error || 'Error desconocido');
                    SIGVE.showNotification(error, 'error');
                }
            } catch (error) {
                SIGVE.showNotification('Error de red al crear vehículo', 'error');
            } finally {
                SIGVE.hideButtonLoading(submitBtn);
            }
        }

        /**
         * Envía el formulario de NUEVA ORDEN
         */
        async function handleSubmitOrder(e) {
            const submitBtn = e.target;
            if (!orderForm.checkValidity()) {
                orderForm.classList.add('was-validated');
                SIGVE.showNotification('Por favor completa los campos obligatorios de la orden.', 'warning');
                return;
            }

            SIGVE.showButtonLoading(submitBtn);
            const formData = new FormData(orderForm);

            try {
                const response = await fetch(CREATE_ORDER_URL, {
                    method: 'POST',
                    body: formData,
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });
                const data = await response.json();

                if (data.success) {
                    modalInstance.hide();
                    const message = `✅ Orden #${data.order.id} creada correctamente.`;
                    if (SIGVE && typeof SIGVE.queueNotification === 'function') {
                        SIGVE.queueNotification(message, 'success');
                    } else {
                        SIGVE.showNotification(message, 'success');
                    }
                    window.location.href = `/taller/orders/${data.order.id}/`;
                } else {
                    const error = data.errors
                        ? Object.values(data.errors)[0][0]
                        : (data.error || 'Error desconocido');
                    SIGVE.showNotification(error, 'error');
                }
            } catch (error) {
                SIGVE.showNotification('Error de red al crear la orden', 'error');
            } finally {
                SIGVE.hideButtonLoading(submitBtn);
            }
        }

        /**
         * Resetea el modal a su estado inicial
         */
        function resetModal() {
            currentStep = 'loading';
            selectedVehicle = null;
            formDataContext = {};
            
            // Limpiar formularios y estados
            orderForm.reset();
            vehicleForm.reset();
            orderForm.classList.remove('was-validated');
            vehicleForm.classList.remove('was-validated');
            searchInput.value = '';
            searchResultsList.innerHTML = '';
            searchResultsContainer.style.display = 'none';
            searchNotFound.style.display = 'none';
            
            // Mostrar estado de carga para la próxima vez
            contentEl.style.display = 'none';
            loadingEl.style.display = 'block';
        }
        
        // Inicializar cuando el DOM esté listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
        } else {
            init();
        }

        // API Pública
        return {
            open,
            goBack
        };

    })(); // Fin OrderModal

})();

function getVehicleStatusBadgeClass(statusName) {
    if (!statusName) return 'bg-secondary';
    const normalized = statusName.toLowerCase();
    if (normalized.includes('disponible')) return 'bg-success';
    if (normalized.includes('taller') || normalized.includes('mantenimiento')) return 'bg-primary';
    if (normalized.includes('fuera') || normalized.includes('servicio') || normalized.includes('baja')) return 'bg-danger';
    if (normalized.includes('pendiente')) return 'bg-warning text-dark';
    return 'bg-secondary';
}