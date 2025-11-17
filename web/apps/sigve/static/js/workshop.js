/**
 * SIGVE - Lógica de Workshops
 *
 * Incluye el controlador del modal de Workshop y la inicialización
 * de la búsqueda en la lista de talleres.
 */

(function() {
    'use strict';

    /**
     * Sistema de gestión del modal de taller
     * Maneja tres modos: crear, ver, editar
     */
    window.WorkshopModal = (function() {
        // Referencias a elementos del DOM
        const modal = document.getElementById('workshopModal');
        const form = document.getElementById('workshopForm');
        const loading = document.getElementById('workshopModalLoading');
        const footer = document.getElementById('workshopModalFooter');
        const titleSpan = document.getElementById('workshopModalTitle');
        
        // Estado actual
        let currentMode = 'create'; // 'create', 'view', 'edit'
        let currentWorkshopId = null;
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
         * @param {number} workshopId - ID del taller (para view/edit)
         * @param {string} source - 'dashboard' o 'list' (para saber desde dónde se abre)
         */
        function open(mode = 'create', workshopId = null, source = 'list') {
            currentMode = mode;
            currentWorkshopId = workshopId;
            
            // Guardar la fuente en el formulario para usarla al enviar
            const sourceInput = document.getElementById('workshopSource');
            if (sourceInput) {
                sourceInput.value = source;
            }
            
            if (mode === 'create') {
                setupCreateMode();
            } else if (mode === 'view' || mode === 'edit') {
                showLoading();
                modalInstance.show();
                loadWorkshopData(workshopId, mode);
            }
        }
        
        /**
         * Configura el modal para crear un taller
         */
        function setupCreateMode() {
            titleSpan.textContent = 'Crear Taller';
            form.action = '/sigve/workshops/create/'; // Asegúrate que esta URL sea correcta o usa la variable de Django
            form.reset();
            document.getElementById('workshopId').value = '';
            setFieldsEnabled(true);
            renderButtons('create');
            hideLoading();
            showForm();
            modalInstance.show();
            
            // Inicializar geocodificación
            setupGeocoding();
        }
        
        /**
         * Carga los datos del taller
         */
        function loadWorkshopData(workshopId, mode) {
            fetch(`/sigve/api/workshops/${workshopId}/`)
                .then(response => {
                    if (!response.ok) {
                         throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        populateForm(data.workshop);
                        hideLoading();
                        showForm();
                        
                        // Aplicar el modo después de mostrar el formulario
                        if (mode === 'view') {
                            setupViewMode();
                        } else if (mode === 'edit') {
                            setupEditMode();
                        }
                    } else {
                        throw new Error(data.error || 'Error al cargar el taller');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    // Refactorizado para usar la utilidad global de sigve.js
                    window.SIGVE.showNotification('Error al cargar los datos del taller', 'error');
                    modalInstance.hide();
                });
        }
        
        /**
         * Configura el modal para ver un taller (solo lectura)
         */
        function setupViewMode() {
            titleSpan.textContent = 'Ver Taller';
            renderButtons('view');
            // Usar setTimeout para asegurar que el DOM esté listo
            setTimeout(() => setFieldsEnabled(false), 0);
        }
        
        /**
         * Configura el modal para editar un taller
         */
        function setupEditMode() {
            titleSpan.textContent = 'Editar Taller';
            form.action = `/sigve/workshops/${currentWorkshopId}/edit/`;
            renderButtons('edit');
            // Usar setTimeout para asegurar que el DOM esté listo
            setTimeout(() => {
                setFieldsEnabled(true);
                setupGeocoding();
            }, 0);
        }
        
        /**
         * Cambia del modo vista al modo edición
         */
        function switchToEditMode() {
            currentMode = 'edit';
            setupEditMode();
        }
        
        /**
         * Cancela la edición y vuelve al modo vista
         */
        function cancelEdit() {
            if (modalInstance) {
                modalInstance.hide();
            }
        }
        
        /**
         * Llena el formulario con los datos del taller
         */
        function populateForm(workshop) {
            document.getElementById('workshopId').value = workshop.id || '';
            document.getElementById('id_name').value = workshop.name || '';
            
            // Buscar campo de dirección por diferentes IDs posibles
            const addressField = document.getElementById('workshop-address') || document.getElementById('id_address');
            if (addressField) {
                addressField.value = workshop.address || '';
            }
            
            document.getElementById('id_phone').value = workshop.phone || '';
            document.getElementById('id_email').value = workshop.email || '';
            
            // Poblar coordenadas si existen
            const latInput = document.getElementById('workshop-latitude');
            const lonInput = document.getElementById('workshop-longitude');
            if (latInput && workshop.latitude) {
                latInput.value = workshop.latitude;
            }
            if (lonInput && workshop.longitude) {
                lonInput.value = workshop.longitude;
            }
        }
        
        /**
         * Habilita o deshabilita los campos del formulario
         */
        function setFieldsEnabled(enabled) {
            const fields = form.querySelectorAll('input, textarea, select');
            fields.forEach(field => {
                if (field.type !== 'hidden') {
                    if (enabled) {
                        field.removeAttribute('readonly');
                        field.removeAttribute('disabled');
                    } else {
                        field.setAttribute('readonly', 'readonly');
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
                    <button type="button" class="btn btn-danger" onclick="WorkshopModal.confirmDelete()">
                        <i class="bi bi-trash"></i> Eliminar
                    </button>
                    <button type="button" class="btn btn-primary" onclick="WorkshopModal.switchToEditMode()">
                        <i class="bi bi-pencil"></i> Editar
                    </button>
                `;
            } else if (mode === 'edit') {
                footer.innerHTML = `
                    <button type="button" class="btn btn-secondary" onclick="WorkshopModal.cancelEdit()">
                        <i class="bi bi-x-lg"></i> Cancelar
                    </button>
                    <button type="submit" class="btn btn-success" id="workshopSubmitBtn">
                        <i class="bi bi-check-lg"></i> Guardar Cambios
                    </button>
                `;
            } else if (mode === 'create') {
                footer.innerHTML = `
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="bi bi-x-lg"></i> Cancelar
                    </button>
                    <button type="submit" class="btn btn-primary" id="workshopSubmitBtn">
                        <i class="bi bi-check-lg"></i> Guardar Taller
                    </button>
                `;
            }
        }
        
        /**
         * Maneja el envío del formulario
         */
        function handleSubmit(e) {
            e.preventDefault();
                
            const submitBtn = document.getElementById('workshopSubmitBtn');
            if (!submitBtn) return;
            
            // Refactorizado para usar la utilidad global
            window.SIGVE.showButtonLoading(submitBtn);
                
            // Enviar formulario
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
                        window.SIGVE.hideButtonLoading(submitBtn);
                        modalInstance.hide();
                        
                        setTimeout(() => {
                            window.location.reload();
                        }, 150);
                        return;
                    } else if (data.errors) {
                        // Errores de validación
                        // Mostramos el primer error
                        const firstError = Object.values(data.errors)[0][0];
                        window.SIGVE.showNotification(firstError, 'error');
                        window.SIGVE.hideButtonLoading(submitBtn);
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                window.SIGVE.showNotification('Error al guardar el taller', 'error');
                window.SIGVE.hideButtonLoading(submitBtn);
            });
        }
        
        /**
         * Confirma la eliminación del taller
         * REFACTORIZADO para usar el DeleteModal genérico
         */
        function confirmDelete() {
            if (!currentWorkshopId) return;
            
            modalInstance.hide();

            // Abrir el modal de confirmación genérico
            window.ConfirmationModal.open({
                formAction: `/sigve/workshops/${currentWorkshopId}/delete/`,
                warningText: `¿Estás seguro de eliminar el taller ${document.getElementById('id_name').value}?`,
                title: 'Confirmar Eliminación',
                btnClass: 'btn-danger',
                btnText: 'Sí, Eliminar'
            });
        }
        
        /**
         * Muestra el spinner de carga
         */
        function showLoading() {
            loading.style.display = 'block';
            form.style.display = 'none';
        }
        
        /**
         * Oculta el spinner y muestra el formulario
         */
        function hideLoading() {
            loading.style.display = 'none';
        }
        
        /**
         * Muestra el formulario
         */
        function showForm() {
            form.style.display = 'block';
        }
        
        /**
         * Configura la geocodificación para el campo de dirección
         */
        function setupGeocoding() {
            if (window.Geocoding) {
                setTimeout(() => {
                    window.Geocoding.setupAddressGeocoding(
                        'workshop-address',
                        'workshop-latitude',
                        'workshop-longitude'
                    );
                }, 100);
            }
        }
        
        /**
         * Resetea el modal a su estado inicial
         */
        function resetModal() {
            currentMode = 'create';
            currentWorkshopId = null;
            form.reset();
            form.classList.remove('was-validated'); // Limpiar validación
            setFieldsEnabled(true);
            footer.innerHTML = '';
            hideLoading();
            showForm();
        }
        
        // Inicializar cuando el DOM esté listo
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
     * Inicialización de la página de lista de Workshops
     */
    document.addEventListener('DOMContentLoaded', function() {
        // Conectar la búsqueda de la tabla
        // Usamos la utilidad global de sigve.js
        if (window.SIGVE && window.SIGVE.setupTableSearch) {
            window.SIGVE.setupTableSearch('tableSearchInput', 'workshopsTable');
        }
    });

})();