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
        initDeleteButtons();
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
     * Limpia errores de un formulario específico
     */
    function clearFormErrorsForAdd(form) {
        if (!form) return;
        
        form.querySelectorAll('.is-invalid').forEach(field => {
            field.classList.remove('is-invalid');
        });
        
        form.querySelectorAll('.invalid-feedback[data-field-error]').forEach(feedback => {
            feedback.textContent = '';
        });
    }
    
    /**
     * Muestra un error en un campo específico del formulario de agregar
     */
    function showFieldErrorForAdd(form, fieldName, errorMessage) {
        if (!form) return;
        
        const field = form.querySelector(`[name="${fieldName}"]`);
        
        if (field) {
            field.classList.add('is-invalid');
            
            let feedback = field.parentElement.querySelector(`.invalid-feedback[data-field-error="${fieldName}"]`);
            if (!feedback) {
                feedback = field.parentElement.querySelector('.invalid-feedback');
                if (feedback) {
                    feedback.setAttribute('data-field-error', fieldName);
                } else {
                    feedback = document.createElement('div');
                    feedback.className = 'invalid-feedback';
                    feedback.setAttribute('data-field-error', fieldName);
                    field.parentElement.appendChild(feedback);
                }
            }
            feedback.textContent = errorMessage;
        } else {
            console.warn(`Campo no encontrado para mostrar error: ${fieldName}`);
            if (window.SIGVE && window.SIGVE.showNotification) {
                window.SIGVE.showNotification(errorMessage, 'error');
            }
        }
    }
    
    /**
     * Valida el formulario de agregar repuesto
     */
    function validateAddForm(form) {
        clearFormErrorsForAdd(form);
        
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');
        
        // Mensajes de error en español
        const errorMessages = {
            'spare_part_id': 'Por favor, selecciona un repuesto del catálogo.',
            'quantity': 'Por favor, ingresa una cantidad.',
            'current_cost': 'Por favor, ingresa un costo de compra.'
        };
        
        requiredFields.forEach(field => {
            const fieldName = field.name;
            let fieldValue = field.value;
            
            // Para selects, verificar que tenga un valor seleccionado
            if (field.tagName === 'SELECT') {
                if (!fieldValue || fieldValue === '') {
                    isValid = false;
                    field.classList.add('is-invalid');
                    const errorMsg = errorMessages[fieldName] || 'Este campo es obligatorio.';
                    showFieldErrorForAdd(form, fieldName, errorMsg);
                }
            } else {
                // Para inputs, usar trim
                fieldValue = fieldValue ? fieldValue.trim() : '';
                if (!fieldValue) {
                    isValid = false;
                    field.classList.add('is-invalid');
                    const errorMsg = errorMessages[fieldName] || 'Este campo es obligatorio.';
                    showFieldErrorForAdd(form, fieldName, errorMsg);
                }
            }
        });
        
        // Validar cantidad
        const quantityField = form.querySelector('[name="quantity"]');
        if (quantityField) {
            const quantity = parseInt(quantityField.value);
            if (isNaN(quantity) || quantity <= 0) {
                isValid = false;
                quantityField.classList.add('is-invalid');
                showFieldErrorForAdd(form, 'quantity', 'La cantidad debe ser mayor a cero.');
            }
        }
        
        // Validar costo
        const costField = form.querySelector('[name="current_cost"]');
        if (costField) {
            const cost = parseFloat(costField.value);
            if (isNaN(cost) || cost < 0) {
                isValid = false;
                costField.classList.add('is-invalid');
                showFieldErrorForAdd(form, 'current_cost', 'El costo debe ser mayor o igual a cero.');
            }
        }
        
        if (!isValid) {
            if (window.SIGVE && window.SIGVE.showNotification) {
                window.SIGVE.showNotification('Por favor, completa todos los campos obligatorios correctamente.', 'error');
            }
        }
        
        return isValid;
    }

    /**
     * Inicializa el modal de agregar repuesto
     */
    function initAddModal() {
        const addModal = document.getElementById('addInventoryModal');
        const sparePartSelect = document.getElementById('sparePartSelect');
        const addForm = addModal ? addModal.querySelector('form') : null;
        
        if (!addModal || !sparePartSelect) return;
        
        // Limpiar formulario cuando se cierra el modal
        addModal.addEventListener('hidden.bs.modal', function() {
            if (addForm) {
                addForm.reset();
                clearFormErrorsForAdd(addForm);
                // Restablecer el select a su estado inicial
                sparePartSelect.innerHTML = '<option value="">Selecciona un repuesto</option>' + 
                    Array.from(sparePartSelect.options).slice(1).map(opt => opt.outerHTML).join('');
            }
        });
        
        // Prevenir validación HTML5 nativa del formulario de agregar
        if (addForm) {
            addForm.addEventListener('invalid', function(e) {
                e.preventDefault();
                // La validación se manejará en handleSubmit
            }, true);
        }
        
        // Manejar envío del formulario de agregar
        if (addForm) {
            addForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                // Validar formulario
                if (!validateAddForm(addForm)) {
                    return;
                }
                
                const submitBtn = addForm.querySelector('button[type="submit"]');
                if (submitBtn && window.SIGVE && window.SIGVE.showButtonLoading) {
                    window.SIGVE.showButtonLoading(submitBtn);
                }
                
                const formData = new FormData(addForm);
                
                fetch(addForm.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => {
                    if (response.redirected) {
                        window.location.href = response.url;
                        return null;
                    }
                    return response.json();
                })
                .then(data => {
                    if (data) {
                        if (data.success) {
                            if (submitBtn && window.SIGVE && window.SIGVE.hideButtonLoading) {
                                window.SIGVE.hideButtonLoading(submitBtn);
                            }
                            const modalInstance = bootstrap.Modal.getInstance(addModal);
                            if (modalInstance) {
                                modalInstance.hide();
                            }
                            setTimeout(() => {
                                window.location.reload();
                            }, 150);
                        } else if (data.errors) {
                            // Errores de validación
                            clearFormErrorsForAdd(addForm);
                            
                            // Mostrar errores por campo
                            for (const [field, errors] of Object.entries(data.errors)) {
                                if (Array.isArray(errors) && errors.length > 0) {
                                    const errorMessage = errors[0];
                                    
                                    if (field === 'general' || field === '__all__') {
                                        if (window.SIGVE && window.SIGVE.showNotification) {
                                            window.SIGVE.showNotification(errorMessage, 'error');
                                        } else {
                                            alert(errorMessage);
                                        }
                                    } else {
                                        showFieldErrorForAdd(addForm, field, errorMessage);
                                    }
                                }
                            }
                            
                            if (submitBtn && window.SIGVE && window.SIGVE.hideButtonLoading) {
                                window.SIGVE.hideButtonLoading(submitBtn);
                            }
                        }
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    if (window.SIGVE && window.SIGVE.showNotification) {
                        window.SIGVE.showNotification('Error al agregar el repuesto', 'error');
                    } else {
                        alert('Error al agregar el repuesto');
                    }
                    if (submitBtn && window.SIGVE && window.SIGVE.hideButtonLoading) {
                        window.SIGVE.hideButtonLoading(submitBtn);
                    }
                });
            });
        }
        
        // Búsqueda mejorada en el select (filtrado de opciones)
        const originalOptions = Array.from(sparePartSelect.options);
        let searchInput = null;
        let searchLoader = null;
        let searchTimeout = null;
        
        // Crear campo de búsqueda si hay muchas opciones
        if (originalOptions.length > 10) {
            const searchContainer = document.createElement('div');
            searchContainer.className = 'mb-2 position-relative';
            searchContainer.innerHTML = `
                <input type="text" 
                       id="sparePartSearch" 
                       class="form-control" 
                       placeholder="Buscar repuesto...">
                <div id="sparePartSearchLoader" class="spare-part-search-loader" style="display: none;">
                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                </div>
            `;
            sparePartSelect.parentNode.insertBefore(searchContainer, sparePartSelect);
            searchInput = document.getElementById('sparePartSearch');
            searchLoader = document.getElementById('sparePartSearchLoader');
            
            searchInput.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase().trim();
                
                // Mostrar loader
                if (searchLoader) {
                    searchLoader.style.display = 'block';
                }
                
                // Limpiar timeout anterior si existe
                if (searchTimeout) {
                    clearTimeout(searchTimeout);
                }
                
                // Ejecutar búsqueda con un pequeño delay para mejor rendimiento
                searchTimeout = setTimeout(function() {
                    const options = Array.from(sparePartSelect.options);
                    let visibleOptions = [];
                    
                    // Filtrar opciones
                    options.forEach(function(option) {
                        if (option.value === '') {
                            // Mantener la opción vacía siempre visible
                            option.style.display = '';
                            return;
                        }
                        
                        const text = option.textContent.toLowerCase();
                        const isVisible = text.includes(searchTerm);
                        option.style.display = isVisible ? '' : 'none';
                        
                        if (isVisible) {
                            visibleOptions.push(option);
                        }
                    });
                    
                    // Si hay al menos una opción visible (excluyendo la vacía), seleccionar la primera automáticamente
                    if (visibleOptions.length > 0 && searchTerm.length > 0) {
                        const selectedOption = visibleOptions[0];
                        const selectedValue = selectedOption.value;
                        
                        // Buscar el índice de la opción
                        let optionIndex = -1;
                        for (let i = 0; i < sparePartSelect.options.length; i++) {
                            if (sparePartSelect.options[i] === selectedOption) {
                                optionIndex = i;
                                break;
                            }
                        }
                        
                        if (optionIndex >= 0 && selectedValue) {
                            // Establecer el valor usando múltiples métodos para asegurar que funcione
                            sparePartSelect.selectedIndex = optionIndex;
                            sparePartSelect.value = selectedValue;
                            
                            // Verificar y forzar si es necesario
                            setTimeout(function() {
                                if (sparePartSelect.value !== selectedValue) {
                                    sparePartSelect.selectedIndex = optionIndex;
                                    sparePartSelect.value = selectedValue;
                                }
                                
                                // Disparar evento change
                                sparePartSelect.dispatchEvent(new Event('change', { bubbles: true }));
                            }, 0);
                        }
                    } else if (visibleOptions.length === 0 && searchTerm.length > 0) {
                        // Si no hay opciones visibles, resetear a la opción vacía
                        sparePartSelect.selectedIndex = 0;
                        sparePartSelect.value = '';
                    } else if (searchTerm.length === 0) {
                        // Si se limpia la búsqueda, resetear a la opción vacía
                        sparePartSelect.selectedIndex = 0;
                        sparePartSelect.value = '';
                    }
                    
                    // Ocultar loader
                    if (searchLoader) {
                        searchLoader.style.display = 'none';
                    }
                }, 150);
            });
            
            // Manejar tecla Escape para limpiar búsqueda
            searchInput.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    e.preventDefault();
                    this.value = '';
                    
                    // Limpiar timeout si existe
                    if (searchTimeout) {
                        clearTimeout(searchTimeout);
                    }
                    
                    // Ocultar loader
                    if (searchLoader) {
                        searchLoader.style.display = 'none';
                    }
                    
                    // Mostrar todas las opciones
                    const options = sparePartSelect.querySelectorAll('option');
                    options.forEach(function(option) {
                        option.style.display = '';
                    });
                    
                    // Resetear el select
                    sparePartSelect.value = '';
                    sparePartSelect.selectedIndex = 0;
                    
                    // Disparar evento input para que se ejecute la lógica de limpieza
                    this.dispatchEvent(new Event('input', { bubbles: true }));
                }
            });
        }
    }

    /**
     * Configura los botones de eliminación de inventario
     */
    function initDeleteButtons() {
        // Botones de eliminar inventario
        document.querySelectorAll('.delete-inventory-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const deleteUrl = this.getAttribute('data-delete-url');
                const itemName = this.getAttribute('data-item-name');
                const itemSku = this.getAttribute('data-item-sku');
                
                if (!window.ConfirmationModal) {
                    console.error('ConfirmationModal no está disponible');
                    return;
                }
                
                if (!deleteUrl) {
                    console.error('URL de eliminación no encontrada');
                    return;
                }
                
                window.ConfirmationModal.open({
                    formAction: deleteUrl,
                    warningText: `¿Eliminar el repuesto "${itemName}" (SKU: ${itemSku}) del inventario? Esta acción no se puede deshacer.`,
                    title: 'Confirmar Eliminación de Inventario',
                    btnClass: 'btn-danger',
                    btnText: 'Sí, Eliminar'
                });
            });
        });
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
            
            // Prevenir validación HTML5 nativa del navegador
            form.addEventListener('invalid', function(e) {
                e.preventDefault();
                // La validación se manejará en handleSubmit
            }, true);
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
            
            // Validar formulario manualmente
            if (!validateForm()) {
                return;
            }
            
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && window.SIGVE && window.SIGVE.showButtonLoading) {
                window.SIGVE.showButtonLoading(submitBtn);
            }
            
            const formData = new FormData(form);
            
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                    return null;
                }
                return response.json();
            })
            .then(data => {
                if (data) {
                    if (data.success) {
                        if (submitBtn && window.SIGVE && window.SIGVE.hideButtonLoading) {
                            window.SIGVE.hideButtonLoading(submitBtn);
                        }
                        modalInstance.hide();
                        setTimeout(() => {
                            window.location.reload();
                        }, 150);
                    } else if (data.errors) {
                        // Errores de validación
                        clearFormErrors();
                        
                        // Mostrar errores por campo
                        for (const [field, errors] of Object.entries(data.errors)) {
                            if (Array.isArray(errors) && errors.length > 0) {
                                const errorMessage = errors[0];
                                
                                if (field === 'general' || field === '__all__') {
                                    if (window.SIGVE && window.SIGVE.showNotification) {
                                        window.SIGVE.showNotification(errorMessage, 'error');
                                    } else {
                                        alert(errorMessage);
                                    }
                                } else {
                                    showFieldError(field, errorMessage);
                                }
                            }
                        }
                        
                        if (submitBtn && window.SIGVE && window.SIGVE.hideButtonLoading) {
                            window.SIGVE.hideButtonLoading(submitBtn);
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (window.SIGVE && window.SIGVE.showNotification) {
                    window.SIGVE.showNotification('Error al guardar los cambios', 'error');
                } else {
                    alert('Error al guardar los cambios');
                }
                if (submitBtn && window.SIGVE && window.SIGVE.hideButtonLoading) {
                    window.SIGVE.hideButtonLoading(submitBtn);
                }
            });
        }
        
        /**
         * Valida el formulario y muestra errores en español
         * @returns {boolean} true si el formulario es válido, false en caso contrario
         */
        function validateForm() {
            clearFormErrors();
            
            let isValid = true;
            const requiredFields = form.querySelectorAll('[required]');
            
            // Mensajes de error en español para campos requeridos
            const errorMessages = {
                'quantity': 'Por favor, ingresa una cantidad.',
                'current_cost': 'Por favor, ingresa un costo actual.'
            };
            
            requiredFields.forEach(field => {
                const fieldName = field.name;
                let fieldValue = field.value;
                
                // Para selects, verificar que tenga un valor seleccionado
                if (field.tagName === 'SELECT') {
                    if (!fieldValue || fieldValue === '') {
                        isValid = false;
                        field.classList.add('is-invalid');
                        const errorMsg = errorMessages[fieldName] || 'Este campo es obligatorio.';
                        showFieldError(fieldName, errorMsg);
                    }
                } else {
                    // Para inputs, usar trim
                    fieldValue = fieldValue ? fieldValue.trim() : '';
                    if (!fieldValue) {
                        isValid = false;
                        field.classList.add('is-invalid');
                        const errorMsg = errorMessages[fieldName] || 'Este campo es obligatorio.';
                        showFieldError(fieldName, errorMsg);
                    }
                }
            });
            
            // Validar cantidad
            const quantityField = document.getElementById('id_quantity');
            if (quantityField) {
                const quantity = parseInt(quantityField.value);
                if (isNaN(quantity) || quantity < 0) {
                    isValid = false;
                    quantityField.classList.add('is-invalid');
                    showFieldError('quantity', 'La cantidad no puede ser negativa.');
                }
            }
            
            // Validar costo
            const costField = document.getElementById('id_current_cost');
            if (costField) {
                const cost = parseFloat(costField.value);
                if (isNaN(cost) || cost < 0) {
                    isValid = false;
                    costField.classList.add('is-invalid');
                    showFieldError('current_cost', 'El costo no puede ser negativo.');
                }
            }
            
            if (!isValid) {
                if (window.SIGVE && window.SIGVE.showNotification) {
                    window.SIGVE.showNotification('Por favor, completa todos los campos obligatorios correctamente.', 'error');
                }
            }
            
            return isValid;
        }
        
        /**
         * Limpia todos los errores del formulario
         */
        function clearFormErrors() {
            if (!form) return;
            
            // Remover clases de error de Bootstrap
            form.querySelectorAll('.is-invalid').forEach(field => {
                field.classList.remove('is-invalid');
            });
            
            // Limpiar mensajes de error dinámicos
            form.querySelectorAll('.invalid-feedback[data-field-error]').forEach(feedback => {
                feedback.textContent = '';
            });
        }
        
        /**
         * Muestra un error en un campo específico del formulario
         * @param {string} fieldName - Nombre del campo
         * @param {string} errorMessage - Mensaje de error a mostrar
         */
        function showFieldError(fieldName, errorMessage) {
            if (!form) return;
            
            const fieldIdMap = {
                'quantity': 'id_quantity',
                'current_cost': 'id_current_cost',
                'supplier_id': 'id_supplier_id',
                'location': 'id_location',
                'workshop_sku': 'id_workshop_sku'
            };
            
            const fieldId = fieldIdMap[fieldName] || `id_${fieldName}`;
            const field = document.getElementById(fieldId);
            
            if (field) {
                field.classList.add('is-invalid');
                
                let feedback = field.parentElement.querySelector(`.invalid-feedback[data-field-error="${fieldName}"]`);
                if (!feedback) {
                    feedback = field.parentElement.querySelector('.invalid-feedback');
                    if (feedback) {
                        feedback.setAttribute('data-field-error', fieldName);
                    } else {
                        feedback = document.createElement('div');
                        feedback.className = 'invalid-feedback';
                        feedback.setAttribute('data-field-error', fieldName);
                        field.parentElement.appendChild(feedback);
                    }
                }
                feedback.textContent = errorMessage;
            } else {
                console.warn(`Campo no encontrado para mostrar error: ${fieldName}`);
                if (window.SIGVE && window.SIGVE.showNotification) {
                    window.SIGVE.showNotification(errorMessage, 'error');
                }
            }
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
            if (form) {
                clearFormErrors();
            }
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

