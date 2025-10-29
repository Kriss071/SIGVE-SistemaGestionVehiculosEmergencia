document.addEventListener('DOMContentLoaded', () => {
    const UI = {
        userList: document.getElementById('userList'),
        userDetailModal: document.getElementById('userDetailModal'),
        userDetailContent: document.getElementById('userDetailContent'),
        closeUserModalBtn: document.getElementById('closeUserDetailModal'),
        searchForm: document.getElementById('userSearchForm'),
        searchInput: document.getElementById('userSearchInput'),
        userLoader: document.getElementById('userLoader'),
        btnAddUser: document.getElementById('btnAddUser'),
    };

    const toggleModal = (modal, show) => {
        if (!modal) {
            console.error("Intento de mostrar/ocultar un modal que no existe.");
            return;
        }
        modal.style.display = show ? 'block' : 'none';
        document.body.style.overflow = show ? 'hidden' : '';
    };

    const renderUserDetail = (user) => {
        if (!UI.userDetailContent) return;

        UI.userDetailContent.innerHTML = `
            <h2>${user.first_name || ''} ${user.last_name || ''}</h2>
            <p><strong>RUT:</strong> ${user.rut || 'N/A'}</p>
            <p><strong>Rol:</strong> ${user.role_name || 'N/A'}</p>
            <p><strong>Teléfono:</strong> ${user.phone || 'N/A'}</p>
            <p><strong>Activo:</strong> ${user.is_active ? 'Sí' : 'No'}</p>
            <p><strong>Taller:</strong> ${user.workshop_name || 'N/A'}</p> 
            
            <hr style="border-top: 1px solid #555; margin: 15px 0;">
            ${UI.userDetailModal.querySelector('#btnEditUserDetail') ? UI.userDetailModal.querySelector('#btnEditUserDetail').outerHTML : ''}
            ${UI.userDetailModal.querySelector('#btnDeleteUserDetail') ? UI.userDetailModal.querySelector('#btnDeleteUserDetail').outerHTML : ''}
        `;
    };

    const handleUserListClick = async (event) => {
        const card = event.target.closest('.user-card');
        if (!card) return;

        const userId = card.dataset.userId;
        if (!userId) {
            console.error("Atributo data-user-id no encontrado en la tarjeta.");
            return;
        }

        console.log(`Clic en usuario con ID: ${userId}`);

        toggleModal(UI.userDetailModal, true);
        if (UI.userDetailContent) {
            UI.userDetailContent.innerHTML = '<p style="color: white; text-align: center;">🔄 Cargando detalles...</p>';
        } else {
             console.error("Elemento userDetailContent no encontrado.");
             return;
        }

        try {
            const response = await fetch(`/administracion/detail/?user_id=${encodeURIComponent(userId)}`);
            
            console.log(`Respuesta de API recibida. Status: ${response.status}`);

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Error ${response.status}: ${errorText || 'No se pudo obtener la información del usuario'}`);
            }

            const data = await response.json();
            
            if (!data.user) {
                 throw new Error("La respuesta de la API no contenía la clave 'user'.");
            }
            
            console.log("Datos del usuario recibidos:", data.user);

            renderUserDetail(data.user);

        } catch (error) {
            console.error("Error al cargar detalle del usuario:", error);
            if (UI.userDetailContent) {
                 UI.userDetailContent.innerHTML = `<p style="color: red; text-align: center;">❌ Error al cargar datos: ${error.message}</p>`;
            }
        }
    };

    if (UI.userList) {
        UI.userList.addEventListener('click', handleUserListClick);
    } else {
        console.warn("Elemento userList no encontrado. Clics en tarjetas no funcionarán.");
    }

    if (UI.closeUserModalBtn) {
        UI.closeUserModalBtn.addEventListener('click', () => toggleModal(UI.userDetailModal, false));
    }

    if (UI.userDetailModal) {
        UI.userDetailModal.addEventListener('click', (event) => {
            if (event.target === UI.userDetailModal) {
                toggleModal(UI.userDetailModal, false);
            }
        });
    }

    console.log("administracion.js cargado y listeners asignados.");
});