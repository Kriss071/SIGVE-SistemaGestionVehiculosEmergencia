package com.capstone.sigve.domain.usecase.workshop

import com.capstone.sigve.domain.repository.WorkshopRepository
import javax.inject.Inject

class UpdateMaintenanceOrderUseCase @Inject constructor(
    private val workshopRepository: WorkshopRepository
) {
    suspend operator fun invoke(
        orderId: Int,
        statusId: Int,
        maintenanceTypeId: Int,
        assignedMechanicId: String?,
        exitDate: String?,
        observations: String?,
        totalCost: Double?
    ): Result<Unit> {
        return workshopRepository.updateMaintenanceOrder(
            orderId = orderId,
            statusId = statusId,
            maintenanceTypeId = maintenanceTypeId,
            assignedMechanicId = assignedMechanicId,
            exitDate = exitDate,
            observations = observations,
            totalCost = totalCost
        )
    }
}

