package com.capstone.sigve.data.mapper

import com.capstone.sigve.data.dto.MaintenanceTaskDto
import com.capstone.sigve.data.dto.MaintenanceTaskPartDto
import com.capstone.sigve.data.dto.MaintenanceTaskWithPartsDto
import com.capstone.sigve.domain.model.MaintenanceTask
import com.capstone.sigve.domain.model.MaintenanceTaskPart

fun MaintenanceTaskPartDto.toDomain(): MaintenanceTaskPart {
    return MaintenanceTaskPart(
        id = id,
        inventoryItem = workshop_inventory.toDomain(),
        quantityUsed = quantity_used,
        costPerUnit = cost_per_unit
    )
}

fun MaintenanceTaskDto.toDomain(): MaintenanceTask {
    return MaintenanceTask(
        id = id,
        taskType = task_type.toDomain(),
        description = description,
        cost = cost,
        parts = emptyList()
    )
}

fun MaintenanceTaskWithPartsDto.toDomain(): MaintenanceTask {
    return MaintenanceTask(
        id = id,
        taskType = task_type.toDomain(),
        description = description,
        cost = cost,
        parts = maintenance_task_part.map { it.toDomain() }
    )
}

fun List<MaintenanceTaskWithPartsDto>.toDomainTaskList(): List<MaintenanceTask> = map { it.toDomain() }

