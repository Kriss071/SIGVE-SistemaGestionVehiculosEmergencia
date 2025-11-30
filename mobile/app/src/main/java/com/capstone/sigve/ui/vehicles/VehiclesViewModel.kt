package com.capstone.sigve.ui.vehicles

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.capstone.sigve.domain.usecase.vehicles.GetVehiclesUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * @deprecated Este ViewModel será reemplazado por ViewModels específicos de cada módulo.
 */
@Deprecated("Usar ViewModels específicos de cada módulo")
@HiltViewModel
class VehiclesViewModel @Inject constructor(
    private val getVehiclesUseCase: GetVehiclesUseCase
) : ViewModel() {

    var uiState by mutableStateOf(VehiclesUiState())
        private set

    init {
        loadVehicles()
    }

    private fun loadVehicles() {
        viewModelScope.launch {
            uiState = uiState.copy(isLoading = true)
            val result = getVehiclesUseCase()
            uiState = result.fold(
                onSuccess = { vehicles ->
                    uiState.copy(isLoading = false, vehicles = vehicles)
                },
                onFailure = { error ->
                    uiState.copy(isLoading = false, error = error.message)
                }
            )
        }
    }
}