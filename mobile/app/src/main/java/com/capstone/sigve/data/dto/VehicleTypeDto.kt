package com.capstone.sigve.data.dto

import kotlinx.serialization.Serializable

@Serializable
data class VehicleTypeDto(
    val id: Int,
    val name: String,
    val description: String? = null
)



