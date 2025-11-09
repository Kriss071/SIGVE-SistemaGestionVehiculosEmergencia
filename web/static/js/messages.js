(() => {
    const STORAGE_KEY = 'SIGVE_PENDING_MESSAGES';
    const DEFAULT_AUTO_DISMISS = 5000;
    const DEFAULT_CONTAINER_ID = 'django-messages-dynamic';
    const DEFAULT_CONTAINER_CLASS = 'position-fixed top-0 end-0 mt-4 p-3';
    const TYPE_CLASS_MAP = {
        success: 'alert-success',
        error: 'alert-danger',
        warning: 'alert-warning',
        info: 'alert-info',
        debug: 'alert-secondary'
    };

    const initializedContainers = [];

    function markInitialized(containerId) {
        if (!containerId) return;
        if (!initializedContainers.includes(containerId)) {
            initializedContainers.push(containerId);
        }
    }

    function unmarkInitialized(containerId) {
        if (!containerId) return;
        const idx = initializedContainers.indexOf(containerId);
        if (idx >= 0) {
            initializedContainers.splice(idx, 1);
        }
    }

    function scheduleAutoDismiss(alertEl, container, delay) {
        const ms = parseInt(delay, 10);
        if (isNaN(ms) || ms <= 0) {
            return;
        }
        setTimeout(() => closeAlert(alertEl, container), ms);
    }

    function closeAlert(alertEl, container) {
        if (!alertEl) return;
        if (window.bootstrap && bootstrap.Alert) {
            try {
                const instance = bootstrap.Alert.getOrCreateInstance(alertEl);
                instance.close();
                return;
            } catch (error) {
                // Fallback below
            }
        }
        alertEl.classList.remove('show');
        setTimeout(() => {
            alertEl.remove();
            cleanupIfEmpty(container);
        }, 300);
    }

    function cleanupIfEmpty(container) {
        if (!container || !container.parentElement) {
            return;
        }
        if (!container.querySelector('.alert')) {
            const containerId = container.id;
            container.remove();
            unmarkInitialized(containerId);
        }
    }

    function initializeMessages(container) {
        if (!container) return;
        if (!container.id) {
            container.id = `${DEFAULT_CONTAINER_ID}-${Date.now()}`;
        }

        if (initializedContainers.includes(container.id)) {
            return;
        }

        markInitialized(container.id);

        container.classList.add('django-messages-container');

        container.addEventListener('closed.bs.alert', () => cleanupIfEmpty(container));

        const delay = container.dataset.autoDismiss || DEFAULT_AUTO_DISMISS;
        container.querySelectorAll('.alert').forEach((alertEl) => {
            scheduleAutoDismiss(alertEl, container, delay);
        });
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = `${text ?? ''}`;
        return div.innerHTML;
    }

    function createAlertElement(message, type, options, container) {
        const alertEl = document.createElement('div');
        const levelClass = TYPE_CLASS_MAP[type] || TYPE_CLASS_MAP.info;
        alertEl.className = `alert ${levelClass} alert-dismissible fade show`;
        alertEl.setAttribute('role', 'alert');

        const wrapper = document.createElement('div');
        wrapper.className = 'd-flex align-items-start gap-2';

        const body = document.createElement('div');
        body.className = 'flex-grow-1';
        if (options.allowHtml) {
            body.innerHTML = message;
        } else {
            body.innerHTML = escapeHtml(message);
        }
        wrapper.appendChild(body);

        const showCloseButton = options.showCloseButton !== undefined ? options.showCloseButton : true;
        if (showCloseButton) {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'btn-close flex-shrink-0';
            button.setAttribute('data-bs-dismiss', 'alert');
            button.setAttribute('aria-label', options.closeLabel || 'Cerrar');
            wrapper.appendChild(button);
        }

        alertEl.appendChild(wrapper);

        if (window.bootstrap && bootstrap.Alert) {
            bootstrap.Alert.getOrCreateInstance(alertEl);
        }

        const autoDismiss = options.autoDismiss ?? container.dataset.autoDismiss;
        scheduleAutoDismiss(alertEl, container, autoDismiss);

        return alertEl;
    }

    function getOrCreateContainer(options = {}) {
        const { containerId, containerClass, autoDismiss } = options;
        let container = null;

        if (containerId) {
            container = document.getElementById(containerId);
        }

        if (!container) {
            container = document.querySelector('.django-messages-container');
        }

        if (!container) {
            container = document.createElement('div');
            container.id = containerId || DEFAULT_CONTAINER_ID;
            container.className = `${containerClass || DEFAULT_CONTAINER_CLASS} django-messages-container`;
            container.dataset.autoDismiss = (autoDismiss ?? DEFAULT_AUTO_DISMISS).toString();
            document.body.prepend(container);
        } else if (typeof autoDismiss === 'number') {
            container.dataset.autoDismiss = autoDismiss.toString();
        }

        initializeMessages(container);
        return container;
    }

    function showNotification(message, type = 'info', options = {}) {
        const container = getOrCreateContainer(options);
        if (!container) return null;

        const alertEl = createAlertElement(message, type, options, container);
        container.appendChild(alertEl);

        if (options.scrollIntoView !== false) {
            container.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }

        return alertEl;
    }

    function queueNotification(message, type = 'info', options = {}) {
        try {
            if (!window.sessionStorage) return;
            const rawQueue = window.sessionStorage.getItem(STORAGE_KEY);
            const queue = rawQueue ? JSON.parse(rawQueue) : [];
            queue.push({
                message,
                type,
                options: {
                    autoDismiss: options.autoDismiss,
                    showCloseButton: options.showCloseButton,
                    allowHtml: options.allowHtml
                }
            });
            window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(queue));
        } catch (error) {
            console.warn('SIGVE: No se pudo guardar la notificación para la siguiente carga.', error);
        }
    }

    function processQueuedNotifications() {
        try {
            if (!window.sessionStorage) return;
            const rawQueue = window.sessionStorage.getItem(STORAGE_KEY);
            if (!rawQueue) return;

            const queue = JSON.parse(rawQueue);
            if (!Array.isArray(queue)) {
                window.sessionStorage.removeItem(STORAGE_KEY);
                return;
            }

            queue.forEach(({ message, type, options }) => {
                if (!message) return;
                showNotification(message, type, options);
            });

            window.sessionStorage.removeItem(STORAGE_KEY);
        } catch (error) {
            console.warn('SIGVE: No se pudieron procesar las notificaciones almacenadas.', error);
            try {
                window.sessionStorage.removeItem(STORAGE_KEY);
            } catch (storageError) {
                // Ignorado intencionalmente
            }
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('.django-messages-container').forEach(initializeMessages);
        processQueuedNotifications();
    });

    const exported = {
        showNotification,
        queueNotification,
        showNotificationAfterReload: queueNotification
    };

    window.SIGVE = Object.assign(window.SIGVE || {}, exported);
})();
