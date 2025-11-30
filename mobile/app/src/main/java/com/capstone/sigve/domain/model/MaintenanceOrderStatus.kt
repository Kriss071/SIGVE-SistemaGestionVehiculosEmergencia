package com.capstone.sigve.domain.model

data class MaintenanceOrderStatus(
    val id: Int,
    val name: String,
    val description: String? = null
) {
    /**
     * Determina si este estado representa una orden completada
     * Una orden está completada si su estado contiene "completada" o "completa"
     */
    val isCompleted: Boolean
        get() = name.lowercase().trim().contains("complet")
    
    /**
     * Determina si este estado representa una orden activa (vehículo en taller)
     * Una orden está activa si NO está completada
     */
    val isActive: Boolean
        get() = !isCompleted
}

