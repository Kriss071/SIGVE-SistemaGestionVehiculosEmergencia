package com.capstone.sigve.data.mapper

import com.capstone.sigve.data.dto.MechanicDto
import com.capstone.sigve.domain.model.Mechanic

fun MechanicDto.toDomain(): Mechanic {
    return Mechanic(
        id = id,
        firstName = first_name,
        lastName = last_name,
        isActive = is_active
    )
}

fun List<MechanicDto>.toDomainList(): List<Mechanic> = map { it.toDomain() }

