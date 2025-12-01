package com.capstone.sigve.ui.workshop

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Clear
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.Inventory
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.QrCode
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.ShoppingCart
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExposedDropdownMenuBox
import androidx.compose.material3.ExposedDropdownMenuDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.derivedStateOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.capstone.sigve.domain.model.SparePart
import com.capstone.sigve.domain.model.Supplier
import com.capstone.sigve.domain.model.WorkshopInventoryItem

@Composable
fun InventoryScreen(
    viewModel: InventoryViewModel = hiltViewModel()
) {
    val uiState by remember { derivedStateOf { viewModel.uiState } }
    val snackbarHostState = remember { SnackbarHostState() }

    LaunchedEffect(uiState.successMessage) {
        uiState.successMessage?.let {
            snackbarHostState.showSnackbar(it)
            viewModel.onDismissSuccessMessage()
        }
    }

    LaunchedEffect(uiState.error) {
        uiState.error?.let {
            snackbarHostState.showSnackbar(it)
            viewModel.onDismissError()
        }
    }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        floatingActionButton = {
            FloatingActionButton(
                onClick = { viewModel.onShowAddDialog() },
                containerColor = MaterialTheme.colorScheme.primary
            ) {
                Icon(Icons.Default.Add, contentDescription = "Agregar repuesto")
            }
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .background(MaterialTheme.colorScheme.background)
        ) {
            // Header con estadísticas
            InventoryHeader(
                totalItems = uiState.totalItems,
                totalValue = uiState.totalValue,
                lowStockItems = uiState.lowStockItems,
                outOfStockItems = uiState.outOfStockItems,
                onRefresh = { viewModel.onRefresh() }
            )

            // Barra de búsqueda y filtros
            SearchAndFilters(
                searchQuery = uiState.searchQuery,
                onSearchChange = viewModel::onSearchQueryChange,
                showOnlyAvailable = uiState.showOnlyAvailable,
                onToggleAvailable = viewModel::onToggleShowOnlyAvailable
            )

            when {
                uiState.isLoading -> {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        CircularProgressIndicator()
                    }
                }

                uiState.inventory.isEmpty() -> {
                    EmptyInventoryMessage()
                }

                uiState.filteredInventory.isEmpty() -> {
                    NoResultsMessage(onClearFilters = { viewModel.onSearchQueryChange("") })
                }

                else -> {
                    InventoryList(
                        items = uiState.filteredInventory,
                        onEditItem = viewModel::onShowEditDialog,
                        onDeleteItem = viewModel::onShowDeleteDialog
                    )
                }
            }
        }
    }

    // Diálogos
    if (uiState.showAddDialog) {
        AddInventoryDialog(
            availableSpareParts = uiState.availableSparePartsToAdd,
            suppliers = uiState.suppliers,
            selectedSparePartId = uiState.formSparePartId,
            selectedSupplierId = uiState.formSupplierId,
            quantity = uiState.formQuantity,
            currentCost = uiState.formCurrentCost,
            location = uiState.formLocation,
            workshopSku = uiState.formWorkshopSku,
            isValid = uiState.isFormValid && !uiState.sparePartAlreadyExists,
            isSaving = uiState.isSaving,
            onSparePartChange = viewModel::onFormSparePartChange,
            onSupplierChange = viewModel::onFormSupplierChange,
            onQuantityChange = viewModel::onFormQuantityChange,
            onCurrentCostChange = viewModel::onFormCurrentCostChange,
            onLocationChange = viewModel::onFormLocationChange,
            onWorkshopSkuChange = viewModel::onFormWorkshopSkuChange,
            onConfirm = viewModel::onConfirmAdd,
            onDismiss = viewModel::onDismissAddDialog
        )
    }

    if (uiState.showEditDialog && uiState.selectedItem != null) {
        EditInventoryDialog(
            item = uiState.selectedItem!!,
            suppliers = uiState.suppliers,
            selectedSupplierId = uiState.formSupplierId,
            quantity = uiState.formQuantity,
            currentCost = uiState.formCurrentCost,
            location = uiState.formLocation,
            workshopSku = uiState.formWorkshopSku,
            isValid = uiState.isFormValid,
            isSaving = uiState.isSaving,
            onSupplierChange = viewModel::onFormSupplierChange,
            onQuantityChange = viewModel::onFormQuantityChange,
            onCurrentCostChange = viewModel::onFormCurrentCostChange,
            onLocationChange = viewModel::onFormLocationChange,
            onWorkshopSkuChange = viewModel::onFormWorkshopSkuChange,
            onConfirm = viewModel::onConfirmEdit,
            onDismiss = viewModel::onDismissEditDialog
        )
    }

    if (uiState.showDeleteDialog && uiState.selectedItem != null) {
        DeleteConfirmDialog(
            item = uiState.selectedItem!!,
            isSaving = uiState.isSaving,
            onConfirm = viewModel::onConfirmDelete,
            onDismiss = viewModel::onDismissDeleteDialog
        )
    }
}

@Composable
private fun InventoryHeader(
    totalItems: Int,
    totalValue: Double,
    lowStockItems: Int,
    outOfStockItems: Int,
    onRefresh: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "Inventario del Taller",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )
            IconButton(onClick = onRefresh) {
                Icon(Icons.Default.Refresh, contentDescription = "Refrescar")
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        // Estadísticas en tarjetas
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            StatCard(
                modifier = Modifier.weight(1f),
                title = "Total",
                value = totalItems.toString(),
                subtitle = "repuestos",
                backgroundColor = MaterialTheme.colorScheme.primaryContainer
            )
            StatCard(
                modifier = Modifier.weight(1f),
                title = "Valor",
                value = "$${String.format("%,.0f", totalValue)}",
                subtitle = "inventario",
                backgroundColor = MaterialTheme.colorScheme.secondaryContainer
            )
            if (lowStockItems > 0 || outOfStockItems > 0) {
                StatCard(
                    modifier = Modifier.weight(1f),
                    title = "Alerta",
                    value = "${lowStockItems + outOfStockItems}",
                    subtitle = "bajo stock",
                    backgroundColor = MaterialTheme.colorScheme.errorContainer,
                    valueColor = MaterialTheme.colorScheme.error
                )
            }
        }
    }
}

@Composable
private fun StatCard(
    modifier: Modifier = Modifier,
    title: String,
    value: String,
    subtitle: String,
    backgroundColor: Color,
    valueColor: Color = MaterialTheme.colorScheme.onSurface
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = backgroundColor),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier.padding(12.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                text = value,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = valueColor
            )
            Text(
                text = subtitle,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun SearchAndFilters(
    searchQuery: String,
    onSearchChange: (String) -> Unit,
    showOnlyAvailable: Boolean,
    onToggleAvailable: () -> Unit
) {
    val focusManager = LocalFocusManager.current

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp)
    ) {
        OutlinedTextField(
            value = searchQuery,
            onValueChange = onSearchChange,
            modifier = Modifier.fillMaxWidth(),
            placeholder = { Text("Buscar por nombre, SKU o marca...") },
            leadingIcon = {
                Icon(Icons.Default.Search, contentDescription = null)
            },
            trailingIcon = {
                if (searchQuery.isNotEmpty()) {
                    IconButton(onClick = { onSearchChange("") }) {
                        Icon(Icons.Default.Clear, contentDescription = "Limpiar")
                    }
                }
            },
            singleLine = true,
            shape = RoundedCornerShape(12.dp),
            keyboardOptions = KeyboardOptions(imeAction = ImeAction.Search),
            keyboardActions = KeyboardActions(onSearch = { focusManager.clearFocus() })
        )

        Spacer(modifier = Modifier.height(8.dp))

        Row(
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            FilterChip(
                selected = showOnlyAvailable,
                onClick = onToggleAvailable,
                label = { Text("Solo disponibles") },
                leadingIcon = if (showOnlyAvailable) {
                    { Icon(Icons.Default.Inventory, contentDescription = null, modifier = Modifier.size(18.dp)) }
                } else null
            )
        }

        Spacer(modifier = Modifier.height(8.dp))
    }
}

@Composable
private fun InventoryList(
    items: List<WorkshopInventoryItem>,
    onEditItem: (WorkshopInventoryItem) -> Unit,
    onDeleteItem: (WorkshopInventoryItem) -> Unit
) {
    LazyColumn(
        contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        items(items, key = { it.id }) { item ->
            InventoryItemCard(
                item = item,
                onEdit = { onEditItem(item) },
                onDelete = { onDeleteItem(item) }
            )
        }
        
        item {
            Spacer(modifier = Modifier.height(80.dp)) // Espacio para FAB
        }
    }
}

@Composable
private fun InventoryItemCard(
    item: WorkshopInventoryItem,
    onEdit: () -> Unit,
    onDelete: () -> Unit
) {
    val stockColor = when {
        item.quantity == 0 -> Color(0xFFE53935)
        item.quantity <= 5 -> Color(0xFFFF9800)
        else -> Color(0xFF4CAF50)
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = item.sparePart.name,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    if (item.sparePart.brand != null) {
                        Text(
                            text = item.sparePart.brand,
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }

                // Badge de stock
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(8.dp))
                        .background(stockColor.copy(alpha = 0.1f))
                        .padding(horizontal = 12.dp, vertical = 6.dp)
                ) {
                    Text(
                        text = "${item.quantity} uds",
                        style = MaterialTheme.typography.labelMedium,
                        fontWeight = FontWeight.Bold,
                        color = stockColor
                    )
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Información adicional
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            Icons.Default.QrCode,
                            contentDescription = null,
                            modifier = Modifier.size(14.dp),
                            tint = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = "SKU: ${item.sparePart.sku}",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                    
                    if (item.workshopSku != null) {
                        Text(
                            text = "SKU Interno: ${item.workshopSku}",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                    
                    if (item.location != null) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                Icons.Default.LocationOn,
                                contentDescription = null,
                                modifier = Modifier.size(14.dp),
                                tint = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            Text(
                                text = item.location,
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                }

                Column(horizontalAlignment = Alignment.End) {
                    Text(
                        text = "$${String.format("%,.0f", item.currentCost)}",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.primary
                    )
                    Text(
                        text = "por unidad",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            if (item.supplier != null) {
                Spacer(modifier = Modifier.height(8.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        Icons.Default.ShoppingCart,
                        contentDescription = null,
                        modifier = Modifier.size(14.dp),
                        tint = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = "Proveedor: ${item.supplier.name}",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            Spacer(modifier = Modifier.height(12.dp))
            HorizontalDivider()
            Spacer(modifier = Modifier.height(8.dp))

            // Acciones
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.End
            ) {
                TextButton(onClick = onDelete) {
                    Icon(
                        Icons.Default.Delete,
                        contentDescription = null,
                        modifier = Modifier.size(18.dp),
                        tint = MaterialTheme.colorScheme.error
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("Eliminar", color = MaterialTheme.colorScheme.error)
                }
                
                Spacer(modifier = Modifier.width(8.dp))
                
                Button(onClick = onEdit) {
                    Icon(
                        Icons.Default.Edit,
                        contentDescription = null,
                        modifier = Modifier.size(18.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("Editar")
                }
            }
        }
    }
}

@Composable
private fun EmptyInventoryMessage() {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .padding(32.dp),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                Icons.Default.Inventory,
                contentDescription = null,
                modifier = Modifier.size(80.dp),
                tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.3f)
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = "Inventario vacío",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
            )
            Text(
                text = "Agrega repuestos usando el botón +",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.4f),
                textAlign = TextAlign.Center
            )
        }
    }
}

@Composable
private fun NoResultsMessage(onClearFilters: () -> Unit) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .padding(32.dp),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                Icons.Default.Search,
                contentDescription = null,
                modifier = Modifier.size(80.dp),
                tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.3f)
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = "Sin resultados",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
            )
            Spacer(modifier = Modifier.height(8.dp))
            TextButton(onClick = onClearFilters) {
                Text("Limpiar búsqueda")
            }
        }
    }
}

// ========== Diálogos ==========

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun AddInventoryDialog(
    availableSpareParts: List<SparePart>,
    suppliers: List<Supplier>,
    selectedSparePartId: Int?,
    selectedSupplierId: Int?,
    quantity: String,
    currentCost: String,
    location: String,
    workshopSku: String,
    isValid: Boolean,
    isSaving: Boolean,
    onSparePartChange: (Int) -> Unit,
    onSupplierChange: (Int?) -> Unit,
    onQuantityChange: (String) -> Unit,
    onCurrentCostChange: (String) -> Unit,
    onLocationChange: (String) -> Unit,
    onWorkshopSkuChange: (String) -> Unit,
    onConfirm: () -> Unit,
    onDismiss: () -> Unit
) {
    var sparePartExpanded by remember { mutableStateOf(false) }
    var supplierExpanded by remember { mutableStateOf(false) }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Agregar Repuesto al Inventario") },
        text = {
            Column(
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // Selector de repuesto maestro
                ExposedDropdownMenuBox(
                    expanded = sparePartExpanded,
                    onExpandedChange = { sparePartExpanded = it }
                ) {
                    OutlinedTextField(
                        value = availableSpareParts.find { it.id == selectedSparePartId }?.let { 
                            "${it.name}${it.brand?.let { b -> " - $b" } ?: ""}"
                        } ?: "",
                        onValueChange = {},
                        label = { Text("Repuesto *") },
                        readOnly = true,
                        trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = sparePartExpanded) },
                        modifier = Modifier
                            .fillMaxWidth()
                            .menuAnchor()
                    )

                    ExposedDropdownMenu(
                        expanded = sparePartExpanded,
                        onDismissRequest = { sparePartExpanded = false }
                    ) {
                        if (availableSpareParts.isEmpty()) {
                            DropdownMenuItem(
                                text = { Text("No hay repuestos disponibles") },
                                onClick = { },
                                enabled = false
                            )
                        } else {
                            availableSpareParts.forEach { sparePart ->
                                DropdownMenuItem(
                                    text = { 
                                        Column {
                                            Text(sparePart.name)
                                            Text(
                                                text = "SKU: ${sparePart.sku}${sparePart.brand?.let { " | $it" } ?: ""}",
                                                style = MaterialTheme.typography.bodySmall,
                                                color = MaterialTheme.colorScheme.onSurfaceVariant
                                            )
                                        }
                                    },
                                    onClick = {
                                        onSparePartChange(sparePart.id)
                                        sparePartExpanded = false
                                    }
                                )
                            }
                        }
                    }
                }

                Row(
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    OutlinedTextField(
                        value = quantity,
                        onValueChange = onQuantityChange,
                        label = { Text("Cantidad *") },
                        modifier = Modifier.weight(1f),
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                        singleLine = true
                    )

                    OutlinedTextField(
                        value = currentCost,
                        onValueChange = onCurrentCostChange,
                        label = { Text("Costo *") },
                        modifier = Modifier.weight(1f),
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                        prefix = { Text("$") },
                        singleLine = true
                    )
                }

                // Selector de proveedor
                ExposedDropdownMenuBox(
                    expanded = supplierExpanded,
                    onExpandedChange = { supplierExpanded = it }
                ) {
                    OutlinedTextField(
                        value = suppliers.find { it.id == selectedSupplierId }?.name ?: "Sin proveedor",
                        onValueChange = {},
                        label = { Text("Proveedor") },
                        readOnly = true,
                        trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = supplierExpanded) },
                        modifier = Modifier
                            .fillMaxWidth()
                            .menuAnchor()
                    )

                    ExposedDropdownMenu(
                        expanded = supplierExpanded,
                        onDismissRequest = { supplierExpanded = false }
                    ) {
                        DropdownMenuItem(
                            text = { Text("Sin proveedor") },
                            onClick = {
                                onSupplierChange(null)
                                supplierExpanded = false
                            }
                        )
                        suppliers.forEach { supplier ->
                            DropdownMenuItem(
                                text = { Text(supplier.name) },
                                onClick = {
                                    onSupplierChange(supplier.id)
                                    supplierExpanded = false
                                }
                            )
                        }
                    }
                }

                OutlinedTextField(
                    value = location,
                    onValueChange = onLocationChange,
                    label = { Text("Ubicación en bodega") },
                    modifier = Modifier.fillMaxWidth(),
                    placeholder = { Text("Ej: Estante A-3") },
                    singleLine = true
                )

                OutlinedTextField(
                    value = workshopSku,
                    onValueChange = onWorkshopSkuChange,
                    label = { Text("SKU interno del taller") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true
                )
            }
        },
        confirmButton = {
            Button(
                onClick = onConfirm,
                enabled = isValid && !isSaving
            ) {
                if (isSaving) {
                    CircularProgressIndicator(modifier = Modifier.size(16.dp))
                } else {
                    Text("Agregar")
                }
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss, enabled = !isSaving) {
                Text("Cancelar")
            }
        }
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun EditInventoryDialog(
    item: WorkshopInventoryItem,
    suppliers: List<Supplier>,
    selectedSupplierId: Int?,
    quantity: String,
    currentCost: String,
    location: String,
    workshopSku: String,
    isValid: Boolean,
    isSaving: Boolean,
    onSupplierChange: (Int?) -> Unit,
    onQuantityChange: (String) -> Unit,
    onCurrentCostChange: (String) -> Unit,
    onLocationChange: (String) -> Unit,
    onWorkshopSkuChange: (String) -> Unit,
    onConfirm: () -> Unit,
    onDismiss: () -> Unit
) {
    var supplierExpanded by remember { mutableStateOf(false) }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Editar Repuesto") },
        text = {
            Column(
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // Información del repuesto (solo lectura)
                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
                    )
                ) {
                    Column(modifier = Modifier.padding(12.dp)) {
                        Text(
                            text = item.sparePart.name,
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = "SKU: ${item.sparePart.sku}",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }

                Row(
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    OutlinedTextField(
                        value = quantity,
                        onValueChange = onQuantityChange,
                        label = { Text("Cantidad *") },
                        modifier = Modifier.weight(1f),
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                        singleLine = true
                    )

                    OutlinedTextField(
                        value = currentCost,
                        onValueChange = onCurrentCostChange,
                        label = { Text("Costo *") },
                        modifier = Modifier.weight(1f),
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                        prefix = { Text("$") },
                        singleLine = true
                    )
                }

                // Selector de proveedor
                ExposedDropdownMenuBox(
                    expanded = supplierExpanded,
                    onExpandedChange = { supplierExpanded = it }
                ) {
                    OutlinedTextField(
                        value = suppliers.find { it.id == selectedSupplierId }?.name ?: "Sin proveedor",
                        onValueChange = {},
                        label = { Text("Proveedor") },
                        readOnly = true,
                        trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = supplierExpanded) },
                        modifier = Modifier
                            .fillMaxWidth()
                            .menuAnchor()
                    )

                    ExposedDropdownMenu(
                        expanded = supplierExpanded,
                        onDismissRequest = { supplierExpanded = false }
                    ) {
                        DropdownMenuItem(
                            text = { Text("Sin proveedor") },
                            onClick = {
                                onSupplierChange(null)
                                supplierExpanded = false
                            }
                        )
                        suppliers.forEach { supplier ->
                            DropdownMenuItem(
                                text = { Text(supplier.name) },
                                onClick = {
                                    onSupplierChange(supplier.id)
                                    supplierExpanded = false
                                }
                            )
                        }
                    }
                }

                OutlinedTextField(
                    value = location,
                    onValueChange = onLocationChange,
                    label = { Text("Ubicación en bodega") },
                    modifier = Modifier.fillMaxWidth(),
                    placeholder = { Text("Ej: Estante A-3") },
                    singleLine = true
                )

                OutlinedTextField(
                    value = workshopSku,
                    onValueChange = onWorkshopSkuChange,
                    label = { Text("SKU interno del taller") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true
                )
            }
        },
        confirmButton = {
            Button(
                onClick = onConfirm,
                enabled = isValid && !isSaving
            ) {
                if (isSaving) {
                    CircularProgressIndicator(modifier = Modifier.size(16.dp))
                } else {
                    Text("Guardar")
                }
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss, enabled = !isSaving) {
                Text("Cancelar")
            }
        }
    )
}

@Composable
private fun DeleteConfirmDialog(
    item: WorkshopInventoryItem,
    isSaving: Boolean,
    onConfirm: () -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        icon = {
            Icon(
                Icons.Default.Warning,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.error
            )
        },
        title = { Text("Eliminar Repuesto") },
        text = {
            Column {
                Text("¿Estás seguro de eliminar este repuesto del inventario?")
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = item.displayName,
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "Cantidad: ${item.quantity} unidades",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        },
        confirmButton = {
            Button(
                onClick = onConfirm,
                enabled = !isSaving,
                colors = ButtonDefaults.buttonColors(
                    containerColor = MaterialTheme.colorScheme.error
                )
            ) {
                if (isSaving) {
                    CircularProgressIndicator(modifier = Modifier.size(16.dp))
                } else {
                    Text("Eliminar")
                }
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss, enabled = !isSaving) {
                Text("Cancelar")
            }
        }
    )
}

