package com.capstone.sigve.data.mapper

import com.capstone.sigve.data.dto.FireStationDto
import com.capstone.sigve.domain.model.FireStation

fun FireStationDto.toDomain(): FireStation {
    return FireStation(
        id = id,
        name = name,
        address = address
    )
}

fun FireStation.toDto(): FireStationDto {
    return FireStationDto(
        id = id,
        name = name,
        address = address
    )
}

