package com.capstone.sigve.domain.usecase.settings

import com.capstone.sigve.domain.model.AppColor
import com.capstone.sigve.domain.repository.SettingsRepository
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject

class GetColorUseCase @Inject constructor(
    private val settingsRepository: SettingsRepository
) {
    operator fun invoke(): Flow<AppColor> {
        return settingsRepository.colorFlow
    }
}

