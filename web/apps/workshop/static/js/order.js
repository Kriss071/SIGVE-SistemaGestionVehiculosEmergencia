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
    let searchInput, searchResultsContainer, searchResultsList, searchNotFound, searchLoader;
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
            searchLoader = document.getElementById('vehicleSearchLoader');
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
                populateSelect('selectFuelType', data.vehicle_catalog_data.fuel_types, true);
                populateSelect('selectTransmissionType', data.vehicle_catalog_data.transmission_types, true);

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
            const query = searchInput.value.trim().toUpperCase();
            
            // Ocultar resultados anteriores si el campo está vacío
            if (query.length < 1) {
                clearTimeout(searchTimer);
                hideSearchLoader();
                searchResultsContainer.style.display = 'none';
                searchNotFound.style.display = 'none';
                return;
            }
            
            // Ocultar resultados anteriores mientras se espera el debounce
            searchResultsContainer.style.display = 'none';
            searchNotFound.style.display = 'none';
            
            clearTimeout(searchTimer);
            searchTimer = setTimeout(() => {
                // Mostrar loader solo después del debounce, justo antes de buscar
                performSearch(query);
            }, 300); // 300ms debounce
        }
        
        /**
         * Muestra el loader de búsqueda
         */
        function showSearchLoader() {
            if (searchLoader) {
                searchLoader.style.display = 'block';
            }
        }
        
        /**
         * Oculta el loader de búsqueda
         */
        function hideSearchLoader() {
            if (searchLoader) {
                searchLoader.style.display = 'none';
            }
        }

        /**
         * Ejecuta la búsqueda AJAX
         */
        async function performSearch(query) {
            if (query.length < 1) {
                hideSearchLoader();
                searchResultsContainer.style.display = 'none';
                searchNotFound.style.display = 'none';
                return;
            }

            // Mostrar loader y ocultar resultados/not found
            showSearchLoader();
            searchResultsContainer.style.display = 'none';
            searchNotFound.style.display = 'none';

            try {
                const response = await fetch(`${SEARCH_URL}?q=${encodeURIComponent(query)}`);
                const data = await response.json();

                // Ocultar loader después de recibir la respuesta
                hideSearchLoader();

                if (data.success && data.vehicles.length > 0) {
                    renderResults(data.vehicles);
                } else {
                    searchResultsContainer.style.display = 'none';
                    searchNotFound.style.display = 'block';
                }
            } catch (error) {
                hideSearchLoader();
                SIGVE.showNotification('Error al buscar vehículo', 'error');
                searchResultsContainer.style.display = 'none';
                searchNotFound.style.display = 'none';
            }
        }

        /**
         * Obtiene la clase CSS para el badge de estado del vehículo
         */
        function getVehicleStatusBadgeClass(statusName) {
            if (!statusName) return 'bg-secondary';
            const normalized = statusName.toLowerCase();
            if (normalized.includes('disponible')) return 'bg-success';
            if (normalized.includes('taller') || normalized.includes('mantenimiento')) return 'bg-primary';
            if (normalized.includes('fuera') || normalized.includes('servicio') || normalized.includes('baja')) return 'bg-danger';
            if (normalized.includes('pendiente')) return 'bg-warning text-dark';
            return 'bg-secondary';
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
         * Limpia todos los errores del formulario
         */
        function clearFormErrors(formElement) {
            if (!formElement) return;
            
            // Remover clases de error de Bootstrap
            formElement.querySelectorAll('.is-invalid').forEach(field => {
                field.classList.remove('is-invalid');
            });
            
            // Limpiar mensajes de error dinámicos
            formElement.querySelectorAll('.invalid-feedback[data-field-error]').forEach(feedback => {
                feedback.remove();
            });
        }
        
        /**
         * Muestra un error en un campo específico del formulario
         * @param {string} fieldName - Nombre del campo
         * @param {string} errorMessage - Mensaje de error a mostrar
         * @param {HTMLElement} formElement - Formulario al que pertenece el campo
         */
        function showFieldError(fieldName, errorMessage, formElement) {
            if (!formElement) return;
            
            const field = formElement.querySelector(`[name="${fieldName}"]`);
            if (!field) return;
            
            // Agregar clase de error
            field.classList.add('is-invalid');
            
            // Crear o actualizar mensaje de error
            let feedback = formElement.querySelector(`.invalid-feedback[data-field-error="${fieldName}"]`);
            if (!feedback) {
                feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                feedback.setAttribute('data-field-error', fieldName);
                
                // Insertar después del campo
                const parent = field.closest('.mb-3') || field.parentElement;
                if (parent) {
                    parent.appendChild(feedback);
                }
            }
            
            feedback.textContent = errorMessage;
        }
        
        /**
         * Valida el formulario de vehículo y muestra errores en español
         * @returns {boolean} true si el formulario es válido, false en caso contrario
         */
        function validateVehicleForm() {
            clearFormErrors(vehicleForm);
            
            let isValid = true;
            const requiredFields = vehicleForm.querySelectorAll('[required]');
            
            // Mensajes de error en español para campos requeridos
            const errorMessages = {
                'license_plate': 'Por favor, ingresa una patente.',
                'brand': 'Por favor, ingresa la marca del vehículo.',
                'model': 'Por favor, ingresa el modelo del vehículo.',
                'year': 'Por favor, ingresa el año del vehículo.',
                'fire_station_id': 'Por favor, selecciona un cuartel.',
                'vehicle_type_id': 'Por favor, selecciona un tipo de vehículo.',
                'engine_number': 'Por favor, ingresa el número de motor.',
                'vin': 'Por favor, ingresa el número de chasis (VIN).'
            };
            
            requiredFields.forEach(field => {
                const fieldName = field.name;
                const fieldValue = field.value.trim();
                
                // Para select, verificar que tenga un valor seleccionado
                if (field.tagName === 'SELECT') {
                    if (!fieldValue || fieldValue === '') {
                        isValid = false;
                        field.classList.add('is-invalid');
                        const errorMsg = errorMessages[fieldName] || 'Este campo es obligatorio.';
                        showFieldError(fieldName, errorMsg, vehicleForm);
                    }
                } else if (!fieldValue) {
                    isValid = false;
                    field.classList.add('is-invalid');
                    const errorMsg = errorMessages[fieldName] || 'Este campo es obligatorio.';
                    showFieldError(fieldName, errorMsg, vehicleForm);
                }
            });
            
            // Validar año si está presente
            const yearField = vehicleForm.querySelector('[name="year"]');
            if (yearField && yearField.value) {
                const year = parseInt(yearField.value);
                if (isNaN(year) || year < 1900 || year > 2100) {
                    isValid = false;
                    yearField.classList.add('is-invalid');
                    showFieldError('year', 'Por favor, ingresa un año válido (entre 1900 y 2100).', vehicleForm);
                }
            }
            
            // Validar formato de patente
            const licensePlateField = vehicleForm.querySelector('[name="license_plate"]');
            if (licensePlateField && licensePlateField.value) {
                const plate = licensePlateField.value.trim().toUpperCase();
                const plateRegex = /^[A-Z0-9\-]{4,20}$/;
                if (!plateRegex.test(plate)) {
                    isValid = false;
                    licensePlateField.classList.add('is-invalid');
                    showFieldError('license_plate', 'La patente debe contener 4 a 20 caracteres alfanuméricos o guiones.', vehicleForm);
                }
            }
            
            // Validar longitud de engine_number
            const engineNumberField = vehicleForm.querySelector('[name="engine_number"]');
            if (engineNumberField && engineNumberField.value) {
                const engineNumber = engineNumberField.value.trim();
                if (engineNumber.length > 100) {
                    isValid = false;
                    engineNumberField.classList.add('is-invalid');
                    showFieldError('engine_number', 'El número de motor no puede exceder 100 caracteres.', vehicleForm);
                }
            }
            
            // Validar longitud de VIN
            const vinField = vehicleForm.querySelector('[name="vin"]');
            if (vinField && vinField.value) {
                const vin = vinField.value.trim();
                if (vin.length > 100) {
                    isValid = false;
                    vinField.classList.add('is-invalid');
                    showFieldError('vin', 'El número de chasis (VIN) no puede exceder 100 caracteres.', vehicleForm);
                }
            }
            
            if (!isValid) {
                SIGVE.showNotification('Por favor, completa todos los campos obligatorios del vehículo correctamente.', 'error');
            }
            
            return isValid;
        }
        
        /**
         * Valida el formulario de orden y muestra errores en español
         * @returns {boolean} true si el formulario es válido, false en caso contrario
         */
        function validateOrderForm() {
            clearFormErrors(orderForm);
            
            let isValid = true;
            const requiredFields = orderForm.querySelectorAll('[required]');
            
            // Mensajes de error en español para campos requeridos
            const errorMessages = {
                'vehicle_id': 'Debe seleccionarse un vehículo.',
                'mileage': 'Por favor, ingresa el kilometraje de ingreso.',
                'maintenance_type_id': 'Por favor, selecciona un tipo de mantención.',
                'order_status_id': 'Por favor, selecciona un estado para la orden.',
                'entry_date': 'Por favor, selecciona una fecha de ingreso.'
            };
            
            requiredFields.forEach(field => {
                const fieldName = field.name;
                const fieldValue = field.value.trim();
                
                // Para select, verificar que tenga un valor seleccionado
                if (field.tagName === 'SELECT') {
                    if (!fieldValue || fieldValue === '') {
                        isValid = false;
                        field.classList.add('is-invalid');
                        const errorMsg = errorMessages[fieldName] || 'Este campo es obligatorio.';
                        showFieldError(fieldName, errorMsg, orderForm);
                    }
                } else if (field.type === 'hidden') {
                    // Para campos ocultos, verificar que tengan valor
                    if (!fieldValue) {
                        isValid = false;
                        const errorMsg = errorMessages[fieldName] || 'Este campo es obligatorio.';
                        SIGVE.showNotification(errorMsg, 'error');
                    }
                } else if (!fieldValue) {
                    isValid = false;
                    field.classList.add('is-invalid');
                    const errorMsg = errorMessages[fieldName] || 'Este campo es obligatorio.';
                    showFieldError(fieldName, errorMsg, orderForm);
                }
            });
            
            // Validar kilometraje si está presente
            const mileageField = orderForm.querySelector('[name="mileage"]');
            if (mileageField && mileageField.value) {
                const mileage = parseInt(mileageField.value);
                if (isNaN(mileage) || mileage < 0) {
                    isValid = false;
                    mileageField.classList.add('is-invalid');
                    showFieldError('mileage', 'El kilometraje debe ser un número mayor o igual a 0.', orderForm);
                }
            }
            
            // Validar fecha de ingreso
            const entryDateField = orderForm.querySelector('[name="entry_date"]');
            if (entryDateField && entryDateField.value) {
                const entryDate = new Date(entryDateField.value);
                const today = new Date();
                today.setHours(0, 0, 0, 0);
                if (entryDate > today) {
                    isValid = false;
                    entryDateField.classList.add('is-invalid');
                    showFieldError('entry_date', 'La fecha de ingreso no puede ser futura.', orderForm);
                }
            }
            
            if (!isValid) {
                SIGVE.showNotification('Por favor, completa todos los campos obligatorios de la orden correctamente.', 'error');
            }
            
            return isValid;
        }
        
        /**
         * Envía el formulario de NUEVO VEHÍCULO
         */
        async function handleSubmitVehicle(e) {
            const submitBtn = e.target;
            
            // Validar formulario manualmente para mostrar mensajes en español
            if (!validateVehicleForm()) {
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
                    // Limpiar errores previos
                    clearFormErrors(vehicleForm);
                    
                    // Mostrar errores del servidor
                    if (data.errors) {
                        // Errores de validación por campo
                        for (const [field, errors] of Object.entries(data.errors)) {
                            if (Array.isArray(errors) && errors.length > 0) {
                                const errorMessage = errors[0];
                                if (field === 'general' || field === '__all__') {
                                    SIGVE.showNotification(errorMessage, 'error');
                                } else {
                                    showFieldError(field, errorMessage, vehicleForm);
                                }
                            }
                        }
                    } else {
                        const error = data.error || 'Error desconocido al crear el vehículo.';
                        SIGVE.showNotification(error, 'error');
                    }
                }
            } catch (error) {
                SIGVE.showNotification('Error de red al crear vehículo. Verifica tu conexión.', 'error');
            } finally {
                SIGVE.hideButtonLoading(submitBtn);
            }
        }

        /**
         * Envía el formulario de NUEVA ORDEN
         */
        async function handleSubmitOrder(e) {
            const submitBtn = e.target;
            
            // Validar formulario manualmente para mostrar mensajes en español
            if (!validateOrderForm()) {
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
                    // Limpiar errores previos
                    clearFormErrors(orderForm);
                    
                    // Mostrar errores del servidor
                    if (data.errors) {
                        // Errores de validación por campo
                        for (const [field, errors] of Object.entries(data.errors)) {
                            if (Array.isArray(errors) && errors.length > 0) {
                                const errorMessage = errors[0];
                                if (field === 'general' || field === '__all__') {
                                    SIGVE.showNotification(errorMessage, 'error');
                                } else {
                                    showFieldError(field, errorMessage, orderForm);
                                }
                            }
                        }
                    } else {
                        const error = data.error || 'Error desconocido al crear la orden.';
                        SIGVE.showNotification(error, 'error');
                    }
                }
            } catch (error) {
                SIGVE.showNotification('Error de red al crear la orden. Verifica tu conexión.', 'error');
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
            
            // Limpiar errores de validación
            clearFormErrors(orderForm);
            clearFormErrors(vehicleForm);
            
            searchInput.value = '';
            searchResultsList.innerHTML = '';
            searchResultsContainer.style.display = 'none';
            searchNotFound.style.display = 'none';
            hideSearchLoader();
            
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