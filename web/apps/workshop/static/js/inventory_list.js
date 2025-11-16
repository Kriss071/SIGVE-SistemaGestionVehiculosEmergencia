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
        // Mantener compatibilidad con el código existente
        window.openUpdateModal = function(itemId, quantity, cost, supplierId, location, workshopSku) {
            // Usar el nuevo modal en modo edición
            if (window.InventoryModal) {
                window.InventoryModal.open('edit', itemId);
            }
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

/**
 * Workshop - Lógica de Inventory Modal (Ver/Editar)
 */
(function() {
    'use strict';

    window.InventoryModal = (function() {
        const modal = document.getElementById('inventoryModal');
        const form = document.getElementById('inventoryForm');
        const loading = document.getElementById('inventoryModalLoading');
        const footer = document.getElementById('inventoryModalFooter');
        const titleSpan = document.getElementById('inventoryModalTitle');
        
        let currentMode = 'view';
        let currentInventoryId = null;
        let modalInstance = null;
        
        function init() {
            if (!modal || !form) return;
            modalInstance = new bootstrap.Modal(modal);
            modal.addEventListener('hidden.bs.modal', resetModal);
            form.addEventListener('submit', handleSubmit);
        }
        
        function open(mode = 'view', inventoryId = null) {
            currentMode = mode;
            currentInventoryId = inventoryId;
            
            if (mode === 'view' || mode === 'edit') {
                showLoading();
                modalInstance.show();
                loadInventoryData(inventoryId, mode);
            }
        }
        
        function loadInventoryData(inventoryId, mode) {
            fetch(`/taller/api/inventory/${inventoryId}/`)
                .then(response => {
                    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        populateForm(data.item);
                        hideLoading();
                        showForm();
                        
                        if (mode === 'view') {
                            setupViewMode();
                        } else if (mode === 'edit') {
                            setupEditMode();
                        }
                    } else {
                        throw new Error(data.error || 'Error al cargar el item');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error al cargar los datos: ' + error.message);
                    modalInstance.hide();
                });
        }
        
        function setupViewMode() {
            titleSpan.textContent = 'Ver Repuesto del Inventario';
            renderButtons('view');
            setTimeout(() => setFieldsEnabled(false), 0);
        }
        
        function setupEditMode() {
            titleSpan.textContent = 'Editar Repuesto del Inventario';
            const baseUrl = form.getAttribute('data-update-url-base');
            form.action = `${baseUrl}${currentInventoryId}/update/`;
            renderButtons('edit');
            setTimeout(() => setFieldsEnabled(true), 0);
        }
        
        function switchToEditMode() {
            currentMode = 'edit';
            setupEditMode();
        }
        
        function populateForm(item) {
            const sparePart = item.spare_part || {};
            const supplier = item.supplier || {};
            
            // Información del repuesto (solo lectura)
            document.getElementById('viewSku').textContent = sparePart.sku || '—';
            document.getElementById('viewName').textContent = sparePart.name || '—';
            document.getElementById('viewBrand').textContent = sparePart.brand || '—';
            
            // Campos editables
            document.getElementById('id_quantity').value = item.quantity || 0;
            document.getElementById('id_current_cost').value = item.current_cost || 0;
            document.getElementById('id_supplier_id').value = supplier.id || '';
            document.getElementById('id_location').value = item.location || '';
            document.getElementById('id_workshop_sku').value = item.workshop_sku || '';
        }
        
        function setFieldsEnabled(enabled) {
            const fields = form.querySelectorAll('input, select');
            fields.forEach(field => {
                if (field.id.startsWith('id_')) {
                    if (enabled) {
                        field.removeAttribute('readonly');
                        field.removeAttribute('disabled');
                    } else {
                        // Para inputs usar readonly, para selects usar disabled
                        if (field.tagName === 'SELECT') {
                            field.setAttribute('disabled', 'disabled');
                        } else {
                            field.setAttribute('readonly', 'readonly');
                        }
                    }
                }
            });
        }
        
        function renderButtons(mode) {
            footer.innerHTML = '';
            
            if (mode === 'view') {
                footer.innerHTML = `
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                        <i class="bi bi-x-lg"></i> Cerrar
                    </button>
                    <button type="button" class="btn btn-primary" onclick="InventoryModal.switchToEditMode()">
                        <i class="bi bi-pencil"></i> Editar
                    </button>
                `;
            } else if (mode === 'edit') {
                footer.innerHTML = `
                    <button type="button" class="btn btn-secondary" onclick="InventoryModal.cancelEdit()">
                        <i class="bi bi-x-lg"></i> Cancelar
                    </button>
                    <button type="submit" class="btn btn-primary">
                        <i class="bi bi-check-lg"></i> Guardar Cambios
                    </button>
                `;
            }
        }
        
        function handleSubmit(e) {
            e.preventDefault();
            
            const quantity = parseInt(document.getElementById('id_quantity').value);
            const cost = parseFloat(document.getElementById('id_current_cost').value);
            
            if (quantity < 0) {
                alert('La cantidad no puede ser negativa');
                return;
            }
            
            if (cost < 0) {
                alert('El costo no puede ser negativo');
                return;
            }
            
            if (!form.checkValidity()) {
                e.stopPropagation();
                form.classList.add('was-validated');
                return;
            }
            
            form.submit();
        }
        
        function showLoading() {
            if (loading) loading.style.display = 'block';
            if (form) form.style.display = 'none';
        }
        
        function hideLoading() {
            if (loading) loading.style.display = 'none';
        }
        
        function showForm() {
            if (form) form.style.display = 'block';
        }
        
        function resetModal() {
            form.classList.remove('was-validated');
            currentMode = 'view';
            currentInventoryId = null;
        }
        
        function cancelEdit() {
            if (modalInstance) modalInstance.hide();
        }
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
        } else {
            init();
        }
        
        return {
            open: open,
            switchToEditMode: switchToEditMode,
            cancelEdit: cancelEdit
        };
    })();

})();

