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

    /**
     * Inicialización del controlador
     */
    function init() {
        // Obtener elementos del formulario
        orderForm = document.getElementById('orderUpdateForm');
        orderStatusSelect = document.getElementById('orderStatusSelect');
        saveOrderBtn = document.getElementById('saveOrderBtn');
        
        // Obtener modal de confirmación
        confirmModal = document.getElementById('confirmCompletionModal');
        confirmBtn = document.getElementById('confirmCompletionBtn');

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

        if (confirmBtn) {
            confirmBtn.addEventListener('click', handleConfirmCompletion);
        }

        // Configurar protección contra doble envío para el formulario de tareas
        setupTaskFormProtection();

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
     * Maneja el envío del formulario
     */
    function handleFormSubmit(event) {
        event.preventDefault();
        
        const selectedStatusName = getSelectedStatusName();
        const isCompletion = isCompletionStatus(selectedStatusName);
        
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
            // Resetear el formulario
            if (taskForm) {
                taskForm.reset();
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


