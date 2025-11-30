package com.capstone.sigve.domain.usecase.workshop

import com.capstone.sigve.domain.model.MaintenanceType
import com.capstone.sigve.domain.repository.WorkshopRepository
import javax.inject.Inject

class GetMaintenanceTypesUseCase @Inject constructor(
    private val workshopRepository: WorkshopRepository
) {
    suspend operator fun invoke(): Result<List<MaintenanceType>> {
        return workshopRepository.getMaintenanceTypes()
    }
}

