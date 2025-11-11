/**
 * Script para gestionar tipos de solicitudes en SIGVE
 */

// Referencias al modal y formulario
const requestTypeModal = document.getElementById('requestTypeModal');
const requestTypeForm = document.getElementById('requestTypeForm');
const modalErrorAlert = document.getElementById('modalErrorAlert');
const modalErrorList = document.getElementById('modalErrorList');
const schemaViewModal = new bootstrap.Modal(document.getElementById('schemaViewModal'));

/**
 * Abre el modal para crear un nuevo tipo de solicitud
 */
function openCreateRequestTypeModal() {
    // Cambiar título del modal
    document.getElementById('modalTitle').textContent = 'Nuevo Tipo de Solicitud';
    
    // Cambiar acción del formulario
    requestTypeForm.action = '/sigve/request-types/create/';
    
    // Limpiar campos
    document.getElementById('requestTypeId').value = '';
    document.getElementById('name').value = '';
    document.getElementById('target_table').value = '';
    document.getElementById('description').value = '';
    document.getElementById('form_schema').value = '';
    
    // Ocultar errores
    modalErrorAlert.classList.add('d-none');
    modalErrorList.innerHTML = '';
}

/**
 * Abre el modal para editar un tipo de solicitud existente
 */
function openEditRequestTypeModal(requestTypeId) {
    // Cambiar título del modal
    document.getElementById('modalTitle').textContent = 'Editar Tipo de Solicitud';
    
    // Cambiar acción del formulario
    requestTypeForm.action = `/sigve/request-types/${requestTypeId}/update/`;
    
    // Ocultar errores
    modalErrorAlert.classList.add('d-none');
    modalErrorList.innerHTML = '';
    
    // Cargar datos del tipo de solicitud
    fetch(`/sigve/api/request-types/${requestTypeId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const rt = data.request_type;
                document.getElementById('requestTypeId').value = rt.id;
                document.getElementById('name').value = rt.name || '';
                document.getElementById('target_table').value = rt.target_table || '';
                document.getElementById('description').value = rt.description || '';
                // form_schema viene como string JSON formateado
                document.getElementById('form_schema').value = rt.form_schema || '';
            } else {
                alert('Error al cargar el tipo de solicitud: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al cargar los datos del tipo de solicitud.');
        });
}

/**
 * Muestra el ejemplo de esquema JSON
 */
function showSchemaExample() {
    const exampleDiv = document.getElementById('schemaExample');
    const bsCollapse = new bootstrap.Collapse(exampleDiv, {
        toggle: true
    });
}

/**
 * Ver el esquema JSON completo de un tipo de solicitud
 */
function viewSchema(requestTypeId) {
    fetch(`/sigve/api/request-types/${requestTypeId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const schemaContent = document.getElementById('schemaContent');
                schemaContent.textContent = data.request_type.form_schema;
                schemaViewModal.show();
            } else {
                alert('Error al cargar el esquema: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al cargar el esquema.');
        });
}

/**
 * Manejo del envío del formulario (AJAX)
 */
requestTypeForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(requestTypeForm);
    const submitBtn = document.getElementById('submitBtn');
    
    // Deshabilitar botón de envío
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Guardando...';
    
    // Ocultar errores previos
    modalErrorAlert.classList.add('d-none');
    modalErrorList.innerHTML = '';
    
    fetch(requestTypeForm.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Cerrar modal y recargar página
            const modalInstance = bootstrap.Modal.getInstance(requestTypeModal);
            modalInstance.hide();
            
            if (data.reload_page) {
                location.reload();
            }
        } else {
            // Mostrar errores
            modalErrorAlert.classList.remove('d-none');
            modalErrorList.innerHTML = '';
            
            if (data.errors) {
                for (const [field, errors] of Object.entries(data.errors)) {
                    errors.forEach(error => {
                        const li = document.createElement('li');
                        li.textContent = `${field}: ${error}`;
                        modalErrorList.appendChild(li);
                    });
                }
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        modalErrorAlert.classList.remove('d-none');
        modalErrorList.innerHTML = '<li>Error de conexión. Intenta nuevamente.</li>';
    })
    .finally(() => {
        // Rehabilitar botón
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-save"></i> Guardar';
    });
});

