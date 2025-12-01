package com.capstone.sigve.data.dto

import kotlinx.serialization.Serializable

/**
 * DTO para proveedor de repuestos
 */
@Serializable
data class SupplierDto(
    val id: Int,
    val name: String,
    val rut: String? = null,
    val address: String? = null,
    val phone: String? = null,
    val email: String? = null
)

