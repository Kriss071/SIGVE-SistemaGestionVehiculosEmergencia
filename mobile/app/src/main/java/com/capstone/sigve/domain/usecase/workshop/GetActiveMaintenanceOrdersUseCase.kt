package com.capstone.sigve.domain.usecase.workshop

import com.capstone.sigve.domain.model.MaintenanceOrder
import com.capstone.sigve.domain.repository.WorkshopRepository
import javax.inject.Inject

class GetActiveMaintenanceOrdersUseCase @Inject constructor(
    private val workshopRepository: WorkshopRepository
) {
    suspend operator fun invoke(workshopId: Int): Result<List<MaintenanceOrder>> {
        return workshopRepository.getActiveMaintenanceOrders(workshopId)
    }
}

