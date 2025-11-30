package com.capstone.sigve.data.mapper

import com.capstone.sigve.data.dto.WorkshopInventoryDto
import com.capstone.sigve.domain.model.WorkshopInventoryItem

fun WorkshopInventoryDto.toDomain(): WorkshopInventoryItem {
    return WorkshopInventoryItem(
        id = id,
        sparePart = spare_part.toDomain(),
        quantity = quantity,
        currentCost = current_cost,
        location = location,
        workshopSku = workshop_sku
    )
}

fun List<WorkshopInventoryDto>.toDomainList(): List<WorkshopInventoryItem> = map { it.toDomain() }

