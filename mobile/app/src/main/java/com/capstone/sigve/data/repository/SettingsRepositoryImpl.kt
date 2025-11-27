package com.capstone.sigve.data.repository

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.longPreferencesKey
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.capstone.sigve.domain.model.AppColor
import com.capstone.sigve.domain.model.AppTheme
import com.capstone.sigve.domain.model.CustomColors
import com.capstone.sigve.domain.repository.SettingsRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject


private val Context.datastore by preferencesDataStore("settings")

class SettingsRepositoryImpl @Inject constructor(
    private val context: Context
) : SettingsRepository {

    private val THEME_KEY = stringPreferencesKey("app_theme")
    private val COLOR_KEY = stringPreferencesKey("app_color")

    private val CUSTOM_PRIMARY = longPreferencesKey("custom_primary")
    private val CUSTOM_SECONDARY = longPreferencesKey("custom_secondary")
    private val CUSTOM_TERTIARY = longPreferencesKey("custom_tertiary")
    private val CUSTOM_BACKGROUND = longPreferencesKey("custom_background")

    override val themeFlow: Flow<AppTheme> = context.datastore.data.map {
        when (it[THEME_KEY]) {
            "LIGHT" -> AppTheme.LIGHT
            "DARK" -> AppTheme.DARK
            else -> AppTheme.SYSTEM
        }
    }

    override val colorFlow: Flow<AppColor> = context.datastore.data.map {
        when (it[COLOR_KEY]) {
            "BLUE" -> AppColor.BLUE
            "GREEN" -> AppColor.GREEN
            "RED" -> AppColor.RED
            "CUSTOM" -> AppColor.CUSTOM
            else -> AppColor.DEFAULT
        }
    }

    override val customColorsFlow: Flow<CustomColors> = context.datastore.data.map {
        CustomColors(
            primary = it[CUSTOM_PRIMARY] ?: 0xFF6200EE,
            secondary = it[CUSTOM_SECONDARY] ?: 0xFF03DAC6,
            tertiary = it[CUSTOM_TERTIARY] ?: 0xFFBB86FC,
            background = it[CUSTOM_BACKGROUND] ?: 0xFFE7E7E7
        )
    }

    override suspend fun setTheme(theme: AppTheme) {
        context.datastore.edit { it[THEME_KEY] = theme.name }
    }

    override suspend fun setColor(color: AppColor) {
        context.datastore.edit { it[COLOR_KEY] = color.name }
    }

    override suspend fun setCustomColors(colors: CustomColors) {
        context.datastore.edit {
            it[CUSTOM_PRIMARY] = colors.primary
            it[CUSTOM_SECONDARY] = colors.secondary
            it[CUSTOM_TERTIARY] = colors.tertiary
            it[CUSTOM_BACKGROUND] = colors.background
        }
    }
}

