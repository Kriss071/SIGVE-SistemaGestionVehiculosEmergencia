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
    
    if (form) form.reset();
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
        
        if (field.help) {
            html += `<div class="form-text">${field.help}</div>`;
        }
        
        html += `</div>`;
    });
    
    console.log('HTML generado:', html); // Debug
    containerElement.innerHTML = html;
}

/**
 * Ver detalles completos de una solicitud
 * Los datos se cargarían desde la API o se pasarían desde el template
 */
function viewRequestDetails(requestId) {
    const requestDetailsContent = document.getElementById('requestDetailsContent');
    requestDetailsContent.innerHTML = `
        <dl class="row">
            <dt class="col-sm-4">ID de Solicitud:</dt>
            <dd class="col-sm-8">#${requestId}</dd>
            <dt class="col-sm-4">Información:</dt>
            <dd class="col-sm-8">
                <div class="alert alert-info mb-0">
                    Los detalles completos de la solicitud se mostrarán aquí.
                    <br>Por ahora, revisa la tabla principal para ver el estado de tus solicitudes.
                </div>
            </dd>
        </dl>
    `;
    requestDetailsModal.show();
}

