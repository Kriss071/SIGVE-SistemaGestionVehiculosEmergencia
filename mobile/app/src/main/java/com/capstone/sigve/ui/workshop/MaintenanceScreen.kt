package com.capstone.sigve.ui.workshop

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.expandVertically
import androidx.compose.animation.shrinkVertically
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Build
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Clear
import androidx.compose.material.icons.filled.DirectionsCar
import androidx.compose.material.icons.filled.FilterList
import androidx.compose.material.icons.filled.History
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.LocalFireDepartment
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.derivedStateOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.capstone.sigve.domain.model.MaintenanceOrder
import com.capstone.sigve.domain.model.MaintenanceOrderStatus
import com.capstone.sigve.domain.model.MaintenanceType

/**
 * Pantalla de Mantenciones - Lista de vehículos con órdenes activas y completadas
 */
@Composable
fun MaintenanceScreen(
    onOrderClick: (Int) -> Unit = {},
    viewModel: WorkshopViewModel = hiltViewModel()
) {
    val uiState by remember { derivedStateOf { viewModel.uiState } }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        // Header
        MaintenanceHeader(
            totalCount = uiState.totalOrdersCount,
            filteredCount = uiState.vehicleCount,
            hasActiveFilters = uiState.hasActiveFilters,
            onRefresh = { viewModel.onRefresh() }
        )

        // Toggle de órdenes completadas
        CompletedOrdersToggle(
            showCompleted = uiState.showCompletedOrders,
            completedCount = uiState.completedOrdersCount,
            activeCount = uiState.activeOrdersCount,
            onToggle = { viewModel.onToggleShowCompleted() }
        )

        // Barra de búsqueda
        SearchBar(
            query = uiState.searchQuery,
            onQueryChange = { viewModel.onSearchQueryChange(it) },
            isFilterExpanded = uiState.isFilterExpanded,
            hasActiveFilters = uiState.hasActiveFilters,
            onToggleFilters = { viewModel.onToggleFilters() },
            onClearFilters = { viewModel.onClearFilters() }
        )

        // Panel de filtros expandible
        AnimatedVisibility(
            visible = uiState.isFilterExpanded,
            enter = expandVertically(),
            exit = shrinkVertically()
        ) {
            FiltersPanel(
                availableStatuses = uiState.availableStatuses,
                selectedStatus = uiState.selectedStatusFilter,
                onStatusSelected = { viewModel.onStatusFilterChange(it) },
                availableMaintenanceTypes = uiState.availableMaintenanceTypes,
                selectedMaintenanceType = uiState.selectedMaintenanceTypeFilter,
                onMaintenanceTypeSelected = { viewModel.onMaintenanceTypeFilterChange(it) },
                availableFireStations = uiState.availableFireStations,
                selectedFireStation = uiState.selectedFireStationFilter,
                onFireStationSelected = { viewModel.onFireStationFilterChange(it) }
            )
        }

        when {
            uiState.isLoading -> {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            }

            uiState.error != null -> {
                ErrorMessage(
                    message = uiState.error!!,
                    onRetry = { viewModel.onRefresh() }
                )
            }

            uiState.activeOrders.isEmpty() && uiState.completedOrders.isEmpty() -> {
                EmptyVehiclesMessage()
            }

            uiState.filteredOrders.isEmpty() -> {
                NoResultsMessage(onClearFilters = { viewModel.onClearFilters() })
            }

            else -> {
                VehiclesList(
                    orders = uiState.filteredOrders,
                    onOrderClick = onOrderClick
                )
            }
        }
    }
}

@Composable
private fun MaintenanceHeader(
    totalCount: Int,
    filteredCount: Int,
    hasActiveFilters: Boolean,
    onRefresh: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column {
            Text(
                text = "Órdenes de Mantención",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )
            Text(
                text = if (hasActiveFilters) {
                    "$filteredCount de $totalCount orden${if (totalCount != 1) "es" else ""}"
                } else {
                    "$totalCount orden${if (totalCount != 1) "es" else ""}"
                },
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
        IconButton(onClick = onRefresh) {
            Icon(
                imageVector = Icons.Default.Refresh,
                contentDescription = "Refrescar"
            )
        }
    }
}

@Composable
private fun CompletedOrdersToggle(
    showCompleted: Boolean,
    completedCount: Int,
    activeCount: Int,
    onToggle: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp)
            .clickable { onToggle() },
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (showCompleted) 
                Color(0xFF4CAF50).copy(alpha = 0.1f) 
            else 
                MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.weight(1f)
            ) {
                Icon(
                    imageVector = if (showCompleted) Icons.Default.History else Icons.Default.Build,
                    contentDescription = null,
                    modifier = Modifier.size(20.dp),
                    tint = if (showCompleted) Color(0xFF4CAF50) else MaterialTheme.colorScheme.primary
                )
                Spacer(modifier = Modifier.width(8.dp))
                Column {
                    Text(
                        text = if (showCompleted) "Todas las órdenes" else "Solo activas",
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Medium
                    )
                    Text(
                        text = if (completedCount > 0) {
                            "$activeCount activas · $completedCount completadas"
                        } else {
                            "$activeCount activas · Sin órdenes completadas"
                        },
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            Switch(
                checked = showCompleted,
                onCheckedChange = { onToggle() },
                colors = SwitchDefaults.colors(
                    checkedThumbColor = Color(0xFF4CAF50),
                    checkedTrackColor = Color(0xFF4CAF50).copy(alpha = 0.5f)
                )
            )
        }
    }
    Spacer(modifier = Modifier.height(8.dp))
}

@Composable
private fun SearchBar(
    query: String,
    onQueryChange: (String) -> Unit,
    isFilterExpanded: Boolean,
    hasActiveFilters: Boolean,
    onToggleFilters: () -> Unit,
    onClearFilters: () -> Unit
) {
    val focusManager = LocalFocusManager.current

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        OutlinedTextField(
            value = query,
            onValueChange = onQueryChange,
            modifier = Modifier.weight(1f),
            placeholder = { Text("Buscar por patente, marca o modelo...") },
            leadingIcon = {
                Icon(
                    imageVector = Icons.Default.Search,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.onSurfaceVariant
                )
            },
            trailingIcon = {
                if (query.isNotEmpty()) {
                    IconButton(onClick = { onQueryChange("") }) {
                        Icon(
                            imageVector = Icons.Default.Clear,
                            contentDescription = "Limpiar búsqueda"
                        )
                    }
                }
            },
            singleLine = true,
            shape = RoundedCornerShape(12.dp),
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = MaterialTheme.colorScheme.primary,
                unfocusedBorderColor = MaterialTheme.colorScheme.outline.copy(alpha = 0.5f)
            ),
            keyboardOptions = KeyboardOptions(imeAction = ImeAction.Search),
            keyboardActions = KeyboardActions(onSearch = { focusManager.clearFocus() })
        )

        // Botón de filtros
        Box {
            IconButton(
                onClick = onToggleFilters,
                modifier = Modifier
                    .clip(RoundedCornerShape(12.dp))
                    .background(
                        if (isFilterExpanded || hasActiveFilters)
                            MaterialTheme.colorScheme.primaryContainer
                        else
                            MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
                    )
            ) {
                Icon(
                    imageVector = Icons.Default.FilterList,
                    contentDescription = "Filtros",
                    tint = if (isFilterExpanded || hasActiveFilters)
                        MaterialTheme.colorScheme.onPrimaryContainer
                    else
                        MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            // Indicador de filtros activos
            if (hasActiveFilters) {
                Box(
                    modifier = Modifier
                        .align(Alignment.TopEnd)
                        .size(10.dp)
                        .clip(CircleShape)
                        .background(Color(0xFFDF2532))
                )
            }
        }
    }

    Spacer(modifier = Modifier.height(8.dp))
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun FiltersPanel(
    availableStatuses: List<MaintenanceOrderStatus>,
    selectedStatus: MaintenanceOrderStatus?,
    onStatusSelected: (MaintenanceOrderStatus?) -> Unit,
    availableMaintenanceTypes: List<MaintenanceType>,
    selectedMaintenanceType: MaintenanceType?,
    onMaintenanceTypeSelected: (MaintenanceType?) -> Unit,
    availableFireStations: List<String>,
    selectedFireStation: String?,
    onFireStationSelected: (String?) -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f))
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // Filtro por Estado
        if (availableStatuses.isNotEmpty()) {
            FilterSection(title = "Estado") {
                Row(
                    modifier = Modifier.horizontalScroll(rememberScrollState()),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    availableStatuses.forEach { status ->
                        val isSelected = selectedStatus?.id == status.id
                        FilterChip(
                            selected = isSelected,
                            onClick = {
                                onStatusSelected(if (isSelected) null else status)
                            },
                            label = { Text(status.name) },
                            colors = FilterChipDefaults.filterChipColors(
                                selectedContainerColor = getStatusColor(status.name).copy(alpha = 0.2f),
                                selectedLabelColor = getStatusColor(status.name)
                            ),
                            border = FilterChipDefaults.filterChipBorder(
                                borderColor = if (isSelected) getStatusColor(status.name) else MaterialTheme.colorScheme.outline,
                                selectedBorderColor = getStatusColor(status.name),
                                enabled = true,
                                selected = isSelected
                            )
                        )
                    }
                }
            }
        }

        // Filtro por Tipo de Mantención
        if (availableMaintenanceTypes.isNotEmpty()) {
            FilterSection(title = "Tipo de Mantención") {
                Row(
                    modifier = Modifier.horizontalScroll(rememberScrollState()),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    availableMaintenanceTypes.forEach { type ->
                        val isSelected = selectedMaintenanceType?.id == type.id
                        FilterChip(
                            selected = isSelected,
                            onClick = {
                                onMaintenanceTypeSelected(if (isSelected) null else type)
                            },
                            label = { Text(type.name) },
                            leadingIcon = if (isSelected) {
                                {
                                    Icon(
                                        imageVector = Icons.Default.Build,
                                        contentDescription = null,
                                        modifier = Modifier.size(18.dp)
                                    )
                                }
                            } else null
                        )
                    }
                }
            }
        }

        // Filtro por Cuartel
        if (availableFireStations.isNotEmpty()) {
            FilterSection(title = "Cuartel de Origen") {
                Row(
                    modifier = Modifier.horizontalScroll(rememberScrollState()),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    availableFireStations.forEach { fireStation ->
                        val isSelected = selectedFireStation == fireStation
                        FilterChip(
                            selected = isSelected,
                            onClick = {
                                onFireStationSelected(if (isSelected) null else fireStation)
                            },
                            label = { Text(fireStation) },
                            leadingIcon = if (isSelected) {
                                {
                                    Icon(
                                        imageVector = Icons.Default.LocalFireDepartment,
                                        contentDescription = null,
                                        modifier = Modifier.size(18.dp),
                                        tint = Color(0xFFDF2532)
                                    )
                                }
                            } else null
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun FilterSection(
    title: String,
    content: @Composable () -> Unit
) {
    Column {
        Text(
            text = title,
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            fontWeight = FontWeight.Medium
        )
        Spacer(modifier = Modifier.height(6.dp))
        content()
    }
}

@Composable
private fun getStatusColor(status: String): Color {
    return when (status.lowercase()) {
        "en taller" -> Color(0xFF4CAF50)
        "pendiente" -> Color(0xFFFF9800)
        "en espera de repuestos" -> Color(0xFF2196F3)
        "completada" -> Color(0xFF9E9E9E)
        else -> MaterialTheme.colorScheme.primary
    }
}

@Composable
private fun VehiclesList(
    orders: List<MaintenanceOrder>,
    onOrderClick: (Int) -> Unit
) {
    LazyColumn(
        contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        items(orders, key = { it.id }) { order ->
            VehicleOrderCard(
                order = order,
                onClick = { onOrderClick(order.id) }
            )
        }
    }
}

@Composable
private fun VehicleOrderCard(
    order: MaintenanceOrder,
    onClick: () -> Unit
) {
    val isCompleted = !order.isActive

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(12.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        colors = if (isCompleted) {
            CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
            )
        } else {
            CardDefaults.cardColors()
        }
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Icono del vehículo
                Box(
                    modifier = Modifier
                        .size(48.dp)
                        .clip(RoundedCornerShape(8.dp))
                        .background(
                            if (isCompleted) 
                                MaterialTheme.colorScheme.surfaceVariant
                            else 
                                MaterialTheme.colorScheme.secondaryContainer
                        ),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = if (isCompleted) Icons.Default.CheckCircle else Icons.Default.DirectionsCar,
                        contentDescription = null,
                        modifier = Modifier.size(28.dp),
                        tint = if (isCompleted) 
                            Color(0xFF4CAF50)
                        else 
                            MaterialTheme.colorScheme.onSecondaryContainer
                    )
                }

                Spacer(modifier = Modifier.width(12.dp))

                // Información del vehículo
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = order.vehicle.licensePlate,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = order.vehicle.displayName,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }

                Spacer(modifier = Modifier.width(8.dp))
                StatusBadge(status = order.status.name)
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Información adicional
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Cuartel de origen
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.LocalFireDepartment,
                        contentDescription = null,
                        modifier = Modifier.size(14.dp),
                        tint = Color(0xFFDF2532)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = order.vehicle.fireStationName,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                }

                // Tipo de mantención
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.Build,
                        contentDescription = null,
                        modifier = Modifier.size(14.dp),
                        tint = MaterialTheme.colorScheme.primary
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = order.maintenanceType.name,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                }
            }
        }
    }
}

@Composable
private fun StatusBadge(status: String) {
    val (backgroundColor, textColor) = when (status.lowercase()) {
        "en taller" -> Pair(Color(0xFF4CAF50), Color.White)
        "pendiente" -> Pair(Color(0xFFFF9800), Color.White)
        "en espera de repuestos" -> Pair(Color(0xFF2196F3), Color.White)
        "completada" -> Pair(Color(0xFF9E9E9E), Color.White)
        else -> Pair(MaterialTheme.colorScheme.surfaceVariant, MaterialTheme.colorScheme.onSurfaceVariant)
    }

    Text(
        text = status,
        style = MaterialTheme.typography.labelSmall,
        color = textColor,
        fontWeight = FontWeight.Medium,
        modifier = Modifier
            .clip(RoundedCornerShape(16.dp))
            .background(backgroundColor)
            .padding(horizontal = 8.dp, vertical = 4.dp)
    )
}

@Composable
private fun EmptyVehiclesMessage() {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .padding(32.dp),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Icon(
                imageVector = Icons.Default.DirectionsCar,
                contentDescription = null,
                modifier = Modifier.size(80.dp),
                tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.3f)
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = "No hay órdenes de mantención",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f),
                textAlign = TextAlign.Center
            )
            Text(
                text = "Las órdenes de mantención aparecerán aquí",
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
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Icon(
                imageVector = Icons.Default.Search,
                contentDescription = null,
                modifier = Modifier.size(80.dp),
                tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.3f)
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = "Sin resultados",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f),
                textAlign = TextAlign.Center
            )
            Text(
                text = "No se encontraron órdenes con los filtros aplicados",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.4f),
                textAlign = TextAlign.Center
            )
            Spacer(modifier = Modifier.height(16.dp))
            TextButton(onClick = onClearFilters) {
                Text("Limpiar filtros")
            }
        }
    }
}

@Composable
private fun ErrorMessage(
    message: String,
    onRetry: () -> Unit
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .padding(32.dp),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Icon(
                imageVector = Icons.Default.Info,
                contentDescription = null,
                modifier = Modifier.size(64.dp),
                tint = MaterialTheme.colorScheme.error
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = message,
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.error,
                textAlign = TextAlign.Center
            )
            Spacer(modifier = Modifier.height(16.dp))
            IconButton(onClick = onRetry) {
                Icon(
                    imageVector = Icons.Default.Refresh,
                    contentDescription = "Reintentar",
                    tint = MaterialTheme.colorScheme.primary
                )
            }
        }
    }
}
