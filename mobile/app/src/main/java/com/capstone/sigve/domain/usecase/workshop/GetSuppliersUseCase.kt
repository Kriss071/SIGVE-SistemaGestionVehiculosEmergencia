package com.capstone.sigve.domain.usecase.workshop

import com.capstone.sigve.domain.model.Supplier
import com.capstone.sigve.domain.repository.WorkshopRepository
import javax.inject.Inject

class GetSuppliersUseCase @Inject constructor(
    private val workshopRepository: WorkshopRepository
) {
    suspend operator fun invoke(workshopId: Int): Result<List<Supplier>> {
        return workshopRepository.getSuppliers(workshopId)
    }
}

