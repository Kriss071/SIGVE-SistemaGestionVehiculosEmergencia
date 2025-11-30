package com.capstone.sigve.data.mapper

import com.capstone.sigve.data.dto.WorkshopDto
import com.capstone.sigve.domain.model.Workshop

fun WorkshopDto.toDomain(): Workshop {
    return Workshop(
        id = id,
        name = name,
        address = address,
        phone = phone,
        email = email
    )
}

fun Workshop.toDto(): WorkshopDto {
    return WorkshopDto(
        id = id,
        name = name,
        address = address,
        phone = phone,
        email = email
    )
}

