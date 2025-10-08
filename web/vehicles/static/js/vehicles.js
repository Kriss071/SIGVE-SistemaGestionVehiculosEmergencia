const modal = document.getElementById("vehicle_modal");
document.getElementById("btnAddVehicle").onclick = () => modal.style.display = "block";
function closeModal() { modal.style.display = "none"; }


window.onclick = function (event) {
    if (event.target == modal) modal.style.display = "none";
}