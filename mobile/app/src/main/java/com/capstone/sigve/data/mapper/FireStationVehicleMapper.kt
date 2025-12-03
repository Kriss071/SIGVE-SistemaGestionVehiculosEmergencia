package com.capstone.sigve.data.mapper

import com.capstone.sigve.data.dto.FireStationVehicleDto
import com.capstone.sigve.domain.model.FireStationVehicle

fun FireStationVehicleDto.toDomain(
    hasActiveMaintenanceOrder: Boolean = false,
    currentWorkshopName: String? = null
): FireStationVehicle {
    return FireStationVehicle(
        id = id,
        licensePlate = license_plate,
        brand = brand,
        model = model,
        year = year,
        mileage = mileage,
        nextRevisionDate = next_revision_date,
        vehicleStatus = vehicle_status.toDomain(),
        vehicleType = vehicle_type.toDomain(),
        hasActiveMaintenanceOrder = hasActiveMaintenanceOrder,
        currentWorkshopName = currentWorkshopName
    )
}

fun List<FireStationVehicleDto>.toDomainList(): List<FireStationVehicle> = map { it.toDomain() }



