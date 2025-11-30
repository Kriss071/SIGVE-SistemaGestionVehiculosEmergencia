package com.capstone.sigve.domain.model

/**
 * Repuesto del catálogo maestro de SIGVE
 */
data class SparePart(
    val id: Int,
    val name: String,
    val sku: String,
    val brand: String? = null,
    val description: String? = null
)

