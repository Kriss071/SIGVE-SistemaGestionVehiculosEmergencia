package com.capstone.sigve.domain.usecase.workshop

import com.capstone.sigve.domain.repository.WorkshopRepository
import javax.inject.Inject

class UpdateInventoryItemUseCase @Inject constructor(
    private val workshopRepository: WorkshopRepository
) {
    suspend operator fun invoke(
        inventoryId: Int,
        supplierId: Int?,
        quantity: Int,
        currentCost: Double,
        location: String?,
        workshopSku: String?
    ): Result<Unit> {
        return workshopRepository.updateInventoryItem(
            inventoryId = inventoryId,
            supplierId = supplierId,
            quantity = quantity,
            currentCost = currentCost,
            location = location,
            workshopSku = workshopSku
        )
    }
}

