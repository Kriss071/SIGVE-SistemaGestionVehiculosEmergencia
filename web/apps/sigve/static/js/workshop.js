/**
 * SIGVE - Lógica de Workshops
 *
 * Incluye el controlador del modal de Workshop y la inicialización
 * de la búsqueda en la lista de talleres.
 */

(function() {
    'use strict';

    /**
     * Sistema de gestión del modal de taller
     * Maneja tres modos: crear, ver, editar
     */
    window.WorkshopModal = (function() {
        // Referencias a elementos del DOM
        const modal = document.getElementById('workshopModal');
        const form = document.getElementById('workshopForm');
        const loading = document.getElementById('workshopModalLoading');
        const footer = document.getElementById('workshopModalFooter');
        const titleSpan = document.getElementById('workshopModalTitle');
        
        // Estado actual
        let currentMode = 'create'; // 'create', 'view', 'edit'
        let currentWorkshopId = null;
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
         * @param {number} workshopId - ID del taller (para view/edit)
         * @param {string} source - 'dashboard' o 'list' (para saber desde dónde se abre)
         */
        function open(mode = 'create', workshopId = null, source = 'list') {
            currentMode = mode;
            currentWorkshopId = workshopId;
            
            // Guardar la fuente en el formulario para usarla al enviar
            const sourceInput = document.getElementById('workshopSource');
            if (sourceInput) {
                sourceInput.value = source;
            }
            
            if (mode === 'create') {
                setupCreateMode();
            } else if (mode === 'view' || mode === 'edit') {
                showLoading();
                modalInstance.show();
                loadWorkshopData(workshopId, mode);
            }
        }
        
        /**
         * Configura el modal para crear un taller
         */
        function setupCreateMode() {
            titleSpan.textContent = 'Crear Taller';
            form.action = '/sigve/workshops/create/'; // Asegúrate que esta URL sea correcta o usa la variable de Django
            form.reset();
            document.getElementById('workshopId').value = '';
            setFieldsEnabled(true);
            renderButtons('create');
            hideLoading();
            showForm();
            modalInstance.show();
            
            // Inicializar geocodificación
            setupGeocoding();
        }
        
        /**
         * Carga los datos del taller
         */
        function loadWorkshopData(workshopId, mode) {
            fetch(`/sigve/api/workshops/${workshopId}/`)
                .then(response => {
                    if (!response.ok) {
                         throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        populateForm(data.workshop);
                        hideLoading();
                        showForm();
                        
                        // Aplicar el modo después de mostrar el formulario
                        if (mode === 'view') {
                            setupViewMode();
                        } else if (mode === 'edit') {
                            setupEditMode();
                        }
                    } else {
                        throw new Error(data.error || 'Error al cargar el taller');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    // Refactorizado para usar la utilidad global de sigve.js
                    window.SIGVE.showNotification('Error al cargar los datos del taller', 'error');
                    modalInstance.hide();
                });
        }
        
        /**
         * Configura el modal para ver un taller (solo lectura)
         */
        function setupViewMode() {
            titleSpan.textContent = 'Ver Taller';
            renderButtons('view');
            // Usar setTimeout para asegurar que el DOM esté listo
            setTimeout(() => setFieldsEnabled(false), 0);
        }
        
        /**
         * Configura el modal para editar un taller
         */
        function setupEditMode() {
            titleSpan.textContent = 'Editar Taller';
            form.action = `/sigve/workshops/${currentWorkshopId}/edit/`;
            renderButtons('edit');
            // Usar setTimeout para asegurar que el DOM esté listo
            setTimeout(() => {
                setFieldsEnabled(true);
                setupGeocoding();
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
         * Cancela la edición y vuelve al modo vista
         */
        function cancelEdit() {
            if (modalInstance) {
                modalInstance.hide();
            }
        }
        
        /**
         * Llena el formulario con los datos del taller
         */
        function populateForm(workshop) {
            document.getElementById('workshopId').value = workshop.id || '';
            document.getElementById('id_name').value = workshop.name || '';
            
            // Buscar campo de dirección por diferentes IDs posibles
            const addressField = document.getElementById('workshop-address') || document.getElementById('id_address');
            if (addressField) {
                addressField.value = workshop.address || '';
            }
            
            document.getElementById('id_phone').value = workshop.phone || '';
            document.getElementById('id_email').value = workshop.email || '';
            
            // Poblar coordenadas si existen
            const latInput = document.getElementById('workshop-latitude');
            const lonInput = document.getElementById('workshop-longitude');
            if (latInput && workshop.latitude) {
                latInput.value = workshop.latitude;
            }
            if (lonInput && workshop.longitude) {
                lonInput.value = workshop.longitude;
            }
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
                    <button type="button" class="btn btn-danger" onclick="WorkshopModal.confirmDelete()">
                        <i class="bi bi-trash"></i> Eliminar
                    </button>
                    <button type="button" class="btn btn-primary" onclick="WorkshopModal.switchToEditMode()">
                        <i class="bi bi-pencil"></i> Editar
                    </button>
                `;
            } else if (mode === 'edit') {
                footer.innerHTML = `
                    <button type="button" class="btn btn-secondary" onclick="WorkshopModal.cancelEdit()">
                        <i class="bi bi-x-lg"></i> Cancelar
                    </button>
                    <button type="submit" class="btn btn-success" id="workshopSubmitBtn">
                        <i class="bi bi-check-lg"></i> Guardar Cambios
                    </button>
                `;
            } else if (mode === 'create') {
                footer.innerHTML = `
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="bi bi-x-lg"></i> Cancelar
                    </button>
                    <button type="submit" class="btn btn-primary" id="workshopSubmitBtn">
                        <i class="bi bi-check-lg"></i> Guardar Taller
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
                
            const submitBtn = document.getElementById('workshopSubmitBtn');
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
                        let hasErrors = false;
                        for (const [field, errors] of Object.entries(data.errors)) {
                            if (Array.isArray(errors) && errors.length > 0) {
                                hasErrors = true;
                                const errorMessage = errors[0]; // Tomar el primer error del campo
                                
                                if (field === 'general' || field === '__all__') {
                                    // Error general, mostrar como notificación
                                    window.SIGVE.showNotification(errorMessage, 'error');
                                } else {
                                    // Error de campo específico
                                    showFieldError(field, errorMessage);
                                }
                            }
                        }
                        
                        // Si no hay errores de campo específicos pero hay errores generales, mostrar notificación
                        if (!hasErrors && data.errors.general) {
                            window.SIGVE.showNotification(data.errors.general[0], 'error');
                        }
                        
                        window.SIGVE.hideButtonLoading(submitBtn);
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                window.SIGVE.showNotification('Error al guardar el taller', 'error');
                window.SIGVE.hideButtonLoading(submitBtn);
            });
        }
        
        /**
         * Confirma la eliminación del taller
         * REFACTORIZADO para usar el DeleteModal genérico
         */
        function confirmDelete() {
            if (!currentWorkshopId) return;
            
            modalInstance.hide();

            // Abrir el modal de confirmación genérico
            window.ConfirmationModal.open({
                formAction: `/sigve/workshops/${currentWorkshopId}/delete/`,
                warningText: `¿Estás seguro de eliminar el taller ${document.getElementById('id_name').value}?`,
                title: 'Confirmar Eliminación',
                btnClass: 'btn-danger',
                btnText: 'Sí, Eliminar'
            });
        }
        
        /**
         * Muestra el spinner de carga
         */
        function showLoading() {
            loading.style.display = 'block';
            form.style.display = 'none';
        }
        
        /**
         * Oculta el spinner y muestra el formulario
         */
        function hideLoading() {
            loading.style.display = 'none';
        }
        
        /**
         * Muestra el formulario
         */
        function showForm() {
            form.style.display = 'block';
        }
        
        /**
         * Configura la geocodificación para el campo de dirección
         */
        function setupGeocoding() {
            if (window.Geocoding) {
                setTimeout(() => {
                    window.Geocoding.setupAddressGeocoding(
                        'workshop-address',
                        'workshop-latitude',
                        'workshop-longitude'
                    );
                }, 100);
            }
        }
        
        /**
         * Valida el formulario y muestra errores en español
         * @returns {boolean} true si el formulario es válido, false en caso contrario
         */
        function validateForm() {
            // Limpiar errores previos
            clearFormErrors();
            
            let isValid = true;
            const requiredFields = form.querySelectorAll('[required]');
            
            // Mensajes de error en español
            const errorMessages = {
                'name': 'Por favor, ingresa un nombre para el taller.',
                'address': 'Por favor, ingresa una dirección.',
                'phone': 'Por favor, ingresa un número de teléfono válido.',
                'email': 'Por favor, ingresa un correo electrónico válido.'
            };
            
            requiredFields.forEach(field => {
                const fieldName = field.name;
                const fieldValue = field.value.trim();
                
                // Validar campo requerido
                if (!fieldValue) {
                    isValid = false;
                    field.classList.add('is-invalid');
                    const errorMsg = errorMessages[fieldName] || 'Este campo es obligatorio.';
                    showFieldError(fieldName, errorMsg);
                } else {
                    // Validar formato de email si es un campo de email
                    if (field.type === 'email' && fieldValue) {
                        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                        if (!emailRegex.test(fieldValue)) {
                            isValid = false;
                            field.classList.add('is-invalid');
                            showFieldError(fieldName, 'Por favor, ingresa un correo electrónico válido.');
                        }
                    }
                }
            });
            
            // Si el formulario no es válido, mostrar mensaje general
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
            
            // Remover mensajes de error dinámicos (los que tienen data-field-error)
            form.querySelectorAll('.invalid-feedback[data-field-error]').forEach(feedback => {
                // Si el feedback tiene contenido personalizado, limpiarlo pero mantener el elemento
                // Solo removemos si fue creado dinámicamente (sin contenido predeterminado)
                const fieldName = feedback.dataset.fieldError;
                const defaultMessages = {
                    'address': 'Por favor, ingresa una dirección.',
                    'name': 'Por favor, ingresa un nombre para el taller.'
                };
                
                // Si no tiene el mensaje predeterminado, significa que fue creado dinámicamente
                if (!defaultMessages[fieldName] || feedback.textContent.trim() !== defaultMessages[fieldName]) {
                    // Restaurar mensaje predeterminado si existe
                    if (defaultMessages[fieldName]) {
                        feedback.textContent = defaultMessages[fieldName];
                    } else {
                        feedback.textContent = '';
                    }
                }
            });
        }
        
        /**
         * Muestra un error en un campo específico del formulario
         * @param {string} fieldName - Nombre del campo (ej: 'phone', 'email', 'address')
         * @param {string} errorMessage - Mensaje de error a mostrar
         */
        function showFieldError(fieldName, errorMessage) {
            // Mapeo de nombres de campos a IDs de elementos
            const fieldIdMap = {
                'name': 'id_name',
                'phone': 'id_phone',
                'email': 'id_email',
                'address': 'workshop-address' // Este campo puede tener diferentes IDs
            };
            
            let fieldId = fieldIdMap[fieldName];
            if (!fieldId) {
                // Si no está en el mapa, intentar con el prefijo estándar
                fieldId = `id_${fieldName}`;
            }
            
            // Buscar el campo (puede tener diferentes IDs)
            let field = document.getElementById(fieldId);
            if (!field && fieldName === 'address') {
                // Intentar con el ID alternativo
                field = document.getElementById('id_address');
            }
            
            if (field) {
                // Agregar clase de error de Bootstrap
                field.classList.add('is-invalid');
                
                // Buscar el elemento de feedback existente
                let feedback = field.parentElement.querySelector(`.invalid-feedback[data-field-error="${fieldName}"]`);
                if (!feedback) {
                    // Si no existe, buscar cualquier invalid-feedback en el mismo contenedor
                    feedback = field.parentElement.querySelector('.invalid-feedback');
                    if (feedback) {
                        // Agregar el atributo data-field-error si no lo tiene
                        feedback.setAttribute('data-field-error', fieldName);
                    } else {
                        // Crear nuevo elemento de feedback si no existe ninguno
                        feedback = document.createElement('div');
                        feedback.className = 'invalid-feedback';
                        feedback.setAttribute('data-field-error', fieldName);
                        field.parentElement.appendChild(feedback);
                    }
                }
                feedback.textContent = errorMessage;
            } else {
                // Si no se encuentra el campo, mostrar como notificación
                console.warn(`Campo no encontrado para mostrar error: ${fieldName}`);
                window.SIGVE.showNotification(`${fieldName}: ${errorMessage}`, 'error');
            }
        }
        
        /**
         * Resetea el modal a su estado inicial
         */
        function resetModal() {
            currentMode = 'create';
            currentWorkshopId = null;
            form.reset();
            form.classList.remove('was-validated'); // Limpiar validación
            clearFormErrors(); // Limpiar errores
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
            confirmDelete
        };
    })();


    /**
     * Inicialización de la página de lista de Workshops
     */
    document.addEventListener('DOMContentLoaded', function() {
        // Conectar la búsqueda de la tabla
        // Usamos la utilidad global de sigve.js
        if (window.SIGVE && window.SIGVE.setupTableSearch) {
            window.SIGVE.setupTableSearch('tableSearchInput', 'workshopsTable');
        }
    });

})();