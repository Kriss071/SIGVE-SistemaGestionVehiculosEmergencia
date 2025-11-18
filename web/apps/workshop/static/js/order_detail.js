/**
 * SIGVE Workshop - Lógica para Detalle de Orden de Mantención
 * 
 * Maneja la confirmación de finalización de órdenes y validaciones del formulario
 */
(function() {
    'use strict';

    // Elementos del DOM
    let orderForm, orderStatusSelect, saveOrderBtn;
    let confirmModal, confirmModalInstance, confirmBtn;
    let originalStatusValue;
    let completionKeywords = ['termin', 'final', 'complet', 'cerrad'];
    let taskForm, taskFormSubmitBtn;
    let isSubmittingTask = false;
    let exitDateRow, exitDateInput;
    let editObservationsBtn, cancelEditObservationsBtn, observationsDisplay, observationsEdit, observationsForm;
    let partToTaskForm, partToTaskSubmitBtn;
    let isSubmittingPart = false;

    /**
     * Inicialización del controlador
     */
    function init() {
        // Obtener elementos del formulario
        orderForm = document.getElementById('orderUpdateForm');
        orderStatusSelect = document.getElementById('orderStatusSelect');
        saveOrderBtn = document.getElementById('saveOrderBtn');
        exitDateRow = document.getElementById('exitDateRow');
        exitDateInput = document.getElementById('exitDateInput');
        
        // Obtener modal de confirmación
        confirmModal = document.getElementById('confirmCompletionModal');
        confirmBtn = document.getElementById('confirmCompletionBtn');
        
        // Elementos de observaciones
        editObservationsBtn = document.getElementById('editObservationsBtn');
        cancelEditObservationsBtn = document.getElementById('cancelEditObservationsBtn');
        observationsDisplay = document.getElementById('observationsDisplay');
        observationsEdit = document.getElementById('observationsEdit');
        observationsForm = document.getElementById('observationsForm');

        // Verificar que los elementos existan
        if (!orderForm || !orderStatusSelect) {
            console.log('OrderDetail: Formulario no encontrado o orden ya está completada');
            return;
        }

        // Guardar el valor original del estado
        originalStatusValue = orderStatusSelect.value;

        // Inicializar modal
        if (confirmModal) {
            confirmModalInstance = new bootstrap.Modal(confirmModal);
        }

        // Event listeners
        if (orderForm) {
            orderForm.addEventListener('submit', handleFormSubmit);
        }

        if (orderStatusSelect) {
            orderStatusSelect.addEventListener('change', handleStatusChange);
            // Verificar estado inicial solo si la orden no está completada
            // (si está completada, el campo ya está visible en el HTML)
            if (!orderStatusSelect.disabled) {
                handleStatusChange();
            }
        }

        if (confirmBtn) {
            confirmBtn.addEventListener('click', handleConfirmCompletion);
        }

        // Configurar edición de observaciones
        setupObservationsEditing();

        // Configurar protección contra doble envío para el formulario de tareas
        setupTaskFormProtection();

        // Configurar validación para el formulario de agregar repuesto a tarea
        setupPartToTaskFormValidation();

        // Configurar botones de eliminación
        setupDeleteButtons();

        console.log('OrderDetail: Controlador inicializado correctamente');
    }

    /**
     * Verifica si un estado es de "Terminada" basándose en keywords
     */
    function isCompletionStatus(statusName) {
        if (!statusName) return false;
        
        const normalized = statusName.toLowerCase();
        return completionKeywords.some(keyword => normalized.includes(keyword));
    }

    /**
     * Obtiene el nombre del estado seleccionado
     */
    function getSelectedStatusName() {
        const selectedOption = orderStatusSelect.options[orderStatusSelect.selectedIndex];
        return selectedOption ? selectedOption.getAttribute('data-status-name') : '';
    }

    /**
     * Maneja el cambio de estado
     */
    function handleStatusChange() {
        const selectedStatusName = getSelectedStatusName();
        const isCompletion = isCompletionStatus(selectedStatusName);
        
        // Mostrar/ocultar campo de fecha de salida
        if (exitDateRow && exitDateInput) {
            if (isCompletion) {
                exitDateRow.style.display = 'table-row';
                exitDateInput.required = true;
                // Establecer fecha mínima como fecha de ingreso
                const entryDateStr = exitDateInput.getAttribute('data-entry-date');
                if (entryDateStr) {
                    exitDateInput.setAttribute('min', entryDateStr);
                }
            } else {
                exitDateRow.style.display = 'none';
                exitDateInput.required = false;
                exitDateInput.value = '';
            }
        }
    }

    /**
     * Maneja el envío del formulario
     */
    function handleFormSubmit(event) {
        event.preventDefault();
        
        const selectedStatusName = getSelectedStatusName();
        const isCompletion = isCompletionStatus(selectedStatusName);
        
        // Validar que si es estado de finalización, tenga fecha de salida
        if (isCompletion) {
            if (!exitDateInput || !exitDateInput.value) {
                alert('Por favor, ingrese la fecha de salida para finalizar la orden.');
                if (exitDateInput) {
                    exitDateInput.focus();
                }
                return;
            }
            
            // Validar que la fecha de salida no sea anterior a la fecha de ingreso
            const entryDateStr = exitDateInput.getAttribute('data-entry-date');
            if (entryDateStr) {
                const entryDate = new Date(entryDateStr);
                const exitDate = new Date(exitDateInput.value);
                entryDate.setHours(0, 0, 0, 0);
                exitDate.setHours(0, 0, 0, 0);
                if (exitDate < entryDate) {
                    alert('La fecha de salida no puede ser anterior a la fecha de ingreso.');
                    exitDateInput.focus();
                    return;
                }
            }
        }
        
        // Si el estado cambió a "Terminada", mostrar modal de confirmación
        if (isCompletion && orderStatusSelect.value !== originalStatusValue) {
            if (confirmModalInstance) {
                confirmModalInstance.show();
            } else {
                // Fallback: confirmación nativa
                if (confirm('¿Está seguro de marcar esta orden como "' + selectedStatusName + '"? No podrá modificarla después.')) {
                    submitForm();
                }
            }
        } else {
            // Enviar directamente si no es cambio a estado terminado
            submitForm();
        }
    }

    /**
     * Maneja la confirmación desde el modal
     */
    function handleConfirmCompletion() {
        if (confirmModalInstance) {
            confirmModalInstance.hide();
        }
        submitForm();
    }

    /**
     * Envía el formulario
     */
    function submitForm() {
        // Mostrar indicador de carga en el botón
        if (saveOrderBtn) {
            showButtonLoading(saveOrderBtn);
        }

        // Enviar formulario
        orderForm.submit();
    }

    /**
     * Muestra indicador de carga en un botón
     */
    function showButtonLoading(button) {
        if (!button) return;
        
        button.disabled = true;
        button.classList.add('btn-loading');
        
        const originalHtml = button.innerHTML;
        button.setAttribute('data-original-html', originalHtml);
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Guardando...';
    }

    /**
     * Oculta indicador de carga en un botón
     */
    function hideButtonLoading(button) {
        if (!button) return;
        
        button.disabled = false;
        button.classList.remove('btn-loading');
        
        const originalHtml = button.getAttribute('data-original-html');
        if (originalHtml) {
            button.innerHTML = originalHtml;
            button.removeAttribute('data-original-html');
        }
    }

    /**
     * Configura protección contra doble envío para el formulario de tareas
     */
    function setupTaskFormProtection() {
        // Buscar el formulario dentro del modal (puede no estar cargado aún)
        const addTaskModal = document.getElementById('addTaskModal');
        if (!addTaskModal) return;

        // Usar evento de Bootstrap para cuando el modal se muestra
        addTaskModal.addEventListener('shown.bs.modal', function() {
            taskForm = addTaskModal.querySelector('form');
            taskFormSubmitBtn = document.getElementById('addTaskSubmitBtn');

            if (taskForm && taskFormSubmitBtn) {
                // Remover listeners anteriores si existen (clonar el formulario para limpiar listeners)
                const newTaskForm = taskForm.cloneNode(true);
                taskForm.parentNode.replaceChild(newTaskForm, taskForm);
                taskForm = newTaskForm;
                taskFormSubmitBtn = document.getElementById('addTaskSubmitBtn');
                
                // Agregar listener para prevenir doble envío
                taskForm.addEventListener('submit', handleTaskFormSubmit);
                
                // Limpiar errores cuando el usuario empiece a escribir
                setupFieldErrorClearing(taskForm);
                
                isSubmittingTask = false;
            }
        });

        // Resetear el flag cuando el modal se oculta
        addTaskModal.addEventListener('hidden.bs.modal', function() {
            isSubmittingTask = false;
            if (taskFormSubmitBtn) {
                taskFormSubmitBtn.disabled = false;
                const originalHtml = taskFormSubmitBtn.getAttribute('data-original-html');
                if (originalHtml) {
                    taskFormSubmitBtn.innerHTML = originalHtml;
                    taskFormSubmitBtn.removeAttribute('data-original-html');
                }
            }
            // Resetear el formulario y limpiar errores
            if (taskForm) {
                taskForm.reset();
                clearFormErrors(taskForm);
            }
        });
    }

    /**
     * Maneja el envío del formulario de tareas con protección contra doble envío
     */
    function handleTaskFormSubmit(event) {
        // Si ya se está enviando, prevenir el envío
        if (isSubmittingTask) {
            event.preventDefault();
            event.stopPropagation();
            return false;
        }

        // Validar formulario antes de enviar
        if (!validateTaskForm()) {
            event.preventDefault();
            event.stopPropagation();
            return false;
        }

        // Marcar como enviando
        isSubmittingTask = true;

        // Deshabilitar el botón y mostrar indicador de carga
        if (taskFormSubmitBtn) {
            showButtonLoading(taskFormSubmitBtn);
        }

        // Permitir que el formulario se envíe normalmente
        // El flag isSubmittingTask prevendrá envíos adicionales
        return true;
    }

    /**
     * Valida el formulario de tareas y muestra errores en español
     * @returns {boolean} true si el formulario es válido, false en caso contrario
     */
    function validateTaskForm() {
        if (!taskForm) return false;
        
        clearFormErrors(taskForm);
        
        let isValid = true;
        
        // Mensajes de error en español para campos requeridos
        const errorMessages = {
            'task_type_id': 'Por favor, selecciona un tipo de tarea.',
            'cost': 'Por favor, ingresa un costo válido (mínimo 0).'
        };
        
        // Validar tipo de tarea
        const taskTypeField = taskForm.querySelector('[name="task_type_id"]');
        if (taskTypeField && taskTypeField.hasAttribute('required')) {
            const taskTypeValue = taskTypeField.value;
            if (!taskTypeValue || taskTypeValue === '') {
                isValid = false;
                taskTypeField.classList.add('is-invalid');
                showFieldError(taskForm, 'task_type_id', errorMessages['task_type_id']);
            }
        }
        
        // Validar costo
        const costField = taskForm.querySelector('[name="cost"]');
        if (costField && costField.hasAttribute('required')) {
            const costValue = costField.value;
            const numValue = parseFloat(costValue);
            // Validar que sea un número válido y no negativo
            if (costValue === '' || costValue === null || isNaN(numValue) || numValue < 0) {
                isValid = false;
                costField.classList.add('is-invalid');
                showFieldError(taskForm, 'cost', errorMessages['cost']);
            }
        }
        
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
     * Configura validación para el formulario de agregar repuesto a tarea
     */
    function setupPartToTaskFormValidation() {
        partToTaskForm = document.getElementById('addPartToTaskForm');
        partToTaskSubmitBtn = document.getElementById('addPartToTaskSubmitBtn');
        
        if (partToTaskForm && partToTaskSubmitBtn) {
            partToTaskForm.addEventListener('submit', handlePartToTaskFormSubmit);
            
            // Limpiar errores cuando el usuario empiece a escribir
            setupFieldErrorClearing(partToTaskForm);
        }
    }

    /**
     * Configura la limpieza automática de errores cuando el usuario empiece a escribir
     * @param {HTMLElement} form - El formulario a configurar
     */
    function setupFieldErrorClearing(form) {
        if (!form) return;
        
        // Limpiar errores en campos cuando el usuario empiece a escribir
        form.querySelectorAll('input, select, textarea').forEach(field => {
            field.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    this.classList.remove('is-invalid');
                    const feedback = this.parentElement.querySelector(`.invalid-feedback[data-field-error="${this.name}"]`);
                    if (feedback) {
                        feedback.textContent = '';
                    }
                    // Verificar si todos los errores se han limpiado para restaurar alineación
                    checkAndRestoreButtonAlignment(form);
                }
            });
            
            field.addEventListener('change', function() {
                if (this.classList.contains('is-invalid')) {
                    this.classList.remove('is-invalid');
                    const feedback = this.parentElement.querySelector(`.invalid-feedback[data-field-error="${this.name}"]`);
                    if (feedback) {
                        feedback.textContent = '';
                    }
                    // Verificar si todos los errores se han limpiado para restaurar alineación
                    checkAndRestoreButtonAlignment(form);
                }
            });
        });
    }

    /**
     * Verifica si hay errores en el formulario y ajusta la alineación del botón
     * @param {HTMLElement} form - El formulario a verificar
     */
    function checkAndRestoreButtonAlignment(form) {
        if (!form || form.id !== 'addPartToTaskForm') return;
        
        // Verificar si aún hay campos con errores
        const hasErrors = form.querySelectorAll('.is-invalid').length > 0;
        const buttonContainer = document.getElementById('addPartToTaskButtonContainer');
        
        if (buttonContainer) {
            if (hasErrors) {
                // Si aún hay errores, mantener centrado
                buttonContainer.classList.remove('align-items-end');
                buttonContainer.classList.add('align-items-center');
            } else {
                // Si no hay errores, restaurar alineación al final
                buttonContainer.classList.remove('align-items-center');
                buttonContainer.classList.add('align-items-end');
            }
        }
    }

    /**
     * Maneja el envío del formulario de agregar repuesto a tarea
     */
    function handlePartToTaskFormSubmit(event) {
        // Si ya se está enviando, prevenir el envío
        if (isSubmittingPart) {
            event.preventDefault();
            event.stopPropagation();
            return false;
        }

        // Validar formulario antes de enviar
        if (!validatePartToTaskForm()) {
            event.preventDefault();
            event.stopPropagation();
            return false;
        }

        // Marcar como enviando
        isSubmittingPart = true;

        // Deshabilitar el botón y mostrar indicador de carga
        if (partToTaskSubmitBtn) {
            showButtonLoading(partToTaskSubmitBtn);
        }

        return true;
    }

    /**
     * Valida el formulario de agregar repuesto a tarea y muestra errores en español
     * @returns {boolean} true si el formulario es válido, false en caso contrario
     */
    function validatePartToTaskForm() {
        if (!partToTaskForm) return false;
        
        clearFormErrors(partToTaskForm);
        
        let isValid = true;
        
        // Mensajes de error en español para campos requeridos
        const errorMessages = {
            'maintenance_task_id': 'Por favor, selecciona una tarea.',
            'workshop_inventory_id': 'Por favor, selecciona un repuesto del inventario.',
            'quantity_used': 'Por favor, ingresa una cantidad válida (mínimo 1).'
        };
        
        // Validar tarea
        const taskField = partToTaskForm.querySelector('[name="maintenance_task_id"]');
        if (taskField && taskField.hasAttribute('required')) {
            const taskValue = taskField.value;
            if (!taskValue || taskValue === '') {
                isValid = false;
                taskField.classList.add('is-invalid');
                showFieldError(partToTaskForm, 'maintenance_task_id', errorMessages['maintenance_task_id']);
            }
        }
        
        // Validar repuesto
        const inventoryField = partToTaskForm.querySelector('[name="workshop_inventory_id"]');
        if (inventoryField && inventoryField.hasAttribute('required')) {
            const inventoryValue = inventoryField.value;
            if (!inventoryValue || inventoryValue === '') {
                isValid = false;
                inventoryField.classList.add('is-invalid');
                showFieldError(partToTaskForm, 'workshop_inventory_id', errorMessages['workshop_inventory_id']);
            }
        }
        
        // Validar cantidad
        const quantityField = partToTaskForm.querySelector('[name="quantity_used"]');
        if (quantityField && quantityField.hasAttribute('required')) {
            const quantityValue = quantityField.value;
            const numValue = parseInt(quantityValue);
            // Validar que sea un número válido y mayor o igual a 1
            if (quantityValue === '' || quantityValue === null || isNaN(numValue) || numValue < 1) {
                isValid = false;
                quantityField.classList.add('is-invalid');
                showFieldError(partToTaskForm, 'quantity_used', errorMessages['quantity_used']);
            }
        }
        
        // Ajustar alineación del botón según si hay errores
        const buttonContainer = document.getElementById('addPartToTaskButtonContainer');
        if (buttonContainer) {
            if (!isValid) {
                // Si hay errores, centrar verticalmente
                buttonContainer.classList.remove('align-items-end');
                buttonContainer.classList.add('align-items-center');
            } else {
                // Si no hay errores, alinear al final
                buttonContainer.classList.remove('align-items-center');
                buttonContainer.classList.add('align-items-end');
            }
        }
        
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
     * Limpia todos los errores del formulario
     * @param {HTMLElement} form - El formulario a limpiar
     */
    function clearFormErrors(form) {
        if (!form) return;
        
        // Remover clases de error de Bootstrap
        form.querySelectorAll('.is-invalid').forEach(field => {
            field.classList.remove('is-invalid');
        });
        
        // Limpiar mensajes de error dinámicos
        form.querySelectorAll('.invalid-feedback[data-field-error]').forEach(feedback => {
            feedback.textContent = '';
            feedback.style.display = '';
        });
        
        // Remover clase was-validated si existe
        form.classList.remove('was-validated');
        
        // Restaurar alineación del botón del formulario de repuestos
        if (form.id === 'addPartToTaskForm') {
            const buttonContainer = document.getElementById('addPartToTaskButtonContainer');
            if (buttonContainer) {
                buttonContainer.classList.remove('align-items-center');
                buttonContainer.classList.add('align-items-end');
            }
        }
    }

    /**
     * Muestra un error en un campo específico del formulario
     * @param {HTMLElement} form - El formulario que contiene el campo
     * @param {string} fieldName - Nombre del campo (ej: 'task_type_id', 'cost')
     * @param {string} errorMessage - Mensaje de error a mostrar
     */
    function showFieldError(form, fieldName, errorMessage) {
        if (!form) return;
        
        const fieldIdMap = {
            'task_type_id': 'id_task_type_id',
            'description': 'id_description',
            'cost': 'id_cost',
            'maintenance_task_id': 'id_maintenance_task_id',
            'workshop_inventory_id': 'id_workshop_inventory_id',
            'quantity_used': 'id_quantity_used'
        };
        
        const fieldId = fieldIdMap[fieldName] || `id_${fieldName}`;
        const field = document.getElementById(fieldId);
        
        if (field) {
            // Agregar clase de error al campo
            field.classList.add('is-invalid');
            
            // Buscar el elemento de feedback de error
            let feedback = field.parentElement.querySelector(`.invalid-feedback[data-field-error="${fieldName}"]`);
            
            // Si no existe, buscar cualquier invalid-feedback en el mismo contenedor
            if (!feedback) {
                feedback = field.parentElement.querySelector('.invalid-feedback');
            }
            
            // Si aún no existe, crear uno nuevo
            if (!feedback) {
                feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                feedback.setAttribute('data-field-error', fieldName);
                // Insertar después del campo
                field.parentElement.appendChild(feedback);
            } else {
                // Asegurar que tenga el atributo data-field-error
                feedback.setAttribute('data-field-error', fieldName);
            }
            
            // Establecer el mensaje de error
            feedback.textContent = errorMessage;
            feedback.style.display = 'block';
            
            // Asegurar que el formulario tenga la clase was-validated para mostrar los errores
            form.classList.add('was-validated');
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
     * Configura los botones de eliminación de tareas y repuestos
     */
    function setupDeleteButtons() {
        // Botones de eliminar tarea
        document.querySelectorAll('.delete-task-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const deleteUrl = this.getAttribute('data-delete-url');
                const taskType = this.getAttribute('data-task-type');
                
                if (!window.ConfirmationModal) {
                    console.error('ConfirmationModal no está disponible');
                    return;
                }
                
                if (!deleteUrl) {
                    console.error('URL de eliminación no encontrada');
                    return;
                }
                
                window.ConfirmationModal.open({
                    formAction: deleteUrl,
                    warningText: `¿Estás seguro de eliminar la tarea "${taskType}"?`,
                    title: 'Confirmar Eliminación de Tarea',
                    btnClass: 'btn-danger',
                    btnText: 'Sí, Eliminar'
                });
            });
        });

        // Botones de eliminar repuesto
        document.querySelectorAll('.delete-part-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const deleteUrl = this.getAttribute('data-delete-url');
                const partName = this.getAttribute('data-part-name');
                const quantity = this.getAttribute('data-quantity');
                
                if (!window.ConfirmationModal) {
                    console.error('ConfirmationModal no está disponible');
                    return;
                }
                
                if (!deleteUrl) {
                    console.error('URL de eliminación no encontrada');
                    return;
                }
                
                window.ConfirmationModal.open({
                    formAction: deleteUrl,
                    warningText: `¿Eliminar el repuesto "${partName}" (${quantity} unid.)? Se devolverá al inventario.`,
                    title: 'Confirmar Eliminación de Repuesto',
                    btnClass: 'btn-danger',
                    btnText: 'Sí, Eliminar'
                });
            });
        });
    }

    /**
     * Configura la funcionalidad de edición de observaciones
     */
    function setupObservationsEditing() {
        if (!editObservationsBtn || !observationsDisplay || !observationsEdit) return;

        editObservationsBtn.addEventListener('click', function() {
            observationsDisplay.style.display = 'none';
            observationsEdit.style.display = 'block';
            const textarea = document.getElementById('observationsTextarea');
            if (textarea) {
                textarea.focus();
            }
        });

        if (cancelEditObservationsBtn) {
            cancelEditObservationsBtn.addEventListener('click', function() {
                observationsEdit.style.display = 'none';
                observationsDisplay.style.display = 'block';
                // Restaurar valor original desde el display
                const textarea = document.getElementById('observationsTextarea');
                const displayText = observationsDisplay.querySelector('p');
                if (textarea && displayText) {
                    const originalText = displayText.textContent.trim();
                    textarea.value = originalText === 'Sin observaciones' ? '' : originalText;
                }
            });
        }

        // Prevenir doble envío del formulario de observaciones
        if (observationsForm) {
            let isSubmittingObservations = false;
            observationsForm.addEventListener('submit', function(e) {
                if (isSubmittingObservations) {
                    e.preventDefault();
                    return false;
                }
                isSubmittingObservations = true;
                const submitBtn = observationsForm.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Guardando...';
                }
                return true;
            });
        }
    }

    // Inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Exponer API pública si es necesario
    window.OrderDetailController = {
        init: init
    };

})();


