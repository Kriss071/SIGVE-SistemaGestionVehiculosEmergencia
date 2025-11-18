/**
 * SIGVE - Lógica de Tipos de Solicitudes (Request Types)
 *
 * Incluye el controlador del modal de Tipo de Solicitud y la inicialización
 * de la búsqueda en la lista de tipos de solicitudes.
 */

(function() {
    'use strict';

    /**
     * Sistema de gestión del modal de tipo de solicitud
     * Maneja dos modos: crear, editar
     */
    window.RequestTypeModal = (function() {
        // Referencias a elementos del DOM
        const modal = document.getElementById('requestTypeModal');
        const form = document.getElementById('requestTypeForm');
        const footer = document.getElementById('requestTypeModalFooter');
        const titleSpan = document.getElementById('requestTypeModalTitle');
        
        // Estado actual
        let currentMode = 'create'; // 'create', 'edit'
        let currentRequestTypeId = null;
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
         * @param {string} mode - 'create', 'edit'
         * @param {number} requestTypeId - ID del tipo de solicitud (para edit)
         */
        function open(mode = 'create', requestTypeId = null) {
            currentMode = mode;
            currentRequestTypeId = requestTypeId;
            
            if (mode === 'create') {
                setupCreateMode();
                modalInstance.show();
            } else if (mode === 'edit') {
                modalInstance.show();
                loadRequestTypeData(requestTypeId);
            }
        }
        
        /**
         * Configura el modal para crear un tipo de solicitud
         */
        function setupCreateMode() {
            titleSpan.textContent = 'Nuevo Tipo de Solicitud';
            form.action = '/sigve/request-types/create/';
            form.reset();
            document.getElementById('requestTypeId').value = '';
            setFieldsEnabled(true);
            renderButtons('create');
            clearFormErrors();
        }
        
        /**
         * Carga los datos del tipo de solicitud
         */
        function loadRequestTypeData(requestTypeId) {
    fetch(`/sigve/api/request-types/${requestTypeId}/`)
                .then(response => {
                    if (!response.ok) {
                         throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
        .then(data => {
            if (data.success) {
                        populateForm(data.request_type);
                        setupEditMode();
            } else {
                        throw new Error(data.error || 'Error al cargar el tipo de solicitud');
            }
        })
        .catch(error => {
            console.error('Error:', error);
                    if (window.SIGVE && window.SIGVE.showNotification) {
                        window.SIGVE.showNotification('Error al cargar los datos del tipo de solicitud', 'error');
                    } else {
            alert('Error al cargar los datos del tipo de solicitud.');
                    }
                    modalInstance.hide();
        });
}

/**
         * Configura el modal para editar un tipo de solicitud
         */
        function setupEditMode() {
            titleSpan.textContent = 'Editar Tipo de Solicitud';
            form.action = `/sigve/request-types/${currentRequestTypeId}/update/`;
            renderButtons('edit');
            setFieldsEnabled(true);
            clearFormErrors();
        }
        
        /**
         * Llena el formulario con los datos del tipo de solicitud
         */
        function populateForm(requestType) {
            document.getElementById('requestTypeId').value = requestType.id || '';
            document.getElementById('name').value = requestType.name || '';
            document.getElementById('target_table').value = requestType.target_table || '';
            document.getElementById('description').value = requestType.description || '';
            document.getElementById('form_schema').value = requestType.form_schema || '';
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
            
            if (mode === 'edit') {
                footer.innerHTML = `
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="bi bi-x-lg"></i> Cancelar
                    </button>
                    <button type="submit" class="btn btn-success" id="requestTypeSubmitBtn">
                        <i class="bi bi-check-lg"></i> Guardar Cambios
                    </button>
                `;
            } else if (mode === 'create') {
                footer.innerHTML = `
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="bi bi-x-lg"></i> Cancelar
                    </button>
                    <button type="submit" class="btn btn-primary" id="requestTypeSubmitBtn">
                        <i class="bi bi-check-lg"></i> Guardar
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
                
            const submitBtn = document.getElementById('requestTypeSubmitBtn');
            if (!submitBtn) return;
            
            setButtonLoading(submitBtn, true);
    
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
                // Verificar si la respuesta es JSON válido
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    return response.json();
                } else {
                    // Si no es JSON, puede ser un error HTML
                    throw new Error('La respuesta del servidor no es válida.');
                }
            })
    .then(data => {
                if (data) {
        if (data.success) {
                        setButtonLoading(submitBtn, false);
            modalInstance.hide();
                        setTimeout(() => {
                            window.location.reload();
                        }, 150);
                        return;
                    } else if (data.errors) {
                        clearFormErrors();
                        
                        // Mostrar errores por campo
                        for (const [field, errors] of Object.entries(data.errors)) {
                            // Los errores pueden venir como array o como string
                            let errorMessage;
                            if (Array.isArray(errors) && errors.length > 0) {
                                errorMessage = errors[0];
                            } else if (typeof errors === 'string') {
                                errorMessage = errors;
                            } else {
                                continue;
                            }
                            
                            if (field === 'general' || field === '__all__') {
                                // Error general: mostrar como notificación
                                if (window.SIGVE && window.SIGVE.showNotification) {
                                    window.SIGVE.showNotification(errorMessage, 'error');
                                } else {
                                    alert(errorMessage);
                                }
                            } else {
                                // Error de campo específico: mostrar en el campo
                                showFieldError(field, errorMessage);
                            }
                        }
                        
                        setButtonLoading(submitBtn, false);
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (window.SIGVE && window.SIGVE.showNotification) {
                    window.SIGVE.showNotification('Error al guardar el tipo de solicitud', 'error');
                } else {
                    alert('Error al guardar el tipo de solicitud.');
                }
                setButtonLoading(submitBtn, false);
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
            
            // Mensajes de error en español para campos requeridos (coinciden con forms.py)
            const errorMessages = {
                'name': 'Por favor, ingresa un nombre para el tipo de solicitud.',
                'target_table': 'Por favor, ingresa el nombre de la tabla objetivo.',
                'form_schema': 'Por favor, ingresa un esquema de formulario válido en formato JSON.'
            };
            
            requiredFields.forEach(field => {
                const fieldName = field.name;
                const fieldValue = field.value.trim();
                
                // Validación básica de campos requeridos
                if (!fieldValue) {
                    isValid = false;
                    field.classList.add('is-invalid');
                    const errorMsg = errorMessages[fieldName] || 'Este campo es obligatorio.';
                    showFieldError(fieldName, errorMsg);
                    return;
                }
                
                // Validaciones adicionales del lado del cliente (UX - feedback inmediato)
                // Nota: La validación completa se hace en el servidor (forms.py)
                if (fieldName === 'form_schema' && fieldValue) {
                    try {
                        const parsed = JSON.parse(fieldValue);
                        if (!parsed.fields || !Array.isArray(parsed.fields)) {
                            isValid = false;
                            field.classList.add('is-invalid');
                            showFieldError(fieldName, 'El esquema JSON debe contener un array "fields" con la definición de los campos del formulario.');
                            return;
                        }
                        if (parsed.fields.length === 0) {
                            isValid = false;
                            field.classList.add('is-invalid');
                            showFieldError(fieldName, 'El esquema debe contener al menos un campo en el array "fields".');
                            return;
                        }
                    } catch (e) {
                        isValid = false;
                        field.classList.add('is-invalid');
                        showFieldError(fieldName, 'El esquema debe ser un JSON válido. Verifica la sintaxis (comas, llaves, comillas).');
                        return;
                    }
                } else if (fieldName === 'target_table' && fieldValue) {
                    if (!/^[a-z_][a-z0-9_]*$/.test(fieldValue)) {
                        isValid = false;
                        field.classList.add('is-invalid');
                        showFieldError(fieldName, 'La tabla objetivo debe contener solo letras minúsculas, números y guiones bajos, sin espacios.');
                        return;
                    }
                }
            });
            
            if (!isValid) {
                const message = 'Por favor, completa todos los campos obligatorios correctamente.';
                if (window.SIGVE && window.SIGVE.showNotification) {
                    window.SIGVE.showNotification(message, 'error');
                } else {
                    alert(message);
                }
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
         * @param {string} fieldName - Nombre del campo (ej: 'name', 'target_table', 'form_schema')
         * @param {string} errorMessage - Mensaje de error a mostrar
         */
        function showFieldError(fieldName, errorMessage) {
            // Los IDs de los campos coinciden con sus nombres
            const field = document.getElementById(fieldName);
            
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
         * Helper para manejar el estado del botón de envío
         */
        function setButtonLoading(button, loading) {
            if (window.SIGVE && window.SIGVE.showButtonLoading && window.SIGVE.hideButtonLoading) {
                if (loading) {
                    window.SIGVE.showButtonLoading(button);
                } else {
                    window.SIGVE.hideButtonLoading(button);
                }
            } else {
                if (loading) {
                    button.disabled = true;
                    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Guardando...';
                } else {
                    button.disabled = false;
                    button.innerHTML = '<i class="bi bi-save"></i> Guardar';
                }
            }
        }
        
        /**
         * Resetea el modal a su estado inicial
         */
        function resetModal() {
            currentMode = 'create';
            currentRequestTypeId = null;
            form.reset();
            form.classList.remove('was-validated');
            clearFormErrors();
            setFieldsEnabled(true);
            footer.innerHTML = '';
        }
        
        // Inicializar cuando el DOM esté listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
        } else {
            init();
        }
        
        // API pública
        return {
            open
        };
    })();

    /**
     * Muestra el ejemplo de esquema JSON
     */
    window.showSchemaExample = function() {
        const exampleDiv = document.getElementById('schemaExample');
        const bsCollapse = new bootstrap.Collapse(exampleDiv, {
            toggle: true
        });
    };

    /**
     * Ver el esquema JSON completo de un tipo de solicitud
     */
    window.viewSchema = function(requestTypeId) {
        fetch(`/sigve/api/request-types/${requestTypeId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const schemaContent = document.getElementById('schemaContent');
                    schemaContent.textContent = data.request_type.form_schema;
                    const schemaViewModal = new bootstrap.Modal(document.getElementById('schemaViewModal'));
                    schemaViewModal.show();
                } else {
                    if (window.SIGVE && window.SIGVE.showNotification) {
                        window.SIGVE.showNotification('Error al cargar el esquema: ' + data.error, 'error');
                    } else {
                        alert('Error al cargar el esquema: ' + data.error);
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
                if (window.SIGVE && window.SIGVE.showNotification) {
                    window.SIGVE.showNotification('Error al cargar el esquema.', 'error');
                } else {
                    alert('Error al cargar el esquema.');
                }
            });
    };

    /**
     * Funciones de compatibilidad con el código anterior
     */
    window.openCreateRequestTypeModal = function() {
        if (window.RequestTypeModal) {
            window.RequestTypeModal.open('create');
        }
    };

    window.openEditRequestTypeModal = function(requestTypeId) {
        if (window.RequestTypeModal) {
            window.RequestTypeModal.open('edit', requestTypeId);
        }
    };

    /**
     * Inicialización de la página de lista de Tipos de Solicitudes
     */
    document.addEventListener('DOMContentLoaded', function() {
        // Conectar la búsqueda de la tabla
        if (window.SIGVE && window.SIGVE.setupTableSearch) {
            window.SIGVE.setupTableSearch('tableSearchInput', 'requestTypesTable');
        }
    });

})();
