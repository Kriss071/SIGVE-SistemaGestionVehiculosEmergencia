package com.capstone.sigve.data.mapper

import com.capstone.sigve.data.dto.MaintenanceOrderDetailDto
import com.capstone.sigve.domain.model.MaintenanceOrderDetail

fun MaintenanceOrderDetailDto.toDomain(): MaintenanceOrderDetail {
    return MaintenanceOrderDetail(
        id = id,
        entryDate = entry_date,
        exitDate = exit_date,
        mileage = mileage,
        totalCost = total_cost,
        observations = observations,
        vehicle = vehicle.toDomain(),
        status = maintenance_order_status.toDomain(),
        maintenanceType = maintenance_type.toDomain(),
        assignedMechanic = assigned_mechanic?.toDomain(),
        tasks = maintenance_task.toDomainTaskList()
    )
}

