/**
 * Fire Station - Requests List JavaScript
 * 
 * Incluye el controlador del modal de solicitudes y la inicialización
 * de la búsqueda en la lista de solicitudes.
 */

(function() {
    'use strict';

    /**
     * Sistema de gestión del modal de solicitud
     */
    window.RequestModal = (function() {
        // Referencias a elementos del DOM
        const modal = document.getElementById('requestModal');
        const form = document.getElementById('requestForm');
        
        // Estado actual
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
        }
        
        /**
         * Abre el modal
         * @param {string} mode - 'create'
         */
        function open(mode = 'create') {
            if (mode === 'create') {
                form.reset();
                modalInstance.show();
            }
        }
        
        /**
         * Maneja el envío del formulario
         */
        function handleSubmit(e) {
            e.preventDefault();
            
            // Validar formulario
            if (!form.checkValidity()) {
                e.stopPropagation();
                form.classList.add('was-validated');
                return;
            }
            
            const submitBtn = document.getElementById('requestSubmitBtn');
            if (!submitBtn) return;
            
            if (window.SIGVE && window.SIGVE.showButtonLoading) {
                window.SIGVE.showButtonLoading(submitBtn);
            }
            
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
                        if (window.SIGVE && window.SIGVE.hideButtonLoading) {
                            window.SIGVE.hideButtonLoading(submitBtn);
                        }
                        modalInstance.hide();
                        setTimeout(() => window.location.reload(), 150);
                        return;
                    } else if (data.errors) {
                        const firstError = Object.values(data.errors)[0][0];
                        if (window.SIGVE && window.SIGVE.showNotification) {
                            window.SIGVE.showNotification(firstError, 'error');
                        }
                        if (window.SIGVE && window.SIGVE.hideButtonLoading) {
                            window.SIGVE.hideButtonLoading(submitBtn);
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (window.SIGVE && window.SIGVE.showNotification) {
                    window.SIGVE.showNotification('Error al crear la solicitud', 'error');
                }
                if (window.SIGVE && window.SIGVE.hideButtonLoading) {
                    window.SIGVE.hideButtonLoading(submitBtn);
                }
            });
        }
        
        /**
         * Resetea el modal a su estado inicial
         */
        function resetModal() {
            form.reset();
            form.classList.remove('was-validated');
        }
        
        // Inicializar
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
     * Inicialización de la página de lista de Solicitudes
     */
    document.addEventListener('DOMContentLoaded', function() {
        // Conectar la búsqueda de la tabla
        if (window.SIGVE && window.SIGVE.setupTableSearch) {
            window.SIGVE.setupTableSearch('tableSearchInput', 'requestsTable');
        }
    });

})();

