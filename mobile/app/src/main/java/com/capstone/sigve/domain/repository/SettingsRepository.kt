package com.capstone.sigve.domain.repository

import com.capstone.sigve.domain.model.AppColor
import com.capstone.sigve.domain.model.AppTheme
import com.capstone.sigve.domain.model.CustomColors
import kotlinx.coroutines.flow.Flow

interface SettingsRepository {
    val themeFlow: Flow<AppTheme>
    val colorFlow: Flow<AppColor>
    val customColorsFlow: Flow<CustomColors>

    suspend fun setTheme(theme: AppTheme)
    suspend fun setColor(color: AppColor)
    suspend fun setCustomColors(colors: CustomColors)
}

