package com.capstone.sigve.data.dto

import kotlinx.serialization.Serializable

/**
 * DTO para inventario de taller con joins a spare_part y supplier
 */
@Serializable
data class WorkshopInventoryDto(
    val id: Int,
    val spare_part: SparePartDto,
    val supplier: SupplierDto? = null,
    val quantity: Int,
    val current_cost: Double,
    val location: String? = null,
    val workshop_sku: String? = null
)

/**
 * DTO para crear un nuevo ítem de inventario
 */
@Serializable
data class CreateWorkshopInventoryDto(
    val spare_part_id: Int,
    val workshop_id: Int,
    val supplier_id: Int? = null,
    val quantity: Int,
    val current_cost: Double,
    val location: String? = null,
    val workshop_sku: String? = null
)

/**
 * DTO para actualizar un ítem de inventario
 */
@Serializable
data class UpdateWorkshopInventoryDto(
    val supplier_id: Int? = null,
    val quantity: Int,
    val current_cost: Double,
    val location: String? = null,
    val workshop_sku: String? = null
)
