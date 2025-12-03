package com.capstone.sigve.ui.firestation

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.capstone.sigve.domain.usecase.firestation.GetVehicleHistoryUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class VehicleHistoryViewModel @Inject constructor(
    private val getVehicleHistoryUseCase: GetVehicleHistoryUseCase
) : ViewModel() {

    var uiState by mutableStateOf(VehicleHistoryUiState())
        private set

    private var currentVehicleId: Int? = null

    fun loadHistory(vehicleId: Int) {
        if (currentVehicleId == vehicleId && uiState.vehicleHistory != null) {
            // Ya está cargado, no recargar
            return
        }
        
        currentVehicleId = vehicleId
        viewModelScope.launch {
            uiState = uiState.copy(isLoading = true, error = null)
            
            val result = getVehicleHistoryUseCase(vehicleId)
            
            if (result.isFailure) {
                uiState = uiState.copy(
                    isLoading = false,
                    error = "Error al cargar historial: ${result.exceptionOrNull()?.message ?: "Error desconocido"}"
                )
            } else {
                uiState = uiState.copy(
                    isLoading = false,
                    vehicleHistory = result.getOrNull(),
                    error = null
                )
            }
        }
    }

    fun onRefresh() {
        currentVehicleId?.let { loadHistory(it) }
    }

    fun onItemClick(itemId: Int) {
        uiState = uiState.copy(
            selectedItemId = if (uiState.selectedItemId == itemId) null else itemId
        )
    }

    fun onDismissError() {
        uiState = uiState.copy(error = null)
    }
}

