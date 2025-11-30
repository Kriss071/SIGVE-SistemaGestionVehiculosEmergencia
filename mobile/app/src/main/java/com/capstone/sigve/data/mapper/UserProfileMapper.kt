package com.capstone.sigve.data.mapper

import com.capstone.sigve.data.dto.UserProfileDto
import com.capstone.sigve.domain.model.UserProfile

fun UserProfileDto.toDomain(): UserProfile {
    return UserProfile(
        id = id,
        firstName = first_name,
        lastName = last_name,
        rut = rut,
        phone = phone,
        isActive = is_active,
        role = role.toDomain(),
        workshopId = workshop_id,
        fireStationId = fire_station_id
    )
}

fun UserProfile.toDto(): UserProfileDto {
    return UserProfileDto(
        id = id,
        first_name = firstName,
        last_name = lastName,
        rut = rut,
        phone = phone,
        is_active = isActive,
        role = role.toDto(),
        workshop_id = workshopId,
        fire_station_id = fireStationId
    )
}

