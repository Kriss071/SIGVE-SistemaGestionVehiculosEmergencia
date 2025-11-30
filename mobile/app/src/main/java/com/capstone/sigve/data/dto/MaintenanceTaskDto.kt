package com.capstone.sigve.data.dto

import kotlinx.serialization.Serializable

/**
 * DTO para tarea de mantención con joins
 */
@Serializable
data class MaintenanceTaskDto(
    val id: Int,
    val task_type: TaskTypeDto,
    val description: String? = null,
    val cost: Double = 0.0
)

/**
 * DTO para tarea con repuestos incluidos (para consultas anidadas)
 */
@Serializable
data class MaintenanceTaskWithPartsDto(
    val id: Int,
    val task_type: TaskTypeDto,
    val description: String? = null,
    val cost: Double = 0.0,
    val maintenance_task_part: List<MaintenanceTaskPartDto> = emptyList()
)

