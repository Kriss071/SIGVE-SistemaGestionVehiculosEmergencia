/**
 * Workshop - Lógica de Suppliers (Proveedores)
 *
 * Incluye el controlador del modal de Proveedor con modos: crear, ver, editar
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
        let currentSupplierIsGlobal = false;
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
         */
        function open(mode = 'create', supplierId = null) {
            currentMode = mode;
            currentSupplierId = supplierId;
            
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
            form.action = '/taller/suppliers/create/';
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
            fetch(`/taller/api/suppliers/${supplierId}/`)
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
                    alert('Error al cargar los datos del proveedor: ' + error.message);
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
            form.action = `/taller/suppliers/${currentSupplierId}/update/`;
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
            
            // Guardar si es global para usarlo en renderButtons
            currentSupplierIsGlobal = supplier.is_global || false;
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
                // En modo vista, solo mostrar botón de editar si no es global
                let editButton = '';
                if (!currentSupplierIsGlobal) {
                    editButton = `
                        <button type="button" class="btn btn-primary" onclick="SupplierModal.switchToEditMode()" id="editBtn">
                            <i class="bi bi-pencil"></i> Editar
                        </button>
                    `;
                }
                footer.innerHTML = `
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="bi bi-x-lg"></i> Cerrar
                    </button>
                    ${editButton}
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
            
            // Validar formulario
            if (!form.checkValidity()) {
                e.stopPropagation();
                form.classList.add('was-validated');
                return;
            }
            
            // Deshabilitar botón y mostrar loading
            submitBtn.disabled = true;
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Guardando...';
            
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
                // Si la respuesta es una redirección, recargar la página
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    return response.json();
                }
            })
            .then(data => {
                if (data && data.success === false) {
                    throw new Error(data.error || 'Error al guardar');
                }
                // Si todo está bien, recargar la página
                window.location.reload();
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error al guardar el proveedor: ' + error.message);
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            });
        }
        
        /**
         * Muestra el indicador de carga
         */
        function showLoading() {
            if (loading) loading.style.display = 'block';
            if (form) form.style.display = 'none';
        }
        
        /**
         * Oculta el indicador de carga
         */
        function hideLoading() {
            if (loading) loading.style.display = 'none';
        }
        
        /**
         * Muestra el formulario
         */
        function showForm() {
            if (form) form.style.display = 'block';
        }
        
        /**
         * Resetea el modal cuando se cierra
         */
        function resetModal() {
            form.classList.remove('was-validated');
            currentMode = 'create';
            currentSupplierId = null;
            currentSupplierIsGlobal = false;
        }
        
        // Inicializar cuando el DOM esté listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
        } else {
            init();
        }
        
        // API pública
        return {
            open: open,
            switchToEditMode: switchToEditMode,
            cancelEdit: cancelEdit
        };
    })();

})();

