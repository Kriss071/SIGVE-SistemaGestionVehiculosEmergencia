package com.capstone.sigve.ui.workshop

import android.util.Log
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.capstone.sigve.domain.usecase.auth.GetCurrentUserUseCase
import com.capstone.sigve.domain.usecase.workshop.AddPartToTaskUseCase
import com.capstone.sigve.domain.usecase.workshop.CreateMaintenanceTaskUseCase
import com.capstone.sigve.domain.usecase.workshop.DeleteMaintenanceTaskUseCase
import com.capstone.sigve.domain.usecase.workshop.GetMaintenanceOrderDetailUseCase
import com.capstone.sigve.domain.usecase.workshop.GetMaintenanceOrderStatusesUseCase
import com.capstone.sigve.domain.usecase.workshop.GetMaintenanceTypesUseCase
import com.capstone.sigve.domain.usecase.workshop.GetTaskTypesUseCase
import com.capstone.sigve.domain.usecase.workshop.GetWorkshopInventoryUseCase
import com.capstone.sigve.domain.usecase.workshop.GetWorkshopMechanicsUseCase
import com.capstone.sigve.domain.usecase.workshop.RemovePartFromTaskUseCase
import com.capstone.sigve.domain.usecase.workshop.UpdateMaintenanceOrderUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class OrderDetailViewModel @Inject constructor(
    savedStateHandle: SavedStateHandle,
    private val getCurrentUserUseCase: GetCurrentUserUseCase,
    private val getMaintenanceOrderDetailUseCase: GetMaintenanceOrderDetailUseCase,
    private val getMaintenanceOrderStatusesUseCase: GetMaintenanceOrderStatusesUseCase,
    private val getMaintenanceTypesUseCase: GetMaintenanceTypesUseCase,
    private val getWorkshopMechanicsUseCase: GetWorkshopMechanicsUseCase,
    private val getTaskTypesUseCase: GetTaskTypesUseCase,
    private val getWorkshopInventoryUseCase: GetWorkshopInventoryUseCase,
    private val updateMaintenanceOrderUseCase: UpdateMaintenanceOrderUseCase,
    private val createMaintenanceTaskUseCase: CreateMaintenanceTaskUseCase,
    private val addPartToTaskUseCase: AddPartToTaskUseCase,
    private val deleteMaintenanceTaskUseCase: DeleteMaintenanceTaskUseCase,
    private val removePartFromTaskUseCase: RemovePartFromTaskUseCase
) : ViewModel() {

    companion object {
        private const val TAG = "OrderDetailViewModel"
    }

    private val orderId: Int = savedStateHandle.get<Int>("orderId") ?: 0

    var uiState by mutableStateOf(OrderDetailUiState())
        private set

    init {
        loadData()
    }

    private fun loadData() {
        viewModelScope.launch {
            Log.d(TAG, "Cargando datos para orden ID: $orderId")
            uiState = uiState.copy(isLoading = true, error = null)

            // Obtener workshopId del usuario actual
            val userResult = getCurrentUserUseCase()
            userResult.fold(
                onSuccess = { user ->
                    val workshopId = user.workshopId
                    if (workshopId == null) {
                        uiState = uiState.copy(
                            isLoading = false,
                            error = "Usuario no asociado a ningún taller"
                        )
                        return@launch
                    }
                    uiState = uiState.copy(workshopId = workshopId)
                    
                    // Cargar catálogos en paralelo
                    launch { loadStatuses() }
                    launch { loadMaintenanceTypes() }
                    launch { loadMechanics(workshopId) }
                    launch { loadTaskTypes() }
                    launch { loadInventory(workshopId) }
                    
                    // Cargar detalle de la orden
                    loadOrderDetail()
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

    private suspend fun loadOrderDetail() {
        getMaintenanceOrderDetailUseCase(orderId).fold(
            onSuccess = { order ->
                Log.d(TAG, "Orden cargada: #${order.id}")
                uiState = uiState.copy(
                    isLoading = false,
                    order = order,
                    selectedStatusId = order.status.id,
                    selectedMaintenanceTypeId = order.maintenanceType.id,
                    selectedMechanicId = order.assignedMechanic?.id,
                    exitDate = order.exitDate,
                    observations = order.observations ?: ""
                )
            },
            onFailure = { error ->
                Log.e(TAG, "Error al cargar orden: ${error.message}", error)
                uiState = uiState.copy(
                    isLoading = false,
                    error = "Error al cargar orden: ${error.message}"
                )
            }
        )
    }

    private suspend fun loadStatuses() {
        getMaintenanceOrderStatusesUseCase().fold(
            onSuccess = { statuses ->
                uiState = uiState.copy(availableStatuses = statuses)
            },
            onFailure = { error ->
                Log.e(TAG, "Error al cargar estados: ${error.message}", error)
            }
        )
    }

    private suspend fun loadMaintenanceTypes() {
        getMaintenanceTypesUseCase().fold(
            onSuccess = { types ->
                uiState = uiState.copy(availableMaintenanceTypes = types)
            },
            onFailure = { error ->
                Log.e(TAG, "Error al cargar tipos de mantención: ${error.message}", error)
            }
        )
    }

    private suspend fun loadMechanics(workshopId: Int) {
        getWorkshopMechanicsUseCase(workshopId).fold(
            onSuccess = { mechanics ->
                uiState = uiState.copy(availableMechanics = mechanics)
            },
            onFailure = { error ->
                Log.e(TAG, "Error al cargar mecánicos: ${error.message}", error)
            }
        )
    }

    private suspend fun loadTaskTypes() {
        getTaskTypesUseCase().fold(
            onSuccess = { types ->
                uiState = uiState.copy(availableTaskTypes = types)
            },
            onFailure = { error ->
                Log.e(TAG, "Error al cargar tipos de tarea: ${error.message}", error)
            }
        )
    }

    private suspend fun loadInventory(workshopId: Int) {
        getWorkshopInventoryUseCase(workshopId).fold(
            onSuccess = { inventory ->
                uiState = uiState.copy(availableInventory = inventory.filter { it.isAvailable })
            },
            onFailure = { error ->
                Log.e(TAG, "Error al cargar inventario: ${error.message}", error)
            }
        )
    }

    fun onRefresh() {
        loadData()
    }

    // ========== Cambios en campos editables ==========

    fun onStatusChange(statusId: Int) {
        uiState = uiState.copy(selectedStatusId = statusId)
        
        // Si se selecciona "Completada", mostrar selector de fecha
        val selectedStatus = uiState.availableStatuses.find { it.id == statusId }
        if (selectedStatus?.name?.lowercase() == "completada") {
            uiState = uiState.copy(showExitDatePicker = true)
        }
    }

    fun onMaintenanceTypeChange(typeId: Int) {
        uiState = uiState.copy(selectedMaintenanceTypeId = typeId)
    }

    fun onMechanicChange(mechanicId: String?) {
        uiState = uiState.copy(selectedMechanicId = mechanicId)
    }

    fun onObservationsChange(text: String) {
        uiState = uiState.copy(observations = text)
    }

    fun onExitDateChange(date: String) {
        uiState = uiState.copy(exitDate = date, showExitDatePicker = false)
    }

    fun onDismissExitDatePicker() {
        uiState = uiState.copy(showExitDatePicker = false)
    }

    // ========== Guardar cambios ==========

    fun onSaveChanges() {
        val currentOrder = uiState.order ?: return
        val statusId = uiState.selectedStatusId ?: return
        val typeId = uiState.selectedMaintenanceTypeId ?: return

        viewModelScope.launch {
            uiState = uiState.copy(isSaving = true, error = null)

            updateMaintenanceOrderUseCase(
                orderId = currentOrder.id,
                statusId = statusId,
                maintenanceTypeId = typeId,
                assignedMechanicId = uiState.selectedMechanicId,
                exitDate = uiState.exitDate,
                observations = uiState.observations.ifBlank { null },
                totalCost = currentOrder.calculatedTotalCost.takeIf { it > 0 }
            ).fold(
                onSuccess = {
                    uiState = uiState.copy(
                        isSaving = false,
                        successMessage = "Orden actualizada correctamente"
                    )
                    // Recargar datos
                    loadData()
                },
                onFailure = { error ->
                    Log.e(TAG, "Error al guardar: ${error.message}", error)
                    uiState = uiState.copy(
                        isSaving = false,
                        error = "Error al guardar: ${error.message}"
                    )
                }
            )
        }
    }

    fun onDismissSuccessMessage() {
        uiState = uiState.copy(successMessage = null)
    }

    fun onDismissError() {
        uiState = uiState.copy(error = null)
    }

    // ========== Diálogos de agregar tarea ==========

    fun onShowAddTaskDialog() {
        uiState = uiState.copy(
            showAddTaskDialog = true,
            newTaskTypeId = null,
            newTaskDescription = "",
            newTaskCost = ""
        )
    }

    fun onDismissAddTaskDialog() {
        uiState = uiState.copy(showAddTaskDialog = false)
    }

    fun onNewTaskTypeChange(typeId: Int) {
        uiState = uiState.copy(newTaskTypeId = typeId)
    }

    fun onNewTaskDescriptionChange(text: String) {
        uiState = uiState.copy(newTaskDescription = text)
    }

    fun onNewTaskCostChange(text: String) {
        // Solo permitir números y punto decimal
        if (text.isEmpty() || text.matches(Regex("^\\d*\\.?\\d*$"))) {
            uiState = uiState.copy(newTaskCost = text)
        }
    }

    fun onConfirmAddTask() {
        val taskTypeId = uiState.newTaskTypeId ?: return
        val cost = uiState.newTaskCost.toDoubleOrNull() ?: 0.0

        viewModelScope.launch {
            uiState = uiState.copy(isSaving = true)

            createMaintenanceTaskUseCase(
                maintenanceOrderId = orderId,
                taskTypeId = taskTypeId,
                description = uiState.newTaskDescription.ifBlank { null },
                cost = cost
            ).fold(
                onSuccess = {
                    uiState = uiState.copy(
                        isSaving = false,
                        showAddTaskDialog = false,
                        successMessage = "Tarea agregada correctamente"
                    )
                    loadData()
                },
                onFailure = { error ->
                    Log.e(TAG, "Error al crear tarea: ${error.message}", error)
                    uiState = uiState.copy(
                        isSaving = false,
                        error = "Error al crear tarea: ${error.message}"
                    )
                }
            )
        }
    }

    // ========== Diálogos de agregar repuesto ==========

    fun onShowAddPartDialog(taskId: Int) {
        uiState = uiState.copy(
            showAddPartDialog = true,
            selectedTaskIdForPart = taskId,
            newPartInventoryId = null,
            newPartQuantity = "1"
        )
    }

    fun onDismissAddPartDialog() {
        uiState = uiState.copy(showAddPartDialog = false, selectedTaskIdForPart = null)
    }

    fun onNewPartInventoryChange(inventoryId: Int) {
        uiState = uiState.copy(newPartInventoryId = inventoryId)
    }

    fun onNewPartQuantityChange(text: String) {
        if (text.isEmpty() || text.matches(Regex("^\\d+$"))) {
            uiState = uiState.copy(newPartQuantity = text)
        }
    }

    fun onConfirmAddPart() {
        val taskId = uiState.selectedTaskIdForPart ?: return
        val inventoryId = uiState.newPartInventoryId ?: return
        val quantity = uiState.newPartQuantity.toIntOrNull() ?: 1
        val inventoryItem = uiState.availableInventory.find { it.id == inventoryId }

        viewModelScope.launch {
            uiState = uiState.copy(isSaving = true)

            addPartToTaskUseCase(
                maintenanceTaskId = taskId,
                workshopInventoryId = inventoryId,
                quantityUsed = quantity,
                costPerUnit = inventoryItem?.currentCost
            ).fold(
                onSuccess = {
                    uiState = uiState.copy(
                        isSaving = false,
                        showAddPartDialog = false,
                        selectedTaskIdForPart = null,
                        successMessage = "Repuesto agregado correctamente"
                    )
                    loadData()
                },
                onFailure = { error ->
                    Log.e(TAG, "Error al agregar repuesto: ${error.message}", error)
                    uiState = uiState.copy(
                        isSaving = false,
                        error = "Error al agregar repuesto: ${error.message}"
                    )
                }
            )
        }
    }

    // ========== Eliminar tarea y repuestos ==========

    fun onDeleteTask(taskId: Int) {
        viewModelScope.launch {
            uiState = uiState.copy(isSaving = true)

            deleteMaintenanceTaskUseCase(taskId).fold(
                onSuccess = {
                    uiState = uiState.copy(
                        isSaving = false,
                        successMessage = "Tarea eliminada"
                    )
                    loadData()
                },
                onFailure = { error ->
                    Log.e(TAG, "Error al eliminar tarea: ${error.message}", error)
                    uiState = uiState.copy(
                        isSaving = false,
                        error = "Error al eliminar tarea: ${error.message}"
                    )
                }
            )
        }
    }

    fun onRemovePart(partId: Int) {
        viewModelScope.launch {
            uiState = uiState.copy(isSaving = true)

            removePartFromTaskUseCase(partId).fold(
                onSuccess = {
                    uiState = uiState.copy(
                        isSaving = false,
                        successMessage = "Repuesto eliminado"
                    )
                    loadData()
                },
                onFailure = { error ->
                    Log.e(TAG, "Error al eliminar repuesto: ${error.message}", error)
                    uiState = uiState.copy(
                        isSaving = false,
                        error = "Error al eliminar repuesto: ${error.message}"
                    )
                }
            )
        }
    }
}

