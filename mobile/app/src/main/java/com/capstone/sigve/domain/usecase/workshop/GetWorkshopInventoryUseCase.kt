package com.capstone.sigve.domain.usecase.workshop

import com.capstone.sigve.domain.model.WorkshopInventoryItem
import com.capstone.sigve.domain.repository.WorkshopRepository
import javax.inject.Inject

class GetWorkshopInventoryUseCase @Inject constructor(
    private val workshopRepository: WorkshopRepository
) {
    suspend operator fun invoke(workshopId: Int): Result<List<WorkshopInventoryItem>> {
        return workshopRepository.getWorkshopInventory(workshopId)
    }
}

