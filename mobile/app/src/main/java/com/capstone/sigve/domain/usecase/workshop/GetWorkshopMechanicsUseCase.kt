package com.capstone.sigve.domain.usecase.workshop

import com.capstone.sigve.domain.model.Mechanic
import com.capstone.sigve.domain.repository.WorkshopRepository
import javax.inject.Inject

class GetWorkshopMechanicsUseCase @Inject constructor(
    private val workshopRepository: WorkshopRepository
) {
    suspend operator fun invoke(workshopId: Int): Result<List<Mechanic>> {
        return workshopRepository.getWorkshopMechanics(workshopId)
    }
}

