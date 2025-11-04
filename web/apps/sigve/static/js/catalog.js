/**
 * SIGVE - Lógica de Catálogos Genéricos
 *
 * Controlador del modal genérico de Catálogo.
 * Maneja tres modos: crear, ver, editar para cualquier catálogo.
 */

(function() {
    'use strict';

    /**
     * Sistema de gestión del modal de catálogo
     */
    window.CatalogModal = (function() {
        // Referencias a elementos del DOM
        const modal = document.getElementById('catalogModal');
        const form = document.getElementById('catalogForm');
        const loading = document.getElementById('catalogModalLoading');
        const footer = document.getElementById('catalogModalFooter');
        const titleSpan = document.getElementById('catalogModalTitle');
        const icon = document.getElementById('catalogModalIcon');
        
        // Estado actual
        let currentMode = 'create'; // 'create', 'view', 'edit'
        let currentItemId = null;
        let currentCatalogName = null;
        let currentSingularName = 'Item'; // Nombre singular por defecto
        let currentIcon = 'bi-list-ul';
        let currentPlaceholder = 'Ej: Nuevo Item';
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
         * @param {string} catalogName - El nombre de la tabla de catálogo (ej: 'vehicle_type')
         * @param {string} singularName - El nombre singular para mostrar (ej: 'Tipo de Vehículo')
         * @param {number} itemId - ID del item (para view/edit)
         * @param {string} source - 'dashboard' o 'list'
         * @param {string} catalogIcon - Clase del icono (ej: 'bi-truck')
         */
        function open(mode = 'create', catalogName, singularName, itemId = null, source = 'list', catalogIcon = 'bi-list-ul', placeholder = 'Ej: Nuevo Item') {
            currentMode = mode;
            currentItemId = itemId;
            currentCatalogName = catalogName;
            currentSingularName = singularName || 'Item';
            currentIcon = catalogIcon || 'bi-list-ul';
            currentPlaceholder = placeholder || 'Ej: Nuevo Item';

            icon.className = `bi ${currentIcon}`;
            
            // Guardar la fuente en el formulario
            const sourceInput = document.getElementById('catalogSource');
            if (sourceInput) {
                sourceInput.value = source;
            }
            
            if (mode === 'create') {
                setupCreateMode();
            } else if (mode === 'view' || mode === 'edit') {
                showLoading();
                modalInstance.show();
                loadCatalogData(itemId, mode);
            }
        }
        
        /**
         * Configura el modal para crear un item
         */
        function setupCreateMode() {
            titleSpan.textContent = `Crear ${currentSingularName}`;
            form.action = `/sigve/catalogs/${currentCatalogName}/create/`;
            form.reset();
            document.getElementById('catalogItemId').value = '';

            const nameInput = document.getElementById('id_name');
            if(nameInput) {
                nameInput.placeholder = currentPlaceholder;
            }

            setFieldsEnabled(true);
            renderButtons('create');
            hideLoading();
            showForm();
            modalInstance.show();
        }
        
        /**
         * Carga los datos del item
         */
        function loadCatalogData(itemId, mode) {
            fetch(`/sigve/api/catalogs/${currentCatalogName}/${itemId}/`)
                .then(response => {
                    if (!response.ok) {
                         throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        populateForm(data.item);

                        const nameInput = document.getElementById('id_name');
                        if(nameInput) {
                            nameInput.placeholder = currentPlaceholder;
                        }

                        hideLoading();
                        showForm();
                        
                        if (mode === 'view') {
                            setupViewMode();
                        } else if (mode === 'edit') {
                            setupEditMode();
                        }
                    } else {
                        throw new Error(data.error || 'Error al cargar el item');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    window.SIGVE.showNotification(`Error al cargar datos: ${error.message}`, 'error');
                    modalInstance.hide();
                });
        }
        
        /**
         * Configura el modal para ver un item (solo lectura)
         */
        function setupViewMode() {
            titleSpan.textContent = `Ver ${currentSingularName}`;
            renderButtons('view');
            setTimeout(() => setFieldsEnabled(false), 0);
        }
        
        /**
         * Configura el modal para editar un item
         */
        function setupEditMode() {
            titleSpan.textContent = `Editar ${currentSingularName}`;
            form.action = `/sigve/catalogs/${currentCatalogName}/${currentItemId}/edit/`;
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
         * Cancela la edición y cierra
         */
        function cancelEdit() {
            if (modalInstance) {
                modalInstance.hide();
            }
        }
        
        /**
         * Llena el formulario con los datos del item
         */
        function populateForm(item) {
            document.getElementById('catalogItemId').value = item.id || '';
            document.getElementById('id_name').value = item.name || '';
            document.getElementById('id_description').value = item.description || '';
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
                    <button type="button" class="btn btn-danger" onclick="CatalogModal.confirmDelete()">
                        <i class="bi bi-trash"></i> Eliminar
                    </button>
                    <button type="button" class="btn btn-primary" onclick="CatalogModal.switchToEditMode()">
                        <i class="bi bi-pencil"></i> Editar
                    </button>
                `;
            } else if (mode === 'edit') {
                footer.innerHTML = `
                    <button type="button" class="btn btn-secondary" onclick="CatalogModal.cancelEdit()">
                        <i class="bi bi-x-lg"></i> Cancelar
                    </button>
                    <button type="submit" class="btn btn-success" id="catalogSubmitBtn">
                        <i class="bi bi-check-lg"></i> Guardar Cambios
                    </button>
                `;
            } else if (mode === 'create') {
                footer.innerHTML = `
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="bi bi-x-lg"></i> Cancelar
                    </button>
                    <button type="submit" class="btn btn-primary" id="catalogSubmitBtn">
                        <i class="bi bi-check-lg"></i> Guardar Item
                    </button>
                `;
            }
        }
        
        /**
         * Maneja el envío del formulario
         */
        function handleSubmit(e) {
            e.preventDefault();
                
            const submitBtn = document.getElementById('catalogSubmitBtn');
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
                        window.SIGVE.showNotification(data.message || 'Item guardado correctamente', 'success');
                        modalInstance.hide();
                        
                        // Recargar la página para actualizar la lista
                        setTimeout(() => {
                            window.location.reload();
                        }, 1000); // Un poco más rápido que 1.5s
                    } else if (data.errors) {
                        const firstError = Object.values(data.errors)[0][0];
                        window.SIGVE.showNotification(firstError, 'error');
                        window.SIGVE.hideButtonLoading(submitBtn);
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                window.SIGVE.showNotification('Error al guardar el item', 'error');
                window.SIGVE.hideButtonLoading(submitBtn);
            });
        }
        
        /**
         * Confirma la eliminación del item (usado desde el modo 'view')
         */
        function confirmDelete() {
            if (!currentItemId || !currentCatalogName) return;
            
            modalInstance.hide();

            // Abrir el modal de confirmación genérico
            window.ConfirmationModal.open({
                formAction: `/sigve/catalogs/${currentCatalogName}/${currentItemId}/delete/`,
                warningText: `¿Estás seguro de eliminar el item '${document.getElementById('id_name').value}'?`,
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
         * Resetea el modal a su estado inicial
         */
        function resetModal() {
            currentMode = 'create';
            currentItemId = null;
            currentCatalogName = null;
            currentSingularName = 'Item';
            currentPlaceholder = 'Ej: Nuevo Item';
            form.reset();

            const nameInput = document.getElementById('id_name');
            if(nameInput) {
                nameInput.placeholder = currentPlaceholder;
            }

            form.classList.remove('was-validated');
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
     * Inicialización de la página de lista de Catálogos
     */
    document.addEventListener('DOMContentLoaded', function() {
        // Conectar la búsqueda de la tabla
        if (window.SIGVE && window.SIGVE.setupTableSearch) {
            window.SIGVE.setupTableSearch('tableSearchInput', 'catalogTable');
        }
    });

})();