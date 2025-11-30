package com.capstone.sigve.data.dto

import kotlinx.serialization.Serializable

/**
 * DTO para repuesto del catálogo maestro
 */
@Serializable
data class SparePartDto(
    val id: Int,
    val name: String,
    val sku: String,
    val brand: String? = null,
    val description: String? = null
)

