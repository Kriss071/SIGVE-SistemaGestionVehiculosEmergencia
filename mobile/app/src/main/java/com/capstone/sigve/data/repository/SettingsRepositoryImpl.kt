package com.capstone.sigve.data.repository

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.capstone.sigve.domain.model.AppTheme
import com.capstone.sigve.domain.repository.SettingsRepository
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject

private val Context.datastore by preferencesDataStore("settings")

class SettingsRepositoryImpl @Inject constructor(
    private val context: Context
) : SettingsRepository {

    private val THEME_KEY = stringPreferencesKey("app_theme")

    override val themeFlow: Flow<AppTheme> = context.datastore.data.map {
        when (it[THEME_KEY]) {
            "LIGHT" -> AppTheme.LIGHT
            "DARK" -> AppTheme.DARK
            else -> AppTheme.SYSTEM
        }
    }

    override suspend fun setTheme(theme: AppTheme) {
        context.datastore.edit { it[THEME_KEY] = theme.name }
    }
}
