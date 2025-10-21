package com.capstone.sigve.ui.auth

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.capstone.sigve.domain.repository.AuthRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class AuthViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {

    var uiState by mutableStateOf(LoginUiState())

    var email by mutableStateOf("")
    var password by mutableStateOf("")

    fun onEmailChange(newEmail: String) {
        email = newEmail
        if (uiState.error != null) uiState = uiState.copy(error = null)
    }

    fun onPasswordChange(newPassword: String) {
        password = newPassword
        if (uiState.error != null) uiState = uiState.copy(error = null)
    }

    fun onLoginClicked() {
        if (uiState.isLoading) return

        viewModelScope.launch {
            uiState = LoginUiState(isLoading = true)

            val result = authRepository.signIn(email, password)

            result.fold(
                onSuccess = {
                    uiState = LoginUiState(loginSuccess = true)
                },
                onFailure = { error ->
                    uiState = LoginUiState(error = error.message ?: "Error desconocido")
                }
            )
        }
    }

    fun onLoginSuccessShown() {
        uiState = uiState.copy(loginSuccess = false)
    }
}