/**
 * SIGVE - Lógica de Users (Usuarios)
 *
 * Incluye el controlador del modal de Usuario.
 */

(function() {
    'use strict';

    const ROLE_ADMIN_SIGVE = 'Admin SIGVE';
    const ROLE_ADMIN_TALLER = 'Admin Taller';
    const ROLE_MECANICO = 'Mecánico';
    const ROLE_JEFE_CUARTEL = 'Jefe Cuartel';

    /**
     * Crea un controlador para bloquear los select de taller y cuartel
     * de forma mutuamente excluyente.
     */
    function createMutualSelectController(workshopSelect, fireStationSelect) {
        if (!workshopSelect || !fireStationSelect) {
            return {
                refresh: () => {},
                reset: () => {},
                lockBoth: () => {},
                lockWorkshop: () => {},
                lockFireStation: () => {},
                unlockAll: () => {}
            };
        }

        let forcedLocks = { workshop: false, fireStation: false };

        const applyLocks = () => {
            const workshopModeLocked = workshopSelect.dataset.modeDisabled === 'true';
            const fireModeLocked = fireStationSelect.dataset.modeDisabled === 'true';

            if (forcedLocks.workshop) {
                workshopSelect.value = '';
                workshopSelect.dataset.roleLocked = 'true';
                workshopSelect.setAttribute('disabled', 'disabled');
            } else {
                delete workshopSelect.dataset.roleLocked;
                if (!workshopModeLocked) {
                    workshopSelect.removeAttribute('disabled');
                }
            }

            if (forcedLocks.fireStation) {
                fireStationSelect.value = '';
                fireStationSelect.dataset.roleLocked = 'true';
                fireStationSelect.setAttribute('disabled', 'disabled');
            } else {
                delete fireStationSelect.dataset.roleLocked;
                if (!fireModeLocked) {
                    fireStationSelect.removeAttribute('disabled');
                }
            }
        };

        return {
            refresh: () => applyLocks(),
            reset: () => {
                forcedLocks = { workshop: false, fireStation: false };
                applyLocks();
            },
            lockBoth: () => {
                forcedLocks = { workshop: true, fireStation: true };
                applyLocks();
            },
            lockWorkshop: () => {
                forcedLocks = { workshop: true, fireStation: false };
                applyLocks();
            },
            lockFireStation: () => {
                forcedLocks = { workshop: false, fireStation: true };
                applyLocks();
            },
            unlockAll: () => {
                forcedLocks = { workshop: false, fireStation: false };
                applyLocks();
            }
        };
    }

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
        const workshopSelect = document.getElementById('id_workshop_id');
        const fireStationSelect = document.getElementById('id_fire_station_id');
        const roleSelect = document.getElementById('id_role_id');
        const passwordRow = document.getElementById('userPasswordRow');
        const passwordInput = document.getElementById('id_password');
        const passwordConfirmInput = document.getElementById('id_password_confirm');
        
        // Estado actual
        let currentMode = 'view'; // 'view', 'edit'
        let currentUserId = null;
        let modalInstance = null;
        let mutualController = null;
        
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

            mutualController = createMutualSelectController(workshopSelect, fireStationSelect);
            roleSelect?.addEventListener('change', handleRoleChange);
        }
        
        /**
         * Abre el modal en el modo especificado
         * @param {string} mode - 'view', 'edit'
         * @param {string} userId - ID del usuario (UUID)
         * @param {string} source - 'dashboard' o 'list'
         */
        function open(mode = 'view', userId = null, source = 'list') {
            currentMode = mode;
            
            const sourceInput = document.getElementById('userSource');
            if (sourceInput) {
                sourceInput.value = source;
            }

            if (mode === 'create') {
                currentUserId = null;
                setupCreateMode();
                hideLoading();
                showForm();
                modalInstance.show();
                return;
            }

            if (!userId) return;

            currentUserId = userId;
            
            showLoading();
            modalInstance.show();
            loadUserData(userId, mode);
            handleRoleChange();
        }
        
        /**
         * Carga los datos del usuario
         */
        function loadUserData(userId, mode) {
            fetch(`/sigve/api/users/${userId}/`)
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
                    window.SIGVE.showNotification('Error al cargar los datos del usuario', 'error');
                    modalInstance.hide();
                });
        }
        
        function setupCreateMode() {
            form.reset();
            form.classList.remove('was-validated');
            document.getElementById('userId').value = '';

            form.action = `/sigve/users/create/`;
            titleSpan.textContent = 'Crear Usuario';
            renderButtons('create');

            setFieldsEnabled(true);
            setPasswordFieldsVisible(true);

            const isActiveCheckbox = document.getElementById('id_is_active');
            if (isActiveCheckbox) {
                isActiveCheckbox.checked = true;
            }

            if (roleSelect) {
                roleSelect.value = '';
            }
            if (workshopSelect) {
                workshopSelect.value = '';
            }
            if (fireStationSelect) {
                fireStationSelect.value = '';
            }

            mutualController?.reset();
            handleRoleChange();
        }

        /**
         * Configura el modal para ver un usuario (solo lectura)
         */
        function setupViewMode() {
            titleSpan.textContent = 'Ver Usuario';
            renderButtons('view');
            setPasswordFieldsVisible(false);
            setTimeout(() => {
                setFieldsEnabled(false);
                mutualController?.refresh();
            }, 0);
        }
        
        /**
         * Configura el modal para editar un usuario
         */
        function setupEditMode() {
            titleSpan.textContent = 'Editar Usuario';
            form.action = `/sigve/users/${currentUserId}/edit/`;
            renderButtons('edit');
            setPasswordFieldsVisible(false);
            setTimeout(() => {
                setFieldsEnabled(true);
                mutualController?.refresh();
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
            document.getElementById('id_email').value = user.email || '';
            document.getElementById('id_first_name').value = user.first_name || '';
            document.getElementById('id_last_name').value = user.last_name || '';
            document.getElementById('id_rut').value = user.rut || '';
            document.getElementById('id_phone').value = user.phone || '';
            setPasswordFieldsVisible(false);
            if (passwordInput) passwordInput.value = '';
            if (passwordConfirmInput) passwordConfirmInput.value = '';

            const roleField = document.getElementById('id_role_id');
            if (roleField) {
                roleField.value = user.role_id != null ? String(user.role_id) : '';
            }

            if (workshopSelect) {
                workshopSelect.value = user.workshop_id != null ? String(user.workshop_id) : '';
            }

            if (fireStationSelect) {
                fireStationSelect.value = user.fire_station_id != null ? String(user.fire_station_id) : '';
            }

            const isActiveCheckbox = document.getElementById('id_is_active');
            if (isActiveCheckbox) {
                isActiveCheckbox.checked = Boolean(user.is_active);
            }

            mutualController?.refresh();
            handleRoleChange();
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
                        delete field.dataset.modeDisabled;
                        if (field.tagName.toLowerCase() === 'select' || field.type === 'checkbox') {
                            if (field.dataset.roleLocked === 'true') {
                                field.setAttribute('disabled', 'disabled');
                            } else {
                                field.removeAttribute('disabled');
                            }
                        }
                    } else {
                        // Los <select> y <input type="checkbox"> usan 'disabled'
                        if (field.tagName.toLowerCase() === 'select' || field.type === 'checkbox') {
                            field.setAttribute('disabled', 'disabled');
                            field.dataset.modeDisabled = 'true';
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
            const userIsActive = document.getElementById('id_is_active').checked;
            
            if (mode === 'view') {
                let activateDeactivateBtn = '';
                
                if (userIsActive) {
                    activateDeactivateBtn = `
                    <button type="button" class="btn btn-warning" onclick="UserModal.confirmDeactivate()">
                        <i class="bi bi-pause-circle"></i> Desactivar
                    </button>`;
                } else {
                    activateDeactivateBtn = `
                    <button type="button" class="btn btn-success" onclick="UserModal.confirmActivate()">
                        <i class="bi bi-play-circle"></i> Activar
                    </button>`;
                }

                footer.innerHTML = `
                    <button type="button" class="btn btn-danger" onclick="UserModal.confirmDelete()">
                        <i class="bi bi-trash"></i> Eliminar
                    </button>
                    ${activateDeactivateBtn}
                    <button type="button" class="btn btn-primary ms-auto" onclick="UserModal.switchToEditMode()">
                        <i class="bi bi-pencil"></i> Editar
                    </button>
                `;
            } else if (mode === 'edit') {
                footer.innerHTML = `
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
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
            
            // Validar formulario manualmente para mostrar mensajes en español
            if (!validateForm()) {
                return;
            }
                
            const submitBtn = document.getElementById('userSubmitBtn');
            if (!submitBtn) return;

            if (currentMode === 'create' && passwordInput && passwordConfirmInput) {
                if (passwordInput.value !== passwordConfirmInput.value) {
                    window.SIGVE.showNotification('Las contraseñas no coinciden.', 'warning');
                    passwordConfirmInput.focus();
                    passwordConfirmInput.classList.add('is-invalid');
                    return;
                }
            }
            
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
                        // Limpiar errores previos
                        clearFormErrors();
                        
                        // Mostrar errores por campo
                        for (const [field, errors] of Object.entries(data.errors)) {
                            if (Array.isArray(errors) && errors.length > 0) {
                                const errorMessage = errors[0];
                                
                                if (field === 'general' || field === '__all__') {
                                    window.SIGVE.showNotification(errorMessage, 'error');
                                } else {
                                    showFieldError(field, errorMessage);
                                }
                            }
                        }
                        
                        window.SIGVE.hideButtonLoading(submitBtn);
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                window.SIGVE.showNotification('Error al guardar el usuario', 'error');
                window.SIGVE.hideButtonLoading(submitBtn);
            });
        }
        
        /**
         * Confirma la desactivación del usuario
         */
        function confirmDeactivate() {
            if (!currentUserId) return;
            modalInstance.hide();
            const userName = document.getElementById('id_first_name').value + ' ' + document.getElementById('id_last_name').value;

            // --- Llama al nuevo modal ---
            window.ConfirmationModal.open({
                formAction: `/sigve/users/${currentUserId}/deactivate/`,
                warningText: `¿Estás seguro de DESACTIVAR al usuario ${userName}?`,
                btnClass: 'btn-warning',
                btnText: 'Sí, Desactivar',
                title: 'Confirmar Desactivación'
            });
        }

        function confirmActivate() {
            if (!currentUserId) return;
            modalInstance.hide();
            const userName = document.getElementById('id_first_name').value + ' ' + document.getElementById('id_last_name').value;

            // --- Llama al nuevo modal ---
            window.ConfirmationModal.open({
                formAction: `/sigve/users/${currentUserId}/activate/`,
                warningText: `¿Estás seguro de ACTIVAR al usuario ${userName}?`,
                btnClass: 'btn-success',
                btnText: 'Sí, Activar',
                title: 'Confirmar Activación'
            });
        }

        /**Confirma la eliminación PERMANENTE del usuario */
        function confirmDelete() {
            if (!currentUserId) return;
            modalInstance.hide();
            const userName = document.getElementById('id_first_name').value + ' ' + document.getElementById('id_last_name').value;

            // --- Llama al nuevo modal ---
            window.ConfirmationModal.open({
                formAction: `/sigve/users/${currentUserId}/delete/`,
                warningText: `¡PELIGRO! ¿Estás seguro de ELIMINAR PERMANENTEMENTE a ${userName}? Esta acción no se puede deshacer.`,
                btnClass: 'btn-danger',
                btnText: 'Sí, Eliminar',
                title: 'Confirmar Eliminación'
            });
        }
        
        /** Muestra el spinner de carga */
        function showLoading() {
            loading.style.display = 'block';
            form.style.display = 'none';
        }
        
        /** Oculta el spinner y muestra el formulario */
        function hideLoading() {
            loading.style.display = 'none';
        }
        
        /** Muestra el formulario */
        function showForm() {
            form.style.display = 'block';
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
                'email': 'Por favor, ingresa un correo electrónico válido.',
                'first_name': 'Por favor, ingresa un nombre.',
                'last_name': 'Por favor, ingresa un apellido.',
                'role_id': 'Por favor, selecciona un rol.',
                'password': 'Por favor, ingresa una contraseña (mínimo 8 caracteres).',
                'password_confirm': 'Por favor, confirma la contraseña.'
            };
            
            requiredFields.forEach(field => {
                const fieldName = field.name;
                const fieldValue = field.value.trim();
                
                // Para select, verificar que tenga un valor seleccionado
                if (field.tagName === 'SELECT') {
                    if (!fieldValue || fieldValue === '') {
                        isValid = false;
                        field.classList.add('is-invalid');
                        const errorMsg = errorMessages[fieldName] || 'Este campo es obligatorio.';
                        showFieldError(fieldName, errorMsg);
                    }
                } else if (!fieldValue) {
                    isValid = false;
                    field.classList.add('is-invalid');
                    const errorMsg = errorMessages[fieldName] || 'Este campo es obligatorio.';
                    showFieldError(fieldName, errorMsg);
                }
            });
            
            // Validar contraseñas si estamos en modo crear
            if (currentMode === 'create' && passwordInput && passwordConfirmInput) {
                if (passwordInput.value && passwordInput.value.length < 8) {
                    isValid = false;
                    passwordInput.classList.add('is-invalid');
                    showFieldError('password', 'La contraseña debe tener al menos 8 caracteres.');
                }
                if (passwordInput.value !== passwordConfirmInput.value) {
                    isValid = false;
                    passwordConfirmInput.classList.add('is-invalid');
                    showFieldError('password_confirm', 'Las contraseñas no coinciden.');
                }
            }
            
            if (!isValid) {
                window.SIGVE.showNotification('Por favor, completa todos los campos obligatorios correctamente.', 'error');
            }
            
            return isValid;
        }
        
        /**
         * Limpia todos los errores del formulario
         */
        function clearFormErrors() {
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
         * @param {string} fieldName - Nombre del campo (ej: 'email', 'rut', 'phone')
         * @param {string} errorMessage - Mensaje de error a mostrar
         */
        function showFieldError(fieldName, errorMessage) {
            const fieldIdMap = {
                'email': 'id_email',
                'first_name': 'id_first_name',
                'last_name': 'id_last_name',
                'rut': 'id_rut',
                'phone': 'id_phone',
                'role_id': 'id_role_id',
                'password': 'id_password',
                'password_confirm': 'id_password_confirm'
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
                window.SIGVE.showNotification(errorMessage, 'error');
            }
        }
        
        /** Resetea el modal a su estado inicial */
        function resetModal() {
            currentMode = 'view';
            currentUserId = null;
            form.reset();
            form.classList.remove('was-validated'); // Limpiar validación
            clearFormErrors(); // Limpiar errores
            const isActiveCheckbox = document.getElementById('id_is_active');
            if (isActiveCheckbox) {
                isActiveCheckbox.checked = false;
            }
            setFieldsEnabled(true);
            mutualController?.reset();
            mutualController?.refresh();
            handleRoleChange();
            setPasswordFieldsVisible(false);
            footer.innerHTML = '';
            hideLoading();
            showForm();
        }

        function handleRoleChange() {
            if (!roleSelect) return;
            const selectedOption = roleSelect.selectedOptions[0];
            const roleName = selectedOption?.dataset.roleName || selectedOption?.textContent?.trim();

            if (roleName === ROLE_ADMIN_SIGVE) {
                mutualController?.lockBoth();
            } else if (roleName === ROLE_ADMIN_TALLER || roleName === ROLE_MECANICO) {
                mutualController?.lockFireStation();
            } else if (roleName === ROLE_JEFE_CUARTEL) {
                mutualController?.lockWorkshop();
            } else {
                mutualController?.unlockAll();
            }
        }

        function setPasswordFieldsVisible(visible) {
            if (!passwordRow) return;

            if (visible) {
                passwordRow.classList.remove('d-none');
                if (passwordInput) {
                    passwordInput.required = true;
                    passwordInput.value = '';
                }
                if (passwordConfirmInput) {
                    passwordConfirmInput.required = true;
                    passwordConfirmInput.value = '';
                }
            } else {
                passwordRow.classList.add('d-none');
                if (passwordInput) {
                    passwordInput.required = false;
                    passwordInput.value = '';
                }
                if (passwordConfirmInput) {
                    passwordConfirmInput.required = false;
                    passwordConfirmInput.value = '';
                }
            }
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
            confirmDeactivate,
            confirmActivate,
            confirmDelete
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