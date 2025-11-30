package com.capstone.sigve.domain.model

data class MaintenanceOrder(
    val id: Int,
    val entryDate: String,
    val exitDate: String? = null,
    val mileage: Int,
    val totalCost: Double? = null,
    val observations: String? = null,
    val vehicle: VehicleSummary,
    val status: MaintenanceOrderStatus,
    val maintenanceType: MaintenanceType
) {
    val isActive: Boolean
        get() = status.isActive
}

