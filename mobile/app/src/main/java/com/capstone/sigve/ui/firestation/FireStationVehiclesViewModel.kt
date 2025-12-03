package com.capstone.sigve.ui.firestation

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.capstone.sigve.domain.usecase.auth.GetCurrentUserUseCase
import com.capstone.sigve.domain.usecase.firestation.GetFireStationVehiclesUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class FireStationVehiclesViewModel @Inject constructor(
    private val getCurrentUserUseCase: GetCurrentUserUseCase,
    private val getFireStationVehiclesUseCase: GetFireStationVehiclesUseCase
) : ViewModel() {

    var uiState by mutableStateOf(FireStationVehiclesUiState())
        private set

    private var fireStationId: Int? = null

    init {
        loadVehicles()
    }

    private fun loadVehicles() {
        viewModelScope.launch {
            uiState = uiState.copy(isLoading = true, error = null)
            
            // Obtener el usuario actual para obtener el fire_station_id
            val userResult = getCurrentUserUseCase()
            if (userResult.isFailure) {
                uiState = uiState.copy(
                    isLoading = false,
                    error = "Error al obtener usuario: ${userResult.exceptionOrNull()?.message}"
                )
                return@launch
            }
            
            val user = userResult.getOrThrow()
            fireStationId = user.fireStationId
            
            if (fireStationId == null) {
                uiState = uiState.copy(
                    isLoading = false,
                    error = "El usuario no tiene un cuartel asignado"
                )
                return@launch
            }
            
            // Cargar vehículos del cuartel
            val vehiclesResult = getFireStationVehiclesUseCase(fireStationId!!)
            
            uiState = if (vehiclesResult.isSuccess) {
                uiState.copy(
                    isLoading = false,
                    vehicles = vehiclesResult.getOrThrow(),
                    error = null
                )
            } else {
                uiState.copy(
                    isLoading = false,
                    error = "Error al cargar vehículos: ${vehiclesResult.exceptionOrNull()?.message}"
                )
            }
        }
    }

    fun onRefresh() {
        loadVehicles()
    }

    fun onSearchQueryChange(query: String) {
        uiState = uiState.copy(searchQuery = query)
    }

    fun onStatusFilterChange(filter: String?) {
        uiState = uiState.copy(
            selectedStatusFilter = if (filter == "all") null else filter
        )
    }

    fun onDismissError() {
        uiState = uiState.copy(error = null)
    }
}



