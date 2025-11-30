package com.capstone.sigve.domain.usecase.workshop

import com.capstone.sigve.domain.repository.WorkshopRepository
import javax.inject.Inject

class AddPartToTaskUseCase @Inject constructor(
    private val workshopRepository: WorkshopRepository
) {
    suspend operator fun invoke(
        maintenanceTaskId: Int,
        workshopInventoryId: Int,
        quantityUsed: Int,
        costPerUnit: Double?
    ): Result<Unit> {
        return workshopRepository.addPartToTask(
            maintenanceTaskId = maintenanceTaskId,
            workshopInventoryId = workshopInventoryId,
            quantityUsed = quantityUsed,
            costPerUnit = costPerUnit
        )
    }
}

