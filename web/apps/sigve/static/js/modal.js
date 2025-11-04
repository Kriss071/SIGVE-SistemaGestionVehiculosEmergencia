/**
 * SIGVE - Lógica de Modales Genéricos
 *
 * Incluye controladores para modales reutilizables como el de confirmación de eliminación.
 */

(function() {
    'use strict';

    /**
     * Controlador para el Modal de Confirmación de Eliminación
     *
     * Este objeto maneja la apertura del modal de confirmación
     * y la asignación de la URL de acción al formulario de eliminación.
     */
    window.ConfirmationModal = (function() {
        let modalInstance;
        let confirmationForm;
        let confirmBtn;
        let modalEl;
        let modalHeader, modalTitle, modalWarningText, titleIcon;

        /**
         * Inicializa el controlador del modal.
         */
        function init() {
            modalEl = document.getElementById('confirmationModal');
            if (!modalEl) {
                // No hay modal de eliminación en esta página
                return;
            }

            modalInstance = new bootstrap.Modal(modalEl);
            
            // Busca el formulario genérico presente en la página
            confirmationForm = document.getElementById('confirmationForm'); 
            confirmBtn = document.getElementById('confirmationModalConfirmBtn');

            // Elementos de UI dinámicos
            modalHeader = document.getElementById('confirmationModalHeader');
            modalTitle = document.getElementById('confirmationModalTitle');
            modalWarningText = document.getElementById('confirmationModalWarningText');

            if (modalHeader) {
                titleIcon = modalHeader.querySelector('h5 i');
            }

            if (!confirmationForm) console.error('Error: No se encontró el <form id="confirmationForm"> en la página.');
            if (!confirmBtn) console.error('Error: No se encontró el <button id="confirmationModalConfirmBtn">');
            if (!modalTitle) console.error('Error: No se encontró el <span id="confirmationModalTitle">');
            if (!modalWarningText) console.error('Error: No se encontró el <p id="confirmationModalWarningText">');
            
            if (confirmBtn) {
                // Clonamos el botón para eliminar listeners antiguos y asignamos el nuevo
                const newConfirmBtn = confirmBtn.cloneNode(true);
                confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
                confirmBtn = newConfirmBtn;
                confirmBtn.addEventListener('click', handleSubmit);
            }
        }

        /**
         * Abre el modal de confirmación con opciones dinámicas.
         * @param {object} options - Opciones para el modal.
         * @param {string} options.formAction - La URL a la que el formulario debe enviar.
         * @param {string} options.warningText - El mensaje de advertencia.
         * @param {string} [options.title] - (Opcional) El título del modal.
         * @param {string} [options.btnClass] - (Opcional) Clase del botón (ej. 'btn-warning').
         * @param {string} [options.btnText] - (Opcional) Texto del botón (ej. 'Sí, Desactivar').
         */
        function open(options) {
            if (!modalInstance || !confirmationForm || !confirmBtn) {
                console.error('ConfirmationModal no está inicializado.');
                return;
            }
            if (!options || !options.formAction) {
                console.error('ConfirmationModal: Falta el parámetro formAction.');
                return;
            }

            // 1. Definir valores por defecto
            const title = options.title || 'Confirmar Acción';
            const btnClass = options.btnClass || 'btn-danger';
            const btnText = options.btnText || 'Confirmar';
            const icon = (btnClass === 'btn-danger') ? 'bi-trash' : (btnClass === 'btn-warning' ? 'bi-exclamation-triangle-fill' : 'bi-check-circle-fill');
            const bgClass = (btnClass === 'btn-danger') ? 'bg-danger' : (btnClass === 'btn-warning' ? 'bg-warning' : 'bg-success') ;
            // 2. Actualizar la UI del modal
            if (modalHeader) modalHeader.className = `modal-header text-white ${bgClass}`;
            if (modalTitle) modalTitle.textContent = title;
            if (titleIcon) titleIcon.className = `bi ${icon} me-2`;
            if (modalWarningText) modalWarningText.textContent = options.warningText || '¿Estás seguro?';
            
            confirmBtn.className = `btn ${btnClass}`;
            confirmBtn.innerHTML = `<i class="bi bi-check-lg"></i> ${btnText}`;

            // 3. Asignar la acción al formulario
            confirmationForm.action = options.formAction;

            // 4. Mostrar el modal
            modalInstance.show();
        }

        /**
         * Maneja el envío del formulario de eliminación.
         */
        function handleSubmit() {
            // Usar la utilidad global de SIGVE para mostrar carga
            if (window.SIGVE && window.SIGVE.showButtonLoading) {
                window.SIGVE.showButtonLoading(confirmBtn);
            } else {
                confirmBtn.disabled = true;
                confirmBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Enviando...';
            }
            
            // Enviar el formulario
            confirmationForm.submit();
        }

        // Inicializar al cargar el DOM
        document.addEventListener('DOMContentLoaded', init);

        // Exponer la API pública
        return {
            open: open
        };
    })();

})();