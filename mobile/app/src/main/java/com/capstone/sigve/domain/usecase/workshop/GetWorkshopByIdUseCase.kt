package com.capstone.sigve.domain.usecase.workshop

import com.capstone.sigve.domain.model.Workshop
import com.capstone.sigve.domain.repository.WorkshopRepository
import javax.inject.Inject

class GetWorkshopByIdUseCase @Inject constructor(
    private val workshopRepository: WorkshopRepository
) {
    suspend operator fun invoke(workshopId: Int): Result<Workshop> {
        return workshopRepository.getWorkshopById(workshopId)
    }
}

