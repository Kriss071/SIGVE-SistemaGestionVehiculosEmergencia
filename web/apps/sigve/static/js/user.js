/**
 * SIGVE - Lógica de Users (Usuarios)
 *
 * Incluye el controlador del modal de Usuario.
 */

(function() {
    'use strict';

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
        let currentMode = 'view'; // 'view', 'edit'
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
            setTimeout(() => setFieldsEnabled(false), 0);
        }
        
        /**
         * Configura el modal para editar un usuario
         */
        function setupEditMode() {
            titleSpan.textContent = 'Editar Usuario';
            form.action = `/sigve/users/${currentUserId}/edit/`;
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
            document.getElementById('id_rut').value = user.rut || '';
            document.getElementById('id_phone').value = user.phone || '';
            document.getElementById('id_role_id').value = user.role_id || '';
            document.getElementById('id_is_active').checked = user.is_active;
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
                        // Los <select> y <input type="checkbox"> usan 'disabled'
                        if (field.tagName.toLowerCase() === 'select' || field.type === 'checkbox') {
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
                        window.SIGVE.showNotification(data.message || 'Usuario actualizado', 'success');
                        modalInstance.hide();
                        setTimeout(() => window.location.reload(), 1500);
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
            document.getElementById('id_is_active').checked = false; // Reset checkbox
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