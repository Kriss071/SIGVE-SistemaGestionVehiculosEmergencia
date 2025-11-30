package com.capstone.sigve.ui.workshop

import com.capstone.sigve.domain.model.MaintenanceOrderDetail
import com.capstone.sigve.domain.model.MaintenanceOrderStatus
import com.capstone.sigve.domain.model.MaintenanceType
import com.capstone.sigve.domain.model.Mechanic
import com.capstone.sigve.domain.model.TaskType
import com.capstone.sigve.domain.model.WorkshopInventoryItem

data class OrderDetailUiState(
    val isLoading: Boolean = true,
    val isSaving: Boolean = false,
    val error: String? = null,
    val successMessage: String? = null,
    val order: MaintenanceOrderDetail? = null,
    
    // Catálogos para dropdowns
    val availableStatuses: List<MaintenanceOrderStatus> = emptyList(),
    val availableMaintenanceTypes: List<MaintenanceType> = emptyList(),
    val availableMechanics: List<Mechanic> = emptyList(),
    val availableTaskTypes: List<TaskType> = emptyList(),
    val availableInventory: List<WorkshopInventoryItem> = emptyList(),
    
    // Campos editables
    val selectedStatusId: Int? = null,
    val selectedMaintenanceTypeId: Int? = null,
    val selectedMechanicId: String? = null,
    val exitDate: String? = null,
    val observations: String = "",
    
    // Diálogos
    val showAddTaskDialog: Boolean = false,
    val showAddPartDialog: Boolean = false,
    val showExitDatePicker: Boolean = false,
    val selectedTaskIdForPart: Int? = null,
    
    // Campos para nuevo task
    val newTaskTypeId: Int? = null,
    val newTaskDescription: String = "",
    val newTaskCost: String = "",
    
    // Campos para nuevo part
    val newPartInventoryId: Int? = null,
    val newPartQuantity: String = "1",
    
    // Workshop ID para cargar mecánicos e inventario
    val workshopId: Int? = null
) {
    val isEditable: Boolean
        get() = order?.isEditable ?: false
    
    val isCompleted: Boolean
        get() = order?.isCompleted ?: false
    
    val showExitDateField: Boolean
        get() {
            val selectedStatus = availableStatuses.find { it.id == selectedStatusId }
            return selectedStatus?.name?.lowercase() == "completada"
        }
    
    val isExitDateRequired: Boolean
        get() = showExitDateField && exitDate.isNullOrBlank()
    
    val canSave: Boolean
        get() = isEditable && !isSaving && selectedStatusId != null && 
                selectedMaintenanceTypeId != null && !isExitDateRequired
    
    val hasChanges: Boolean
        get() {
            val currentOrder = order ?: return false
            return selectedStatusId != currentOrder.status.id ||
                   selectedMaintenanceTypeId != currentOrder.maintenanceType.id ||
                   selectedMechanicId != currentOrder.assignedMechanic?.id ||
                   observations != (currentOrder.observations ?: "") ||
                   exitDate != currentOrder.exitDate
        }
}

