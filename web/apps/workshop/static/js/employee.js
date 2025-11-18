/**
 * Workshop - Lógica de Employees (Empleados)
 *
 * Incluye el controlador del modal de Empleado con modos: crear, ver, editar
 */

(function() {
    'use strict';

    /**
     * Sistema de gestión del modal de empleado
     * Maneja tres modos: crear, ver, editar
     */
    window.EmployeeModal = (function() {
        // Referencias a elementos del DOM
        const modal = document.getElementById('employeeModal');
        const form = document.getElementById('employeeForm');
        const loading = document.getElementById('employeeModalLoading');
        const footer = document.getElementById('employeeModalFooter');
        const titleSpan = document.getElementById('employeeModalTitle');
        
        // Estado actual
        let currentMode = 'create'; // 'create', 'view', 'edit'
        let currentEmployeeId = null;
        let currentEmployeeData = null; // Guardar datos del empleado actual
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
            
            // Evento para mostrar/ocultar campos de contraseña en modo crear
            const emailField = document.getElementById('id_email');
            if (emailField) {
                emailField.addEventListener('input', togglePasswordFields);
            }
        }
        
        /**
         * Abre el modal en el modo especificado
         * @param {string} mode - 'create', 'view', 'edit'
         * @param {string} employeeId - ID del empleado (para view/edit)
         */
        function open(mode = 'create', employeeId = null) {
            currentMode = mode;
            currentEmployeeId = employeeId;
            
            if (mode === 'create') {
                setupCreateMode();
            } else if (mode === 'view' || mode === 'edit') {
                showLoading();
                modalInstance.show();
                loadEmployeeData(employeeId, mode);
            }
        }
        
        /**
         * Configura el modal para crear un empleado
         */
        function setupCreateMode() {
            titleSpan.textContent = 'Crear Empleado';
            form.action = '/taller/employees/create/';
            form.reset();
            document.getElementById('employeeId').value = '';
            currentEmployeeData = null;
            setFieldsEnabled(true);
            showPasswordFields(true);
            renderButtons('create');
            hideLoading();
            showForm();
            modalInstance.show();
        }
        
        /**
         * Carga los datos del empleado
         */
        function loadEmployeeData(employeeId, mode) {
            fetch(`/taller/api/employees/${employeeId}/`)
                .then(response => {
                    if (!response.ok) {
                         throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        populateForm(data.employee);
                        hideLoading();
                        showForm();
                        
                        // Aplicar el modo después de mostrar el formulario
                        if (mode === 'view') {
                            setupViewMode();
                        } else if (mode === 'edit') {
                            setupEditMode();
                        }
                    } else {
                        throw new Error(data.error || 'Error al cargar el empleado');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error al cargar los datos del empleado: ' + error.message);
                    modalInstance.hide();
                });
        }
        
        /**
         * Configura el modal para ver un empleado (solo lectura)
         */
        function setupViewMode() {
            titleSpan.textContent = 'Ver Empleado';
            renderButtons('view');
            showPasswordFields(false);
            
            // Actualizar botón de estado si hay datos del empleado
            if (currentEmployeeData) {
                updateStatusButton(
                    currentEmployeeData.is_active,
                    currentEmployeeData.id,
                    currentEmployeeData.first_name,
                    currentEmployeeData.last_name
                );
            }
            
            setTimeout(() => setFieldsEnabled(false), 0);
        }
        
        /**
         * Configura el modal para editar un empleado
         */
        function setupEditMode() {
            titleSpan.textContent = 'Editar Empleado';
            form.action = `/taller/employees/${currentEmployeeId}/update/`;
            
            // Actualizar botón de estado si hay datos del empleado
            if (currentEmployeeData) {
                updateStatusButton(
                    currentEmployeeData.is_active,
                    currentEmployeeData.id,
                    currentEmployeeData.first_name,
                    currentEmployeeData.last_name
                );
            }
            renderButtons('edit');
            showPasswordFields(false);
            setTimeout(() => setFieldsEnabled(true), 0);
        }
        
        /**
         * Cambia del modo vista al modo edición
         */
        function switchToEditMode() {
            currentMode = 'edit';
            setupEditMode();
            
            // Asegurar que el botón de estado se actualice
            if (currentEmployeeData) {
                updateStatusButton(
                    currentEmployeeData.is_active,
                    currentEmployeeData.id,
                    currentEmployeeData.first_name,
                    currentEmployeeData.last_name
                );
            }
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
         * Llena el formulario con los datos del empleado
         */
        function populateForm(employee) {
            currentEmployeeData = employee; // Guardar datos del empleado
            
            document.getElementById('employeeId').value = employee.id || '';
            document.getElementById('id_first_name').value = employee.first_name || '';
            document.getElementById('id_last_name').value = employee.last_name || '';
            document.getElementById('id_rut').value = employee.rut || '';
            document.getElementById('id_phone').value = employee.phone || '';
            document.getElementById('id_role_id').value = employee.role_id || '';
            
            // Email (solo en vista/edición, no se puede cambiar)
            const emailField = document.getElementById('id_email');
            if (emailField) {
                // En Supabase no tenemos acceso directo al email desde user_profile
                emailField.value = 'Ver en Supabase Auth';
                emailField.disabled = true;
            }
            
            // Actualizar botón de estado
            updateStatusButton(employee.is_active, employee.id, employee.first_name, employee.last_name);
        }
        
        /**
         * Habilita o deshabilita los campos del formulario
         */
        function setFieldsEnabled(enabled) {
            const fields = form.querySelectorAll('input, textarea, select');
            fields.forEach(field => {
                if (field.type !== 'hidden' && field.id !== 'id_email') {
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
         * Actualiza el botón de estado (activo/inactivo)
         */
        function updateStatusButton(isActive, employeeId, firstName, lastName) {
            const statusButtonContainer = document.getElementById('statusButtonContainer');
            if (!statusButtonContainer) return;
            
            const employeeName = `${firstName} ${lastName}`;
            const escapedName = employeeName.replace(/'/g, "\\'").replace(/"/g, '&quot;');
            
            if (isActive) {
                statusButtonContainer.innerHTML = `
                    <button type="button" class="btn btn-warning" 
                            onclick="DeactivateEmployeeModal.open('${employeeId}', '${escapedName}')">
                        <i class="bi bi-pause-circle"></i> Desactivar
                    </button>
                `;
            } else {
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
                statusButtonContainer.innerHTML = `
                    <form method="post" action="/taller/employees/${employeeId}/activate/" style="display:inline-block; margin:0;">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                        <button type="submit" class="btn btn-success">
                            <i class="bi bi-play-circle"></i> Activar
                        </button>
                    </form>
                `;
            }
        }
        
        /**
         * Muestra u oculta los campos de contraseña
         */
        function showPasswordFields(show) {
            const passwordGroup = document.getElementById('passwordFieldsGroup');
            if (passwordGroup) {
                passwordGroup.style.display = show ? 'block' : 'none';
            }
            
            const passwordField = document.getElementById('id_password');
            const passwordConfirmField = document.getElementById('id_password_confirm');
            
            if (passwordField) {
                passwordField.required = show;
            }
            if (passwordConfirmField) {
                passwordConfirmField.required = show;
            }
        }
        
        /**
         * Toggle de campos de contraseña (para modo crear)
         */
        function togglePasswordFields() {
            // Esta función puede expandirse si se necesita lógica adicional
        }
        
        /**
         * Renderiza los botones del footer según el modo
         */
        function renderButtons(mode) {
            const statusButtonContainer = document.getElementById('statusButtonContainer');
            
            // Limpiar solo los botones de acción, mantener el contenedor de estado
            const actionButtons = footer.querySelectorAll('button:not(#statusButtonContainer button)');
            actionButtons.forEach(btn => btn.remove());
            
            // Limpiar el contenedor de estado si es modo crear
            if (mode === 'create' && statusButtonContainer) {
                statusButtonContainer.innerHTML = '';
            }
            
            // Agregar los botones según el modo
            if (mode === 'view') {
                footer.innerHTML = `
                    <div id="statusButtonContainer" class="me-auto"></div>
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="bi bi-x-lg"></i> Cerrar
                    </button>
                    <button type="button" class="btn btn-primary" onclick="EmployeeModal.switchToEditMode()" id="editBtn">
                        <i class="bi bi-pencil"></i> Editar
                    </button>
                `;
            } else if (mode === 'edit') {
                footer.innerHTML = `
                    <div id="statusButtonContainer" class="me-auto"></div>
                    <button type="button" class="btn btn-secondary" onclick="EmployeeModal.cancelEdit()">
                        <i class="bi bi-x-lg"></i> Cancelar
                    </button>
                    <button type="submit" class="btn btn-success" id="employeeSubmitBtn">
                        <i class="bi bi-check-lg"></i> Guardar Cambios
                    </button>
                `;
            } else if (mode === 'create') {
                footer.innerHTML = `
                    <div id="statusButtonContainer" class="me-auto" style="display:none;"></div>
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="bi bi-x-lg"></i> Cancelar
                    </button>
                    <button type="submit" class="btn btn-primary" id="employeeSubmitBtn">
                        <i class="bi bi-check-lg"></i> Crear Empleado
                    </button>
                `;
            }
            
            // Actualizar el botón de estado si hay datos del empleado y no es modo crear
            if (mode !== 'create' && currentEmployeeData) {
                updateStatusButton(
                    currentEmployeeData.is_active,
                    currentEmployeeData.id,
                    currentEmployeeData.first_name,
                    currentEmployeeData.last_name
                );
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
                
            const submitBtn = document.getElementById('employeeSubmitBtn');
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
                if (!data) return; // Ya se manejó la redirección
                
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
                } else {
                    throw new Error(data.error || 'Error al guardar');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                const errorMessage = 'Error al guardar el empleado: ' + error.message;
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
            
            // Verificar si estamos en modo edición o creación
            const isEditMode = currentMode === 'edit';
            const passwordFieldsGroup = document.getElementById('passwordFieldsGroup');
            const isPasswordGroupVisible = passwordFieldsGroup && passwordFieldsGroup.style.display !== 'none';
            
            // Campos que no deben validarse en modo edición
            const fieldsToSkipInEdit = ['email', 'password', 'password_confirm'];
            
            // Obtener todos los campos requeridos
            const requiredFields = form.querySelectorAll('[required]');
            
            // Mensajes de error en español para campos requeridos
            const errorMessages = {
                'first_name': 'Por favor, ingresa el nombre.',
                'last_name': 'Por favor, ingresa el apellido.',
                'email': 'Por favor, ingresa un correo electrónico válido.',
                'password': 'La contraseña debe tener al menos 6 caracteres.',
                'password_confirm': 'Por favor, confirma la contraseña.',
                'role_id': 'Por favor, selecciona un rol.'
            };
            
            requiredFields.forEach(field => {
                const fieldName = field.name;
                
                // Saltar campos que no deben validarse en modo edición
                if (isEditMode && fieldsToSkipInEdit.includes(fieldName)) {
                    return;
                }
                
                // Saltar campos que están ocultos (dentro de passwordFieldsGroup cuando está oculto)
                if (!isPasswordGroupVisible && fieldsToSkipInEdit.includes(fieldName)) {
                    return;
                }
                
                // Saltar campos que están deshabilitados o readonly
                if (field.disabled || field.readOnly) {
                    return;
                }
                
                // Saltar campos que están ocultos (checking parent visibility)
                if (field.offsetParent === null) {
                    return;
                }
                
                let fieldValue = field.value;
                
                // Para selects, verificar que tenga un valor seleccionado
                if (field.tagName === 'SELECT') {
                    if (!fieldValue || fieldValue === '') {
                        isValid = false;
                        field.classList.add('is-invalid');
                        const errorMsg = errorMessages[fieldName] || 'Este campo es obligatorio.';
                        showFieldError(fieldName, errorMsg);
                    }
                } else {
                    // Para inputs, usar trim
                    fieldValue = fieldValue ? fieldValue.trim() : '';
                    if (!fieldValue) {
                        isValid = false;
                        field.classList.add('is-invalid');
                        const errorMsg = errorMessages[fieldName] || 'Este campo es obligatorio.';
                        showFieldError(fieldName, errorMsg);
                    }
                }
            });
            
            // Validar email solo si está visible y tiene valor (solo en modo crear)
            if (!isEditMode && isPasswordGroupVisible) {
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
            }
            
            // Validar contraseñas solo si están visibles (modo crear)
            if (isPasswordGroupVisible) {
                const passwordField = document.getElementById('id_password');
                const passwordConfirmField = document.getElementById('id_password_confirm');
                
                if (passwordField && passwordField.value.trim()) {
                    if (passwordField.value.length < 6) {
                        isValid = false;
                        passwordField.classList.add('is-invalid');
                        showFieldError('password', 'La contraseña debe tener al menos 6 caracteres.');
                    }
                }
                
                if (passwordField && passwordConfirmField) {
                    if (passwordField.value !== passwordConfirmField.value) {
                        isValid = false;
                        passwordConfirmField.classList.add('is-invalid');
                        showFieldError('password_confirm', 'Las contraseñas no coinciden.');
                    }
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
         * @param {string} fieldName - Nombre del campo (ej: 'first_name', 'rut', 'phone', 'email')
         * @param {string} errorMessage - Mensaje de error a mostrar
         */
        function showFieldError(fieldName, errorMessage) {
            if (!form) return;
            
            const fieldIdMap = {
                'first_name': 'id_first_name',
                'last_name': 'id_last_name',
                'rut': 'id_rut',
                'phone': 'id_phone',
                'email': 'id_email',
                'password': 'id_password',
                'password_confirm': 'id_password_confirm',
                'role_id': 'id_role_id'
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
                if (window.SIGVE && window.SIGVE.showNotification) {
                    window.SIGVE.showNotification(errorMessage, 'error');
                } else {
                    alert(errorMessage);
                }
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
            currentEmployeeId = null;
            currentEmployeeData = null;
            form.reset();
            form.classList.remove('was-validated');
            clearFormErrors();
            setFieldsEnabled(true);
            showPasswordFields(true);
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

    /**
     * Sistema de gestión del modal de confirmación de desactivación
     */
    window.DeactivateEmployeeModal = (function() {
        const modal = document.getElementById('deactivateEmployeeModal');
        const form = document.getElementById('deactivateEmployeeForm');
        const employeeNameSpan = document.getElementById('deactivateEmployeeName');
        let modalInstance = null;
        
        function init() {
            if (!modal || !form) return;
            modalInstance = new bootstrap.Modal(modal);
        }
        
        function open(employeeId, employeeName) {
            if (!modalInstance) return;
            
            form.action = `/taller/employees/${employeeId}/deactivate/`;
            employeeNameSpan.textContent = employeeName;
            modalInstance.show();
        }
        
        // Inicializar cuando el DOM esté listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
        } else {
            init();
        }
        
        return {
            open: open
        };
    })();

})();

