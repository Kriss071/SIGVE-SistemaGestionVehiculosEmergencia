package com.capstone.sigve.domain.model

/**
 * Representa un vehículo del cuartel con información completa de estado y tipo
 */
data class FireStationVehicle(
    val id: Int,
    val licensePlate: String,
    val brand: String,
    val model: String,
    val year: Int,
    val mileage: Int?,
    val nextRevisionDate: String?,
    val vehicleStatus: VehicleStatus,
    val vehicleType: VehicleType,
    val hasActiveMaintenanceOrder: Boolean = false,
    val currentWorkshopName: String? = null
) {
    val displayName: String
        get() = "$brand $model ($year)"
    
    val fullDescription: String
        get() = "$licensePlate - $displayName"
    
    val isAvailable: Boolean
        get() = vehicleStatus.isAvailable && !hasActiveMaintenanceOrder
    
    val isInMaintenance: Boolean
        get() = vehicleStatus.isInMaintenance || hasActiveMaintenanceOrder
    
    val needsRevisionSoon: Boolean
        get() {
            if (nextRevisionDate == null) return false
            // Comparar con fecha actual + 30 días
            return try {
                val sdf = java.text.SimpleDateFormat("yyyy-MM-dd", java.util.Locale.getDefault())
                val revisionDate = sdf.parse(nextRevisionDate)
                val thirtyDaysFromNow = java.util.Calendar.getInstance().apply {
                    add(java.util.Calendar.DAY_OF_YEAR, 30)
                }.time
                revisionDate?.before(thirtyDaysFromNow) == true
            } catch (e: Exception) {
                false
            }
        }
}



