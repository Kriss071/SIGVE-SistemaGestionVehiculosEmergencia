/**
 * SIGVE Admin Panel - Custom JavaScript
 */

// ===== Inicialización =====
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 SIGVE Admin Panel inicializado');
    
    // Auto-cerrar alertas después de 5 segundos
    autoCloseAlerts();
    
    // Tooltip de Bootstrap
    initializeTooltips();
    
    // Validación de formularios
    initializeFormValidation();
});

// ===== Auto-cerrar Alertas =====
function autoCloseAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// ===== Tooltips de Bootstrap =====
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// ===== Validación de Formularios =====
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

// ===== Utilidades =====

/**
 * Muestra un spinner de carga en un botón
 * @param {HTMLElement} button - El botón a modificar
 */
function showButtonLoading(button) {
    button.disabled = true;
    button.dataset.originalHtml = button.innerHTML;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Cargando...';
}

/**
 * Restaura el botón a su estado original
 * @param {HTMLElement} button - El botón a restaurar
 */
function hideButtonLoading(button) {
    button.disabled = false;
    button.innerHTML = button.dataset.originalHtml;
}

/**
 * Formatea un número como moneda chilena
 * @param {number} amount - El monto a formatear
 * @returns {string} - El monto formateado
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-CL', {
        style: 'currency',
        currency: 'CLP'
    }).format(amount);
}

/**
 * Formatea una fecha al formato chileno
 * @param {string|Date} date - La fecha a formatear
 * @returns {string} - La fecha formateada
 */
function formatDate(date) {
    const d = new Date(date);
    return new Intl.DateTimeFormat('es-CL', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    }).format(d);
}

/**
 * Formatea una fecha y hora al formato chileno
 * @param {string|Date} datetime - La fecha y hora a formatear
 * @returns {string} - La fecha y hora formateadas
 */
function formatDateTime(datetime) {
    const d = new Date(datetime);
    return new Intl.DateTimeFormat('es-CL', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    }).format(d);
}

/**
 * Valida RUT chileno
 * @param {string} rut - El RUT a validar
 * @returns {boolean} - True si es válido
 */
function validateRUT(rut) {
    // Elimina puntos y guión
    rut = rut.replace(/\./g, '').replace(/-/g, '');
    
    if (rut.length < 8) return false;
    
    const body = rut.slice(0, -1);
    const dv = rut.slice(-1).toUpperCase();
    
    let sum = 0;
    let multiplier = 2;
    
    for (let i = body.length - 1; i >= 0; i--) {
        sum += parseInt(body[i]) * multiplier;
        multiplier = multiplier < 7 ? multiplier + 1 : 2;
    }
    
    const calculatedDv = 11 - (sum % 11);
    const expectedDv = calculatedDv === 11 ? '0' : calculatedDv === 10 ? 'K' : calculatedDv.toString();
    
    return dv === expectedDv;
}

/**
 * Formatea RUT chileno
 * @param {string} rut - El RUT a formatear
 * @returns {string} - El RUT formateado
 */
function formatRUT(rut) {
    // Elimina puntos y guión
    rut = rut.replace(/\./g, '').replace(/-/g, '');
    
    if (rut.length < 2) return rut;
    
    const body = rut.slice(0, -1);
    const dv = rut.slice(-1);
    
    // Agrega puntos cada 3 dígitos desde el final
    const formattedBody = body.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    
    return `${formattedBody}-${dv}`;
}

// ===== Búsqueda en Tablas =====
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

// ===== Exportar Utilidades =====
window.SIGVE = Object.assign(window.SIGVE || {}, {
    showButtonLoading,
    hideButtonLoading,
    formatCurrency,
    formatDate,
    formatDateTime,
    validateRUT,
    formatRUT,
    setupTableSearch
});


