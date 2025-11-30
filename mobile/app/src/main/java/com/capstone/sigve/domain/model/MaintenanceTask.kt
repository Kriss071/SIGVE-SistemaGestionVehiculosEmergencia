package com.capstone.sigve.domain.model

/**
 * Tarea específica realizada en una orden de mantención
 */
data class MaintenanceTask(
    val id: Int,
    val taskType: TaskType,
    val description: String? = null,
    val cost: Double = 0.0,
    val parts: List<MaintenanceTaskPart> = emptyList()
) {
    val totalPartsCost: Double
        get() = parts.sumOf { it.totalCost }
    
    val totalCost: Double
        get() = cost + totalPartsCost
}

