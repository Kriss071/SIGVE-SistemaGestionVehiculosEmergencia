package com.capstone.sigve.domain.repository

import com.capstone.sigve.domain.model.AppTheme
import kotlinx.coroutines.flow.Flow

interface SettingsRepository {
    val themeFlow: Flow<AppTheme>
    suspend fun setTheme(theme: AppTheme)
}
