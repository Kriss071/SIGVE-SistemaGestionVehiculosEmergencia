/**
 * Fire Station - Users List JavaScript
 * 
 * Incluye el controlador del modal de usuarios y la inicialización
 * de la búsqueda en la lista de usuarios.
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
     * Sistema de gestión del modal de usuario
     * Maneja dos modos: ver, editar
     */
    window.UserModal = (function() {
        // Referencias a elementos del DOM
        const modal = document.getElementById('userModal');
        const form = document.getElementById('userForm');
        const loading = document.getElementById('userModalLoading');
        const footer = document.getElementById('userModalFooter');
        const titleSpan = document.getElementById('userModalTitle');
        
        // Estado actual
        let currentMode = 'view'; // 'view', 'edit', 'create'
        let currentUserId = null;
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
         * @param {string} mode - 'view', 'edit', 'create'
         * @param {string} userId - ID del usuario (UUID) - solo para view/edit
         */
        function open(mode = 'view', userId = null) {
            currentMode = mode;
            currentUserId = userId;
            
            if (mode === 'create') {
                setupCreateMode();
            } else if (mode === 'view' || mode === 'edit') {
                showLoading();
                modalInstance.show();
                loadUserData(userId, mode);
            }
        }
        
        /**
         * Carga los datos del usuario
         */
        function loadUserData(userId, mode) {
            fetch(`/fire-station/api/users/${userId}/`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        populateForm(data.user);
                        hideLoading();
                        showForm();
                        
                        if (mode === 'view') {
                            setupViewMode();
                        } else if (mode === 'edit') {
                            setupEditMode();
                        }
                    } else {
                        throw new Error(data.error || 'Error al cargar el usuario');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    FS.showNotification('Error al cargar los datos del usuario', 'error');
                    modalInstance.hide();
                });
        }
        
        /**
         * Configura el modal para crear un usuario
         */
        function setupCreateMode() {
            titleSpan.textContent = 'Crear Usuario';
            form.action = '/fire-station/users/create/';
            form.reset();
            form.classList.remove('was-validated');
            
            // Limpiar clases de validación
            const invalidFields = form.querySelectorAll('.is-invalid');
            invalidFields.forEach(field => field.classList.remove('is-invalid'));
            
            document.getElementById('userId').value = '';
            
            // Mostrar campos de credenciales, ocultar email de solo lectura
            document.getElementById('passwordFieldsGroup').style.display = 'block';
            document.getElementById('emailViewGroup').style.display = 'none';
            
            // Limpiar email view
            document.getElementById('id_email_view').value = '';
            
            // Asegurar que los campos requeridos estén habilitados
            const emailField = document.getElementById('id_email');
            const emailViewField = document.getElementById('id_email_view');
            const passwordField = document.getElementById('id_password');
            const passwordConfirmField = document.getElementById('id_password_confirm');
            
            // Deshabilitar el campo de email view para que no se envíe
            if (emailViewField) {
                emailViewField.disabled = true;
                emailViewField.removeAttribute('name');
            }
            
            // Habilitar el campo de email para create
            if (emailField) {
                emailField.removeAttribute('readonly');
                emailField.removeAttribute('disabled');
                emailField.required = true;
                emailField.name = 'email'; // Asegurar que tenga el name correcto
            }
            if (passwordField) {
                passwordField.removeAttribute('readonly');
                passwordField.removeAttribute('disabled');
                passwordField.required = true;
            }
            if (passwordConfirmField) {
                passwordConfirmField.removeAttribute('readonly');
                passwordConfirmField.removeAttribute('disabled');
                passwordConfirmField.required = true;
            }
            
            setFieldsEnabled(true);
            renderButtons('create');
            hideLoading();
            showForm();
            modalInstance.show();
        }
        
        /**
         * Configura el modal para ver un usuario (solo lectura)
         */
        function setupViewMode() {
            titleSpan.textContent = 'Ver Usuario';
            
            // Ocultar campos de credenciales, mostrar email de solo lectura
            document.getElementById('passwordFieldsGroup').style.display = 'none';
            document.getElementById('emailViewGroup').style.display = 'block';
            
            // Deshabilitar el campo de email de create para que no se envíe
            const emailField = document.getElementById('id_email');
            if (emailField) {
                emailField.disabled = true;
                emailField.removeAttribute('name');
                emailField.required = false;
            }
            
            // Remover required de los campos de contraseña ya que no se usan en modo view
            const passwordField = document.getElementById('id_password');
            const passwordConfirmField = document.getElementById('id_password_confirm');
            if (passwordField) {
                passwordField.required = false;
                passwordField.disabled = true;
            }
            if (passwordConfirmField) {
                passwordConfirmField.required = false;
                passwordConfirmField.disabled = true;
            }
            
            renderButtons('view');
            setTimeout(() => setFieldsEnabled(false), 0);
        }
        
        /**
         * Configura el modal para editar un usuario
         */
        function setupEditMode() {
            titleSpan.textContent = 'Editar Usuario';
            form.action = `/fire-station/users/${currentUserId}/edit/`;
            
            // Ocultar campos de credenciales, mostrar email de solo lectura
            document.getElementById('passwordFieldsGroup').style.display = 'none';
            document.getElementById('emailViewGroup').style.display = 'block';
            
            // Deshabilitar el campo de email de create para que no se envíe
            const emailField = document.getElementById('id_email');
            if (emailField) {
                emailField.disabled = true;
                emailField.removeAttribute('name');
                emailField.required = false;
            }
            
            // Remover required de los campos de contraseña ya que no se usan en modo edit
            const passwordField = document.getElementById('id_password');
            const passwordConfirmField = document.getElementById('id_password_confirm');
            if (passwordField) {
                passwordField.required = false;
                passwordField.disabled = true;
            }
            if (passwordConfirmField) {
                passwordConfirmField.required = false;
                passwordConfirmField.disabled = true;
            }
            
            // Asegurar que los campos editables estén habilitados
            const firstNameField = document.getElementById('id_first_name');
            const lastNameField = document.getElementById('id_last_name');
            const rutField = document.getElementById('id_rut');
            const phoneField = document.getElementById('id_phone');
            const roleField = document.getElementById('id_role_id');
            const isActiveField = document.getElementById('id_is_active');
            
            if (firstNameField) {
                firstNameField.removeAttribute('readonly');
                firstNameField.removeAttribute('disabled');
            }
            if (lastNameField) {
                lastNameField.removeAttribute('readonly');
                lastNameField.removeAttribute('disabled');
            }
            if (rutField) {
                rutField.removeAttribute('readonly');
                rutField.removeAttribute('disabled');
            }
            if (phoneField) {
                phoneField.removeAttribute('readonly');
                phoneField.removeAttribute('disabled');
            }
            if (roleField) {
                roleField.removeAttribute('disabled');
            }
            if (isActiveField) {
                isActiveField.removeAttribute('disabled');
            }
            
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
         * Llena el formulario con los datos del usuario
         */
        function populateForm(user) {
            document.getElementById('userId').value = user.id || '';
            document.getElementById('id_first_name').value = user.first_name || '';
            document.getElementById('id_last_name').value = user.last_name || '';
            
            // Usar el campo de email de solo lectura para view/edit
            const emailViewField = document.getElementById('id_email_view');
            if (emailViewField) {
                emailViewField.value = user.email || '';
            }
            
            document.getElementById('id_rut').value = user.rut || '';
            document.getElementById('id_phone').value = user.phone || '';
            
            // El role_id puede venir directamente o dentro de role.id
            const roleId = user.role_id || (user.role && user.role.id) || '';
            document.getElementById('id_role_id').value = roleId;
            
            document.getElementById('id_is_active').checked = user.is_active !== undefined ? user.is_active : true;
        }
        
        /**
         * Habilita o deshabilita los campos del formulario
         */
        function setFieldsEnabled(enabled) {
            const fields = form.querySelectorAll('input:not([type="hidden"]), textarea, select');
            fields.forEach(field => {
                // El email view siempre es readonly
                if (field.id === 'id_email_view') {
                    field.setAttribute('readonly', 'readonly');
                    return;
                }
                
                // Los campos de password solo se usan en modo create
                if (field.id === 'id_password' || field.id === 'id_password_confirm' || field.id === 'id_email') {
                    // Solo habilitar si estamos en modo create
                    if (currentMode === 'create') {
                        if (enabled) {
                            field.removeAttribute('readonly');
                            field.removeAttribute('disabled');
                        } else {
                            if (field.tagName === 'SELECT') {
                                field.setAttribute('disabled', 'disabled');
                            } else {
                                field.setAttribute('readonly', 'readonly');
                            }
                        }
                    }
                    return;
                }
                
                if (enabled) {
                    field.removeAttribute('readonly');
                    field.removeAttribute('disabled');
                } else {
                    field.setAttribute('readonly', 'readonly');
                    if (field.tagName === 'SELECT') {
                        field.setAttribute('disabled', 'disabled');
                    }
                    if (field.type === 'checkbox') {
                        field.setAttribute('disabled', 'disabled');
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
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="bi bi-x-lg"></i> Cerrar
                    </button>
                    <button type="button" class="btn btn-dark" onclick="UserModal.switchToEditMode()">
                        <i class="bi bi-pencil"></i> Editar
                    </button>
                `;
            } else if (mode === 'edit') {
                footer.innerHTML = `
                    <button type="button" class="btn btn-secondary" onclick="UserModal.cancelEdit()">
                        <i class="bi bi-x-lg"></i> Cancelar
                    </button>
                    <button type="submit" class="btn btn-success" id="userSubmitBtn">
                        <i class="bi bi-check-lg"></i> Guardar Cambios
                    </button>
                `;
            } else if (mode === 'create') {
                footer.innerHTML = `
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="bi bi-x-lg"></i> Cancelar
                    </button>
                    <button type="submit" class="btn btn-primary" id="userSubmitBtn">
                        <i class="bi bi-check-lg"></i> Crear Usuario
                    </button>
                `;
            }
        }
        
        /**
         * Maneja el envío del formulario
         */
        function handleSubmit(e) {
            e.preventDefault();
            
            console.log('handleSubmit llamado, modo:', currentMode);
            
            const submitBtn = document.getElementById('userSubmitBtn');
            if (!submitBtn) {
                console.error('No se encontró el botón de submit');
                return;
            }
            
            // Validar contraseñas si estamos en modo create (antes de checkValidity)
            if (currentMode === 'create') {
                const password = document.getElementById('id_password').value;
                const passwordConfirm = document.getElementById('id_password_confirm').value;
                
                if (password !== passwordConfirm) {
                    FS.showNotification('Las contraseñas no coinciden', 'error');
                    document.getElementById('id_password_confirm').setCustomValidity('Las contraseñas no coinciden');
                    form.classList.add('was-validated');
                    return;
                } else {
                    document.getElementById('id_password_confirm').setCustomValidity('');
                }
            }
            
            // Verificar campos requeridos manualmente
            const requiredFields = form.querySelectorAll('[required]');
            let invalidFields = [];
            
            requiredFields.forEach(field => {
                // Ignorar campos ocultos o deshabilitados
                if (field.offsetParent === null || field.disabled) {
                    return;
                }
                
                // En modo edit, ignorar campos de contraseña
                if (currentMode === 'edit' && (field.id === 'id_password' || field.id === 'id_password_confirm')) {
                    return;
                }
                
                if (!field.value || (field.type === 'checkbox' && !field.checked)) {
                    invalidFields.push(field.id || field.name);
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (invalidFields.length > 0) {
                console.log('Campos inválidos encontrados:', invalidFields);
                form.classList.add('was-validated');
                FS.showNotification('Por favor completa todos los campos requeridos', 'error');
                return;
            }
            
            // Validar formulario
            if (!form.checkValidity()) {
                console.log('Formulario no válido según checkValidity()');
                e.stopPropagation();
                form.classList.add('was-validated');
                
                // Mostrar qué campos están inválidos
                const invalidElements = form.querySelectorAll(':invalid');
                invalidElements.forEach(element => {
                    console.log('Campo inválido:', element.id || element.name, element.validationMessage);
                    element.classList.add('is-invalid');
                });
                
                return;
            }
            
            console.log('Formulario válido, procediendo a enviar...');
            
            FS.showButtonLoading(submitBtn, currentMode === 'create' ? 'Creando...' : 'Guardando...');
            
            // Crear FormData y asegurarse de que solo se incluyan los campos correctos
            const formData = new FormData(form);
            
            // Debug: mostrar qué se está enviando
            console.log(`Enviando datos en modo ${currentMode}:`);
            console.log('URL:', form.action);
            for (let [key, value] of formData.entries()) {
                console.log(key + ': ' + value);
            }
            
            // Verificar que la URL esté configurada
            if (!form.action) {
                console.error('El formulario no tiene una URL de acción configurada');
                FS.hideButtonLoading(submitBtn);
                FS.showNotification('Error: URL de acción no configurada', 'error');
                return;
            }
            
            console.log('Enviando petición fetch a:', form.action);
            
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
                        // Mostrar todos los errores de validación
                        let errorMessages = [];
                        for (const [field, errors] of Object.entries(data.errors)) {
                            if (Array.isArray(errors)) {
                                errors.forEach(error => {
                                    errorMessages.push(`${field}: ${error}`);
                                });
                            } else {
                                errorMessages.push(`${field}: ${errors}`);
                            }
                        }
                        
                        // Mostrar el primer error como notificación
                        const firstError = errorMessages[0] || 'Error al guardar el usuario';
                        FS.showNotification(firstError, 'error');
                        
                        // También mostrar errores en los campos correspondientes
                        for (const [field, errors] of Object.entries(data.errors)) {
                            const fieldElement = document.getElementById(`id_${field}`);
                            if (fieldElement) {
                                fieldElement.classList.add('is-invalid');
                                const errorText = Array.isArray(errors) ? errors[0] : errors;
                                const feedbackElement = fieldElement.nextElementSibling;
                                if (feedbackElement && feedbackElement.classList.contains('invalid-feedback')) {
                                    feedbackElement.textContent = errorText;
                                }
                            }
                        }
                        
                        FS.hideButtonLoading(submitBtn);
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                FS.showNotification('Error al guardar el usuario', 'error');
                FS.hideButtonLoading(submitBtn);
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
            currentMode = 'view';
            currentUserId = null;
            form.reset();
            form.classList.remove('was-validated');
            
            // Limpiar clases de validación
            const invalidFields = form.querySelectorAll('.is-invalid');
            invalidFields.forEach(field => field.classList.remove('is-invalid'));
            
            // Ocultar campos de credenciales y email view
            document.getElementById('passwordFieldsGroup').style.display = 'none';
            document.getElementById('emailViewGroup').style.display = 'none';
            
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
            cancelEdit
        };
    })();

    /**
     * Inicialización de la página de lista de Usuarios
     */
    document.addEventListener('DOMContentLoaded', function() {
        // Conectar la búsqueda de la tabla
        if (window.SIGVE && window.SIGVE.setupTableSearch) {
            window.SIGVE.setupTableSearch('tableSearchInput', 'usersTable');
        }
    });

})();

