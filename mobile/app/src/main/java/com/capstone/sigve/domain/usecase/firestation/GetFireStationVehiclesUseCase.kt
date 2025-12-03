package com.capstone.sigve.domain.usecase.firestation

import com.capstone.sigve.domain.model.FireStationVehicle
import com.capstone.sigve.domain.repository.FireStationRepository
import javax.inject.Inject

class GetFireStationVehiclesUseCase @Inject constructor(
    private val fireStationRepository: FireStationRepository
) {
    suspend operator fun invoke(fireStationId: Int): Result<List<FireStationVehicle>> {
        return fireStationRepository.getFireStationVehicles(fireStationId)
    }
}



