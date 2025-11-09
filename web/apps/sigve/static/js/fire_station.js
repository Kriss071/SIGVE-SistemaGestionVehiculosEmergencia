/**
 * SIGVE - Lógica de Cuarteles (Fire Stations)
 *
 * Incluye el controlador del modal de Cuartel y la inicialización
 * de la búsqueda en la lista de cuarteles.
 */

(function() {
    'use strict';

    /**
     * Sistema de gestión del modal de cuartel
     * Maneja tres modos: crear, ver, editar
     */
    window.FireStationModal = (function() {
        // Referencias a elementos del DOM
        const modal = document.getElementById('fireStationModal');
        const form = document.getElementById('fireStationForm');
        const loading = document.getElementById('fireStationModalLoading');
        const footer = document.getElementById('fireStationModalFooter');
        const titleSpan = document.getElementById('fireStationModalTitle');
        
        // Estado actual
        let currentMode = 'create'; // 'create', 'view', 'edit'
        let currentFireStationId = null;
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
         * @param {number} stationId - ID del cuartel (para view/edit)
         * @param {string} source - 'dashboard' o 'list'
         */
        function open(mode = 'create', stationId = null, source = 'list') {
            currentMode = mode;
            currentFireStationId = stationId;
            
            const sourceInput = document.getElementById('fireStationSource');
            if (sourceInput) {
                sourceInput.value = source;
            }
            
            if (mode === 'create') {
                setupCreateMode();
            } else if (mode === 'view' || mode === 'edit') {
                showLoading();
                modalInstance.show();
                loadFireStationData(stationId, mode);
            }
        }
        
        /**
         * Configura el modal para crear un cuartel
         */
        function setupCreateMode() {
            titleSpan.textContent = 'Crear Cuartel';
            form.action = '/sigve/fire-stations/create/'; // Ajusta esta URL a tu URL de Django
            form.reset();
            document.getElementById('fireStationId').value = '';
            setFieldsEnabled(true);
            renderButtons('create');
            hideLoading();
            showForm();
            modalInstance.show();
        }
        
        /**
         * Carga los datos del cuartel
         */
        function loadFireStationData(stationId, mode) {
            // Asumimos una API endpoint; ajusta si es necesario
            fetch(`/sigve/api/fire-stations/${stationId}/`) 
                .then(response => {
                    if (!response.ok) {
                         throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        populateForm(data.fire_station); // Asumiendo que la API devuelve {success: true, station: {...}}
                        hideLoading();
                        showForm();
                        
                        if (mode === 'view') {
                            setupViewMode();
                        } else if (mode === 'edit') {
                            setupEditMode();
                        }
                    } else {
                        throw new Error(data.error || 'Error al cargar el cuartel');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    window.SIGVE.showNotification('Error al cargar los datos del cuartel', 'error');
                    modalInstance.hide();
                });
        }
        
        /**
         * Configura el modal para ver un cuartel (solo lectura)
         */
        function setupViewMode() {
            titleSpan.textContent = 'Ver Cuartel';
            renderButtons('view');
            setTimeout(() => setFieldsEnabled(false), 0);
        }
        
        /**
         * Configura el modal para editar un cuartel
         */
        function setupEditMode() {
            titleSpan.textContent = 'Editar Cuartel';
            form.action = `/sigve/fire-stations/${currentFireStationId}/edit/`; // Ajusta esta URL
            renderButtons('edit');
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
         * Llena el formulario con los datos del cuartel
         * (IDs corregidos para coincidir con el HTML)
         */
        function populateForm(station) {
            document.getElementById('fireStationId').value = station.id || '';
            document.getElementById('id_name').value = station.name || '';
            document.getElementById('id_address').value = station.address || '';
            document.getElementById('id_commune').value = station.commune_id || '';
        }
        
        /**
         * Habilita o deshabilita los campos del formulario
         * (Corregido para incluir 'select')
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
                        // 'disabled' es mejor para 'select' en modo readonly
                        if (field.tagName === 'SELECT') {
                            field.setAttribute('disabled', 'disabled');
                        }
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
                    <button type="button" class="btn btn-outline-danger" onclick="FireStationModal.confirmDelete()">
                        <i class="bi bi-trash"></i> Eliminar
                    </button>
                    <button type="button" class="btn btn-danger" onclick="FireStationModal.switchToEditMode()">
                        <i class="bi bi-pencil"></i> Editar
                    </button>
                `;
            } else if (mode === 'edit') {
                footer.innerHTML = `
                    <button type="button" class="btn btn-secondary" onclick="FireStationModal.cancelEdit()">
                        <i class="bi bi-x-lg"></i> Cancelar
                    </button>
                    <button type="submit" class="btn btn-success" id="fireStationSubmitBtn">
                        <i class="bi bi-check-lg"></i> Guardar Cambios
                    </button>
                `;
            } else if (mode === 'create') {
                footer.innerHTML = `
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="bi bi-x-lg"></i> Cancelar
                    </button>
                    <button type="submit" class="btn btn-danger" id="fireStationSubmitBtn">
                        <i class="bi bi-check-lg"></i> Guardar Cuartel
                    </button>
                `;
            }
        }
        
        /**
         * Maneja el envío del formulario
         */
        function handleSubmit(e) {
            e.preventDefault();
                
            const submitBtn = document.getElementById('fireStationSubmitBtn');
            if (!submitBtn) return;
            
            window.SIGVE.showButtonLoading(submitBtn);
                
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
                        setTimeout(() => window.location.reload(), 150);
                        return;
                    } else if (data.errors) {
                        const firstError = Object.values(data.errors)[0][0];
                        window.SIGVE.showNotification(firstError, 'error');
                        window.SIGVE.hideButtonLoading(submitBtn);
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                window.SIGVE.showNotification('Error al guardar el cuartel', 'error');
                window.SIGVE.hideButtonLoading(submitBtn);
            });
        }
        
        /**
         * Confirma la eliminación del cuartel (usando DeleteModal)
         */
        function confirmDelete() {
            if (!currentFireStationId) return;

            modalInstance.hide();
            
            window.ConfirmationModal.open({
                formAction: `/sigve/fire-stations/${currentFireStationId}/delete/`,
                warningText: `¿Estás seguro de eliminar el cuartel ${document.getElementById('id_name').value}?`,
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
            currentFireStationId = null;
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
     * Inicialización de la página de lista de Cuarteles
     */
    document.addEventListener('DOMContentLoaded', function() {
        // Conectar la búsqueda de la tabla
        if (window.SIGVE && window.SIGVE.setupTableSearch) {
            window.SIGVE.setupTableSearch('tableSearchInput', 'fireStationsTable');
        }
    });

})();