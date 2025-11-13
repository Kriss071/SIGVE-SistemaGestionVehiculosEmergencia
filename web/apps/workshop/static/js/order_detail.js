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


