package com.capstone.sigve.ui.workshop

import android.util.Log
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.capstone.sigve.domain.model.MaintenanceOrderStatus
import com.capstone.sigve.domain.model.MaintenanceType
import com.capstone.sigve.domain.usecase.auth.GetCurrentUserUseCase
import com.capstone.sigve.domain.usecase.workshop.GetActiveMaintenanceOrdersUseCase
import com.capstone.sigve.domain.usecase.workshop.GetWorkshopByIdUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class WorkshopViewModel @Inject constructor(
    private val getCurrentUserUseCase: GetCurrentUserUseCase,
    private val getWorkshopByIdUseCase: GetWorkshopByIdUseCase,
    private val getActiveMaintenanceOrdersUseCase: GetActiveMaintenanceOrdersUseCase
) : ViewModel() {

    companion object {
        private const val TAG = "WorkshopViewModel"
    }

    var uiState by mutableStateOf(WorkshopUiState())
        private set

    init {
        loadWorkshopData()
    }

    fun loadWorkshopData() {
        viewModelScope.launch {
            Log.d(TAG, "Iniciando carga de datos del taller...")
            uiState = uiState.copy(isLoading = true, error = null)

            // Primero obtener el usuario actual para saber su workshop_id
            Log.d(TAG, "Obteniendo usuario actual...")
            val userResult = getCurrentUserUseCase()
            
            userResult.fold(
                onSuccess = { userProfile ->
                    Log.d(TAG, "Usuario obtenido: ${userProfile.fullName}, Rol: ${userProfile.role.name}")
                    Log.d(TAG, "Workshop ID del usuario: ${userProfile.workshopId}")
                    
                    val workshopId = userProfile.workshopId
                    
                    if (workshopId == null) {
                        Log.w(TAG, "Usuario no tiene workshop_id asignado")
                        uiState = uiState.copy(
                            isLoading = false,
                            error = "Usuario no asociado a ningún taller"
                        )
                        return@launch
                    }

                    // Obtener información del taller
                    Log.d(TAG, "Obteniendo información del taller ID: $workshopId")
                    val workshopResult = getWorkshopByIdUseCase(workshopId)
                    workshopResult.fold(
                        onSuccess = { workshop ->
                            Log.d(TAG, "Taller obtenido: ${workshop.name}")
                            uiState = uiState.copy(workshop = workshop)
                        },
                        onFailure = { error ->
                            Log.e(TAG, "Error al cargar taller: ${error.message}", error)
                            uiState = uiState.copy(
                                isLoading = false,
                                error = "Error al cargar taller: ${error.message}"
                            )
                            return@launch
                        }
                    )

                    // Obtener órdenes activas del taller
                    Log.d(TAG, "Obteniendo órdenes activas del taller...")
                    val ordersResult = getActiveMaintenanceOrdersUseCase(workshopId)
                    ordersResult.fold(
                        onSuccess = { orders ->
                            Log.d(TAG, "Órdenes activas obtenidas: ${orders.size}")
                            orders.forEach { order ->
                                Log.d(TAG, "  - Orden #${order.id}: ${order.vehicle.licensePlate} - ${order.status.name}")
                            }
                            uiState = uiState.copy(
                                isLoading = false,
                                activeOrders = orders
                            )
                        },
                        onFailure = { error ->
                            Log.e(TAG, "Error al cargar órdenes: ${error.message}", error)
                            uiState = uiState.copy(
                                isLoading = false,
                                error = "Error al cargar órdenes: ${error.message}"
                            )
                        }
                    )
                },
                onFailure = { error ->
                    Log.e(TAG, "Error al obtener usuario: ${error.message}", error)
                    uiState = uiState.copy(
                        isLoading = false,
                        error = "Error al obtener usuario: ${error.message}"
                    )
                }
            )
        }
    }

    fun onRefresh() {
        Log.d(TAG, "Refrescando datos...")
        loadWorkshopData()
    }

    // ========== Funciones de búsqueda y filtros ==========
    
    fun onSearchQueryChange(query: String) {
        uiState = uiState.copy(searchQuery = query)
    }

    fun onStatusFilterChange(status: MaintenanceOrderStatus?) {
        uiState = uiState.copy(selectedStatusFilter = status)
    }

    fun onMaintenanceTypeFilterChange(type: MaintenanceType?) {
        uiState = uiState.copy(selectedMaintenanceTypeFilter = type)
    }

    fun onFireStationFilterChange(fireStation: String?) {
        uiState = uiState.copy(selectedFireStationFilter = fireStation)
    }

    fun onToggleFilters() {
        uiState = uiState.copy(isFilterExpanded = !uiState.isFilterExpanded)
    }

    fun onClearFilters() {
        uiState = uiState.copy(
            searchQuery = "",
            selectedStatusFilter = null,
            selectedMaintenanceTypeFilter = null,
            selectedFireStationFilter = null
        )
    }
}
