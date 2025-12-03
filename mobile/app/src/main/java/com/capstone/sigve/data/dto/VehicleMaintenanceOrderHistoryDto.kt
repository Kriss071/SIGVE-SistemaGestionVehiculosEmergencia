package com.capstone.sigve.data.dto

import kotlinx.serialization.Serializable

/**
 * DTO para orden de mantención en el historial con joins
 * Query: select(*, workshop:workshop_id(name), maintenance_order_status:order_status_id(*), 
 *       maintenance_type:maintenance_type_id(*), assigned_mechanic:assigned_mechanic_id(first_name, last_name))
 */
@Serializable
data class VehicleMaintenanceOrderHistoryDto(
    val id: Int,
    val entry_date: String,
    val exit_date: String? = null,
    val mileage: Int,
    val total_cost: Double? = null,
    val observations: String? = null,
    val workshop: WorkshopNameDto? = null,
    val maintenance_order_status: MaintenanceOrderStatusDto,
    val maintenance_type: MaintenanceTypeDto,
    val assigned_mechanic: UserNameDto? = null
)

/**
 * DTO auxiliar para obtener solo nombre del taller
 */
@Serializable
data class WorkshopNameDto(
    val name: String
)

