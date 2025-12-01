package com.capstone.sigve.ui.workshop

import android.util.Log
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.capstone.sigve.domain.model.WorkshopInventoryItem
import com.capstone.sigve.domain.usecase.auth.GetCurrentUserUseCase
import com.capstone.sigve.domain.usecase.workshop.CreateInventoryItemUseCase
import com.capstone.sigve.domain.usecase.workshop.DeleteInventoryItemUseCase
import com.capstone.sigve.domain.usecase.workshop.GetMasterSparePartsUseCase
import com.capstone.sigve.domain.usecase.workshop.GetSuppliersUseCase
import com.capstone.sigve.domain.usecase.workshop.GetWorkshopInventoryUseCase
import com.capstone.sigve.domain.usecase.workshop.UpdateInventoryItemUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class InventoryViewModel @Inject constructor(
    private val getCurrentUserUseCase: GetCurrentUserUseCase,
    private val getWorkshopInventoryUseCase: GetWorkshopInventoryUseCase,
    private val getMasterSparePartsUseCase: GetMasterSparePartsUseCase,
    private val getSuppliersUseCase: GetSuppliersUseCase,
    private val createInventoryItemUseCase: CreateInventoryItemUseCase,
    private val updateInventoryItemUseCase: UpdateInventoryItemUseCase,
    private val deleteInventoryItemUseCase: DeleteInventoryItemUseCase
) : ViewModel() {

    companion object {
        private const val TAG = "InventoryViewModel"
    }

    var uiState by mutableStateOf(InventoryUiState())
        private set

    init {
        loadData()
    }

    private fun loadData() {
        viewModelScope.launch {
            uiState = uiState.copy(isLoading = true, error = null)

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
                    
                    // Cargar datos en paralelo
                    launch { loadInventory(workshopId) }
                    launch { loadMasterSpareParts() }
                    launch { loadSuppliers(workshopId) }
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

    private suspend fun loadInventory(workshopId: Int) {
        getWorkshopInventoryUseCase(workshopId).fold(
            onSuccess = { inventory ->
                Log.d(TAG, "Inventario cargado: ${inventory.size} items")
                uiState = uiState.copy(
                    isLoading = false,
                    inventory = inventory
                )
            },
            onFailure = { error ->
                Log.e(TAG, "Error al cargar inventario: ${error.message}", error)
                uiState = uiState.copy(
                    isLoading = false,
                    error = "Error al cargar inventario: ${error.message}"
                )
            }
        )
    }

    private suspend fun loadMasterSpareParts() {
        getMasterSparePartsUseCase().fold(
            onSuccess = { spareParts ->
                Log.d(TAG, "Repuestos maestros cargados: ${spareParts.size}")
                uiState = uiState.copy(masterSpareParts = spareParts)
            },
            onFailure = { error ->
                Log.e(TAG, "Error al cargar repuestos maestros: ${error.message}", error)
            }
        )
    }

    private suspend fun loadSuppliers(workshopId: Int) {
        getSuppliersUseCase(workshopId).fold(
            onSuccess = { suppliers ->
                Log.d(TAG, "Proveedores cargados: ${suppliers.size}")
                uiState = uiState.copy(suppliers = suppliers)
            },
            onFailure = { error ->
                Log.e(TAG, "Error al cargar proveedores: ${error.message}", error)
            }
        )
    }

    fun onRefresh() {
        loadData()
    }

    // ========== Búsqueda y filtros ==========

    fun onSearchQueryChange(query: String) {
        uiState = uiState.copy(searchQuery = query)
    }

    fun onToggleShowOnlyAvailable() {
        uiState = uiState.copy(showOnlyAvailable = !uiState.showOnlyAvailable)
    }

    // ========== Diálogos ==========

    fun onShowAddDialog() {
        uiState = uiState.copy(
            showAddDialog = true,
            formSparePartId = null,
            formSupplierId = null,
            formQuantity = "",
            formCurrentCost = "",
            formLocation = "",
            formWorkshopSku = ""
        )
    }

    fun onDismissAddDialog() {
        uiState = uiState.copy(showAddDialog = false)
    }

    fun onShowEditDialog(item: WorkshopInventoryItem) {
        uiState = uiState.copy(
            showEditDialog = true,
            selectedItem = item,
            formSparePartId = item.sparePart.id,
            formSupplierId = item.supplier?.id,
            formQuantity = item.quantity.toString(),
            formCurrentCost = item.currentCost.toString(),
            formLocation = item.location ?: "",
            formWorkshopSku = item.workshopSku ?: ""
        )
    }

    fun onDismissEditDialog() {
        uiState = uiState.copy(showEditDialog = false, selectedItem = null)
    }

    fun onShowDeleteDialog(item: WorkshopInventoryItem) {
        uiState = uiState.copy(showDeleteDialog = true, selectedItem = item)
    }

    fun onDismissDeleteDialog() {
        uiState = uiState.copy(showDeleteDialog = false, selectedItem = null)
    }

    // ========== Campos del formulario ==========

    fun onFormSparePartChange(sparePartId: Int) {
        uiState = uiState.copy(formSparePartId = sparePartId)
    }

    fun onFormSupplierChange(supplierId: Int?) {
        uiState = uiState.copy(formSupplierId = supplierId)
    }

    fun onFormQuantityChange(quantity: String) {
        if (quantity.isEmpty() || quantity.matches(Regex("^\\d+$"))) {
            uiState = uiState.copy(formQuantity = quantity)
        }
    }

    fun onFormCurrentCostChange(cost: String) {
        if (cost.isEmpty() || cost.matches(Regex("^\\d*\\.?\\d*$"))) {
            uiState = uiState.copy(formCurrentCost = cost)
        }
    }

    fun onFormLocationChange(location: String) {
        uiState = uiState.copy(formLocation = location)
    }

    fun onFormWorkshopSkuChange(sku: String) {
        uiState = uiState.copy(formWorkshopSku = sku)
    }

    // ========== Acciones CRUD ==========

    fun onConfirmAdd() {
        val workshopId = uiState.workshopId ?: return
        val sparePartId = uiState.formSparePartId ?: return
        val quantity = uiState.formQuantity.toIntOrNull() ?: return
        val cost = uiState.formCurrentCost.toDoubleOrNull() ?: return

        viewModelScope.launch {
            uiState = uiState.copy(isSaving = true)

            createInventoryItemUseCase(
                workshopId = workshopId,
                sparePartId = sparePartId,
                supplierId = uiState.formSupplierId,
                quantity = quantity,
                currentCost = cost,
                location = uiState.formLocation.ifBlank { null },
                workshopSku = uiState.formWorkshopSku.ifBlank { null }
            ).fold(
                onSuccess = {
                    uiState = uiState.copy(
                        isSaving = false,
                        showAddDialog = false,
                        successMessage = "Repuesto agregado al inventario"
                    )
                    loadData()
                },
                onFailure = { error ->
                    Log.e(TAG, "Error al crear ítem: ${error.message}", error)
                    uiState = uiState.copy(
                        isSaving = false,
                        error = "Error al agregar repuesto: ${error.message}"
                    )
                }
            )
        }
    }

    fun onConfirmEdit() {
        val item = uiState.selectedItem ?: return
        val quantity = uiState.formQuantity.toIntOrNull() ?: return
        val cost = uiState.formCurrentCost.toDoubleOrNull() ?: return

        viewModelScope.launch {
            uiState = uiState.copy(isSaving = true)

            updateInventoryItemUseCase(
                inventoryId = item.id,
                supplierId = uiState.formSupplierId,
                quantity = quantity,
                currentCost = cost,
                location = uiState.formLocation.ifBlank { null },
                workshopSku = uiState.formWorkshopSku.ifBlank { null }
            ).fold(
                onSuccess = {
                    uiState = uiState.copy(
                        isSaving = false,
                        showEditDialog = false,
                        selectedItem = null,
                        successMessage = "Repuesto actualizado"
                    )
                    loadData()
                },
                onFailure = { error ->
                    Log.e(TAG, "Error al actualizar ítem: ${error.message}", error)
                    uiState = uiState.copy(
                        isSaving = false,
                        error = "Error al actualizar repuesto: ${error.message}"
                    )
                }
            )
        }
    }

    fun onConfirmDelete() {
        val item = uiState.selectedItem ?: return

        viewModelScope.launch {
            uiState = uiState.copy(isSaving = true)

            deleteInventoryItemUseCase(item.id).fold(
                onSuccess = {
                    uiState = uiState.copy(
                        isSaving = false,
                        showDeleteDialog = false,
                        selectedItem = null,
                        successMessage = "Repuesto eliminado del inventario"
                    )
                    loadData()
                },
                onFailure = { error ->
                    Log.e(TAG, "Error al eliminar ítem: ${error.message}", error)
                    uiState = uiState.copy(
                        isSaving = false,
                        error = "Error al eliminar repuesto: ${error.message}"
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
}

