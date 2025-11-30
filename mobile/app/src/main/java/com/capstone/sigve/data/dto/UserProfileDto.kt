package com.capstone.sigve.data.dto

import kotlinx.serialization.Serializable

/**
 * DTO para el perfil de usuario con el rol embebido (join con tabla role)
 * Supabase permite hacer select con foreign keys: select(*,role(*))
 */
@Serializable
data class UserProfileDto(
    val id: String,
    val first_name: String,
    val last_name: String,
    val rut: String? = null,
    val phone: String? = null,
    val is_active: Boolean = true,
    val role: RoleDto,  // Join con tabla role
    val workshop_id: Int? = null,
    val fire_station_id: Int? = null
)

