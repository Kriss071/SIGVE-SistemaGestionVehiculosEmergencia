package com.capstone.sigve.domain.model

/**
 * Representa una orden de mantención en el historial del vehículo
 * Versión simplificada para mostrar en el historial
 */
data class VehicleMaintenanceOrderHistory(
    val id: Int,
    val entryDate: String,
    val exitDate: String?,
    val mileage: Int,
    val totalCost: Double?,
    val observations: String?,
    val status: MaintenanceOrderStatus,
    val maintenanceType: MaintenanceType,
    val workshopName: String?,
    val assignedMechanicName: String?
) {
    val isActive: Boolean
        get() = status.isActive
    
    val isCompleted: Boolean
        get() = status.name.lowercase() == "completada"
    
    val durationDays: Int?
        get() {
            if (exitDate == null) return null
            return try {
                val sdf = java.text.SimpleDateFormat("yyyy-MM-dd", java.util.Locale.getDefault())
                val entry = sdf.parse(entryDate)
                val exit = sdf.parse(exitDate)
                if (entry != null && exit != null) {
                    val diff = exit.time - entry.time
                    (diff / (1000 * 60 * 60 * 24)).toInt()
                } else null
            } catch (e: Exception) {
                null
            }
        }
}

