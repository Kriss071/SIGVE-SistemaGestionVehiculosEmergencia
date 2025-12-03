package com.capstone.sigve.domain.model

/**
 * Representa un registro de cambio de estado de un vehículo
 */
data class VehicleStatusLog(
    val id: Int,
    val vehicleId: Int,
    val changedByUserId: String?,
    val changedByUserName: String?,
    val vehicleStatus: VehicleStatus,
    val changeDate: String,
    val reason: String?
)

