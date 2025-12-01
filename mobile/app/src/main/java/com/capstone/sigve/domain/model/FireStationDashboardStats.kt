package com.capstone.sigve.domain.model

/**
 * Estadísticas del dashboard del cuartel
 */
data class FireStationDashboardStats(
    val totalVehicles: Int = 0,
    val availableVehicles: Int = 0,
    val inMaintenanceVehicles: Int = 0,
    val decommissionedVehicles: Int = 0,
    val vehiclesNeedingRevision: Int = 0,
    val vehiclesByType: Map<String, Int> = emptyMap(),
    val activeMaintenanceOrders: Int = 0
) {
    val availabilityPercentage: Float
        get() = if (totalVehicles > 0) (availableVehicles.toFloat() / totalVehicles) * 100 else 0f
    
    val operationalVehicles: Int
        get() = totalVehicles - decommissionedVehicles
}

