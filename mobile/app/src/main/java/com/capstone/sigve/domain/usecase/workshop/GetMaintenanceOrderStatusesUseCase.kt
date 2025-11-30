package com.capstone.sigve.domain.usecase.workshop

import com.capstone.sigve.domain.model.MaintenanceOrderStatus
import com.capstone.sigve.domain.repository.WorkshopRepository
import javax.inject.Inject

class GetMaintenanceOrderStatusesUseCase @Inject constructor(
    private val workshopRepository: WorkshopRepository
) {
    suspend operator fun invoke(): Result<List<MaintenanceOrderStatus>> {
        return workshopRepository.getMaintenanceOrderStatuses()
    }
}

