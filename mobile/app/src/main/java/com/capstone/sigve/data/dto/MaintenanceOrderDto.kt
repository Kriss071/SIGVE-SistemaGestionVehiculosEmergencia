package com.capstone.sigve.data.dto

import kotlinx.serialization.Serializable

/**
 * DTO para orden de mantención con joins a tablas relacionadas
 * Supabase query: select(*, vehicle(*,fire_station(*)), maintenance_order_status(*), maintenance_type(*))
 */
@Serializable
data class MaintenanceOrderDto(
    val id: Int,
    val entry_date: String,
    val exit_date: String? = null,
    val mileage: Int,
    val total_cost: Double? = null,
    val observations: String? = null,
    val vehicle: VehicleSimpleDto,
    val maintenance_order_status: MaintenanceOrderStatusDto,
    val maintenance_type: MaintenanceTypeDto
)

