package com.capstone.sigve.data.mapper

import com.capstone.sigve.data.dto.VehicleMaintenanceOrderHistoryDto
import com.capstone.sigve.data.dto.VehicleStatusLogDto
import com.capstone.sigve.domain.model.VehicleMaintenanceOrderHistory
import com.capstone.sigve.domain.model.VehicleStatusLog

/**
 * Mapper para convertir VehicleStatusLogDto a VehicleStatusLog
 */
fun VehicleStatusLogDto.toDomain(): VehicleStatusLog {
    return VehicleStatusLog(
        id = id,
        vehicleId = vehicle_id,
        changedByUserId = changed_by_user_id,
        changedByUserName = changed_by_user?.fullName,
        vehicleStatus = vehicle_status.toDomain(),
        changeDate = change_date,
        reason = reason
    )
}

fun List<VehicleStatusLogDto>.toDomainList(): List<VehicleStatusLog> = map { it.toDomain() }

/**
 * Mapper para convertir VehicleMaintenanceOrderHistoryDto a VehicleMaintenanceOrderHistory
 */
fun VehicleMaintenanceOrderHistoryDto.toDomain(): VehicleMaintenanceOrderHistory {
    return VehicleMaintenanceOrderHistory(
        id = id,
        entryDate = entry_date,
        exitDate = exit_date,
        mileage = mileage,
        totalCost = total_cost,
        observations = observations,
        status = maintenance_order_status.toDomain(),
        maintenanceType = maintenance_type.toDomain(),
        workshopName = workshop?.name,
        assignedMechanicName = assigned_mechanic?.fullName
    )
}

fun List<VehicleMaintenanceOrderHistoryDto>.toDomainHistoryList(): List<VehicleMaintenanceOrderHistory> = 
    map { it.toDomain() }

