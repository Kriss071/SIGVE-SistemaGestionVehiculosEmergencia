package com.capstone.sigve.ui.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.capstone.sigve.data.repository.SettingsRepository
import com.capstone.sigve.domain.model.AppColor
import com.capstone.sigve.domain.model.AppTheme
import com.capstone.sigve.domain.model.CustomColors
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

class SettingsViewModel(private val settingsRepo: SettingsRepository): ViewModel() {

    private val _theme: StateFlow<AppTheme> = settingsRepo.themeFlow.stateIn(
        viewModelScope,
        SharingStarted.Eagerly,
        AppTheme.SYSTEM
    )

    private val _color: StateFlow<AppColor> = settingsRepo.colorFlow.stateIn(
        viewModelScope,
        SharingStarted.Eagerly,
        AppColor.DEFAULT
    )

    private val _customColors: StateFlow<CustomColors> = settingsRepo.customColorsFlow.stateIn(
        viewModelScope,
        SharingStarted.Eagerly,
        CustomColors()
    )

    // Getters
    val theme: StateFlow<AppTheme>
        get() = _theme

    val color: StateFlow<AppColor>
        get() = _color

    val customColors: StateFlow<CustomColors>
        get() = _customColors


    fun setTheme(theme: AppTheme){
        viewModelScope.launch { settingsRepo.setTheme(theme) }
    }

    fun setColor(color: AppColor){
        viewModelScope.launch { settingsRepo.setColor(color) }
    }

    fun setCustomColors(colors: CustomColors){
        viewModelScope.launch { settingsRepo.setCustomColors(colors) }
    }
}