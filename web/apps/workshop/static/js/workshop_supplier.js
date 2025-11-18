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
            
            // Prevenir validación HTML5 nativa del navegador
            form.addEventListener('invalid', function(e) {
                e.preventDefault();
                // La validación se manejará en handleSubmit
            }, true);
            
            // Limpiar errores cuando el usuario empiece a escribir
            setupFieldErrorClearing();
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
            const nameField = document.getElementById('id_name');
            const rutField = document.getElementById('id_rut');
            const addressField = document.getElementById('id_address');
            const phoneField = document.getElementById('id_phone');
            const emailField = document.getElementById('id_email');
            
            if (nameField) nameField.value = supplier.name || '';
            if (rutField) rutField.value = supplier.rut || '';
            if (addressField) addressField.value = supplier.address || '';
            if (phoneField) phoneField.value = supplier.phone || '';
            if (emailField) emailField.value = supplier.email || '';
            
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
                        // Para inputs y textareas usar readonly, para selects usar disabled
                        if (field.tagName === 'SELECT') {
                            field.setAttribute('disabled', 'disabled');
                        } else {
                            field.setAttribute('readonly', 'readonly');
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
            
            // Validar formulario manualmente para mostrar mensajes en español
            if (!validateForm()) {
                return;
            }
                
            const submitBtn = document.getElementById('supplierSubmitBtn');
            if (!submitBtn) return;
            
            // Mostrar indicador de carga
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
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = originalText;
                        modalInstance.hide();
                        
                        setTimeout(() => {
                            window.location.reload();
                        }, 150);
                        return;
                    } else if (data.errors) {
                        // Errores de validación
                        // Limpiar errores previos
                        clearFormErrors();
                        
                        // Mostrar errores por campo
                        for (const [field, errors] of Object.entries(data.errors)) {
                            if (Array.isArray(errors) && errors.length > 0) {
                                const errorMessage = errors[0];
                                
                                if (field === 'general' || field === '__all__') {
                                    if (window.SIGVE && window.SIGVE.showNotification) {
                                        window.SIGVE.showNotification(errorMessage, 'error');
                                    } else {
                                        alert(errorMessage);
                                    }
                                } else {
                                    showFieldError(field, errorMessage);
                                }
                            }
                        }
                        
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = originalText;
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                const errorMessage = 'Error al guardar el proveedor: ' + error.message;
                if (window.SIGVE && window.SIGVE.showNotification) {
                    window.SIGVE.showNotification(errorMessage, 'error');
                } else {
                    alert(errorMessage);
                }
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            });
        }
        
        /**
         * Valida el formulario y muestra errores en español
         * @returns {boolean} true si el formulario es válido, false en caso contrario
         */
        function validateForm() {
            clearFormErrors();
            
            let isValid = true;
            const requiredFields = form.querySelectorAll('[required]');
            
            // Mensajes de error en español para campos requeridos
            const errorMessages = {
                'name': 'Por favor, ingresa un nombre para el proveedor.'
            };
            
            requiredFields.forEach(field => {
                const fieldName = field.name;
                const fieldValue = field.value.trim();
                
                if (!fieldValue) {
                    isValid = false;
                    field.classList.add('is-invalid');
                    const errorMsg = errorMessages[fieldName] || 'Este campo es obligatorio.';
                    showFieldError(fieldName, errorMsg);
                }
            });
            
            // Validar email si tiene valor
            const emailField = document.getElementById('id_email');
            if (emailField && emailField.value.trim()) {
                const emailValue = emailField.value.trim();
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(emailValue)) {
                    isValid = false;
                    emailField.classList.add('is-invalid');
                    showFieldError('email', 'Por favor, ingresa un correo electrónico válido.');
                }
            }
            
            if (!isValid) {
                if (window.SIGVE && window.SIGVE.showNotification) {
                    window.SIGVE.showNotification('Por favor, completa todos los campos obligatorios.', 'error');
                } else {
                    alert('Por favor, completa todos los campos obligatorios.');
                }
            }
            
            return isValid;
        }
        
        /**
         * Limpia todos los errores del formulario
         */
        function clearFormErrors() {
            if (!form) return;
            
            // Remover clases de error de Bootstrap
            form.querySelectorAll('.is-invalid').forEach(field => {
                field.classList.remove('is-invalid');
            });
            
            // Limpiar mensajes de error dinámicos
            form.querySelectorAll('.invalid-feedback[data-field-error]').forEach(feedback => {
                feedback.textContent = '';
            });
        }
        
        /**
         * Muestra un error en un campo específico del formulario
         * @param {string} fieldName - Nombre del campo (ej: 'name', 'rut', 'phone', 'email')
         * @param {string} errorMessage - Mensaje de error a mostrar
         */
        function showFieldError(fieldName, errorMessage) {
            if (!form) return;
            
            const fieldIdMap = {
                'name': 'id_name',
                'rut': 'id_rut',
                'phone': 'id_phone',
                'email': 'id_email',
                'address': 'id_address'
            };
            
            const fieldId = fieldIdMap[fieldName] || `id_${fieldName}`;
            const field = document.getElementById(fieldId);
            
            if (field) {
                field.classList.add('is-invalid');
                
                let feedback = field.parentElement.querySelector(`.invalid-feedback[data-field-error="${fieldName}"]`);
                if (!feedback) {
                    feedback = field.parentElement.querySelector('.invalid-feedback');
                    if (feedback) {
                        feedback.setAttribute('data-field-error', fieldName);
                    } else {
                        feedback = document.createElement('div');
                        feedback.className = 'invalid-feedback';
                        feedback.setAttribute('data-field-error', fieldName);
                        field.parentElement.appendChild(feedback);
                    }
                }
                feedback.textContent = errorMessage;
            } else {
                console.warn(`Campo no encontrado para mostrar error: ${fieldName}`);
                alert(errorMessage);
            }
        }
        
        /**
         * Configura la limpieza automática de errores cuando el usuario empiece a escribir
         */
        function setupFieldErrorClearing() {
            if (!form) return;
            
            // Limpiar errores en campos cuando el usuario empiece a escribir
            form.querySelectorAll('input, select, textarea').forEach(field => {
                field.addEventListener('input', function() {
                    if (this.classList.contains('is-invalid')) {
                        this.classList.remove('is-invalid');
                        const feedback = this.parentElement.querySelector(`.invalid-feedback[data-field-error="${this.name}"]`);
                        if (feedback) {
                            feedback.textContent = '';
                        }
                    }
                });
                
                field.addEventListener('change', function() {
                    if (this.classList.contains('is-invalid')) {
                        this.classList.remove('is-invalid');
                        const feedback = this.parentElement.querySelector(`.invalid-feedback[data-field-error="${this.name}"]`);
                        if (feedback) {
                            feedback.textContent = '';
                        }
                    }
                });
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
            currentMode = 'create';
            currentSupplierId = null;
            currentSupplierIsGlobal = false;
            form.reset();
            form.classList.remove('was-validated');
            clearFormErrors();
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
            open: open,
            switchToEditMode: switchToEditMode,
            cancelEdit: cancelEdit
        };
    })();

})();

