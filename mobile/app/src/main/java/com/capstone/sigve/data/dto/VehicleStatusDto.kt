package com.capstone.sigve.data.dto

import kotlinx.serialization.Serializable

@Serializable
data class VehicleStatusDto(
    val id: Int,
    val name: String,
    val description: String? = null
)

