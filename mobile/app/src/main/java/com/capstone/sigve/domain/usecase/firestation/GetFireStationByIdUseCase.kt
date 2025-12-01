package com.capstone.sigve.domain.usecase.firestation

import com.capstone.sigve.domain.model.FireStation
import com.capstone.sigve.domain.repository.FireStationRepository
import javax.inject.Inject

class GetFireStationByIdUseCase @Inject constructor(
    private val fireStationRepository: FireStationRepository
) {
    suspend operator fun invoke(fireStationId: Int): Result<FireStation> {
        return fireStationRepository.getFireStationById(fireStationId)
    }
}

