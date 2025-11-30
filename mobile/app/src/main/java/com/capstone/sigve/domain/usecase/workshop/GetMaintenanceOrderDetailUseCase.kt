package com.capstone.sigve.domain.usecase.workshop

import com.capstone.sigve.domain.model.MaintenanceOrderDetail
import com.capstone.sigve.domain.repository.WorkshopRepository
import javax.inject.Inject

class GetMaintenanceOrderDetailUseCase @Inject constructor(
    private val workshopRepository: WorkshopRepository
) {
    suspend operator fun invoke(orderId: Int): Result<MaintenanceOrderDetail> {
        return workshopRepository.getMaintenanceOrderById(orderId)
    }
}

