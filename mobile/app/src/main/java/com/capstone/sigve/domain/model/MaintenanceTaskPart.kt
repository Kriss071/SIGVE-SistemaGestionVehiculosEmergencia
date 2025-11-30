package com.capstone.sigve.domain.model

/**
 * Repuesto usado en una tarea de mantención
 */
data class MaintenanceTaskPart(
    val id: Int,
    val inventoryItem: WorkshopInventoryItem,
    val quantityUsed: Int,
    val costPerUnit: Double? = null
) {
    val totalCost: Double
        get() = (costPerUnit ?: inventoryItem.currentCost) * quantityUsed
}

