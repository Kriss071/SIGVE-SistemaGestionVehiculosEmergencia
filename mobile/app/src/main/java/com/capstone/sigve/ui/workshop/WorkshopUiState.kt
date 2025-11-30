package com.capstone.sigve.ui.workshop

import com.capstone.sigve.domain.model.MaintenanceOrder
import com.capstone.sigve.domain.model.Workshop

data class WorkshopUiState(
    val isLoading: Boolean = true,
    val error: String? = null,
    val workshop: Workshop? = null,
    val activeOrders: List<MaintenanceOrder> = emptyList()
) {
    val workshopName: String
        get() = workshop?.name ?: "Taller"
    
    val vehicleCount: Int
        get() = activeOrders.size
}

