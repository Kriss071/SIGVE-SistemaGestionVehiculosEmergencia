package com.capstone.sigve.data.dto

import kotlinx.serialization.Serializable

/**
 * DTO para detalle completo de orden de mantención
 * Incluye todas las relaciones anidadas
 */
@Serializable
data class MaintenanceOrderDetailDto(
    val id: Int,
    val entry_date: String,
    val exit_date: String? = null,
    val mileage: Int,
    val total_cost: Double? = null,
    val observations: String? = null,
    val vehicle: VehicleSimpleDto,
    val maintenance_order_status: MaintenanceOrderStatusDto,
    val maintenance_type: MaintenanceTypeDto,
    val assigned_mechanic: MechanicDto? = null,
    val maintenance_task: List<MaintenanceTaskWithPartsDto> = emptyList()
)

