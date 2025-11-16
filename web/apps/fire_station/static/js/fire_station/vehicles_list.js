/**
 * Fire Station - Vehicles List JavaScript
 * 
 * Incluye el controlador del modal de vehículos y la inicialización
 * de la búsqueda en la lista de vehículos.
 */

(function() {
    'use strict';

    // Helpers locales (evitar dependencia de otros módulos/app)
    const FS = (function() {
        function showButtonLoading(button, loadingText) {
            if (!button) return;
            button.disabled = true;
            if (!button.dataset.originalHtml) {
                button.dataset.originalHtml = button.innerHTML;
            }
            const text = loadingText || 'Cargando...';
            button.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>${text}`;
        }

        function hideButtonLoading(button) {
            if (!button) return;
            button.disabled = false;
            if (button.dataset.originalHtml) {
                button.innerHTML = button.dataset.originalHtml;
                delete button.dataset.originalHtml;
            }
        }

        function showNotification(message, type) {
            // Usar sistema global si existe (messages.js), si no, fallback a alert
            if (window.SIGVE && typeof window.SIGVE.showNotification === 'function') {
                window.SIGVE.showNotification(message, type || 'info');
            } else {
                alert(message);
            }
        }

        return { showButtonLoading, hideButtonLoading, showNotification };
    })();

    /**
     * Sistema de gestión del modal de vehículo
     * Maneja tres modos: crear, ver, editar
     */
    window.VehicleModal = (function() {
        // Referencias a elementos del DOM
        const modal = document.getElementById('vehicleModal');
        const form = document.getElementById('vehicleForm');
        const loading = document.getElementById('vehicleModalLoading');
        const footer = document.getElementById('vehicleModalFooter');
        const titleSpan = document.getElementById('vehicleModalTitle');
        
        // Estado actual
        let currentMode = 'create'; // 'create', 'view', 'edit'
        let currentVehicleId = null;
        let modalInstance = null;
        
        /**
         * Inicializa el modal
         */
        function init() {
            if (!modal || !form) return;
            
            modalInstance = new bootstrap.Modal(modal);
            
            // Evento al cerrar el modal
            modal.addEventListener('hidden.bs.modal', resetModal);
            
            // Evento al enviar el formulario
            form.addEventListener('submit', handleSubmit);
        }
        
        /**
         * Abre el modal en el modo especificado
         * @param {string} mode - 'create', 'view', 'edit'
         * @param {number} vehicleId - ID del vehículo (para view/edit)
         */
        function open(mode = 'create', vehicleId = null) {
            currentMode = mode;
            currentVehicleId = vehicleId;
            
            if (mode === 'create') {
                setupCreateMode();
            } else if (mode === 'view' || mode === 'edit') {
                showLoading();
                modalInstance.show();
                loadVehicleData(vehicleId, mode);
            }
        }
        
        /**
         * Configura el modal para crear un vehículo
         */
        function setupCreateMode() {
            titleSpan.textContent = 'Crear Vehículo';
            form.action = '/fire-station/vehicles/create/';
            form.reset();
            document.getElementById('vehicleId').value = '';
            setFieldsEnabled(true);
            setFieldsNonEditableVisible(true);
            renderButtons('create');
            hideLoading();
            showForm();
            modalInstance.show();
        }
        
        /**
         * Carga los datos del vehículo
         */
        function loadVehicleData(vehicleId, mode) {
            fetch(`/fire-station/api/vehicles/${vehicleId}/`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        populateForm(data.vehicle);
                        hideLoading();
                        showForm();
                        
                        if (mode === 'view') {
                            setupViewMode();
                        } else if (mode === 'edit') {
                            setupEditMode();
                        }
                    } else {
                        throw new Error(data.error || 'Error al cargar el vehículo');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    FS.showNotification('Error al cargar los datos del vehículo', 'error');
                    modalInstance.hide();
                });
        }
        
        /**
         * Configura el modal para ver un vehículo (solo lectura)
         */
        function setupViewMode() {
            titleSpan.textContent = 'Ver Vehículo';
            renderButtons('view');
            setTimeout(() => setFieldsEnabled(false), 0);
        }
        
        /**
         * Configura el modal para editar un vehículo
         */
        function setupEditMode() {
            titleSpan.textContent = 'Editar Vehículo';
            form.action = `/fire-station/vehicles/${currentVehicleId}/edit/`;
            renderButtons('edit');
            setFieldsNonEditableVisible(false);
            setTimeout(() => setFieldsEnabled(true), 0);
        }
        
        /**
         * Cambia del modo vista al modo edición
         */
        function switchToEditMode() {
            currentMode = 'edit';
            setupEditMode();
        }
        
        /**
         * Cancela la edición y cierra el modal
         */
        function cancelEdit() {
            if (modalInstance) {
                modalInstance.hide();
            }
        }
        
        /**
         * Llena el formulario con los datos del vehículo
         */
        function populateForm(vehicle) {
            document.getElementById('vehicleId').value = vehicle.id || '';
            document.getElementById('id_license_plate').value = vehicle.license_plate || '';
            document.getElementById('id_brand').value = vehicle.brand || '';
            document.getElementById('id_model').value = vehicle.model || '';
            document.getElementById('id_year').value = vehicle.year || '';
            document.getElementById('id_vehicle_type_id').value = vehicle.vehicle_type_id || '';
            document.getElementById('id_vehicle_status_id').value = vehicle.vehicle_status_id || '';
            
            // Campos opcionales
            document.getElementById('id_engine_number').value = vehicle.engine_number || '';
            document.getElementById('id_vin').value = vehicle.vin || '';
            document.getElementById('id_mileage').value = vehicle.mileage || '';
            document.getElementById('id_fuel_type_id').value = vehicle.fuel_type_id || '';
            document.getElementById('id_transmission_type_id').value = vehicle.transmission_type_id || '';
            document.getElementById('id_oil_type_id').value = vehicle.oil_type_id || '';
            document.getElementById('id_coolant_type_id').value = vehicle.coolant_type_id || '';
            document.getElementById('id_oil_capacity_liters').value = vehicle.oil_capacity_liters || '';
            document.getElementById('id_registration_date').value = vehicle.registration_date || '';
            document.getElementById('id_next_revision_date').value = vehicle.next_revision_date || '';
        }
        
        /**
         * Habilita o deshabilita los campos del formulario
         */
        function setFieldsEnabled(enabled) {
            const fields = form.querySelectorAll('input, textarea, select');
            fields.forEach(field => {
                if (field.type !== 'hidden') {
                    // Campos no editables siempre readonly en modo edición
                    if (currentMode === 'edit' && 
                        (field.id === 'id_license_plate' || field.id === 'id_engine_number' || field.id === 'id_vin')) {
                        field.setAttribute('readonly', 'readonly');
                        field.classList.add('bg-light');
                    } else {
                        if (enabled) {
                            field.removeAttribute('readonly');
                            field.removeAttribute('disabled');
                            field.classList.remove('bg-light');
                        } else {
                            field.setAttribute('readonly', 'readonly');
                            if (field.tagName === 'SELECT') {
                                field.setAttribute('disabled', 'disabled');
                            }
                            field.classList.add('bg-light');
                        }
                    }
                }
            });
        }
        
        /**
         * Oculta o muestra los campos no editables
         */
        function setFieldsNonEditableVisible(visible) {
            const nonEditableFields = ['id_license_plate', 'id_engine_number', 'id_vin'];
            nonEditableFields.forEach(fieldId => {
                const field = document.getElementById(fieldId);
                if (field) {
                    const container = field.closest('.mb-3');
                    if (!visible) {
                        // En modo edición, se muestran como readonly
                        field.setAttribute('readonly', 'readonly');
                        field.classList.add('bg-light');
                    }
                }
            });
        }
        
        /**
         * Renderiza los botones del footer según el modo
         */
        function renderButtons(mode) {
            footer.innerHTML = '';
            
            if (mode === 'view') {
                footer.innerHTML = `
                    <button type="button" class="btn btn-outline-danger" onclick="VehicleModal.confirmDelete()">
                        <i class="bi bi-trash"></i> Eliminar
                    </button>
                    <button type="button" class="btn btn-danger" onclick="VehicleModal.switchToEditMode()">
                        <i class="bi bi-pencil"></i> Editar
                    </button>
                `;
            } else if (mode === 'edit') {
                footer.innerHTML = `
                    <button type="button" class="btn btn-secondary" onclick="VehicleModal.cancelEdit()">
                        <i class="bi bi-x-lg"></i> Cancelar
                    </button>
                    <button type="submit" class="btn btn-success" id="vehicleSubmitBtn">
                        <i class="bi bi-check-lg"></i> Guardar Cambios
                    </button>
                `;
            } else if (mode === 'create') {
                footer.innerHTML = `
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="bi bi-x-lg"></i> Cancelar
                    </button>
                    <button type="submit" class="btn btn-danger" id="vehicleSubmitBtn">
                        <i class="bi bi-check-lg"></i> Guardar Vehículo
                    </button>
                `;
            }
        }
        
        /**
         * Maneja el envío del formulario
         */
        function handleSubmit(e) {
            e.preventDefault();
            
            const submitBtn = document.getElementById('vehicleSubmitBtn');
            if (!submitBtn) return;
            
            // Normalizar patente (UX)
            const licensePlateInput = document.getElementById('id_license_plate');
            if (licensePlateInput && typeof licensePlateInput.value === 'string') {
                licensePlateInput.value = (licensePlateInput.value || '').trim().toUpperCase();
            }

            FS.showButtonLoading(submitBtn, 'Guardando...');
            
            const formData = new FormData(form);
            
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                    return null;
                }
                return response.json();
            })
            .then(data => {
                if (data) {
                    if (data.success) {
                        FS.hideButtonLoading(submitBtn);
                        modalInstance.hide();
                        setTimeout(() => window.location.reload(), 150);
                        return;
                    } else if (data.errors) {
                        const firstError = Object.values(data.errors)[0][0];
                        FS.showNotification(firstError, 'error');
                        FS.hideButtonLoading(submitBtn);
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                FS.showNotification('Error al guardar el vehículo', 'error');
                FS.hideButtonLoading(submitBtn);
            });
        }
        
        /**
         * Confirma la eliminación del vehículo
         */
        function confirmDelete() {
            if (!currentVehicleId) return;

            modalInstance.hide();
            
            window.ConfirmationModal.open({
                formAction: `/fire-station/vehicles/${currentVehicleId}/delete/`,
                warningText: `¿Estás seguro de eliminar el vehículo ${document.getElementById('id_license_plate').value}?`,
                title: 'Confirmar Eliminación',
                btnClass: 'btn-danger',
                btnText: 'Sí, Eliminar'
            });
        }
        
        /**
         * Funciones de utilidad para mostrar/ocultar carga
         */
        function showLoading() {
            loading.style.display = 'block';
            form.style.display = 'none';
        }
        
        function hideLoading() {
            loading.style.display = 'none';
        }
        
        function showForm() {
            form.style.display = 'block';
        }
        
        /**
         * Resetea el modal a su estado inicial
         */
        function resetModal() {
            currentMode = 'create';
            currentVehicleId = null;
            form.reset();
            form.classList.remove('was-validated');
            setFieldsEnabled(true);
            footer.innerHTML = '';
            hideLoading();
            showForm();
        }
        
        // Inicializar
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
        } else {
            init();
        }
        
        // API pública
        return {
            open,
            switchToEditMode,
            cancelEdit,
            confirmDelete
        };
    })();

    /**
     * Inicialización de la página de lista de Vehículos
     */
    document.addEventListener('DOMContentLoaded', function() {
        // Conectar la búsqueda de la tabla
        if (window.SIGVE && window.SIGVE.setupTableSearch) {
            window.SIGVE.setupTableSearch('tableSearchInput', 'vehiclesTable');

            // Agregar control de "sin resultados" junto a la búsqueda global
            const searchInput = document.getElementById('tableSearchInput');
            if (searchInput) {
                const triggerUpdate = function() {
                    // Dejar que SIGVE aplique su filtrado y luego evaluar
                    window.requestAnimationFrame(() => {
                        updateNoResultsRowByTable('vehiclesTable');
                    });
                };
                searchInput.addEventListener('keyup', triggerUpdate);
                // Inicial
                triggerUpdate();
            }
        } else {
            setupLocalTableSearch('tableSearchInput', 'vehiclesTable');
        }
        
        // Inicializar el filtrado automático
        initAutoFilter();
    });

    /**
     * Actualiza una fila de "sin resultados" según visibilidad de filas
     * @param {HTMLTableSectionElement} tbody
     * @param {number} colSpan
     */
    function updateNoResultsRow(tbody, colSpan) {
        // Excluir fila previa de no resultados
        const dataRows = Array.from(tbody.querySelectorAll('tr:not(.no-results-row)'));
        const visibleRows = dataRows.filter(r => window.getComputedStyle(r).display !== 'none');
        let noResultsRow = tbody.querySelector('tr.no-results-row');

        if (visibleRows.length === 0) {
            if (!noResultsRow) {
                noResultsRow = document.createElement('tr');
                noResultsRow.className = 'no-results-row';
                const td = document.createElement('td');
                td.colSpan = colSpan;
                td.className = 'text-center text-muted';
                td.textContent = 'No hay resultados en la tabla';
                noResultsRow.appendChild(td);
                tbody.appendChild(noResultsRow);
            }
        } else if (noResultsRow) {
            noResultsRow.remove();
        }
    }

    /**
     * Actualiza "sin resultados" buscando por id de tabla
     * @param {string} tableId
     */
    function updateNoResultsRowByTable(tableId) {
        const table = document.getElementById(tableId);
        if (!table) return;
        const tbody = (table.tBodies && table.tBodies[0]) ? table.tBodies[0] : table.querySelector('tbody');
        if (!tbody) return;
        const colSpan = (table.tHead && table.tHead.rows[0] ? table.tHead.rows[0].cells.length : (tbody.rows[0] ? tbody.rows[0].cells.length : 1)) || 1;
        updateNoResultsRow(tbody, colSpan);
    }

    /**
     * Búsqueda local de filas dentro de una tabla (fallback si no existe SIGVE.setupTableSearch)
     * @param {string} inputId
     * @param {string} tableId
     */
    function setupLocalTableSearch(inputId, tableId) {
        const input = document.getElementById(inputId);
        const table = document.getElementById(tableId);
        if (!input || !table) return;

        const tbody = (table.tBodies && table.tBodies[0]) ? table.tBodies[0] : table.querySelector('tbody');
        if (!tbody) return;

        const colSpan = (table.tHead && table.tHead.rows[0] ? table.tHead.rows[0].cells.length : (tbody.rows[0] ? tbody.rows[0].cells.length : 1)) || 1;

        input.addEventListener('input', function() {
            const query = (this.value || '').toLowerCase().trim();
            const rows = Array.from(tbody.querySelectorAll('tr:not(.no-results-row)'));

            if (!query) {
                rows.forEach(row => { row.style.display = ''; });
                updateNoResultsRow(tbody, colSpan);
                return;
            }

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });

            updateNoResultsRow(tbody, colSpan);
        });

        // Inicial
        updateNoResultsRow(tbody, colSpan);
    }

    /**
     * Inicializa el filtrado automático de vehículos
     */
    function initAutoFilter() {
        console.log("Inicializando filtrado automático de vehículos");
        const filterForm = document.getElementById('filterForm');
        const filterLoader = document.getElementById('filterLoader');
        
        if (!filterForm) return;
        
        // Función para mostrar el loader
        function showLoader() {
            if (filterLoader) {
                filterLoader.style.display = 'flex';
            }
        }
        
        // Filtrado inmediato para selects (Estado y Tipo)
        const statusFilter = document.getElementById('statusFilter');
        const typeFilter = document.getElementById('typeFilter');
        
        if (statusFilter) {
            statusFilter.addEventListener('change', function() {
                showLoader();
                filterForm.submit();
            });
        }
        
        if (typeFilter) {
            typeFilter.addEventListener('change', function() {
                showLoader();
                filterForm.submit();
            });
        }
        
        // Filtrado con debounce para el input de patente
        const licensePlateInput = document.getElementById('licensePlateFilter');
        let debounceTimer = null;
        
        if (licensePlateInput) {
            licensePlateInput.addEventListener('input', function() {
                clearTimeout(debounceTimer);
                const inputValue = this.value.trim();
                
                // Si el campo está vacío, verificar si hay otros filtros activos
                if (inputValue.length === 0) {
                    const hasStatusFilter = statusFilter && statusFilter.value;
                    const hasTypeFilter = typeFilter && typeFilter.value;
                    
                    if (!hasStatusFilter && !hasTypeFilter) {
                        // No hay filtros, enviar formulario para limpiar todos los filtros
                        showLoader();
                        filterForm.submit();
                        return;
                    } else {
                        // Hay otros filtros activos, enviar formulario para mantenerlos pero quitar el de patente
                        showLoader();
                        filterForm.submit();
                        return;
                    }
                }
                
                // Esperar el debounce antes de mostrar el loader y enviar el formulario
                debounceTimer = setTimeout(function() {
                    // Mostrar loader justo antes de enviar el formulario
                    showLoader();
                    filterForm.submit();
                }, 1000); // Espera 1 segundo después de que el usuario deje de escribir
            });
        }
    }

})();

