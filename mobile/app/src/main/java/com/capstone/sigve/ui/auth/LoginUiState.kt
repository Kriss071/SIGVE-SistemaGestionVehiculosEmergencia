package com.capstone.sigve.ui.auth

import com.capstone.sigve.domain.model.AppModule
import com.capstone.sigve.domain.model.UserProfile

data class LoginUiState(
    val isLoading: Boolean = false,
    val error: String? = null,
    val userProfile: UserProfile? = null,
    val navigateTo: AppModule? = null
)