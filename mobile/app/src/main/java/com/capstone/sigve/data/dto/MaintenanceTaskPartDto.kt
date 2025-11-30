package com.capstone.sigve.data.dto

import kotlinx.serialization.Serializable

/**
 * DTO para repuestos usados en una tarea con join a workshop_inventory
 */
@Serializable
data class MaintenanceTaskPartDto(
    val id: Int,
    val workshop_inventory: WorkshopInventoryDto,
    val quantity_used: Int,
    val cost_per_unit: Double? = null
)

