package com.capstone.sigve.ui.vehicles

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.capstone.sigve.domain.repository.VehiclesRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class VehiclesViewModel @Inject constructor(
    private val vehiclesRepository: VehiclesRepository
) : ViewModel() {

    var uiState by mutableStateOf(VehiclesUiState())
        private set

    init {
        loadVehicles()
    }

    private fun loadVehicles() {
        viewModelScope.launch {
            uiState = uiState.copy(isLoading = true)
            val result = vehiclesRepository.getVehicles()
            uiState = result.fold(onSuccess = { vehicles ->
                uiState.copy(isLoading = false, vehicles = vehicles)
            }, onFailure = { error ->
                uiState.copy(isLoading = false, error = error.message)
            })
        }
    }

}