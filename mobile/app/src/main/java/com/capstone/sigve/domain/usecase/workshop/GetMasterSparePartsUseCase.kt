package com.capstone.sigve.domain.usecase.workshop

import com.capstone.sigve.domain.model.SparePart
import com.capstone.sigve.domain.repository.WorkshopRepository
import javax.inject.Inject

class GetMasterSparePartsUseCase @Inject constructor(
    private val workshopRepository: WorkshopRepository
) {
    suspend operator fun invoke(): Result<List<SparePart>> {
        return workshopRepository.getMasterSpareParts()
    }
}

