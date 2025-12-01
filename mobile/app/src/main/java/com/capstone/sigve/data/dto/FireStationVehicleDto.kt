package com.capstone.sigve.data.dto

import kotlinx.serialization.Serializable

/**
 * DTO para vehículo del cuartel con información de estado y tipo
 * Usado en consultas con joins para el dashboard
 */
@Serializable
data class FireStationVehicleDto(
    val id: Int,
    val license_plate: String,
    val brand: String,
    val model: String,
    val year: Int,
    val mileage: Int? = null,
    val next_revision_date: String? = null,
    val vehicle_status: VehicleStatusDto,
    val vehicle_type: VehicleTypeDto
)

/**
 * DTO para contar órdenes de mantención activas por vehículo
 */
@Serializable
data class VehicleMaintenanceInfoDto(
    val vehicle_id: Int,
    val workshop_name: String? = null
)

