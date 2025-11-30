package com.capstone.sigve.domain.model

/**
 * Mecánico del taller (resumen de UserProfile)
 */
data class Mechanic(
    val id: String,
    val firstName: String,
    val lastName: String,
    val isActive: Boolean = true
) {
    val fullName: String
        get() = "$firstName $lastName"
}

