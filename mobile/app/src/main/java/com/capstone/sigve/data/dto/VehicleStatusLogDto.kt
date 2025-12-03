package com.capstone.sigve.data.dto

import kotlinx.serialization.Serializable

/**
 * DTO para log de cambio de estado de vehículo con joins
 * Query: select(*, vehicle_status(*), changed_by_user:changed_by_user_id(first_name, last_name))
 */
@Serializable
data class VehicleStatusLogDto(
    val id: Int,
    val vehicle_id: Int,
    val changed_by_user_id: String? = null,
    val vehicle_status: VehicleStatusDto,
    val change_date: String,
    val reason: String? = null,
    val changed_by_user: UserNameDto? = null
)

/**
 * DTO auxiliar para obtener solo nombre del usuario
 */
@Serializable
data class UserNameDto(
    val first_name: String,
    val last_name: String
) {
    val fullName: String
        get() = "$first_name $last_name"
}

