package com.capstone.sigve.data.dto

import kotlinx.serialization.Serializable

/**
 * DTO para tipo de tarea de taller
 */
@Serializable
data class TaskTypeDto(
    val id: Int,
    val name: String,
    val description: String? = null
)

