package com.capstone.sigve.domain.model

/**
 * Resumen de un vehículo para mostrar en listas
 */
data class VehicleSummary(
    val id: Int,
    val licensePlate: String,
    val brand: String,
    val model: String,
    val year: Int,
    val fireStation: FireStation? = null
) {
    val displayName: String
        get() = "$brand $model ($year)"
    
    val fireStationName: String
        get() = fireStation?.name ?: "Sin cuartel"
}

