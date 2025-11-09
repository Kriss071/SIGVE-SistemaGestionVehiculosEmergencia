// JavaScript principal para el módulo Workshop

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




