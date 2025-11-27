package com.capstone.sigve.domain.usecase.settings

import com.capstone.sigve.domain.model.AppTheme
import com.capstone.sigve.domain.repository.SettingsRepository
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject

class GetThemeUseCase @Inject constructor(
    private val settingsRepository: SettingsRepository
) {
    operator fun invoke(): Flow<AppTheme> {
        return settingsRepository.themeFlow
    }
}

