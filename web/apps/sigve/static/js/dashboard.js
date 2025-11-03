/**
 * Lógica del Dashboard de SIGVE
 * Inicializa el gráfico de estado de vehículos.
 */
document.addEventListener('DOMContentLoaded', function() {
    
    const chartElement = document.getElementById('vehiclesChart');
    
    // Solo ejecutar si el elemento del gráfico existe en esta página
    if (chartElement) {
        // Obtener los datos desde los atributos data-* del elemento canvas
        const availableVehicles = chartElement.dataset.available || 0;
        const inWorkshopVehicles = chartElement.dataset.maintenance || 0;

        const ctx = chartElement.getContext('2d');
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Disponibles', 'En Taller'],
                datasets: [{
                    // Usar los datos leídos de los atributos data-*
                    data: [availableVehicles, inWorkshopVehicles],
                    backgroundColor: ['#198754', '#ffc107'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    }
                }
            }
        });
    }

});