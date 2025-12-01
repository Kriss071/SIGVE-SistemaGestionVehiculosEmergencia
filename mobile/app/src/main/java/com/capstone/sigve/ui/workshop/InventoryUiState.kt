package com.capstone.sigve.ui.workshop

import com.capstone.sigve.domain.model.SparePart
import com.capstone.sigve.domain.model.Supplier
import com.capstone.sigve.domain.model.WorkshopInventoryItem

data class InventoryUiState(
    val isLoading: Boolean = true,
    val isSaving: Boolean = false,
    val error: String? = null,
    val successMessage: String? = null,
    val inventory: List<WorkshopInventoryItem> = emptyList(),
    val workshopId: Int? = null,
    
    // Catálogos para crear/editar
    val masterSpareParts: List<SparePart> = emptyList(),
    val suppliers: List<Supplier> = emptyList(),
    
    // Búsqueda y filtros
    val searchQuery: String = "",
    val showOnlyAvailable: Boolean = false,
    
    // Diálogos
    val showAddDialog: Boolean = false,
    val showEditDialog: Boolean = false,
    val showDeleteDialog: Boolean = false,
    val selectedItem: WorkshopInventoryItem? = null,
    
    // Campos del formulario
    val formSparePartId: Int? = null,
    val formSupplierId: Int? = null,
    val formQuantity: String = "",
    val formCurrentCost: String = "",
    val formLocation: String = "",
    val formWorkshopSku: String = ""
) {
    val filteredInventory: List<WorkshopInventoryItem>
        get() = inventory.filter { item ->
            val matchesSearch = searchQuery.isBlank() ||
                item.sparePart.name.contains(searchQuery, ignoreCase = true) ||
                item.sparePart.sku.contains(searchQuery, ignoreCase = true) ||
                item.sparePart.brand?.contains(searchQuery, ignoreCase = true) == true ||
                item.workshopSku?.contains(searchQuery, ignoreCase = true) == true
            
            val matchesAvailability = !showOnlyAvailable || item.isAvailable
            
            matchesSearch && matchesAvailability
        }
    
    val totalItems: Int
        get() = inventory.size
    
    val totalValue: Double
        get() = inventory.sumOf { it.totalValue }
    
    val lowStockItems: Int
        get() = inventory.count { it.quantity <= 5 && it.quantity > 0 }
    
    val outOfStockItems: Int
        get() = inventory.count { it.quantity == 0 }
    
    val isFormValid: Boolean
        get() = formSparePartId != null &&
                formQuantity.toIntOrNull() != null &&
                formCurrentCost.toDoubleOrNull() != null
    
    // Para crear, verificar que el repuesto no exista ya en el inventario
    val sparePartAlreadyExists: Boolean
        get() = formSparePartId != null && 
                inventory.any { it.sparePart.id == formSparePartId }
    
    // Repuestos disponibles para agregar (que no estén ya en inventario)
    val availableSparePartsToAdd: List<SparePart>
        get() {
            val existingIds = inventory.map { it.sparePart.id }.toSet()
            return masterSpareParts.filter { it.id !in existingIds }
        }
}

