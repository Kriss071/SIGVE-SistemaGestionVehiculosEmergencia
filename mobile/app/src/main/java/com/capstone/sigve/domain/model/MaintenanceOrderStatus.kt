package com.capstone.sigve.domain.model

data class MaintenanceOrderStatus(
    val id: Int,
    val name: String,
    val description: String? = null
) {
    /**
     * Determina si este estado representa una orden activa (vehículo en taller)
     */
    val isActive: Boolean
        get() = name.lowercase() in listOf(
            "pendiente",
            "en taller",
            "en espera de repuestos"
        )
}

