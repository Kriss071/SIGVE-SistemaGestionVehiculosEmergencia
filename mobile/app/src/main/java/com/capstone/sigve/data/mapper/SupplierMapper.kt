package com.capstone.sigve.data.mapper

import com.capstone.sigve.data.dto.SupplierDto
import com.capstone.sigve.domain.model.Supplier

fun SupplierDto.toDomain(): Supplier {
    return Supplier(
        id = id,
        name = name,
        rut = rut,
        address = address,
        phone = phone,
        email = email
    )
}

fun List<SupplierDto>.toDomainList(): List<Supplier> = map { it.toDomain() }

