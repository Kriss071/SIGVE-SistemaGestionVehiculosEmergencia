/**
 * SIGVE Global Utilities
 * Contiene el objeto global 'SIGVE' para notificaciones,
 * carga de botones y búsqueda en tablas.
 */

window.SIGVE = (function(previousSIGVE = {}) {
    'use strict';

    const TOAST_DEFAULT_DELAY = 5000;
    const PERSISTENT_TOASTS_KEY = 'SIGVE_PENDING_TOASTS';

    const TYPE_CONFIG = {
        success: { bgClass: 'bg-success', icon: 'bi-check-circle', title: 'Éxito' },
        error: { bgClass: 'bg-danger', icon: 'bi-x-circle', title: 'Error' },
        warning: { bgClass: 'bg-warning', icon: 'bi-exclamation-triangle', title: 'Advertencia' },
        info: { bgClass: 'bg-info', icon: 'bi-info-circle', title: 'Información' }
    };

    function getToastContainer() {
        let toastContainer = document.getElementById('toastContainer') || document.querySelector('.toast-container');

        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }

        return toastContainer;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Muestra una notificación toast
     * @param {string} message - El mensaje a mostrar
     * @param {string} type - 'success', 'error', 'warning', 'info'
     * @param {number} delay - Tiempo de vida del toast en milisegundos
     */
    function showNotification(message, type = 'info', delay = TOAST_DEFAULT_DELAY) {
        const toastContainer = getToastContainer();

        const config = TYPE_CONFIG[type] || TYPE_CONFIG.info;
        const toastId = `toast-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;

        const toastHTML = `
            <div id="${toastId}" class="toast align-items-center text-white ${config.bgClass} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="bi ${config.icon} me-2"></i>${escapeHtml(message)}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHTML);

        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay
        });
        toast.show();

        toastElement.addEventListener('hidden.bs.toast', () => toastElement.remove());
    }

    function queueNotification(message, type = 'info', delay = TOAST_DEFAULT_DELAY) {
        try {
            if (!window.sessionStorage) {
                return;
            }

            const rawQueue = window.sessionStorage.getItem(PERSISTENT_TOASTS_KEY);
            const queue = rawQueue ? JSON.parse(rawQueue) : [];

            queue.push({ message, type, delay });
            window.sessionStorage.setItem(PERSISTENT_TOASTS_KEY, JSON.stringify(queue));
        } catch (error) {
            console.warn('SIGVE: No se pudo persistir el toast en sessionStorage.', error);
        }
    }

    function showSuccess(message, delay) {
        showNotification(message, 'success', delay);
    }

    function showError(message, delay) {
        showNotification(message, 'error', delay);
    }

    function showWarning(message, delay) {
        showNotification(message, 'warning', delay);
    }

    function showInfo(message, delay) {
        showNotification(message, 'info', delay);
    }

    function showValidationErrors(errors) {
        if (!errors) return;

        if (typeof errors === 'object') {
            Object.entries(errors).forEach(([field, details]) => {
                if (Array.isArray(details)) {
                    details.forEach(message => showError(`${field}: ${message}`));
                } else {
                    showError(`${field}: ${details}`);
                }
            });
            return;
        }

        showError(errors);
    }

    /**
     * Muestra el estado de carga en un botón
     * @param {HTMLElement} btn - El elemento botón
     */
    function showButtonLoading(btn) {
        if (!btn) return;
        btn.disabled = true;
        
        // Guardar texto original
        if (!btn.dataset.originalText) {
            btn.dataset.originalText = btn.innerHTML;
        }
        
        btn.innerHTML = `
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            Cargando...
        `;
    }

    /**
     * Oculta el estado de carga de un botón
     * @param {HTMLElement} btn - El elemento botón
     */
    function hideButtonLoading(btn) {
        if (!btn) return;
        btn.disabled = false;
        
        // Restaurar texto original
        if (btn.dataset.originalText) {
            btn.innerHTML = btn.dataset.originalText;
        }
    }

    /**
     * Configura la búsqueda en vivo para una tabla
     * @param {string} inputId - ID del input de búsqueda
     * @param {string} tableId - ID de la tabla a filtrar
     */
    function setupTableSearch(inputId, tableId) {
        const searchInput = document.getElementById(inputId);
        const table = document.getElementById(tableId);
        
        if (!searchInput || !table) return;
        
        searchInput.addEventListener('keyup', function() {
            const filter = this.value.toLowerCase();
            const rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
            
            Array.from(rows).forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            });
        });
    }

    function processDjangoMessages() {
        const djangoMessages = document.querySelectorAll('.django-message');
        if (!djangoMessages.length) return;

        const typeMap = {
            error: 'error',
            success: 'success',
            warning: 'warning',
            info: 'info',
            debug: 'info'
        };

        djangoMessages.forEach(messageElement => {
            const type = typeMap[messageElement.dataset.type] || 'info';
            const message = messageElement.textContent.trim();
            if (message) {
                showNotification(message, type);
            }
            messageElement.remove();
        });
    }

    function processQueuedToasts() {
        try {
            if (!window.sessionStorage) {
                return;
            }

            const rawQueue = window.sessionStorage.getItem(PERSISTENT_TOASTS_KEY);
            if (!rawQueue) return;

            const queue = JSON.parse(rawQueue);
            if (!Array.isArray(queue)) {
                window.sessionStorage.removeItem(PERSISTENT_TOASTS_KEY);
                return;
            }

            queue.forEach(({ message, type, delay }) => {
                if (!message) return;
                showNotification(message, type, delay);
            });

            window.sessionStorage.removeItem(PERSISTENT_TOASTS_KEY);
        } catch (error) {
            console.warn('SIGVE: No se pudieron procesar los toasts persistentes.', error);
            try {
                window.sessionStorage.removeItem(PERSISTENT_TOASTS_KEY);
            } catch (_) {
                // Ignorado de forma intencional
            }
        }
    }

    function initializeToastSystem() {
        processDjangoMessages();
        processQueuedToasts();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeToastSystem, { once: true });
    } else {
        initializeToastSystem();
    }
    
    // API Pública
    return Object.assign(previousSIGVE, {
        showNotification,
        showSuccess,
        showError,
        showWarning,
        showInfo,
        showValidationErrors,
        showButtonLoading,
        hideButtonLoading,
        setupTableSearch,
        queueNotification,
        showNotificationAfterReload: queueNotification
    });

})(window.SIGVE);