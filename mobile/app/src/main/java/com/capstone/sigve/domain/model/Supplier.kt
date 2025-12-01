package com.capstone.sigve.domain.model

/**
 * Proveedor de repuestos
 */
data class Supplier(
    val id: Int,
    val name: String,
    val rut: String? = null,
    val address: String? = null,
    val phone: String? = null,
    val email: String? = null
)

