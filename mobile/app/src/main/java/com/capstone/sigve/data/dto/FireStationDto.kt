package com.capstone.sigve.data.dto

import kotlinx.serialization.Serializable

@Serializable
data class FireStationDto(
    val id: Int,
    val name: String,
    val address: String? = null
)

