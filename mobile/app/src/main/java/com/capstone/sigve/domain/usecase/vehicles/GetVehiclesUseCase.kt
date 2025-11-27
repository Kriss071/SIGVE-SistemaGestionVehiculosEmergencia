package com.capstone.sigve.domain.usecase.vehicles

import com.capstone.sigve.domain.model.Vehicle
import com.capstone.sigve.domain.repository.VehiclesRepository
import javax.inject.Inject

class GetVehiclesUseCase @Inject constructor(
    private val vehiclesRepository: VehiclesRepository
) {
    suspend operator fun invoke(): Result<List<Vehicle>> {
        return vehiclesRepository.getVehicles()
    }
}

