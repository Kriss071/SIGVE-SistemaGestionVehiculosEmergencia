package com.capstone.sigve.ui.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.capstone.sigve.domain.model.AppColor
import com.capstone.sigve.domain.model.AppTheme
import com.capstone.sigve.domain.model.CustomColors
import com.capstone.sigve.domain.usecase.settings.GetColorUseCase
import com.capstone.sigve.domain.usecase.settings.GetCustomColorsUseCase
import com.capstone.sigve.domain.usecase.settings.GetThemeUseCase
import com.capstone.sigve.domain.usecase.settings.SetColorUseCase
import com.capstone.sigve.domain.usecase.settings.SetCustomColorsUseCase
import com.capstone.sigve.domain.usecase.settings.SetThemeUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class SettingsViewModel @Inject constructor(
    getThemeUseCase: GetThemeUseCase,
    getColorUseCase: GetColorUseCase,
    getCustomColorsUseCase: GetCustomColorsUseCase,
    private val setThemeUseCase: SetThemeUseCase,
    private val setColorUseCase: SetColorUseCase,
    private val setCustomColorsUseCase: SetCustomColorsUseCase
) : ViewModel() {

    val theme: StateFlow<AppTheme> = getThemeUseCase().stateIn(
        viewModelScope,
        SharingStarted.Eagerly,
        AppTheme.SYSTEM
    )

    val color: StateFlow<AppColor> = getColorUseCase().stateIn(
        viewModelScope,
        SharingStarted.Eagerly,
        AppColor.DEFAULT
    )

    val customColors: StateFlow<CustomColors> = getCustomColorsUseCase().stateIn(
        viewModelScope,
        SharingStarted.Eagerly,
        CustomColors()
    )

    fun setTheme(theme: AppTheme) {
        viewModelScope.launch { setThemeUseCase(theme) }
    }

    fun setColor(color: AppColor) {
        viewModelScope.launch { setColorUseCase(color) }
    }

    fun setCustomColors(colors: CustomColors) {
        viewModelScope.launch { setCustomColorsUseCase(colors) }
    }
}