
//  Manejar el modal del formulario de vehículos

const modal = document.getElementById("vehicle_modal");

document.getElementById("btnAddVehicle").onclick = () => modal.style.display = "block";

function closeModal() {
    modal.style.display = "none";
}

window.onclick = function (event) {
    if (event.target == modal) modal.style.display = "none";
}

// Toast Control

document.addEventListener("DOMContentLoaded", function () {
    const toasts = document.querySelectorAll(".toast");
    const delay = 4000;
    const appearDelay = 500;

    toasts.forEach((toast, index) => {
        
        // Animación de entrada
        setTimeout(() => toast.classList.add("show"), appearDelay + (200 * index));

        // Animación de salida y eliminación
        setTimeout(() => {
            toast.classList.add("hide");
            setTimeout(() => toast.remove(), 500);
        }, delay + (index * 200));
    });
});