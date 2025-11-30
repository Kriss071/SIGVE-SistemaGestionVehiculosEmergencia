package com.capstone.sigve.data.mapper

import com.capstone.sigve.data.dto.RoleDto
import com.capstone.sigve.domain.model.Role

fun RoleDto.toDomain(): Role {
    return Role(
        id = id,
        name = name,
        description = description
    )
}

fun Role.toDto(): RoleDto {
    return RoleDto(
        id = id,
        name = name,
        description = description
    )
}


