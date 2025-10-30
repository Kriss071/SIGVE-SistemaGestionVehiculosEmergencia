/**
 * backoffice.js
 * Gestiona la interactividad de los modales para las operaciones CRUD 
 * en el panel de administración (Empleados, Talleres, etc.).
 */
document.addEventListener('DOMContentLoaded', function () {

    // Selectores comunes
    const getCsrfToken = () => document.querySelector('[name=csrfmiddlewaretoken]').value;

    // ===================================================================
    // 2. LÓGICA PARA TALLERES (WORKSHOP)
    // ===================================================================

    const updateEmployeeModalEl = document.getElementById('updateEmployeeModal');
    const deleteEmployeeModalEl = document.getElementById('deleteEmployeeModal');

    // 1.1 LÓGICA PARA RELLENAR EL FORMULARIO DE EDICIÓN DE EMPLEADO
    if (updateEmployeeModalEl) {
        const loader = document.getElementById('updateEmployeeLoader');
        const form = document.getElementById('updateEmployeeForm');
        
        updateEmployeeModalEl.addEventListener('show.bs.modal', function (event) {
            console.log("Modal de edición de EMPLEADO detectado.");

            loader.classList.remove('d-none');
            form.classList.add('d-none');

            const button = event.relatedTarget;
            const row = button.closest('tr');
            const employeeId = row.dataset.id;

            if (!employeeId) {
                console.error('ERROR: No se pudo encontrar el ID del empleado (data-id).');
                return;
            }

            const apiUrl = `/administracion/api/employees/${employeeId}/`;
            const formActionUrl = `/administracion/employees/update/${employeeId}/`;

            fetch(apiUrl)
                .then(response => {
                    if (!response.ok) throw new Error(`Error de red: ${response.status}`);
                    return response.json();
                })
                .then(data => {
                    console.log("Datos de EMPLEADO recibidos:", data);

                    form.action = formActionUrl;

                    // IDs de formulario de Django con prefijo 'update'
                    form.querySelector('#id_update-id').value = data.id || '';
                    form.querySelector('#id_update-first_name').value = data.first_name || '';
                    form.querySelector('#id_update-last_name').value = data.last_name || '';
                    form.querySelector('#id_update-rut').value = data.rut || '';
                    form.querySelector('#id_update-phone').value = data.phone || '';
                    form.querySelector('#id_update-role_id').value = data.role_id || '';
                    form.querySelector('#id_update-workshop_id').value = data.workshop_id || '';
                    form.querySelector('#id_update-is_active').checked = data.is_active;

                    loader.classList.add('d-none');
                    form.classList.remove('d-none');
                })
                .catch(error => {
                    console.error('FALLO CRÍTICO en API de empleado:', error);
                    alert('No se pudieron cargar los datos para editar.');
                    loader.classList.add('d-none');
                });
        });
    }

    // 1.2 LÓGICA PARA PREPARAR EL MODAL DE ELIMINACIÓN DE EMPLEADO
    if (deleteEmployeeModalEl) {
        deleteEmployeeModalEl.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const row = button.closest('tr');
            const employeeId = row.dataset.id;
            const employeeName = row.dataset.fullName;
            const employeeRUT = row.dataset.rut || 'N/A';

            if (!employeeId) {
                console.error('No se pudo encontrar el ID para eliminar.');
                return;
            }

            const formActionUrl = `/administracion/employees/delete/${employeeId}/`;
            document.getElementById('deleteEmployeeForm').action = formActionUrl;
            document.getElementById('deleteEmployeeName').textContent = employeeName;
            document.getElementById('deleteEmployeeRUT').textContent = employeeRUT;
        });
    }


    // ===================================================================
    // 2. LÓGICA PARA TALLERES (NUEVA)
    // ===================================================================

    const updateWorkshopModalEl = document.getElementById('updateWorkshopModal');
    const deleteWorkshopModalEl = document.getElementById('deleteWorkshopModal');

    // 2.1 LÓGICA PARA RELLENAR EL FORMULARIO DE EDICIÓN DE TALLER
    if (updateWorkshopModalEl) {
        const loader = document.getElementById('updateWorkshopLoader');
        const form = document.getElementById('updateWorkshopForm');

        updateWorkshopModalEl.addEventListener('show.bs.modal', function (event) {
            console.log("Modal de edición de TALLER detectado.");

            loader.classList.remove('d-none');
            form.classList.add('d-none');

            const button = event.relatedTarget;
            const row = button.closest('tr');
            const workshopId = row.dataset.id; // data-id="1"

            if (!workshopId) {
                console.error('ERROR: No se pudo encontrar el ID del taller (data-id).');
                return;
            }

            // URLs para la API y el formulario de Taller
            const apiUrl = `/administracion/api/workshops/${workshopId}/`;
            const formActionUrl = `/administracion/workshops/update/${workshopId}/`;

            fetch(apiUrl)
                .then(response => {
                    if (!response.ok) throw new Error(`Error de red: ${response.status}`);
                    return response.json();
                })
                .then(data => {
                    console.log("Datos de TALLER recibidos:", data);

                    form.action = formActionUrl;

                    // IDs de formulario de Django con prefijo 'update'
                    form.querySelector('#id_update-id').value = data.id || '';
                    form.querySelector('#id_update-name').value = data.name || '';
                    form.querySelector('#id_update-address').value = data.address || '';
                    form.querySelector('#id_update-phone').value = data.phone || '';
                    form.querySelector('#id_update-email').value = data.email || '';

                    loader.classList.add('d-none');
                    form.classList.remove('d-none');
                })
                .catch(error => {
                    console.error('FALLO CRÍTICO en API de taller:', error);
                    alert('No se pudieron cargar los datos para editar.');
                    loader.classList.add('d-none');
                });
        });
    }

    // 2.2 LÓGICA PARA PREPARAR EL MODAL DE ELIMINACIÓN DE TALLER
    if (deleteWorkshopModalEl) {
        deleteWorkshopModalEl.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const row = button.closest('tr');
            const workshopId = row.dataset.id;
            const workshopName = row.dataset.name; // data-name="..."

            if (!workshopId) {
                console.error('No se pudo encontrar el ID para eliminar.');
                return;
            }

            const formActionUrl = `/administracion/workshops/delete/${workshopId}/`;
            document.getElementById('deleteWorkshopForm').action = formActionUrl;
            document.getElementById('deleteWorkshopName').textContent = workshopName;
        });
    }


    // ===================================================================
    // 3. LÓGICA PARA PROVEEDORES (NUEVA)
    // ===================================================================

    const updateSupplierModalEl = document.getElementById('updateSupplierModal');
    const deleteSupplierModalEl = document.getElementById('deleteSupplierModal');

    // 3.1 LÓGICA PARA RELLENAR EL FORMULARIO DE EDICIÓN DE PROVEEDOR
    if (updateSupplierModalEl) {
        const loader = document.getElementById('updateSupplierLoader');
        const form = document.getElementById('updateSupplierForm');

        updateSupplierModalEl.addEventListener('show.bs.modal', function (event) {
            console.log("Modal de edición de PROVEEDOR detectado.");

            loader.classList.remove('d-none');
            form.classList.add('d-none');

            const button = event.relatedTarget;
            const row = button.closest('tr');
            const supplierId = row.dataset.id; // data-id="1"

            if (!supplierId) {
                console.error('ERROR: No se pudo encontrar el ID del proveedor (data-id).');
                return;
            }

            // URLs para la API y el formulario de Proveedor
            const apiUrl = `/administracion/api/suppliers/${supplierId}/`;
            const formActionUrl = `/administracion/suppliers/update/${supplierId}/`;

            fetch(apiUrl)
                .then(response => {
                    if (!response.ok) throw new Error(`Error de red: ${response.status}`);
                    return response.json();
                })
                .then(data => {
                    console.log("Datos de PROVEEDOR recibidos:", data);

                    form.action = formActionUrl;

                    // IDs de formulario de Django con prefijo 'update'
                    form.querySelector('#id_update-id').value = data.id || '';
                    form.querySelector('#id_update-name').value = data.name || '';
                    form.querySelector('#id_update-rut').value = data.rut || '';
                    form.querySelector('#id_update-address').value = data.address || '';
                    form.querySelector('#id_update-phone').value = data.phone || '';
                    form.querySelector('#id_update-email').value = data.email || '';

                    loader.classList.add('d-none');
                    form.classList.remove('d-none');
                })
                .catch(error => {
                    console.error('FALLO CRÍTICO en API de proveedor:', error);
                    alert('No se pudieron cargar los datos para editar.');
                    loader.classList.add('d-none');
                });
        });
    }

    // 3.2 LÓGICA PARA PREPARAR EL MODAL DE ELIMINACIÓN DE PROVEEDOR
    if (deleteSupplierModalEl) {
        deleteSupplierModalEl.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const row = button.closest('tr');
            const supplierId = row.dataset.id;
            const supplierName = row.dataset.name; // data-name="..."

            if (!supplierId) {
                console.error('No se pudo encontrar el ID para eliminar.');
                return;
            }

            const formActionUrl = `/administracion/suppliers/delete/${supplierId}/`;
            document.getElementById('deleteSupplierForm').action = formActionUrl;
            document.getElementById('deleteSupplierName').textContent = supplierName;
        });
    }

});

