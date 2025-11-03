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
    window.DeleteModal = (function() {
        let modalInstance;
        let deleteForm;
        let confirmBtn;
        let modalEl;

        /**
         * Inicializa el controlador del modal de eliminación.
         */
        function init() {
            modalEl = document.getElementById('deleteConfirmationModal');
            if (!modalEl) {
                // No hay modal de eliminación en esta página
                return;
            }

            modalInstance = new bootstrap.Modal(modalEl);
            
            // Busca el formulario de eliminación genérico presente en la página
            deleteForm = document.getElementById('deleteForm'); 
            confirmBtn = document.getElementById('confirmDeleteBtn');

            if (!deleteForm) {
                console.error('Error: No se encontró el <form id="deleteForm"> en la página.');
            }
            if (!confirmBtn) {
                console.error('Error: No se encontró el <button id="confirmDeleteBtn"> en el modal.');
            }
        }

        /**
         * Abre el modal de confirmación.
         * @param {object} options - Opciones de configuración.
         * @param {string} options.formAction - La URL a la que el formulario debe enviar.
         * @param {string} [options.itemName] - Nombre del ítem a eliminar (opcional).
         * @param {string} [options.warningText] - Texto de advertencia personalizado (opcional).
         */
        function open(options) {
            if (!modalInstance || !deleteForm || !confirmBtn || !options.formAction) {
                console.error('DeleteModal no está inicializado o falta la URL de acción (formAction).');
                return;
            }

            // 1. Configurar el contenido del modal
            const itemNameEl = document.getElementById('deleteModalItemName');
            const warningEl = document.getElementById('deleteModalWarning');
            
            if (itemNameEl) {
                itemNameEl.textContent = options.itemName || 'Este ítem';
                itemNameEl.style.display = options.itemName ? 'block' : 'none';
            }
            if (warningEl) {
                warningEl.textContent = options.warningText || 'Esta acción no se puede deshacer.';
            }

            // 2. Asignar la acción al formulario
            deleteForm.action = options.formAction;
            
            // 3. Limpiar y re-asignar el evento click para evitar duplicados
            // Clonamos el botón para eliminar listeners antiguos
            const newConfirmBtn = confirmBtn.cloneNode(true);
            confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
            confirmBtn = newConfirmBtn;
            
            confirmBtn.addEventListener('click', handleSubmit);

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
                confirmBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Eliminando...';
            }
            
            // Enviar el formulario
            deleteForm.submit();
        }

        // Inicializar al cargar el DOM
        document.addEventListener('DOMContentLoaded', init);

        // Exponer la API pública
        return {
            open: open
        };
    })();

})();