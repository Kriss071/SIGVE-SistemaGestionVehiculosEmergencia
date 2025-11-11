/**
 * SIGVE - Lógica del Listado de Órdenes de Mantención
 * 
 * Maneja el filtrado automático de órdenes con loader
 */
(function() {
    'use strict';

    /**
     * Inicializa el filtrado automático de órdenes
     */
    function init() {
        const filterForm = document.getElementById('filterForm');
        const filterLoader = document.getElementById('filterLoader');
        
        if (!filterForm) return;
        
        // Función para mostrar el loader
        function showLoader() {
            if (filterLoader) {
                filterLoader.style.display = 'flex';
            }
        }
        
        // Filtrado inmediato para selects (Estado y Cuartel)
        const statusFilter = document.getElementById('statusFilter');
        const fireStationFilter = document.getElementById('fireStationFilter');
        
        if (statusFilter) {
            statusFilter.addEventListener('change', function() {
                showLoader();
                filterForm.submit();
            });
        }
        
        if (fireStationFilter) {
            fireStationFilter.addEventListener('change', function() {
                showLoader();
                filterForm.submit();
            });
        }
        
        // Filtrado con debounce para el input de patente
        const licensePlateInput = document.getElementById('licensePlateFilter');
        let debounceTimer = null;
        
        if (licensePlateInput) {
            licensePlateInput.addEventListener('input', function() {
                clearTimeout(debounceTimer);
                const inputValue = this.value.trim();
                
                // Si el campo está vacío, no hacer nada
                if (inputValue.length === 0) {
                    // Verificar si hay otros filtros activos
                    const hasStatusFilter = statusFilter && statusFilter.value;
                    const hasFireStationFilter = fireStationFilter && fireStationFilter.value;
                    
                    if (!hasStatusFilter && !hasFireStationFilter) {
                        // No hay filtros, ocultar loader si está visible
                        if (filterLoader) {
                            filterLoader.style.display = 'none';
                        }
                        return;
                    }
                }
                
                // Esperar el debounce antes de mostrar el loader y enviar el formulario
                debounceTimer = setTimeout(function() {
                    // Mostrar loader justo antes de enviar el formulario
                    showLoader();
                    filterForm.submit();
                }, 1000); // Espera 500ms después de que el usuario deje de escribir
            });
        }
    }

    // Inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();

