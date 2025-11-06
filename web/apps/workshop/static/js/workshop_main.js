// JavaScript principal para el módulo Workshop

// Sistema de notificaciones Toast
document.addEventListener('DOMContentLoaded', function() {
    // Procesar mensajes de Django y convertirlos en toasts
    const djangoMessages = document.querySelectorAll('.django-message');
    
    djangoMessages.forEach(function(messageDiv) {
        const type = messageDiv.getAttribute('data-type');
        const message = messageDiv.textContent;
        
        showToast(message, type);
    });
});

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    
    if (!toastContainer) return;
    
    const toastId = 'toast-' + Date.now();
    
    // Mapear tipos de Django a Bootstrap
    let bgClass = 'bg-info';
    let icon = 'bi-info-circle';
    
    if (type === 'success') {
        bgClass = 'bg-success';
        icon = 'bi-check-circle';
    } else if (type === 'error') {
        bgClass = 'bg-danger';
        icon = 'bi-x-circle';
    } else if (type === 'warning') {
        bgClass = 'bg-warning';
        icon = 'bi-exclamation-triangle';
    }
    
    const toastHTML = `
        <div id="${toastId}" class="toast align-items-center text-white ${bgClass} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi ${icon} me-2"></i>${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: 5000 });
    toast.show();
    
    // Eliminar del DOM después de ocultarse
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

// Formatear inputs de patente a mayúsculas
document.addEventListener('DOMContentLoaded', function() {
    const licensePlateInputs = document.querySelectorAll('input[name="license_plate"]');
    
    licensePlateInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            this.value = this.value.toUpperCase();
        });
    });
});

// Confirmación de eliminación genérica
function confirmDelete(message = '¿Estás seguro de eliminar este elemento?') {
    return confirm(message);
}




