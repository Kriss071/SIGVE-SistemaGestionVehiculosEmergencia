package com.capstone.sigve.domain.model

/**
 * Representa el tipo de vehículo (ej: Carro Bomba, Camioneta)
 */
data class VehicleType(
    val id: Int,
    val name: String,
    val description: String? = null
)



