package com.capstone.sigve.domain.usecase.settings

import com.capstone.sigve.domain.model.CustomColors
import com.capstone.sigve.domain.repository.SettingsRepository
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject

class GetCustomColorsUseCase @Inject constructor(
    private val settingsRepository: SettingsRepository
) {
    operator fun invoke(): Flow<CustomColors> {
        return settingsRepository.customColorsFlow
    }
}

