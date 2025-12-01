package com.capstone.sigve.domain.usecase.workshop

import com.capstone.sigve.domain.repository.WorkshopRepository
import javax.inject.Inject

class DeleteInventoryItemUseCase @Inject constructor(
    private val workshopRepository: WorkshopRepository
) {
    suspend operator fun invoke(inventoryId: Int): Result<Unit> {
        return workshopRepository.deleteInventoryItem(inventoryId)
    }
}

