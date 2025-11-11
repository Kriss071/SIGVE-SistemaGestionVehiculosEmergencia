/**
 * SIGVE - Lógica del Listado de Vehículos
 * 
 * Maneja el filtrado automático de vehículos con loader y el modal de creación
 */

(function() {
    'use strict';

    // Verificar que SIGVE esté disponible
    if (!window.SIGVE) {
        console.error("sigve.js no está cargado. El modal no funcionará.");
        window.SIGVE = { 
            showNotification: (msg, type) => console.log(type, msg),
            showButtonLoading: btn => btn.disabled = true,
            hideButtonLoading: btn => btn.disabled = false
        };
    }

    // URLs de la API
    const CONTEXT_API_URL = '/taller/api/vehicles/context/';
    const CREATE_API_URL = '/taller/api/vehicles/create/';

    // Elementos del DOM
    const modalEl = document.getElementById('vehicleModal');
    const modalContent = document.getElementById('vehicleModalContent');
    const modalLoading = document.getElementById('vehicleModalLoading');
    const modalFooter = document.getElementById('vehicleModalFooter');
    const createVehicleForm = document.getElementById('createVehicleForm');
    const saveVehicleBtn = document.getElementById('saveVehicleBtn');
    const licensePlateInput = document.getElementById('vehicleLicensePlate');
    const licensePlateError = document.getElementById('licensePlateError');

    // Variables globales
    let catalogData = null;
    let fireStations = [];
    let vehicleModal = null;

    /**
     * Inicializa el filtrado automático de vehículos
     */
    function initFilters() {
        const filterForm = document.getElementById('filterForm');
        const filterLoader = document.getElementById('filterLoader');
        
        if (!filterForm) return;
        
        // Función para mostrar el loader
        function showLoader() {
            if (filterLoader) {
                filterLoader.style.display = 'flex';
            }
        }
        
        // Filtrado inmediato para select (Cuartel)
        const fireStationFilter = document.getElementById('fireStationFilter');
        
        if (fireStationFilter) {
            fireStationFilter.addEventListener('change', function() {
                showLoader();
                filterForm.submit();
            });
        }
        
        // Filtrado con debounce para el input de patente
        const licensePlateFilter = document.getElementById('licensePlateFilter');
        let debounceTimer = null;
        
        if (licensePlateFilter) {
            licensePlateFilter.addEventListener('input', function() {
                clearTimeout(debounceTimer);
                const inputValue = this.value.trim();
                
                // Si el campo está vacío, no hacer nada
                if (inputValue.length === 0) {
                    // Verificar si hay otros filtros activos
                    const hasFireStationFilter = fireStationFilter && fireStationFilter.value;
                    
                    if (!hasFireStationFilter) {
                        // No hay filtros, ocultar loader si está visible
                        if (filterLoader) {
                            filterLoader.style.display = 'none';
                        }
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

    /**
     * Modal de Vehículos
     */
    window.VehicleModal = (function() {

        /**
         * Inicializa el modal
         */
        function init() {
            if (modalEl) {
                vehicleModal = new bootstrap.Modal(modalEl);
                
                // Limpiar formulario al cerrar el modal
                modalEl.addEventListener('hidden.bs.modal', function() {
                    resetForm();
                });
            }
        }

        /**
         * Abre el modal y carga los datos necesarios
         */
        async function open() {
            if (!vehicleModal) {
                init();
            }

            // Mostrar loader
            modalContent.style.display = 'none';
            modalLoading.style.display = 'block';
            modalFooter.style.display = 'none';

            // Abrir modal
            vehicleModal.show();

            try {
                // Cargar datos del contexto
                await loadContext();
                
                // Ocultar loader y mostrar contenido
                modalLoading.style.display = 'none';
                modalContent.style.display = 'block';
                modalFooter.style.display = 'block';
                
                // Populate selects
                populateSelects();
                
                // Focus en el primer campo
                if (licensePlateInput) {
                    licensePlateInput.focus();
                }
            } catch (error) {
                console.error('Error cargando contexto del modal:', error);
                SIGVE.showNotification('Error al cargar el formulario', 'error');
                vehicleModal.hide();
            }
        }

        /**
         * Carga los datos de contexto necesarios para el formulario
         */
        async function loadContext() {
            try {
                const response = await fetch(CONTEXT_API_URL);
                const data = await response.json();

                if (data.success) {
                    catalogData = data.vehicle_catalog_data;
                    fireStations = data.fire_stations || [];
                } else {
                    throw new Error('Error al cargar datos del contexto');
                }
            } catch (error) {
                console.error('Error cargando contexto:', error);
                throw error;
            }
        }

        /**
         * Popula los selects del formulario
         */
        function populateSelects() {
            // Tipo de vehículo
            const vehicleTypeSelect = document.getElementById('selectVehicleType');
            if (vehicleTypeSelect && catalogData && catalogData.vehicle_types) {
                vehicleTypeSelect.innerHTML = '<option value="">Seleccionar...</option>';
                catalogData.vehicle_types.forEach(type => {
                    const option = document.createElement('option');
                    option.value = type.id;
                    option.textContent = type.name;
                    vehicleTypeSelect.appendChild(option);
                });
            }

            // Cuartel
            const fireStationSelect = document.getElementById('selectFireStation');
            if (fireStationSelect && fireStations) {
                fireStationSelect.innerHTML = '<option value="">Seleccionar...</option>';
                fireStations.forEach(station => {
                    const option = document.createElement('option');
                    option.value = station.id;
                    option.textContent = station.name;
                    fireStationSelect.appendChild(option);
                });
            }

            // Tipo de combustible
            const fuelTypeSelect = document.getElementById('selectFuelType');
            if (fuelTypeSelect && catalogData && catalogData.fuel_types) {
                fuelTypeSelect.innerHTML = '<option value="">Seleccionar...</option>';
                catalogData.fuel_types.forEach(type => {
                    const option = document.createElement('option');
                    option.value = type.id;
                    option.textContent = type.name;
                    fuelTypeSelect.appendChild(option);
                });
            }

            // Tipo de transmisión
            const transmissionTypeSelect = document.getElementById('selectTransmissionType');
            if (transmissionTypeSelect && catalogData && catalogData.transmission_types) {
                transmissionTypeSelect.innerHTML = '<option value="">Seleccionar...</option>';
                catalogData.transmission_types.forEach(type => {
                    const option = document.createElement('option');
                    option.value = type.id;
                    option.textContent = type.name;
                    transmissionTypeSelect.appendChild(option);
                });
            }
        }

        /**
         * Guarda el vehículo
         */
        async function save() {
            if (!createVehicleForm) return;

            // Validar formulario
            if (!createVehicleForm.checkValidity()) {
                createVehicleForm.classList.add('was-validated');
                return;
            }

            // Deshabilitar botón
            if (saveVehicleBtn) {
                saveVehicleBtn.disabled = true;
                saveVehicleBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Guardando...';
            }

            // Obtener datos del formulario
            const formData = new FormData(createVehicleForm);
            const data = Object.fromEntries(formData.entries());

            // Convertir campos numéricos y eliminar campos vacíos
            const processedData = {};
            Object.keys(data).forEach(key => {
                const value = data[key];
                // Solo incluir campos con valores
                if (value !== '' && value !== null && value !== undefined) {
                    // Convertir campos numéricos
                    if (['year', 'vehicle_type_id', 'fire_station_id', 'fuel_type_id', 'transmission_type_id'].includes(key)) {
                        processedData[key] = parseInt(value);
                    } else {
                        processedData[key] = value;
                    }
                }
            });
            
            data = processedData;

            try {
                // Crear FormData para enviar
                const submitFormData = new FormData();
                Object.keys(data).forEach(key => {
                    if (data[key] !== undefined && data[key] !== null) {
                        submitFormData.append(key, data[key]);
                    }
                });

                // Agregar CSRF token
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                submitFormData.append('csrfmiddlewaretoken', csrfToken);

                const response = await fetch(CREATE_API_URL, {
                    method: 'POST',
                    body: submitFormData,
                    headers: {
                        'X-CSRFToken': csrfToken
                    }
                });

                const result = await response.json();

                if (result.success) {
                    SIGVE.showNotification('Vehículo creado correctamente', 'success');
                    vehicleModal.hide();
                    // Recargar la página para mostrar el nuevo vehículo
                    window.location.reload();
                } else {
                    // Mostrar errores
                    if (result.errors) {
                        // Errores de validación del formulario
                        // Limpiar errores previos
                        createVehicleForm.querySelectorAll('.is-invalid').forEach(el => {
                            el.classList.remove('is-invalid');
                        });
                        
                        // Mostrar errores de cada campo
                        Object.keys(result.errors).forEach(field => {
                            const fieldInput = createVehicleForm.querySelector(`[name="${field}"]`);
                            if (fieldInput) {
                                fieldInput.classList.add('is-invalid');
                                const errorMsg = Array.isArray(result.errors[field]) 
                                    ? result.errors[field][0] 
                                    : result.errors[field];
                                
                                // Mostrar error específico para patente
                                if (field === 'license_plate' && licensePlateError) {
                                    licensePlateError.textContent = errorMsg;
                                    licensePlateError.style.display = 'block';
                                }
                            }
                        });
                        
                        // Mostrar notificación con el primer error
                        const firstError = Object.values(result.errors)[0];
                        const errorMessage = Array.isArray(firstError) ? firstError[0] : firstError;
                        SIGVE.showNotification(errorMessage, 'error');
                    } else if (result.error) {
                        SIGVE.showNotification(result.error, 'error');
                    } else {
                        SIGVE.showNotification('Error al crear el vehículo', 'error');
                    }
                }
            } catch (error) {
                console.error('Error guardando vehículo:', error);
                SIGVE.showNotification('Error al crear el vehículo', 'error');
            } finally {
                // Rehabilitar botón
                if (saveVehicleBtn) {
                    saveVehicleBtn.disabled = false;
                    saveVehicleBtn.innerHTML = '<i class="bi bi-save"></i> Guardar Vehículo';
                }
            }
        }

        /**
         * Resetea el formulario
         */
        function resetForm() {
            if (createVehicleForm) {
                createVehicleForm.reset();
                createVehicleForm.classList.remove('was-validated');
                
                // Limpiar todos los errores
                createVehicleForm.querySelectorAll('.is-invalid').forEach(el => {
                    el.classList.remove('is-invalid');
                });
                
                if (licensePlateError) {
                    licensePlateError.style.display = 'none';
                }
            }
        }

        return {
            open: open,
            save: save,
            init: init
        };
    })();

    // Inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            initFilters();
            VehicleModal.init();
        });
    } else {
        initFilters();
        VehicleModal.init();
    }

})();

