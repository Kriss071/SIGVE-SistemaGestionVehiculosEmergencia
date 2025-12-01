package com.capstone.sigve.domain.usecase.firestation

import com.capstone.sigve.domain.model.FireStationDashboardStats
import com.capstone.sigve.domain.repository.FireStationRepository
import javax.inject.Inject

class GetFireStationStatsUseCase @Inject constructor(
    private val fireStationRepository: FireStationRepository
) {
    suspend operator fun invoke(fireStationId: Int): Result<FireStationDashboardStats> {
        return fireStationRepository.getFireStationStats(fireStationId)
    }
}

