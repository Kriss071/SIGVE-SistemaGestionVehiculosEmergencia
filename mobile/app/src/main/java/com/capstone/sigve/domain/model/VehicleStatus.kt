package com.capstone.sigve.domain.model

/**
 * Representa el estado de un vehículo
 */
data class VehicleStatus(
    val id: Int,
    val name: String,
    val description: String? = null
) {
    val isAvailable: Boolean
        get() = name.lowercase().contains("disponible")
    
    val isInMaintenance: Boolean
        get() = name.lowercase().contains("mantención") || name.lowercase().contains("mantencion")
    
    val isDecommissioned: Boolean
        get() = name.lowercase().contains("baja")
}

