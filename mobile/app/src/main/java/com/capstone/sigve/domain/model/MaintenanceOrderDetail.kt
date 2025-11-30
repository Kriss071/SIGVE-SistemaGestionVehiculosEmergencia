package com.capstone.sigve.domain.model

/**
 * Detalle completo de una orden de mantención
 * Incluye todas las tareas realizadas y repuestos usados
 */
data class MaintenanceOrderDetail(
    val id: Int,
    val entryDate: String,
    val exitDate: String? = null,
    val mileage: Int,
    val totalCost: Double? = null,
    val observations: String? = null,
    val vehicle: VehicleSummary,
    val status: MaintenanceOrderStatus,
    val maintenanceType: MaintenanceType,
    val assignedMechanic: Mechanic? = null,
    val tasks: List<MaintenanceTask> = emptyList()
) {
    val isCompleted: Boolean
        get() = status.name.lowercase() == "completada"
    
    val isEditable: Boolean
        get() = !isCompleted
    
    val calculatedTotalCost: Double
        get() = tasks.sumOf { it.totalCost }
    
    val taskCount: Int
        get() = tasks.size
    
    val partsCount: Int
        get() = tasks.sumOf { it.parts.size }
}

