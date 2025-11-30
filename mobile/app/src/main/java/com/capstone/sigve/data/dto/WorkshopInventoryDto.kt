package com.capstone.sigve.data.dto

import kotlinx.serialization.Serializable

/**
 * DTO para inventario de taller con join a spare_part
 */
@Serializable
data class WorkshopInventoryDto(
    val id: Int,
    val spare_part: SparePartDto,
    val quantity: Int,
    val current_cost: Double,
    val location: String? = null,
    val workshop_sku: String? = null
)

