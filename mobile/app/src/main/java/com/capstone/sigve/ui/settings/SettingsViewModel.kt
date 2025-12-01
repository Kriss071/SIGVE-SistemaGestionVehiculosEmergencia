package com.capstone.sigve.ui.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.capstone.sigve.domain.model.AppTheme
import com.capstone.sigve.domain.usecase.settings.GetThemeUseCase
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
    private val setThemeUseCase: SetThemeUseCase
) : ViewModel() {

    val theme: StateFlow<AppTheme> = getThemeUseCase().stateIn(
        viewModelScope,
        SharingStarted.Eagerly,
        AppTheme.SYSTEM
    )

    fun setTheme(theme: AppTheme) {
        viewModelScope.launch { setThemeUseCase(theme) }
    }
}
