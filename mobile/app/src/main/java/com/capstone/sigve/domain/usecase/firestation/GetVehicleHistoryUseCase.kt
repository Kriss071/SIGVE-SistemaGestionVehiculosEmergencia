package com.capstone.sigve.domain.usecase.firestation

import com.capstone.sigve.domain.model.VehicleHistory
import com.capstone.sigve.domain.repository.FireStationRepository
import javax.inject.Inject

class GetVehicleHistoryUseCase @Inject constructor(
    private val fireStationRepository: FireStationRepository
) {
    suspend operator fun invoke(vehicleId: Int): Result<VehicleHistory> {
        return fireStationRepository.getVehicleHistory(vehicleId)
    }
}

