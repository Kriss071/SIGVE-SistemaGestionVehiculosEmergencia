/**
 * SIGVE - Lógica de Repuestos (Spare Parts)
 *
 * Incluye el controlador del modal de Repuesto y la inicialización
 * de la búsqueda en la lista de repuestos.
 */

(function() {
    'use strict';

    /**
     * Sistema de gestión del modal de repuesto
     * Maneja tres modos: crear, ver, editar
     */
    window.SparePartModal = (function() {
        // Referencias a elementos del DOM
        const modal = document.getElementById('sparePartModal');
        const form = document.getElementById('sparePartForm');
        const loading = document.getElementById('sparePartModalLoading');
        const footer = document.getElementById('sparePartModalFooter');
        const titleSpan = document.getElementById('sparePartModalTitle');
        
        // Estado actual
        let currentMode = 'create'; // 'create', 'view', 'edit'
        let currentSparePartId = null;
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
        }
        
        /**
         * Abre el modal en el modo especificado
         * @param {string} mode - 'create', 'view', 'edit'
         * @param {number} sparePartId - ID del repuesto (para view/edit)
         * @param {string} source - 'dashboard' o 'list'
         */
        function open(mode = 'create', sparePartId = null, source = 'list') {
            currentMode = mode;
            currentSparePartId = sparePartId;
            
            const sourceInput = document.getElementById('sparePartSource');
            if (sourceInput) {
                sourceInput.value = source;
            }
            
            if (mode === 'create') {
                setupCreateMode();
            } else if (mode === 'view' || mode === 'edit') {
                showLoading();
                modalInstance.show();
                loadSparePartData(sparePartId, mode);
            }
        }
        
        /**
         * Configura el modal para crear un repuesto
         */
        function setupCreateMode() {
            titleSpan.textContent = 'Crear Repuesto';
            form.action = '/sigve/spare-parts/create/';
            form.reset();
            document.getElementById('sparePartId').value = '';
            setFieldsEnabled(true);
            renderButtons('create');
            hideLoading();
            showForm();
            modalInstance.show();
        }
        
        /**
         * Carga los datos del repuesto
         */
        function loadSparePartData(sparePartId, mode) {
            fetch(`/sigve/api/spare-parts/${sparePartId}/`)
                .then(response => {
                    if (!response.ok) {
                         throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        populateForm(data.spare_part);
                        hideLoading();
                        showForm();
                        
                        if (mode === 'view') {
                            setupViewMode();
                        } else if (mode === 'edit') {
                            setupEditMode();
                        }
                    } else {
                        throw new Error(data.error || 'Error al cargar el repuesto');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    window.SIGVE.showNotification('Error al cargar los datos del repuesto', 'error');
                    modalInstance.hide();
                });
        }
        
        /**
         * Configura el modal para ver un repuesto (solo lectura)
         */
        function setupViewMode() {
            titleSpan.textContent = 'Ver Repuesto';
            renderButtons('view');
            setTimeout(() => setFieldsEnabled(false), 0);
        }
        
        /**
         * Configura el modal para editar un repuesto
         */
        function setupEditMode() {
            titleSpan.textContent = 'Editar Repuesto';
            form.action = `/sigve/spare-parts/${currentSparePartId}/edit/`;
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
         * Llena el formulario con los datos del repuesto
         */
        function populateForm(sparePart) {
            document.getElementById('sparePartId').value = sparePart.id || '';
            document.getElementById('id_name').value = sparePart.name || '';
            document.getElementById('id_sp_sku').value = sparePart.sku || '';
            document.getElementById('id_sp_brand').value = sparePart.brand || '';
            document.getElementById('id_sp_description').value = sparePart.description || '';
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
                        // 'disabled' es mejor para 'select' en modo readonly
                        if (field.tagName === 'SELECT') {
                            field.setAttribute('disabled', 'disabled');
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
                footer.innerHTML = `
                    <button type="button" class="btn btn-outline-danger" onclick="SparePartModal.confirmDelete()">
                        <i class="bi bi-trash"></i> Eliminar
                    </button>
                    <button type="button" class="btn btn-success" onclick="SparePartModal.switchToEditMode()">
                        <i class="bi bi-pencil"></i> Editar
                    </button>
                `;
            } else if (mode === 'edit') {
                footer.innerHTML = `
                    <button type="button" class="btn btn-secondary" onclick="SparePartModal.cancelEdit()">
                        <i class="bi bi-x-lg"></i> Cancelar
                    </button>
                    <button type="submit" class="btn btn-success" id="sparePartSubmitBtn">
                        <i class="bi bi-check-lg"></i> Guardar Cambios
                    </button>
                `;
            } else if (mode === 'create') {
                footer.innerHTML = `
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="bi bi-x-lg"></i> Cancelar
                    </button>
                    <button type="submit" class="btn btn-success" id="sparePartSubmitBtn">
                        <i class="bi bi-check-lg"></i> Guardar Repuesto
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
                
            const submitBtn = document.getElementById('sparePartSubmitBtn');
            if (!submitBtn) return;
            
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
                window.SIGVE.showNotification('Error al guardar el repuesto', 'error');
                window.SIGVE.hideButtonLoading(submitBtn);
            });
        }
        
        /**
         * Confirma la eliminación del repuesto (usando DeleteModal)
         */
        function confirmDelete() {
            if (!currentSparePartId) return;

            modalInstance.hide();
            
            window.ConfirmationModal.open({
                formAction: `/sigve/spare-parts/${currentSparePartId}/delete/`,
                warningText: `¿Estás seguro de eliminar el repuesto ${document.getElementById('id_name').value}?`,
                title: 'Confirmar Eliminación',
                btnClass: 'btn-danger',
                btnText: 'Sí, Eliminar'
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
         * Valida el formulario y muestra errores en español
         * @returns {boolean} true si el formulario es válido, false en caso contrario
         */
        function validateForm() {
            clearFormErrors();
            
            let isValid = true;
            const requiredFields = form.querySelectorAll('[required]');
            
            // Mensajes de error en español para campos requeridos
            const errorMessages = {
                'name': 'Por favor, ingresa un nombre para el repuesto.',
                'sku': 'Por favor, ingresa un SKU.'
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
            
            if (!isValid) {
                window.SIGVE.showNotification('Por favor, completa todos los campos obligatorios.', 'error');
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
         * @param {string} fieldName - Nombre del campo (ej: 'name', 'sku')
         * @param {string} errorMessage - Mensaje de error a mostrar
         */
        function showFieldError(fieldName, errorMessage) {
            const fieldIdMap = {
                'name': 'id_name',
                'sku': 'id_sp_sku'
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
        
        /**
         * Resetea el modal a su estado inicial
         */
        function resetModal() {
            currentMode = 'create';
            currentSparePartId = null;
            form.reset();
            form.classList.remove('was-validated'); // Limpiar validación
            clearFormErrors(); // Limpiar errores
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
            cancelEdit,
            confirmDelete
        };
    })();


    /**
     * Inicialización de la página de lista de Repuestos
     */
    document.addEventListener('DOMContentLoaded', function() {
        // Conectar la búsqueda de la tabla
        if (window.SIGVE && window.SIGVE.setupTableSearch) {
            window.SIGVE.setupTableSearch('tableSearchInput', 'sparePartsTable');
        }
    });

})();

