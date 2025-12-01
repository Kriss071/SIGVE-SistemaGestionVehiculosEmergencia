package com.capstone.sigve.data.mapper

import com.capstone.sigve.data.dto.VehicleTypeDto
import com.capstone.sigve.domain.model.VehicleType

fun VehicleTypeDto.toDomain(): VehicleType {
    return VehicleType(
        id = id,
        name = name,
        description = description
    )
}

fun List<VehicleTypeDto>.toDomainList(): List<VehicleType> = map { it.toDomain() }

