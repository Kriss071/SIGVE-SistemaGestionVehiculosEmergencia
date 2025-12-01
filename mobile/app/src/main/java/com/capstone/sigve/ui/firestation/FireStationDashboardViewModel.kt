package com.capstone.sigve.ui.firestation

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.capstone.sigve.domain.usecase.auth.GetCurrentUserUseCase
import com.capstone.sigve.domain.usecase.firestation.GetFireStationByIdUseCase
import com.capstone.sigve.domain.usecase.firestation.GetFireStationStatsUseCase
import com.capstone.sigve.domain.usecase.firestation.GetFireStationVehiclesUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class FireStationDashboardViewModel @Inject constructor(
    private val getCurrentUserUseCase: GetCurrentUserUseCase,
    private val getFireStationByIdUseCase: GetFireStationByIdUseCase,
    private val getFireStationVehiclesUseCase: GetFireStationVehiclesUseCase,
    private val getFireStationStatsUseCase: GetFireStationStatsUseCase
) : ViewModel() {

    var uiState by mutableStateOf(FireStationDashboardUiState())
        private set

    private var fireStationId: Int? = null

    init {
        loadDashboardData()
    }

    private fun loadDashboardData() {
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
            
            // Cargar datos del cuartel en paralelo
            val fireStationDeferred = getFireStationByIdUseCase(fireStationId!!)
            val vehiclesDeferred = getFireStationVehiclesUseCase(fireStationId!!)
            val statsDeferred = getFireStationStatsUseCase(fireStationId!!)
            
            // Procesar resultados
            val fireStationResult = fireStationDeferred
            val vehiclesResult = vehiclesDeferred
            val statsResult = statsDeferred
            
            if (fireStationResult.isFailure) {
                uiState = uiState.copy(
                    isLoading = false,
                    error = "Error al cargar cuartel: ${fireStationResult.exceptionOrNull()?.message}"
                )
                return@launch
            }
            
            uiState = uiState.copy(
                isLoading = false,
                fireStation = fireStationResult.getOrNull(),
                vehicles = vehiclesResult.getOrDefault(emptyList()),
                stats = statsResult.getOrDefault(uiState.stats),
                error = if (vehiclesResult.isFailure || statsResult.isFailure) {
                    "Algunos datos no se pudieron cargar completamente"
                } else null
            )
        }
    }

    fun onRefresh() {
        loadDashboardData()
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

