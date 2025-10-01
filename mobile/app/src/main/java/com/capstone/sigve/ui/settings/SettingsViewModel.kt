package com.capstone.sigve.ui.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.capstone.sigve.data.repository.SettingsRepository
import com.capstone.sigve.domain.model.AppColor
import com.capstone.sigve.domain.model.AppTheme
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

class SettingsViewModel(private val settingsRepo: SettingsRepository): ViewModel() {

    val theme: StateFlow<AppTheme> = settingsRepo.themeFlow.stateIn(
        viewModelScope,
        SharingStarted.Eagerly,
        AppTheme.SYSTEM
    )

    val color: StateFlow<AppColor> = settingsRepo.colorFlow.stateIn(
        viewModelScope,
        SharingStarted.Eagerly,
        AppColor.DEFAULT
    )

    fun setTheme(theme: AppTheme){
        viewModelScope.launch { settingsRepo.setTheme(theme) }
    }

    fun setColor(color: AppColor){
        viewModelScope.launch { settingsRepo.setColor(color) }
    }

}