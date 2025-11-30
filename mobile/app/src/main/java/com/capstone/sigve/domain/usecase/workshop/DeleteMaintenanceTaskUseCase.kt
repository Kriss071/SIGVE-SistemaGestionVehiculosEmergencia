package com.capstone.sigve.domain.usecase.workshop

import com.capstone.sigve.domain.repository.WorkshopRepository
import javax.inject.Inject

class DeleteMaintenanceTaskUseCase @Inject constructor(
    private val workshopRepository: WorkshopRepository
) {
    suspend operator fun invoke(taskId: Int): Result<Unit> {
        return workshopRepository.deleteMaintenanceTask(taskId)
    }
}

