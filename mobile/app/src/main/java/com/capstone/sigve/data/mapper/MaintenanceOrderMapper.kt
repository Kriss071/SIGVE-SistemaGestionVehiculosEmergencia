package com.capstone.sigve.data.mapper

import com.capstone.sigve.data.dto.MaintenanceOrderDto
import com.capstone.sigve.data.dto.MaintenanceOrderStatusDto
import com.capstone.sigve.data.dto.MaintenanceTypeDto
import com.capstone.sigve.data.dto.VehicleSimpleDto
import com.capstone.sigve.domain.model.MaintenanceOrder
import com.capstone.sigve.domain.model.MaintenanceOrderStatus
import com.capstone.sigve.domain.model.MaintenanceType
import com.capstone.sigve.domain.model.VehicleSummary

fun MaintenanceOrderStatusDto.toDomain(): MaintenanceOrderStatus {
    return MaintenanceOrderStatus(
        id = id,
        name = name,
        description = description
    )
}

fun MaintenanceTypeDto.toDomain(): MaintenanceType {
    return MaintenanceType(
        id = id,
        name = name,
        description = description
    )
}

fun VehicleSimpleDto.toDomain(): VehicleSummary {
    return VehicleSummary(
        id = id,
        licensePlate = license_plate,
        brand = brand,
        model = model,
        year = year,
        fireStation = fire_station?.toDomain()
    )
}

fun MaintenanceOrderDto.toDomain(): MaintenanceOrder {
    return MaintenanceOrder(
        id = id,
        entryDate = entry_date,
        exitDate = exit_date,
        mileage = mileage,
        totalCost = total_cost,
        observations = observations,
        vehicle = vehicle.toDomain(),
        status = maintenance_order_status.toDomain(),
        maintenanceType = maintenance_type.toDomain()
    )
}

fun List<MaintenanceOrderDto>.toDomainList(): List<MaintenanceOrder> = map { it.toDomain() }

