package com.capstone.sigve.domain.usecase.workshop

import com.capstone.sigve.domain.model.TaskType
import com.capstone.sigve.domain.repository.WorkshopRepository
import javax.inject.Inject

class GetTaskTypesUseCase @Inject constructor(
    private val workshopRepository: WorkshopRepository
) {
    suspend operator fun invoke(): Result<List<TaskType>> {
        return workshopRepository.getTaskTypes()
    }
}

