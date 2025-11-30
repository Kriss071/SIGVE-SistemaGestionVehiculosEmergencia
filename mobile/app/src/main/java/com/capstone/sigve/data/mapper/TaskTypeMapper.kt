package com.capstone.sigve.data.mapper

import com.capstone.sigve.data.dto.TaskTypeDto
import com.capstone.sigve.domain.model.TaskType

fun TaskTypeDto.toDomain(): TaskType {
    return TaskType(
        id = id,
        name = name,
        description = description
    )
}

fun List<TaskTypeDto>.toDomainList(): List<TaskType> = map { it.toDomain() }

