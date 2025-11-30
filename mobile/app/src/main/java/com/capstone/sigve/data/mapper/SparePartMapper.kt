package com.capstone.sigve.data.mapper

import com.capstone.sigve.data.dto.SparePartDto
import com.capstone.sigve.domain.model.SparePart

fun SparePartDto.toDomain(): SparePart {
    return SparePart(
        id = id,
        name = name,
        sku = sku,
        brand = brand,
        description = description
    )
}

fun List<SparePartDto>.toDomainList(): List<SparePart> = map { it.toDomain() }

