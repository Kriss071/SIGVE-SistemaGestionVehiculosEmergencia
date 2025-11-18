/**
 * Fire Station - Dashboard JavaScript
 * 
 * Lógica para el dashboard del cuartel de bomberos
 */

(function() {
    'use strict';

    /**
     * Inicialización del dashboard
     */
    document.addEventListener('DOMContentLoaded', function() {
        console.log('Fire Station Dashboard cargado correctamente');
        
        // Inicializar gráfico de vehículos por tipo
        initializeVehiclesByTypeChart();
    });

    /**
     * Inicializa el gráfico de barras para vehículos por tipo
     */
    function initializeVehiclesByTypeChart() {
        const chartElement = document.getElementById('vehiclesByTypeChart');
        
        if (!chartElement) {
            return;
        }

        // Obtener datos desde los data attributes
        const labelsStr = chartElement.dataset.labels || '';
        const valuesStr = chartElement.dataset.values || '';
        
        if (!labelsStr || !valuesStr) {
            return;
        }

        // Parsear los datos
        const labels = labelsStr.split(',').filter(label => label.trim() !== '');
        const data = valuesStr.split(',').map(val => parseInt(val.trim())).filter(val => !isNaN(val));
        
        if (labels.length === 0 || data.length === 0 || labels.length !== data.length) {
            return;
        }

        // Colores para las barras
        const colors = [
            'rgba(13, 110, 253, 0.8)',   // primary
            'rgba(25, 135, 84, 0.8)',    // success
            'rgba(255, 193, 7, 0.8)',    // warning
            'rgba(220, 53, 69, 0.8)',    // danger
            'rgba(108, 117, 125, 0.8)',  // secondary
            'rgba(13, 202, 240, 0.8)',   // info
            'rgba(111, 66, 193, 0.8)',   // purple
            'rgba(253, 126, 20, 0.8)',   // orange
        ];

        const ctx = chartElement.getContext('2d');
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Cantidad de Vehículos',
                    data: data,
                    backgroundColor: colors.slice(0, labels.length),
                    borderColor: colors.slice(0, labels.length).map(color => color.replace('0.8', '1')),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.parsed.y + ' vehículo(s)';
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1,
                            precision: 0
                        }
                    }
                }
            }
        });
    }

})();

