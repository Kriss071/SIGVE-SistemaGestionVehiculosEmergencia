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
    // 3. LÓGICA PARA PROVEEDORES
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

    const updateVehicleTypeModalEl = document.getElementById('updateVehicleTypeModal');
    const deleteVehicleTypeModalEl = document.getElementById('deleteVehicleTypeModal');

    // ===================================================================
    // LÓGICA PARA TIPOS DE VEHÍCULOS
    // ===================================================================
    // 4.1 LÓGICA PARA RELLENAR EL FORMULARIO DE EDICIÓN DE TIPO DE VEHÍCULO
    if (updateVehicleTypeModalEl) {
        const loader = document.getElementById('updateVehicleTypeLoader');
        const form = document.getElementById('updateVehicleTypeForm');

        updateVehicleTypeModalEl.addEventListener('show.bs.modal', function (event) {
            console.log("Modal de edición de TIPO DE VEHÍCULO detectado.");

            loader.classList.remove('d-none');
            form.classList.add('d-none');

            const button = event.relatedTarget;
            const row = button.closest('tr');
            const vehicleTypeId = row.dataset.id; // data-id="1"

            if (!vehicleTypeId) {
                console.error('ERROR: No se pudo encontrar el ID del tipo (data-id).');
                return;
            }

            // URLs para la API y el formulario de Tipo de Vehículo
            const apiUrl = `/administracion/api/vehicle-types/${vehicleTypeId}/`;
            const formActionUrl = `/administracion/vehicle-types/update/${vehicleTypeId}/`;

            fetch(apiUrl)
                .then(response => {
                    if (!response.ok) throw new Error(`Error de red: ${response.status}`);
                    return response.json();
                })
                .then(data => {
                    console.log("Datos de TIPO DE VEHÍCULO recibidos:", data);

                    form.action = formActionUrl;

                    // IDs de formulario de Django con prefijo 'update'
                    form.querySelector('#id_update-id').value = data.id || '';
                    form.querySelector('#id_update-name').value = data.name || '';
                    form.querySelector('#id_update-description').value = data.description || '';

                    loader.classList.add('d-none');
                    form.classList.remove('d-none');
                })
                .catch(error => {
                    console.error('FALLO CRÍTICO en API de tipo de vehículo:', error);
                    alert('No se pudieron cargar los datos para editar.');
                    loader.classList.add('d-none');
                });
        });
    }

    // 4.2 LÓGICA PARA PREPARAR EL MODAL DE ELIMINACIÓN DE TIPO DE VEHÍCULO
    if (deleteVehicleTypeModalEl) {
        deleteVehicleTypeModalEl.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const row = button.closest('tr');
            const vehicleTypeId = row.dataset.id;
            const vehicleTypeName = row.dataset.name; // data-name="..."

            if (!vehicleTypeId) {
                console.error('No se pudo encontrar el ID para eliminar.');
                return;
            }

            const formActionUrl = `/administracion/vehicle-types/delete/${vehicleTypeId}/`;
            document.getElementById('deleteVehicleTypeForm').action = formActionUrl;
            document.getElementById('deleteVehicleTypeName').textContent = vehicleTypeName;
        });
    }


    // ===================================================================
    // LÓGICA PARA CUARTELES (FIRE STATION) (NUEVA)
    // ===================================================================
    const updateFireStationModalEl = document.getElementById('updateFireStationModal');
    const deleteFireStationModalEl = document.getElementById('deleteFireStationModal');

    // LÓGICA PARA RELLENAR EL FORMULARIO DE EDICIÓN
    if (updateFireStationModalEl) {
        const loader = document.getElementById('updateFireStationLoader');
        const form = document.getElementById('updateFireStationForm');
        updateFireStationModalEl.addEventListener('show.bs.modal', function (event) {
            console.log("Modal de edición de FireStation detectado.");
            loader.classList.remove('d-none');
            form.classList.add('d-none');
            const button = event.relatedTarget;
            const row = button.closest('tr');
            const itemId = row.dataset.id;
            if (!itemId) {
                console.error('ERROR: No se pudo encontrar el ID (data-id).');
                return;
            }
            const apiUrl = `/administracion/api/fire_stations/${itemId}/`;
            const formActionUrl = `/administracion/fire_stations/update/${itemId}/`;
            fetch(apiUrl)
                .then(response => {
                    if (!response.ok) throw new Error(`Error de red: ${response.status}`);
                    return response.json();
                })
                .then(data => {
                    console.log("Datos de FireStation recibidos:", data);
                    form.action = formActionUrl;
                    // Rellena los campos del formulario (con prefijo 'update')
                    form.querySelector('#id_update-id').value = data.id || '';
                    form.querySelector('#id_update-name').value = data.name || '';
                    form.querySelector('#id_update-address').value = data.address || '';
                    form.querySelector('#id_update-commune_id').value = data.commune_id || '';
                    loader.classList.add('d-none');
                    form.classList.remove('d-none');
                })
                .catch(error => {
                    console.error('FALLO CRÍTICO en API de fire_station:', error);
                    alert('No se pudieron cargar los datos para editar.');
                    loader.classList.add('d-none');
                });
        });
    }

    // LÓGICA PARA PREPARAR EL MODAL DE ELIMINACIÓN
    if (deleteFireStationModalEl) {
        deleteFireStationModalEl.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const row = button.closest('tr');
            const itemId = row.dataset.id;
            const itemName = row.dataset.name;
            if (!itemId) {
                console.error('No se pudo encontrar el ID para eliminar.');
                return;
            }
            const formActionUrl = `/administracion/fire_stations/delete/${itemId}/`;
            document.getElementById('deleteFireStationForm').action = formActionUrl;
            document.getElementById('deleteFireStationName').textContent = itemName;
        });
    }

    // ===================================================================
    // LÓGICA PARA VEHICLE STATUS (NUEVA)
    // ===================================================================
    const updateVehicleStatusModalEl = document.getElementById('updateVehicleStatusModal');
    const deleteVehicleStatusModalEl = document.getElementById('deleteVehicleStatusModal');

    // LÓGICA PARA RELLENAR EL FORMULARIO DE EDICIÓN
    if (updateVehicleStatusModalEl) {
        const loader = document.getElementById('updateVehicleStatusLoader');
        const form = document.getElementById('updateVehicleStatusForm');
        updateVehicleStatusModalEl.addEventListener('show.bs.modal', function (event) {
            console.log("Modal de edición de VehicleStatus detectado.");
            loader.classList.remove('d-none');
            form.classList.add('d-none');
            const button = event.relatedTarget;
            const row = button.closest('tr');
            const itemId = row.dataset.id;
            if (!itemId) {
                console.error('ERROR: No se pudo encontrar el ID (data-id).');
                return;
            }
            const apiUrl = `/administracion/api/vehicle-statuses/${itemId}/`;
            const formActionUrl = `/administracion/vehicle-statuses/update/${itemId}/`;
            fetch(apiUrl)
                .then(response => {
                    if (!response.ok) throw new Error(`Error de red: ${response.status}`);
                    return response.json();
                })
                .then(data => {
                    console.log("Datos de VehicleStatus recibidos:", data);
                    form.action = formActionUrl;
                    // Rellena los campos del formulario (con prefijo 'update')
                    form.querySelector('#id_update-id').value = data.id || '';
                    form.querySelector('#id_update-name').value = data.name || '';
                    form.querySelector('#id_update-description').value = data.description || '';
                    loader.classList.add('d-none');
                    form.classList.remove('d-none');
                })
                .catch(error => {
                    console.error('FALLO CRÍTICO en API de vehicle_status:', error);
                    alert('No se pudieron cargar los datos para editar.');
                    loader.classList.add('d-none');
                });
        });
    }

    // LÓGICA PARA PREPARAR EL MODAL DE ELIMINACIÓN
    if (deleteVehicleStatusModalEl) {
        deleteVehicleStatusModalEl.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const row = button.closest('tr');
            const itemId = row.dataset.id;
            const itemName = row.dataset.name;
            if (!itemId) {
                console.error('No se pudo encontrar el ID para eliminar.');
                return;
            }
            const formActionUrl = `/administracion/vehicle-statuses/delete/${itemId}/`;
            document.getElementById('deleteVehicleStatusForm').action = formActionUrl;
            document.getElementById('deleteVehicleStatusName').textContent = itemName;
        });
    }

    // ===================================================================
    // LÓGICA PARA FUEL TYPE (NUEVA)
    // ===================================================================
    const updateFuelTypeModalEl = document.getElementById('updateFuelTypeModal');
    const deleteFuelTypeModalEl = document.getElementById('deleteFuelTypeModal');

    // LÓGICA PARA RELLENAR EL FORMULARIO DE EDICIÓN
    if (updateFuelTypeModalEl) {
        const loader = document.getElementById('updateFuelTypeLoader');
        const form = document.getElementById('updateFuelTypeForm');
        updateFuelTypeModalEl.addEventListener('show.bs.modal', function (event) {
            console.log("Modal de edición de FuelType detectado.");
            loader.classList.remove('d-none');
            form.classList.add('d-none');
            const button = event.relatedTarget;
            const row = button.closest('tr');
            const itemId = row.dataset.id;
            if (!itemId) {
                console.error('ERROR: No se pudo encontrar el ID (data-id).');
                return;
            }
            const apiUrl = `/administracion/api/fuel-types/${itemId}/`;
            const formActionUrl = `/administracion/fuel-types/update/${itemId}/`;
            fetch(apiUrl)
                .then(response => {
                    if (!response.ok) throw new Error(`Error de red: ${response.status}`);
                    return response.json();
                })
                .then(data => {
                    console.log("Datos de FuelType recibidos:", data);
                    form.action = formActionUrl;
                    // Rellena los campos del formulario (con prefijo 'update')
                    form.querySelector('#id_update-id').value = data.id || '';
                    form.querySelector('#id_update-name').value = data.name || '';
                    loader.classList.add('d-none');
                    form.classList.remove('d-none');
                })
                .catch(error => {
                    console.error('FALLO CRÍTICO en API de fuel_type:', error);
                    alert('No se pudieron cargar los datos para editar.');
                    loader.classList.add('d-none');
                });
        });
    }

    // LÓGICA PARA PREPARAR EL MODAL DE ELIMINACIÓN
    if (deleteFuelTypeModalEl) {
        deleteFuelTypeModalEl.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const row = button.closest('tr');
            const itemId = row.dataset.id;
            const itemName = row.dataset.name;
            if (!itemId) {
                console.error('No se pudo encontrar el ID para eliminar.');
                return;
            }
            const formActionUrl = `/administracion/fuel-types/delete/${itemId}/`;
            document.getElementById('deleteFuelTypeForm').action = formActionUrl;
            document.getElementById('deleteFuelTypeName').textContent = itemName;
        });
    }

    // ===================================================================
    // LÓGICA PARA TRANSMISSION TYPE (NUEVA)
    // ===================================================================
    const updateTransmissionTypeModalEl = document.getElementById('updateTransmissionTypeModal');
    const deleteTransmissionTypeModalEl = document.getElementById('deleteTransmissionTypeModal');

    // LÓGICA PARA RELLENAR EL FORMULARIO DE EDICIÓN
    if (updateTransmissionTypeModalEl) {
        const loader = document.getElementById('updateTransmissionTypeLoader');
        const form = document.getElementById('updateTransmissionTypeForm');
        updateTransmissionTypeModalEl.addEventListener('show.bs.modal', function (event) {
            console.log("Modal de edición de TransmissionType detectado.");
            loader.classList.remove('d-none');
            form.classList.add('d-none');

            const button = event.relatedTarget;
            const row = button.closest('tr');
            const itemId = row.dataset.id;
            const apiUrl = `/administracion/api/transmission-types/${itemId}/`;
            const formActionUrl = `/administracion/transmission-types/update/${itemId}/`;

            fetch(apiUrl)
                .then(response => response.json())
                .then(data => {
                    console.log("Datos de TransmissionType recibidos:", data);
                    form.action = formActionUrl;
                    form.querySelector('#id_update-id').value = data.id || '';
                    form.querySelector('#id_update-name').value = data.name || '';
                    loader.classList.add('d-none');
                    form.classList.remove('d-none');
                })
                .catch(error => {
                    console.error('FALLO en API de transmission_type:', error);
                    alert('No se pudieron cargar los datos para editar.');
                    loader.classList.add('d-none');
                });
        });
    }

    // LÓGICA PARA PREPARAR EL MODAL DE ELIMINACIÓN
    if (deleteTransmissionTypeModalEl) {
        deleteTransmissionTypeModalEl.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const row = button.closest('tr');
            const itemId = row.dataset.id;
            const itemName = row.dataset.name;
            const formActionUrl = `/administracion/transmission-types/delete/${itemId}/`;
            document.getElementById('deleteTransmissionTypeForm').action = formActionUrl;
            document.getElementById('deleteTransmissionTypeName').textContent = itemName;
        });
    }

    // ===================================================================
    // LÓGICA PARA OIL TYPE (NUEVA)
    // ===================================================================
    const updateOilTypeModalEl = document.getElementById('updateOilTypeModal');
    const deleteOilTypeModalEl = document.getElementById('deleteOilTypeModal');

    // LÓGICA PARA RELLENAR EL FORMULARIO DE EDICIÓN
    if (updateOilTypeModalEl) {
        const loader = document.getElementById('updateOilTypeLoader');
        const form = document.getElementById('updateOilTypeForm');
        updateOilTypeModalEl.addEventListener('show.bs.modal', function (event) {
            console.log("Modal de edición de OilType detectado.");
            loader.classList.remove('d-none');
            form.classList.add('d-none');

            const button = event.relatedTarget;
            const row = button.closest('tr');
            const itemId = row.dataset.id;
            const apiUrl = `/administracion/api/oil-types/${itemId}/`;
            const formActionUrl = `/administracion/oil-types/update/${itemId}/`;

            fetch(apiUrl)
                .then(response => response.json())
                .then(data => {
                    console.log("Datos de OilType recibidos:", data);
                    form.action = formActionUrl;
                    form.querySelector('#id_update-id').value = data.id || '';
                    form.querySelector('#id_update-name').value = data.name || '';
                    form.querySelector('#id_update-description').value = data.description || ''; // <-- Se incluye la descripción
                    loader.classList.add('d-none');
                    form.classList.remove('d-none');
                })
                .catch(error => {
                    console.error('FALLO en API de oil_type:', error);
                    alert('No se pudieron cargar los datos para editar.');
                    loader.classList.add('d-none');
                });
        });
    }

    // LÓGICA PARA PREPARAR EL MODAL DE ELIMINACIÓN
    if (deleteOilTypeModalEl) {
        deleteOilTypeModalEl.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const row = button.closest('tr');
            const itemId = row.dataset.id;
            const itemName = row.dataset.name;
            const formActionUrl = `/administracion/oil-types/delete/${itemId}/`;
            document.getElementById('deleteOilTypeForm').action = formActionUrl;
            document.getElementById('deleteOilTypeName').textContent = itemName;
        });
    }

});

