/**
 * Script para gestionar solicitudes del taller a SIGVE
 */

// Variables globales que se inicializarán cuando el DOM esté listo
let requestModal, requestForm, dynamicFields, submitBtn, requestTypeDescription, requestDetailsModal;

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    requestModal = document.getElementById('requestModal');
    requestForm = document.getElementById('requestForm');
    dynamicFields = document.getElementById('dynamicFields');
    submitBtn = document.getElementById('submitBtn');
    requestTypeDescription = document.getElementById('requestTypeDescription');
    const requestDetailsModalElement = document.getElementById('requestDetailsModal');
    if (requestDetailsModalElement) {
        requestDetailsModal = new bootstrap.Modal(requestDetailsModalElement);
    }
    
    // Prevenir validación HTML5 nativa del navegador
    if (requestForm) {
        requestForm.addEventListener('invalid', function(e) {
            e.preventDefault();
            // La validación se manejará en handleSubmit
        }, true);
        
        // Evento al enviar el formulario
        requestForm.addEventListener('submit', handleFormSubmit);
        
        // Limpiar errores cuando el usuario empiece a escribir
        setupFieldErrorClearing();
    }
    
    // Agregar event listener al modal cuando se muestra
    if (requestModal) {
        requestModal.addEventListener('shown.bs.modal', function() {
            // Agregar event listener al select de tipo de solicitud cuando el modal se muestra
            const requestTypeSelect = document.getElementById('request_type_id');
            if (requestTypeSelect) {
                // Remover listener anterior si existe
                requestTypeSelect.removeEventListener('change', handleRequestTypeChange);
                // Agregar nuevo listener
                requestTypeSelect.addEventListener('change', handleRequestTypeChange);
            }
        });
        
        // Limpiar errores cuando se cierra el modal
        requestModal.addEventListener('hidden.bs.modal', function() {
            clearFormErrors();
        });
    }
});

/**
 * Maneja el cambio en el select de tipo de solicitud
 */
function handleRequestTypeChange(e) {
    const value = e.target.value;
    console.log('Cambio detectado, valor:', value);
    loadRequestTypeSchema(value);
}

/**
 * Abre el modal para crear una nueva solicitud
 */
function openCreateRequestModal() {
    // Obtener elementos del DOM (por si no están inicializados)
    const form = document.getElementById('requestForm');
    const fields = document.getElementById('dynamicFields');
    const desc = document.getElementById('requestTypeDescription');
    const btn = document.getElementById('submitBtn');
    
    if (form) {
        form.reset();
        clearFormErrors();
    }
    if (fields) fields.innerHTML = '<p class="text-muted text-center py-4"><i class="bi bi-arrow-up"></i> Selecciona un tipo de solicitud para ver los campos disponibles</p>';
    if (desc) desc.textContent = '';
    if (btn) btn.disabled = true;
}

/**
 * Carga el esquema de un tipo de solicitud y genera los campos dinámicamente
 * @param {string} requestTypeId - ID del tipo de solicitud (opcional, si no se pasa se obtiene del select)
 */
function loadRequestTypeSchema(requestTypeId = null) {
    console.log('loadRequestTypeSchema llamada'); // Debug
    
    // Obtener elementos del DOM dentro de la función
    const requestTypeSelect = document.getElementById('request_type_id');
    const fieldsDiv = document.getElementById('dynamicFields');
    const descDiv = document.getElementById('requestTypeDescription');
    const submitButton = document.getElementById('submitBtn');
    
    if (!requestTypeSelect || !fieldsDiv || !descDiv || !submitButton) {
        console.error('Elementos del DOM no encontrados:', {
            requestTypeSelect: !!requestTypeSelect,
            fieldsDiv: !!fieldsDiv,
            descDiv: !!descDiv,
            submitButton: !!submitButton
        });
        return;
    }
    
    // Si no se pasó el ID, obtenerlo del select
    if (!requestTypeId) {
        requestTypeId = requestTypeSelect.value;
    }
    
    console.log('Request Type ID seleccionado:', requestTypeId); // Debug
    
    if (!requestTypeId) {
        fieldsDiv.innerHTML = '<p class="text-muted text-center py-4"><i class="bi bi-arrow-up"></i> Selecciona un tipo de solicitud para ver los campos disponibles</p>';
        descDiv.textContent = '';
        submitButton.disabled = true;
        return;
    }
    
    // Mostrar indicador de carga
    fieldsDiv.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Cargando...</span></div></div>';
    
    console.log('Haciendo fetch a:', `/taller/api/request-types/${requestTypeId}/schema/`); // Debug
    
    // Obtener el esquema del tipo de solicitud
    fetch(`/taller/api/request-types/${requestTypeId}/schema/`)
        .then(async response => {
            // Verificar el Content-Type antes de parsear
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                // Si no es JSON, leer como texto para ver el error
                const text = await response.text();
                console.error('Respuesta no es JSON:', text);
                throw new Error(`El servidor devolvió un error (${response.status}). Revisa la consola para más detalles.`);
            }
            
            if (!response.ok) {
                // Intentar parsear el JSON del error
                try {
                    const errorData = await response.json();
                    throw new Error(errorData.error || `Error HTTP ${response.status}`);
                } catch (e) {
                    throw new Error(`Error HTTP ${response.status}: ${response.statusText}`);
                }
            }
            
            return response.json();
        })
        .then(data => {
            console.log('Respuesta de la API:', data); // Debug
            
            // Obtener elementos nuevamente por si acaso
            const fieldsDiv = document.getElementById('dynamicFields');
            const descDiv = document.getElementById('requestTypeDescription');
            const submitButton = document.getElementById('submitBtn');
            
            if (!fieldsDiv || !descDiv || !submitButton) {
                console.error('Elementos del DOM no encontrados en el callback');
                return;
            }
            
            if (data.success) {
                const requestType = data.request_type;
                
                // Mostrar descripción
                if (requestType.description) {
                    descDiv.textContent = requestType.description;
                } else {
                    descDiv.textContent = '';
                }
                
                // Generar campos dinámicos
                // form_schema puede venir como objeto o como string JSON
                let formSchema = requestType.form_schema;
                if (typeof formSchema === 'string') {
                    try {
                        formSchema = JSON.parse(formSchema);
                    } catch (e) {
                        console.error('Error al parsear form_schema:', e);
                        fieldsDiv.innerHTML = '<div class="alert alert-danger">Error al procesar el esquema del formulario.</div>';
                        submitButton.disabled = true;
                        return;
                    }
                }
                
                console.log('Form schema procesado:', formSchema); // Debug
                
                if (formSchema && formSchema.fields && Array.isArray(formSchema.fields)) {
                    generateDynamicFields(formSchema.fields, fieldsDiv);
                    submitButton.disabled = false;
                } else {
                    console.error('form_schema inválido:', formSchema);
                    fieldsDiv.innerHTML = '<div class="alert alert-warning">Este tipo de solicitud no tiene campos definidos correctamente.</div>';
                    submitButton.disabled = true;
                }
            } else {
                fieldsDiv.innerHTML = '<div class="alert alert-danger">Error al cargar el esquema: ' + (data.error || 'Error desconocido') + '</div>';
                submitButton.disabled = true;
            }
        })
        .catch(error => {
            console.error('Error completo:', error);
            const fieldsDiv = document.getElementById('dynamicFields');
            const submitButton = document.getElementById('submitBtn');
            if (fieldsDiv) {
                fieldsDiv.innerHTML = '<div class="alert alert-danger">Error: ' + error.message + '. Revisa la consola del navegador para más detalles.</div>';
            }
            if (submitButton) {
                submitButton.disabled = true;
            }
        });
}

/**
 * Genera los campos del formulario basándose en el esquema
 */
function generateDynamicFields(fields, containerElement) {
    // Si no se pasa el contenedor, intentar obtenerlo
    if (!containerElement) {
        containerElement = document.getElementById('dynamicFields');
    }
    
    if (!containerElement) {
        console.error('No se pudo encontrar el contenedor para los campos dinámicos');
        return;
    }
    
    let html = '';
    
    console.log('Generando campos para:', fields); // Debug
    
    fields.forEach(field => {
        const isRequired = field.required ? 'required' : '';
        const requiredLabel = field.required ? '<span class="text-danger">*</span>' : '';
        
        html += `<div class="mb-3">`;
        html += `<label for="${field.name}" class="form-label">${field.label} ${requiredLabel}</label>`;
        
        switch (field.type) {
            case 'text':
                html += `<input type="text" class="form-control" id="${field.name}" name="${field.name}" ${isRequired} placeholder="${field.placeholder || ''}">`;
                break;
            case 'number':
                html += `<input type="number" class="form-control" id="${field.name}" name="${field.name}" ${isRequired} placeholder="${field.placeholder || ''}" step="${field.step || '1'}">`;
                break;
            case 'email':
                html += `<input type="email" class="form-control" id="${field.name}" name="${field.name}" ${isRequired} placeholder="${field.placeholder || ''}">`;
                break;
            case 'textarea':
                html += `<textarea class="form-control" id="${field.name}" name="${field.name}" ${isRequired} rows="${field.rows || 3}" placeholder="${field.placeholder || ''}"></textarea>`;
                break;
            case 'select':
                html += `<select class="form-select" id="${field.name}" name="${field.name}" ${isRequired}>`;
                html += `<option value="">-- Seleccionar --</option>`;
                if (field.options) {
                    field.options.forEach(option => {
                        html += `<option value="${option.value}">${option.label}</option>`;
                    });
                }
                html += `</select>`;
                break;
            default:
                html += `<input type="text" class="form-control" id="${field.name}" name="${field.name}" ${isRequired}>`;
        }
        
        // Agregar invalid-feedback para cada campo
        if (field.required) {
            const errorMessage = field.error_message || `Por favor, completa el campo "${field.label}".`;
            html += `<div class="invalid-feedback" data-field-error="${field.name}">${errorMessage}</div>`;
        }
        
        if (field.help) {
            html += `<div class="form-text">${field.help}</div>`;
        }
        
        html += `</div>`;
    });
    
    console.log('HTML generado:', html); // Debug
    containerElement.innerHTML = html;
    
    // Reconfigurar la limpieza de errores para los nuevos campos
    setupFieldErrorClearing();
}

/**
 * Maneja el envío del formulario
 */
function handleFormSubmit(e) {
    e.preventDefault();
    
    if (!requestForm) return;
    
    // Validar formulario manualmente
    if (!validateRequestForm()) {
        return;
    }
    
    if (!submitBtn) return;
    
    // Mostrar indicador de carga
    submitBtn.disabled = true;
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Enviando...';
    
    // Enviar formulario
    const formData = new FormData(requestForm);
    
    fetch(requestForm.action, {
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
            
            // Cerrar modal
            if (requestModal) {
                const modalInstance = bootstrap.Modal.getInstance(requestModal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            }
            
            // Recargar página después de un breve delay
            setTimeout(() => {
                window.location.reload();
            }, 150);
            return;
        } else if (data.errors) {
            // Errores de validación
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
            throw new Error(data.error || 'Error al enviar la solicitud');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        const errorMessage = 'Error al enviar la solicitud: ' + error.message;
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
 * Valida el formulario de solicitud
 * @returns {boolean} true si el formulario es válido, false en caso contrario
 */
function validateRequestForm() {
    if (!requestForm) return false;
    
    clearFormErrors();
    
    let isValid = true;
    const requiredFields = requestForm.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        const fieldName = field.name;
        let fieldValue = field.value;
        
        // Para selects, verificar que tenga un valor seleccionado
        if (field.tagName === 'SELECT') {
            if (!fieldValue || fieldValue === '') {
                isValid = false;
                field.classList.add('is-invalid');
                const errorMsg = getFieldErrorMessage(fieldName) || 'Este campo es obligatorio.';
                showFieldError(fieldName, errorMsg);
            }
        } else {
            // Para inputs y textareas, usar trim
            fieldValue = fieldValue ? fieldValue.trim() : '';
            if (!fieldValue) {
                isValid = false;
                field.classList.add('is-invalid');
                const errorMsg = getFieldErrorMessage(fieldName) || 'Este campo es obligatorio.';
                showFieldError(fieldName, errorMsg);
            }
        }
        
        // Validar email si es un campo de tipo email
        if (field.type === 'email' && fieldValue) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(fieldValue)) {
                isValid = false;
                field.classList.add('is-invalid');
                showFieldError(fieldName, 'Por favor, ingresa un correo electrónico válido.');
            }
        }
    });
    
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
 * Obtiene el mensaje de error para un campo específico
 */
function getFieldErrorMessage(fieldName) {
    const errorMessages = {
        'request_type_id': 'Por favor, selecciona un tipo de solicitud.'
    };
    return errorMessages[fieldName];
}

/**
 * Limpia todos los errores del formulario
 */
function clearFormErrors() {
    if (!requestForm) return;
    
    // Remover clases de error de Bootstrap
    requestForm.querySelectorAll('.is-invalid').forEach(field => {
        field.classList.remove('is-invalid');
    });
    
    // Limpiar mensajes de error dinámicos
    requestForm.querySelectorAll('.invalid-feedback[data-field-error]').forEach(feedback => {
        feedback.textContent = '';
    });
}

/**
 * Muestra un error en un campo específico del formulario
 * @param {string} fieldName - Nombre del campo
 * @param {string} errorMessage - Mensaje de error a mostrar
 */
function showFieldError(fieldName, errorMessage) {
    if (!requestForm) return;
    
    const field = requestForm.querySelector(`[name="${fieldName}"]`);
    
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
    if (!requestForm) return;
    
    // Limpiar errores en campos cuando el usuario empiece a escribir
    requestForm.querySelectorAll('input, select, textarea').forEach(field => {
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
 * Ver detalles completos de una solicitud
 */
function viewRequestDetails(requestId) {
    const requestDetailsContent = document.getElementById('requestDetailsContent');
    
    // Mostrar indicador de carga
    requestDetailsContent.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
            <p class="text-muted mt-2">Cargando detalles de la solicitud...</p>
        </div>
    `;
    
    // Mostrar el modal
    if (requestDetailsModal) {
        requestDetailsModal.show();
    }
    
    // Cargar datos desde la API
    fetch(`/taller/api/requests/${requestId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success && data.request) {
                renderRequestDetails(data.request);
            } else {
                throw new Error(data.error || 'Error al cargar los detalles de la solicitud');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            requestDetailsContent.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle"></i> 
                    Error al cargar los detalles de la solicitud: ${error.message}
                </div>
            `;
        });
}

/**
 * Renderiza los detalles de una solicitud
 */
function renderRequestDetails(request) {
    const requestDetailsContent = document.getElementById('requestDetailsContent');
    
    // Formatear fechas
    const formatDate = (dateString) => {
        if (!dateString) return '—';
        try {
            const date = new Date(dateString);
            return date.toLocaleString('es-CL', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch {
            return dateString;
        }
    };
    
    // Formatear estado
    const getStatusBadge = (status) => {
        const statusMap = {
            'pendiente': '<span class="badge bg-warning text-dark"><i class="bi bi-clock"></i> Pendiente</span>',
            'aprobada': '<span class="badge bg-success"><i class="bi bi-check-circle"></i> Aprobada</span>',
            'rechazada': '<span class="badge bg-danger"><i class="bi bi-x-circle"></i> Rechazada</span>'
        };
        return statusMap[status] || `<span class="badge bg-secondary">${status}</span>`;
    };
    
    // Renderizar datos solicitados
    const renderRequestedData = (requestedData, formSchema) => {
        if (!requestedData || Object.keys(requestedData).length === 0) {
            return '<p class="text-muted mb-0">No hay datos solicitados.</p>';
        }
        
        let html = '<div class="table-responsive"><table class="table table-sm table-bordered">';
        
        // Si hay form_schema, usar los labels de los campos
        const fieldLabels = {};
        if (formSchema && formSchema.fields && Array.isArray(formSchema.fields)) {
            formSchema.fields.forEach(field => {
                fieldLabels[field.name] = field.label || field.name;
            });
        }
        
        for (const [key, value] of Object.entries(requestedData)) {
            const label = fieldLabels[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            html += `
                <tr>
                    <th style="width: 30%;">${label}</th>
                    <td>${value || '—'}</td>
                </tr>
            `;
        }
        
        html += '</table></div>';
        return html;
    };
    
    const html = `
        <dl class="row mb-4">
            <dt class="col-sm-4">ID de Solicitud:</dt>
            <dd class="col-sm-8"><strong>#${request.id}</strong></dd>
            
            <dt class="col-sm-4">Tipo de Solicitud:</dt>
            <dd class="col-sm-8">${request.request_type ? request.request_type.name : '—'}</dd>
            
            <dt class="col-sm-4">Estado:</dt>
            <dd class="col-sm-8">${getStatusBadge(request.status)}</dd>
            
            <dt class="col-sm-4">Solicitante:</dt>
            <dd class="col-sm-8">
                ${request.user_profile 
                    ? `${request.user_profile.first_name} ${request.user_profile.last_name}` 
                    : '—'}
            </dd>
            
            <dt class="col-sm-4">Fecha de Creación:</dt>
            <dd class="col-sm-8">${formatDate(request.created_at)}</dd>
            
            ${request.updated_at && request.updated_at !== request.created_at ? `
            <dt class="col-sm-4">Fecha de Actualización:</dt>
            <dd class="col-sm-8">${formatDate(request.updated_at)}</dd>
            ` : ''}
        </dl>
        
        <hr>
        
        <h6 class="mb-3"><i class="bi bi-file-text"></i> Datos Solicitados</h6>
        ${renderRequestedData(request.requested_data, request.request_type ? request.request_type.form_schema : null)}
        
        ${request.admin_notes ? `
        <hr>
        <h6 class="mb-3"><i class="bi bi-chat-left-text"></i> Comentarios del Administrador</h6>
        <div class="alert ${request.status === 'aprobada' ? 'alert-success' : request.status === 'rechazada' ? 'alert-danger' : 'alert-info'}">
            <div class="d-flex align-items-start">
                <i class="bi bi-person-circle me-2 fs-5"></i>
                <div>
                    <strong>Respuesta del Administrador:</strong>
                    <p class="mb-0 mt-2">${request.admin_notes}</p>
                </div>
            </div>
        </div>
        ` : ''}
    `;
    
    requestDetailsContent.innerHTML = html;
}

