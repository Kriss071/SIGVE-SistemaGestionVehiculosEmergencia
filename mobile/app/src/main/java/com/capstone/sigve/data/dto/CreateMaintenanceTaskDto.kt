package com.capstone.sigve.data.dto

import kotlinx.serialization.Serializable

/**
 * DTO para crear una nueva tarea de mantención
 */
@Serializable
data class CreateMaintenanceTaskDto(
    val task_type_id: Int,
    val maintenance_order_id: Int,
    val description: String? = null,
    val cost: Double = 0.0
)

/**
 * DTO para crear un nuevo repuesto en una tarea
 */
@Serializable
data class CreateMaintenanceTaskPartDto(
    val maintenance_task_id: Int,
    val workshop_inventory_id: Int,
    val quantity_used: Int,
    val cost_per_unit: Double? = null
)

/**
 * DTO para actualizar una orden de mantención
 */
@Serializable
data class UpdateMaintenanceOrderDto(
    val order_status_id: Int,
    val maintenance_type_id: Int,
    val assigned_mechanic_id: String? = null,
    val exit_date: String? = null,
    val observations: String? = null,
    val total_cost: Double? = null
)

