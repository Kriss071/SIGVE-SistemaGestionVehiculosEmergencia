package com.capstone.sigve.domain.usecase.settings

import com.capstone.sigve.domain.model.AppTheme
import com.capstone.sigve.domain.repository.SettingsRepository
import javax.inject.Inject

class SetThemeUseCase @Inject constructor(
    private val settingsRepository: SettingsRepository
) {
    suspend operator fun invoke(theme: AppTheme) {
        settingsRepository.setTheme(theme)
    }
}

