package com.capstone.sigve.domain.usecase.workshop

import com.capstone.sigve.domain.model.WorkshopInventoryItem
import com.capstone.sigve.domain.repository.WorkshopRepository
import javax.inject.Inject

class CreateInventoryItemUseCase @Inject constructor(
    private val workshopRepository: WorkshopRepository
) {
    suspend operator fun invoke(
        workshopId: Int,
        sparePartId: Int,
        supplierId: Int?,
        quantity: Int,
        currentCost: Double,
        location: String?,
        workshopSku: String?
    ): Result<WorkshopInventoryItem> {
        return workshopRepository.createInventoryItem(
            workshopId = workshopId,
            sparePartId = sparePartId,
            supplierId = supplierId,
            quantity = quantity,
            currentCost = currentCost,
            location = location,
            workshopSku = workshopSku
        )
    }
}

