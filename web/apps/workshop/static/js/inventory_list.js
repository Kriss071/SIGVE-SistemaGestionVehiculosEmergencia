/**
 * SIGVE - Lógica del Listado de Inventario del Taller
 * 
 * Maneja la búsqueda en tiempo real, modales y validaciones
 */
(function() {
    'use strict';

    /**
     * Inicializa todas las funcionalidades del listado de inventario
     */
    function init() {
        initSearch();
        initUpdateModal();
        initAddModal();
    }

    /**
     * Inicializa la búsqueda en tiempo real de repuestos
     */
    function initSearch() {
        const searchInput = document.getElementById('inventorySearch');
        const inventoryTable = document.getElementById('inventoryTable');
        
        if (!searchInput || !inventoryTable) return;
        
        let debounceTimer = null;
        
        searchInput.addEventListener('keyup', function() {
            clearTimeout(debounceTimer);
            const searchTerm = this.value.toLowerCase().trim();
            
            debounceTimer = setTimeout(function() {
                filterTable(searchTerm);
            }, 300); // Debounce de 300ms
        });
        
        // Limpiar búsqueda con Escape
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                this.value = '';
                filterTable('');
            }
        });
    }

    /**
     * Filtra las filas de la tabla según el término de búsqueda
     */
    function filterTable(searchTerm) {
        const table = document.getElementById('inventoryTable');
        if (!table) return;
        
        const rows = table.querySelectorAll('tbody tr');
        let visibleCount = 0;
        
        rows.forEach(function(row) {
            const text = row.textContent.toLowerCase();
            const matches = !searchTerm || text.includes(searchTerm);
            
            if (matches) {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        });
        
        // Mostrar mensaje si no hay resultados
        showNoResultsMessage(visibleCount === 0 && searchTerm.length > 0);
    }

    /**
     * Muestra u oculta el mensaje de "no hay resultados"
     */
    function showNoResultsMessage(show) {
        let noResultsRow = document.getElementById('noResultsRow');
        
        if (show && !noResultsRow) {
            const table = document.getElementById('inventoryTable');
            if (!table) return;
            
            const tbody = table.querySelector('tbody');
            if (!tbody) return;
            
            noResultsRow = document.createElement('tr');
            noResultsRow.id = 'noResultsRow';
            noResultsRow.innerHTML = `
                <td colspan="8" class="text-center py-4 text-muted">
                    <i class="bi bi-search"></i> No se encontraron repuestos que coincidan con la búsqueda
                </td>
            `;
            tbody.appendChild(noResultsRow);
        } else if (!show && noResultsRow) {
            noResultsRow.remove();
        }
    }

    /**
     * Inicializa el modal de actualización de inventario
     */
    function initUpdateModal() {
        // La función openUpdateModal se define globalmente para ser llamada desde el template
        window.openUpdateModal = function(itemId, quantity, cost, supplierId, location, workshopSku) {
            const modal = new bootstrap.Modal(document.getElementById('updateInventoryModal'));
            const form = document.getElementById('updateInventoryForm');
            
            if (!form) {
                console.error('Formulario de actualización no encontrado');
                return;
            }
            
            // Construir la URL de actualización
            // La URL base es algo como '/taller/inventory/', necesitamos agregar '{id}/update/'
            const baseUrl = form.getAttribute('data-update-url-base');
            if (baseUrl) {
                // La URL base termina en 'inventory/', agregamos el ID y '/update/'
                form.action = `${baseUrl}${itemId}/update/`;
            } else {
                // Fallback: construir la URL manualmente
                form.action = `/taller/inventory/${itemId}/update/`;
            }
            
            // Llenar los campos del formulario
            const quantityInput = document.getElementById('updateQuantity');
            const costInput = document.getElementById('updateCost');
            const supplierSelect = document.getElementById('updateSupplier');
            const locationInput = document.getElementById('updateLocation');
            const workshopSkuInput = document.getElementById('updateWorkshopSku');
            
            if (quantityInput) quantityInput.value = quantity || 0;
            if (costInput) costInput.value = cost || 0;
            if (supplierSelect) supplierSelect.value = supplierId || '';
            if (locationInput) locationInput.value = location || '';
            if (workshopSkuInput) workshopSkuInput.value = workshopSku || '';
            
            // Mostrar el modal
            modal.show();
        };
        
        // Validación del formulario antes de enviar
        const updateForm = document.getElementById('updateInventoryForm');
        if (updateForm) {
            updateForm.addEventListener('submit', function(e) {
                const quantity = parseInt(document.getElementById('updateQuantity').value);
                const cost = parseFloat(document.getElementById('updateCost').value);
                
                if (quantity < 0) {
                    e.preventDefault();
                    alert('La cantidad no puede ser negativa');
                    return false;
                }
                
                if (cost < 0) {
                    e.preventDefault();
                    alert('El costo no puede ser negativa');
                    return false;
                }
            });
        }
    }

    /**
     * Abre el modal de solicitudes para solicitar un nuevo repuesto maestro
     */
    window.openRequestSparePartModal = function() {
        // Cerrar el modal de agregar inventario si está abierto
        const addInventoryModal = bootstrap.Modal.getInstance(document.getElementById('addInventoryModal'));
        if (addInventoryModal) {
            addInventoryModal.hide();
        }
        
        // Abrir el modal de solicitudes
        const requestModalElement = document.getElementById('requestModal');
        if (requestModalElement) {
            const requestModal = new bootstrap.Modal(requestModalElement);
            
            // Limpiar el formulario antes de abrir
            if (typeof openCreateRequestModal === 'function') {
                openCreateRequestModal();
            }
            
            // Buscar y pre-seleccionar el tipo de solicitud para "Agregar Repuesto Maestro"
            // Esto se hace después de que el modal se muestre
            requestModalElement.addEventListener('shown.bs.modal', function onShown() {
                const requestTypeSelect = document.getElementById('request_type_id');
                if (requestTypeSelect) {
                    // Buscar una opción que contenga palabras clave relacionadas con repuestos
                    const options = requestTypeSelect.options;
                    for (let i = 0; i < options.length; i++) {
                        const optionText = options[i].text.toLowerCase();
                        if (optionText.includes('repuesto') || optionText.includes('spare part') || 
                            optionText.includes('catálogo') || optionText.includes('catalogo')) {
                            requestTypeSelect.value = options[i].value;
                            // Disparar el evento change para cargar el esquema
                            if (typeof handleRequestTypeChange === 'function') {
                                handleRequestTypeChange({ target: requestTypeSelect });
                            } else if (typeof loadRequestTypeSchema === 'function') {
                                loadRequestTypeSchema(options[i].value);
                            }
                            break;
                        }
                    }
                }
                // Remover el listener después de usarlo
                requestModalElement.removeEventListener('shown.bs.modal', onShown);
            }, { once: true });
            
            requestModal.show();
        } else {
            console.error('Modal de solicitudes no encontrado');
            // Fallback: redirigir a la página de solicitudes
            window.location.href = '/taller/requests/';
        }
    };

    /**
     * Inicializa el modal de agregar repuesto
     */
    function initAddModal() {
        const addModal = document.getElementById('addInventoryModal');
        const sparePartSelect = document.getElementById('sparePartSelect');
        
        if (!addModal || !sparePartSelect) return;
        
        // Limpiar formulario cuando se cierra el modal
        addModal.addEventListener('hidden.bs.modal', function() {
            const form = addModal.querySelector('form');
            if (form) {
                form.reset();
                // Restablecer el select a su estado inicial
                sparePartSelect.innerHTML = '<option value="">Selecciona un repuesto</option>' + 
                    Array.from(sparePartSelect.options).slice(1).map(opt => opt.outerHTML).join('');
            }
        });
        
        // Búsqueda mejorada en el select (filtrado de opciones)
        const originalOptions = Array.from(sparePartSelect.options);
        let searchInput = null;
        
        // Crear campo de búsqueda si hay muchas opciones
        if (originalOptions.length > 10) {
            const searchContainer = document.createElement('div');
            searchContainer.className = 'mb-2';
            searchContainer.innerHTML = `
                <input type="text" 
                       id="sparePartSearch" 
                       class="form-control form-control-sm" 
                       placeholder="Buscar repuesto...">
            `;
            sparePartSelect.parentNode.insertBefore(searchContainer, sparePartSelect);
            searchInput = document.getElementById('sparePartSearch');
            
            searchInput.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase().trim();
                const options = sparePartSelect.querySelectorAll('option');
                
                options.forEach(function(option) {
                    if (option.value === '') {
                        // Mantener la opción vacía siempre visible
                        option.style.display = '';
                        return;
                    }
                    
                    const text = option.textContent.toLowerCase();
                    option.style.display = text.includes(searchTerm) ? '' : 'none';
                });
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

