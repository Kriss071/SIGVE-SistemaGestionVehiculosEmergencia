package com.capstone.sigve.domain.usecase.workshop

import com.capstone.sigve.domain.repository.WorkshopRepository
import javax.inject.Inject

class RemovePartFromTaskUseCase @Inject constructor(
    private val workshopRepository: WorkshopRepository
) {
    suspend operator fun invoke(partId: Int): Result<Unit> {
        return workshopRepository.removePartFromTask(partId)
    }
}

