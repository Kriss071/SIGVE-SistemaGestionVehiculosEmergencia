/**
 * employee.js
 * Gestiona la interactividad de los modales para las operaciones CRUD de empleados.
 * - Carga datos de un empleado en el modal de edición mediante una llamada a la API.
 * - Prepara el modal de confirmación de eliminación con los datos del empleado.
 */
document.addEventListener('DOMContentLoaded', function () {

    const updateModalEl = document.getElementById('updateEmployeeModal');
    const deleteModalEl = document.getElementById('deleteEmployeeModal');

    // ===================================================================
    // 1. LÓGICA PARA RELLENAR EL FORMULARIO DE EDICIÓN
    // ===================================================================

    if (updateModalEl) {
        const loader = document.getElementById('updateEmployeeLoader');
        const form = document.getElementById('updateEmployeeForm');
        // Escuchamos el evento que Bootstrap 5 dispara JUSTO ANTES de mostrar el modal.
        updateModalEl.addEventListener('show.bs.modal', function (event) {
            console.log("Modal de edición detectado. Iniciando proceso...");

            // Asegurarnos de que el loader esté visible y el form oculto al empezar.
            loader.classList.remove('d-none');
            form.classList.add('d-none');

            // 'event.relatedTarget' es el botón específico que disparó la apertura del modal.
            const button = event.relatedTarget;
            const row = button.closest('tr');
            const employeeId = row.dataset.id;

            if (!employeeId) {
                console.error('ERROR: No se pudo encontrar el ID del empleado en la fila de la tabla (data-id).');
                return;
            }
            console.log(`Empleado a editar ID: ${employeeId}`);

            // Construimos las URLs que necesitamos dinámicamente.
            const apiUrl = `/administracion/api/employees/${employeeId}/`;
            const formActionUrl = `/administracion/employees/update/${employeeId}/`;

            console.log(`Llamando a la API en: ${apiUrl}`);
            const updateForm = document.getElementById('updateEmployeeForm');

            // Hacemos la llamada a nuestra API para obtener los datos del empleado.
            fetch(apiUrl)
                .then(response => {
                    if (!response.ok) {
                        // Si la respuesta no es exitosa (ej: 404, 500), lanzamos un error.
                        throw new Error(`Error de red: ${response.status} - ${response.statusText}`);
                    }
                    return response.json(); // Convertimos la respuesta a formato JSON.
                })
                .then(data => {
                    console.log("Datos recibidos de la API:", data);

                    // ---- ¡AQUÍ OCURRE LA MAGIA! Rellenamos el formulario. ----

                    // Asignamos la URL correcta al 'action' del formulario.
                    updateForm.action = formActionUrl;

                    // Django usa prefijos en los IDs, por eso buscamos 'id_update-first_name', etc.
                    updateForm.querySelector('#id_update-id').value = data.id || '';
                    updateForm.querySelector('#id_update-first_name').value = data.first_name || '';
                    updateForm.querySelector('#id_update-last_name').value = data.last_name || '';
                    updateForm.querySelector('#id_update-rut').value = data.rut || '';
                    updateForm.querySelector('#id_update-phone').value = data.phone || '';
                    updateForm.querySelector('#id_update-role_id').value = data.role_id || '';
                    updateForm.querySelector('#id_update-workshop_id').value = data.workshop_id || '';
                    updateForm.querySelector('#id_update-is_active').checked = data.is_active;

                    console.log("Formulario de edición rellenado exitosamente. ✅");

                    // Ocultar el loader y mostrar el formulario ya poblado.
                    loader.classList.add('d-none');
                    form.classList.remove('d-none');
                })
                .catch(error => {
                    console.error('FALLO CRÍTICO en la llamada a la API:', error);
                    alert('No se pudieron cargar los datos para editar. Revisa la consola del navegador para más detalles (F12).');

                    // También ocultamos el loader para no dejarlo girando.
                    loader.classList.add('d-none');
                });
        });
    }


    // ===================================================================
    // 2. LÓGICA PARA PREPARAR EL MODAL DE ELIMINACIÓN (YA FUNCIONA)
    // ===================================================================

    if (deleteModalEl) {
        deleteModalEl.addEventListener('show.bs.modal', function (event) {
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

            const deleteForm = document.getElementById('deleteEmployeeForm');
            deleteForm.action = formActionUrl;

            document.getElementById('deleteEmployeeName').textContent = employeeName;
            document.getElementById('deleteEmployeeRUT').textContent = employeeRUT;
        });
    }
});