package com.capstone.sigve.data.repository

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.capstone.sigve.domain.model.AppColor
import com.capstone.sigve.domain.model.AppTheme
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map


private val Context.datastore by preferencesDataStore("settings")

class SettingsRepository(private val context: Context) {

    private val THEME_KEY = stringPreferencesKey("app_theme")
    private val COLOR_KEY = stringPreferencesKey("app_color")

    val themeFlow: Flow<AppTheme> = context.datastore.data.map {
        when (it[THEME_KEY]) {
            "LIGHT" -> AppTheme.LIGHT
            "DARK" -> AppTheme.DARK
            else -> AppTheme.SYSTEM
        }
    }

    val colorFlow: Flow<AppColor> = context.datastore.data.map {
        when (it[COLOR_KEY]) {
            "BLUE" -> AppColor.BLUE
            "GREEN" -> AppColor.GREEN
            "RED" -> AppColor.RED
            else -> AppColor.DEFAULT
        }
    }

    suspend fun setTheme(theme: AppTheme){
        context.datastore.edit { it[THEME_KEY] = theme.name }
    }

    suspend fun setColor(color: AppColor){
        context.datastore.edit { it[COLOR_KEY] = color.name}
    }
}