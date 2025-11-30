package com.capstone.sigve.data.dto

import kotlinx.serialization.Serializable

/**
 * DTO simplificado de Vehicle para usar en joins
 * Incluye fire_station para mostrar de dónde viene el vehículo
 */
@Serializable
data class VehicleSimpleDto(
    val id: Int,
    val license_plate: String,
    val brand: String,
    val model: String,
    val year: Int,
    val fire_station: FireStationDto? = null
)

