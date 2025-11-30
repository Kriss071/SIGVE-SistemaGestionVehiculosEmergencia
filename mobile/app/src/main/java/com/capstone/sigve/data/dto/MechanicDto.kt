package com.capstone.sigve.data.dto

import kotlinx.serialization.Serializable

/**
 * DTO para mecánico (resumen de user_profile)
 */
@Serializable
data class MechanicDto(
    val id: String,
    val first_name: String,
    val last_name: String,
    val is_active: Boolean = true
)

