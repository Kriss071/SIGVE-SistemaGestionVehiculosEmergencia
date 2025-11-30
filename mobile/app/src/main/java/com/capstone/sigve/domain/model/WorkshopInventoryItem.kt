package com.capstone.sigve.domain.model

/**
 * Ítem de inventario de un taller específico
 */
data class WorkshopInventoryItem(
    val id: Int,
    val sparePart: SparePart,
    val quantity: Int,
    val currentCost: Double,
    val location: String? = null,
    val workshopSku: String? = null
) {
    val displayName: String
        get() = "${sparePart.name}${sparePart.brand?.let { " - $it" } ?: ""}"
    
    val isAvailable: Boolean
        get() = quantity > 0
}

