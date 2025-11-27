package com.capstone.sigve.domain.usecase.settings

import com.capstone.sigve.domain.model.CustomColors
import com.capstone.sigve.domain.repository.SettingsRepository
import javax.inject.Inject

class SetCustomColorsUseCase @Inject constructor(
    private val settingsRepository: SettingsRepository
) {
    suspend operator fun invoke(colors: CustomColors) {
        settingsRepository.setCustomColors(colors)
    }
}

