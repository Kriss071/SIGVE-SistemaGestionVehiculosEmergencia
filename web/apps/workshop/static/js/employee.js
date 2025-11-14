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
            setTimeout(() => setFieldsEnabled(false), 0);
        }
        
        /**
         * Configura el modal para editar un empleado
         */
        function setupEditMode() {
            titleSpan.textContent = 'Editar Empleado';
            form.action = `/taller/employees/${currentEmployeeId}/update/`;
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
            
            // Checkbox is_active
            const isActiveCheckbox = document.getElementById('id_is_active');
            if (isActiveCheckbox) {
                isActiveCheckbox.checked = employee.is_active;
            }
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
                        field.setAttribute('readonly', 'readonly');
                    }
                }
            });
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
            footer.innerHTML = '';
            
            if (mode === 'view') {
                footer.innerHTML = `
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="bi bi-x-lg"></i> Cerrar
                    </button>
                    <button type="button" class="btn btn-primary" onclick="EmployeeModal.switchToEditMode()" id="editBtn">
                        <i class="bi bi-pencil"></i> Editar
                    </button>
                `;
            } else if (mode === 'edit') {
                footer.innerHTML = `
                    <button type="button" class="btn btn-secondary" onclick="EmployeeModal.cancelEdit()">
                        <i class="bi bi-x-lg"></i> Cancelar
                    </button>
                    <button type="submit" class="btn btn-success" id="employeeSubmitBtn">
                        <i class="bi bi-check-lg"></i> Guardar Cambios
                    </button>
                `;
            } else if (mode === 'create') {
                footer.innerHTML = `
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="bi bi-x-lg"></i> Cancelar
                    </button>
                    <button type="submit" class="btn btn-primary" id="employeeSubmitBtn">
                        <i class="bi bi-check-lg"></i> Crear Empleado
                    </button>
                `;
            }
        }
        
        /**
         * Maneja el envío del formulario
         */
        function handleSubmit(e) {
            e.preventDefault();
                
            const submitBtn = document.getElementById('employeeSubmitBtn');
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
                    return null;
                } else {
                    return response.json();
                }
            })
            .then(data => {
                if (!data) return; // Ya se manejó la redirección
                
                if (data.success === false) {
                    // Manejar errores específicos del servidor
                    if (data.errors) {
                        let errorMessage = '';
                        if (data.errors.general) {
                            errorMessage = data.errors.general.join('\n');
                        } else {
                            // Mostrar errores de campos
                            for (const [field, errors] of Object.entries(data.errors)) {
                                errorMessage += `${field}: ${errors.join(', ')}\n`;
                            }
                        }
                        throw new Error(errorMessage || 'Error al guardar');
                    }
                    throw new Error(data.error || 'Error al guardar');
                }
                
                // Si todo está bien, recargar la página
                if (data.reload_page) {
                    window.location.reload();
                } else {
                    window.location.reload();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error al guardar el empleado: ' + error.message);
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
            currentEmployeeId = null;
            showPasswordFields(true);
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

