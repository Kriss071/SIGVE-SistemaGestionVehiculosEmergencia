/**
 * SIGVE - Lógica de Users (Usuarios)
 *
 * Incluye el controlador del modal de Usuario.
 */

(function() {
    'use strict';

    /**
     * Crea un controlador para bloquear los select de taller y cuartel
     * de forma mutuamente excluyente.
     */
    function createMutualSelectController(workshopSelect, fireStationSelect) {
        if (!workshopSelect || !fireStationSelect) {
            return {
                refresh: () => {},
                reset: () => {}
            };
        }

        const updateState = (clearOnChange = false) => {
            const workshopLocked = workshopSelect.dataset.modalDisabled === 'true';
            const fireLocked = fireStationSelect.dataset.modalDisabled === 'true';

            if (!workshopLocked) {
                workshopSelect.removeAttribute('disabled');
            }
            if (!fireLocked) {
                fireStationSelect.removeAttribute('disabled');
            }

            if (workshopSelect.value) {
                if (clearOnChange && !fireLocked) {
                    fireStationSelect.value = '';
                }
                if (!fireLocked) {
                    fireStationSelect.dataset.mutualDisabled = 'true';
                    fireStationSelect.setAttribute('disabled', 'disabled');
                }
            } else if (!fireLocked) {
                delete fireStationSelect.dataset.mutualDisabled;
                fireStationSelect.removeAttribute('disabled');
            }

            if (fireStationSelect.value) {
                if (clearOnChange && !workshopLocked) {
                    workshopSelect.value = '';
                }
                if (!workshopLocked) {
                    workshopSelect.dataset.mutualDisabled = 'true';
                    workshopSelect.setAttribute('disabled', 'disabled');
                }
            } else if (!workshopLocked) {
                delete workshopSelect.dataset.mutualDisabled;
                workshopSelect.removeAttribute('disabled');
            }
        };

        const onWorkshopChange = () => updateState(true);
        const onFireStationChange = () => updateState(true);

        workshopSelect.addEventListener('change', onWorkshopChange);
        fireStationSelect.addEventListener('change', onFireStationChange);

        return {
            refresh: () => updateState(false),
            reset: () => {
                if (workshopSelect.dataset.modalDisabled !== 'true') {
                    workshopSelect.value = '';
                    delete workshopSelect.dataset.mutualDisabled;
                    workshopSelect.removeAttribute('disabled');
                }
                if (fireStationSelect.dataset.modalDisabled !== 'true') {
                    fireStationSelect.value = '';
                    delete fireStationSelect.dataset.mutualDisabled;
                    fireStationSelect.removeAttribute('disabled');
                }
            }
        };
    }

    /**
     * Modal para la creación de usuarios.
     */
    window.UserCreateModal = (function() {
        const modal = document.getElementById('userCreateModal');
        const form = document.getElementById('userCreateForm');
        const loading = document.getElementById('userCreateModalLoading');
        const submitBtn = document.getElementById('userCreateSubmitBtn');
        let modalInstance = null;
        let mutualController = null;

        function init() {
            if (!modal || !form) {
                return;
            }

            modalInstance = new bootstrap.Modal(modal);
            modal.addEventListener('hidden.bs.modal', resetModal);
            form.addEventListener('submit', handleSubmit);

            mutualController = createMutualSelectController(
                document.getElementById('id_create_workshop_id'),
                document.getElementById('id_create_fire_station_id')
            );
        }

        function open(source = 'list') {
            if (!modalInstance) {
                return;
            }
            const sourceInput = document.getElementById('userCreateSource');
            if (sourceInput) {
                sourceInput.value = source;
            }

            hideLoading();
            form.style.display = 'block';
            mutualController?.refresh();
            modalInstance.show();
        }

        function handleSubmit(event) {
            event.preventDefault();
            if (!submitBtn) {
                return;
            }

            const passwordField = document.getElementById('id_create_password');
            const confirmField = document.getElementById('id_create_password_confirm');

            if (passwordField && confirmField && passwordField.value !== confirmField.value) {
                window.SIGVE?.showNotification('Las contraseñas no coinciden.', 'warning');
                confirmField.focus();
                return;
            }

            window.SIGVE?.showButtonLoading(submitBtn);
            showLoading();

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
                if (!data) {
                    return;
                }

                if (data.success) {
                    window.SIGVE?.hideButtonLoading(submitBtn);
                    modalInstance.hide();
                    setTimeout(() => window.location.reload(), 150);
                } else if (data.errors) {
                    const firstError = Object.values(data.errors)[0][0];
                    window.SIGVE?.showNotification(firstError, 'error');
                    window.SIGVE?.hideButtonLoading(submitBtn);
                    hideLoading();
                } else {
                    window.SIGVE?.showNotification('Error desconocido al crear el usuario.', 'error');
                    window.SIGVE?.hideButtonLoading(submitBtn);
                    hideLoading();
                }
            })
            .catch(error => {
                console.error('Error creando usuario:', error);
                window.SIGVE?.showNotification('Error al crear el usuario.', 'error');
                window.SIGVE?.hideButtonLoading(submitBtn);
                hideLoading();
            });
        }

        function showLoading() {
            if (loading) {
                loading.style.display = 'block';
            }
            if (form) {
                form.style.display = 'none';
            }
        }

        function hideLoading() {
            if (loading) {
                loading.style.display = 'none';
            }
        }

        function resetModal() {
            form?.reset();
            form?.classList.remove('was-validated');
            hideLoading();
            if (form) {
                form.style.display = 'block';
            }
            const activeCheckbox = document.getElementById('id_create_is_active');
            if (activeCheckbox) {
                activeCheckbox.checked = true;
            }
            mutualController?.reset();
            mutualController?.refresh();
            window.SIGVE?.hideButtonLoading(submitBtn);
        }

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
        } else {
            init();
        }

        return {
            open
        };
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
        const workshopSelect = document.getElementById('id_workshop_id');
        const fireStationSelect = document.getElementById('id_fire_station_id');
        
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

            mutualController = createMutualSelectController(workshopSelect, fireStationSelect);
        }
        
        /**
         * Abre el modal en el modo especificado
         * @param {string} mode - 'view', 'edit'
         * @param {string} userId - ID del usuario (UUID)
         * @param {string} source - 'dashboard' o 'list'
         */
        function open(mode = 'view', userId = null, source = 'list') {
            if (!userId) return;

            currentMode = mode;
            currentUserId = userId;
            
            const sourceInput = document.getElementById('userSource');
            if (sourceInput) {
                sourceInput.value = source;
            }
            
            showLoading();
            modalInstance.show();
            loadUserData(userId, mode);
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
        
        /**
         * Configura el modal para ver un usuario (solo lectura)
         */
        function setupViewMode() {
            titleSpan.textContent = 'Ver Usuario';
            renderButtons('view');
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
                        delete field.dataset.modalDisabled;
                        if (field.tagName.toLowerCase() === 'select' || field.type === 'checkbox') {
                            field.removeAttribute('disabled');
                        }
                    } else {
                        // Los <select> y <input type="checkbox"> usan 'disabled'
                        if (field.tagName.toLowerCase() === 'select' || field.type === 'checkbox') {
                            field.setAttribute('disabled', 'disabled');
                            field.dataset.modalDisabled = 'true';
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
            }
        }
        
        /**
         * Maneja el envío del formulario
         */
        function handleSubmit(e) {
            e.preventDefault();
                
            const submitBtn = document.getElementById('userSubmitBtn');
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
        
        /** Resetea el modal a su estado inicial */
        function resetModal() {
            currentMode = 'view';
            currentUserId = null;
            form.reset();
            form.classList.remove('was-validated');
            const isActiveCheckbox = document.getElementById('id_is_active');
            if (isActiveCheckbox) {
                isActiveCheckbox.checked = false;
            }
            setFieldsEnabled(true);
            mutualController?.reset();
            mutualController?.refresh();
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