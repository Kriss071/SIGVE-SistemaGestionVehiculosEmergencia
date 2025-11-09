/**
 * SIGVE - Lógica de Suppliers (Proveedores)
 *
 * Incluye el controlador del modal de Proveedor.
 */

(function() {
    'use strict';

    /**
     * Sistema de gestión del modal de proveedor
     * Maneja tres modos: crear, ver, editar
     */
    window.SupplierModal = (function() {
        // Referencias a elementos del DOM
        const modal = document.getElementById('supplierModal');
        const form = document.getElementById('supplierForm');
        const loading = document.getElementById('supplierModalLoading');
        const footer = document.getElementById('supplierModalFooter');
        const titleSpan = document.getElementById('supplierModalTitle');
        
        // Estado actual
        let currentMode = 'create'; // 'create', 'view', 'edit'
        let currentSupplierId = null;
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
         * @param {number} supplierId - ID del proveedor (para view/edit)
         * @param {string} source - 'dashboard' o 'list' (para saber desde dónde se abre)
         */
        function open(mode = 'create', supplierId = null, source = 'list') {
            currentMode = mode;
            currentSupplierId = supplierId;
            
            // Guardar la fuente en el formulario para usarla al enviar
            const sourceInput = document.getElementById('supplierSource');
            if (sourceInput) {
                sourceInput.value = source;
            }
            
            if (mode === 'create') {
                setupCreateMode();
            } else if (mode === 'view' || mode === 'edit') {
                showLoading();
                modalInstance.show();
                loadSupplierData(supplierId, mode);
            }
        }
        
        /**
         * Configura el modal para crear un proveedor
         */
        function setupCreateMode() {
            titleSpan.textContent = 'Crear Proveedor';
            form.action = '/sigve/suppliers/create/'; // URL de creación
            form.reset();
            document.getElementById('supplierId').value = '';
            setFieldsEnabled(true);
            renderButtons('create');
            hideLoading();
            showForm();
            modalInstance.show();
        }
        
        /**
         * Carga los datos del proveedor
         */
        function loadSupplierData(supplierId, mode) {
            fetch(`/sigve/api/suppliers/${supplierId}/`)
                .then(response => {
                    if (!response.ok) {
                         throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        populateForm(data.supplier);
                        hideLoading();
                        showForm();
                        
                        // Aplicar el modo después de mostrar el formulario
                        if (mode === 'view') {
                            setupViewMode();
                        } else if (mode === 'edit') {
                            setupEditMode();
                        }
                    } else {
                        throw new Error(data.error || 'Error al cargar el proveedor');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    window.SIGVE.showNotification('Error al cargar los datos del proveedor', 'error');
                    modalInstance.hide();
                });
        }
        
        /**
         * Configura el modal para ver un proveedor (solo lectura)
         */
        function setupViewMode() {
            titleSpan.textContent = 'Ver Proveedor';
            renderButtons('view');
            setTimeout(() => setFieldsEnabled(false), 0);
        }
        
        /**
         * Configura el modal para editar un proveedor
         */
        function setupEditMode() {
            titleSpan.textContent = 'Editar Proveedor';
            form.action = `/sigve/suppliers/${currentSupplierId}/edit/`;
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
         * Llena el formulario con los datos del proveedor
         */
        function populateForm(supplier) {
            document.getElementById('supplierId').value = supplier.id || '';
            document.getElementById('id_name').value = supplier.name || '';
            document.getElementById('id_rut').value = supplier.rut || '';
            document.getElementById('id_address').value = supplier.address || '';
            document.getElementById('id_phone').value = supplier.phone || '';
            document.getElementById('id_email').value = supplier.email || '';
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
                    <button type="button" class="btn btn-danger" onclick="SupplierModal.confirmDelete()">
                        <i class="bi bi-trash"></i> Eliminar
                    </button>
                    <button type="button" class="btn btn-primary" onclick="SupplierModal.switchToEditMode()">
                        <i class="bi bi-pencil"></i> Editar
                    </button>
                `;
            } else if (mode === 'edit') {
                footer.innerHTML = `
                    <button type="button" class="btn btn-secondary" onclick="SupplierModal.cancelEdit()">
                        <i class="bi bi-x-lg"></i> Cancelar
                    </button>
                    <button type="submit" class="btn btn-success" id="supplierSubmitBtn">
                        <i class="bi bi-check-lg"></i> Guardar Cambios
                    </button>
                `;
            } else if (mode === 'create') {
                footer.innerHTML = `
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="bi bi-x-lg"></i> Cancelar
                    </button>
                    <button type="submit" class="btn btn-primary" id="supplierSubmitBtn">
                        <i class="bi bi-check-lg"></i> Guardar Proveedor
                    </button>
                `;
            }
        }
        
        /**
         * Maneja el envío del formulario
         */
        function handleSubmit(e) {
            e.preventDefault();
                
            const submitBtn = document.getElementById('supplierSubmitBtn');
            if (!submitBtn) return;
            
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
                // Si la respuesta es una redirección, la seguimos
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
                        const firstError = Object.values(data.errors)[0][0];
                        window.SIGVE.showNotification(firstError, 'error');
                        window.SIGVE.hideButtonLoading(submitBtn);
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                window.SIGVE.showNotification('Error al guardar el proveedor', 'error');
                window.SIGVE.hideButtonLoading(submitBtn);
            });
        }
        
        /**
         * Confirma la eliminación del proveedor
         */
        function confirmDelete() {
            if (!currentSupplierId) return;
            
            modalInstance.hide();

            window.ConfirmationModal.open({
                formAction: `/sigve/suppliers/${currentSupplierId}/delete/`,
                warningText: `¿Estás seguro de eliminar el proveedor ${document.getElementById('id_name').value}?`,
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
            currentSupplierId = null;
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
     * Inicialización de la página de lista de Proveedores
     */
    document.addEventListener('DOMContentLoaded', function() {
        // Conectar la búsqueda de la tabla
        if (window.SIGVE && window.SIGVE.setupTableSearch) {
            window.SIGVE.setupTableSearch('tableSearchInput', 'suppliersTable');
        }
    });

})();