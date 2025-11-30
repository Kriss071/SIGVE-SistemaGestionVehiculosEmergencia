package com.capstone.sigve.domain.model

data class UserProfile(
    val id: String,
    val firstName: String,
    val lastName: String,
    val rut: String? = null,
    val phone: String? = null,
    val isActive: Boolean = true,
    val role: Role,
    val workshopId: Int? = null,
    val fireStationId: Int? = null
) {
    val fullName: String get() = "$firstName $lastName"
    
    val appModule: AppModule get() = role.getAppModule()
}

