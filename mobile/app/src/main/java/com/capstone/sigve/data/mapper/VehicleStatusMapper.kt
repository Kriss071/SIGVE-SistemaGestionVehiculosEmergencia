package com.capstone.sigve.data.mapper

import com.capstone.sigve.data.dto.VehicleStatusDto
import com.capstone.sigve.domain.model.VehicleStatus

fun VehicleStatusDto.toDomain(): VehicleStatus {
    return VehicleStatus(
        id = id,
        name = name,
        description = description
    )
}

fun List<VehicleStatusDto>.toDomainList(): List<VehicleStatus> = map { it.toDomain() }



