package com.capstone.sigve.domain.model

data class Workshop(
    val id: Int,
    val name: String,
    val address: String? = null,
    val phone: String? = null,
    val email: String? = null
)

