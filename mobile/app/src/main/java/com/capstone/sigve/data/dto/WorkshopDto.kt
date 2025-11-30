package com.capstone.sigve.data.dto

import kotlinx.serialization.Serializable

@Serializable
data class WorkshopDto(
    val id: Int,
    val name: String,
    val address: String? = null,
    val phone: String? = null,
    val email: String? = null
)

