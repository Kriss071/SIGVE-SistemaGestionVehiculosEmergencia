package com.capstone.sigve.ui.workshop

import com.capstone.sigve.domain.model.MaintenanceOrder
import com.capstone.sigve.domain.model.MaintenanceOrderStatus
import com.capstone.sigve.domain.model.MaintenanceType
import com.capstone.sigve.domain.model.Workshop

data class WorkshopUiState(
    val isLoading: Boolean = true,
    val error: String? = null,
    val workshop: Workshop? = null,
    val activeOrders: List<MaintenanceOrder> = emptyList(),
    
    // Campos de búsqueda y filtros
    val searchQuery: String = "",
    val selectedStatusFilter: MaintenanceOrderStatus? = null,
    val selectedMaintenanceTypeFilter: MaintenanceType? = null,
    val selectedFireStationFilter: String? = null,
    val isFilterExpanded: Boolean = false
) {
    val workshopName: String
        get() = workshop?.name ?: "Taller"
    
    // Opciones disponibles para filtros (extraídas de las órdenes cargadas)
    val availableStatuses: List<MaintenanceOrderStatus>
        get() = activeOrders.map { it.status }.distinctBy { it.id }
    
    val availableMaintenanceTypes: List<MaintenanceType>
        get() = activeOrders.map { it.maintenanceType }.distinctBy { it.id }
    
    val availableFireStations: List<String>
        get() = activeOrders.mapNotNull { it.vehicle.fireStation?.name }.distinct().sorted()
    
    // Lista filtrada de órdenes
    val filteredOrders: List<MaintenanceOrder>
        get() = activeOrders.filter { order ->
            val matchesSearch = searchQuery.isBlank() || 
                order.vehicle.licensePlate.contains(searchQuery, ignoreCase = true) ||
                order.vehicle.brand.contains(searchQuery, ignoreCase = true) ||
                order.vehicle.model.contains(searchQuery, ignoreCase = true)
            
            val matchesStatus = selectedStatusFilter == null || 
                order.status.id == selectedStatusFilter.id
            
            val matchesMaintenanceType = selectedMaintenanceTypeFilter == null || 
                order.maintenanceType.id == selectedMaintenanceTypeFilter.id
            
            val matchesFireStation = selectedFireStationFilter == null || 
                order.vehicle.fireStation?.name == selectedFireStationFilter
            
            matchesSearch && matchesStatus && matchesMaintenanceType && matchesFireStation
        }
    
    val vehicleCount: Int
        get() = filteredOrders.size
    
    val totalOrdersCount: Int
        get() = activeOrders.size
    
    val hasActiveFilters: Boolean
        get() = searchQuery.isNotBlank() || 
            selectedStatusFilter != null || 
            selectedMaintenanceTypeFilter != null || 
            selectedFireStationFilter != null
}
