/**
 * Utilidades globales complementarias para SIGVE.
 * Este archivo depende de que `messages.js` haya inicializado `window.SIGVE`.
 */

(function(global) {
    'use strict';

    const SIGVE = Object.assign(global.SIGVE || {}, {});

    function notify(message, type = 'info', delay) {
        if (typeof SIGVE.showNotification !== 'function') {
            console.warn('SIGVE: showNotification no está disponible.');
            return;
        }
        const options = {};
        if (typeof delay === 'number') {
            options.autoDismiss = delay;
        }
        SIGVE.showNotification(message, type, options);
    }

    function showSuccess(message, delay) {
        notify(message, 'success', delay);
    }

    function showError(message, delay) {
        notify(message, 'error', delay);
    }

    function showWarning(message, delay) {
        notify(message, 'warning', delay);
    }

    function showInfo(message, delay) {
        notify(message, 'info', delay);
    }

    function queueNotification(message, type = 'info', delay) {
        if (typeof SIGVE.queueNotification === 'function') {
            SIGVE.queueNotification(message, type, { autoDismiss: delay });
        }
    }

    function showValidationErrors(errors) {
        if (!errors) {
            return;
        }
        if (typeof errors === 'object') {
            Object.entries(errors).forEach(([field, details]) => {
                if (Array.isArray(details)) {
                    details.forEach(msg => showError(`${field}: ${msg}`));
                } else {
                    showError(`${field}: ${details}`);
                }
            });
            return;
        }
        showError(errors);
    }

    Object.assign(SIGVE, {
        showSuccess,
        showError,
        showWarning,
        showInfo,
        showValidationErrors,
        queueNotification,
        showNotificationAfterReload: queueNotification
    });

    global.SIGVE = SIGVE;
})(window);