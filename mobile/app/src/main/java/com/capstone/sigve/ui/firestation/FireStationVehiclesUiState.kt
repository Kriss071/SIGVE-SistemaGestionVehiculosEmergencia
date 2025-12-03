package com.capstone.sigve.ui.firestation

import com.capstone.sigve.domain.model.FireStationVehicle

/**
 * Estado de la UI de la pantalla de vehículos del cuartel
 */
data class FireStationVehiclesUiState(
    val isLoading: Boolean = true,
    val error: String? = null,
    val vehicles: List<FireStationVehicle> = emptyList(),
    val searchQuery: String = "",
    val selectedStatusFilter: String? = null
) {
    // Vehículos filtrados según búsqueda y filtro de estado
    val filteredVehicles: List<FireStationVehicle>
        get() {
            var result = vehicles
            
            if (searchQuery.isNotBlank()) {
                val query = searchQuery.lowercase()
                result = result.filter { vehicle ->
                    vehicle.licensePlate.lowercase().contains(query) ||
                    vehicle.brand.lowercase().contains(query) ||
                    vehicle.model.lowercase().contains(query) ||
                    vehicle.vehicleType.name.lowercase().contains(query)
                }
            }
            
            if (selectedStatusFilter != null) {
                result = result.filter { vehicle ->
                    when (selectedStatusFilter) {
                        "available" -> vehicle.isAvailable
                        "maintenance" -> vehicle.isInMaintenance
                        "decommissioned" -> vehicle.vehicleStatus.isDecommissioned
                        else -> true
                    }
                }
            }
            
            return result
        }
    
    // Agrupación de vehículos por tipo
    val vehiclesByType: Map<String, List<FireStationVehicle>>
        get() = filteredVehicles.groupBy { it.vehicleType.name }
    
    // Estados disponibles para filtrar
    val availableFilters: List<Pair<String, String>>
        get() = listOf(
            "all" to "Todos",
            "available" to "Disponibles",
            "maintenance" to "En Mantención",
            "decommissioned" to "De Baja"
        )
}



