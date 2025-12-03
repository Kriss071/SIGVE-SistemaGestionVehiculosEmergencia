package com.capstone.sigve.ui.firestation

import com.capstone.sigve.domain.model.VehicleHistory
import com.capstone.sigve.domain.model.VehicleHistoryItem

/**
 * Estado de la UI del historial de vehículo
 */
data class VehicleHistoryUiState(
    val isLoading: Boolean = true,
    val error: String? = null,
    val vehicleHistory: VehicleHistory? = null,
    val selectedItemId: Int? = null // Para expandir/colapsar items
) {
    val sortedItems: List<VehicleHistoryItem>
        get() = vehicleHistory?.sortedItems ?: emptyList()
    
    val hasItems: Boolean
        get() = sortedItems.isNotEmpty()
}

