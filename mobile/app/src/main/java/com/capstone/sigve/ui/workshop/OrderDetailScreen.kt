package com.capstone.sigve.ui.workshop

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
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
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Build
import androidx.compose.material.icons.filled.CalendarMonth
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.DirectionsCar
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.Error
import androidx.compose.material.icons.filled.ExpandLess
import androidx.compose.material.icons.filled.ExpandMore
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.LocalFireDepartment
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Speed
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DatePicker
import androidx.compose.material3.DatePickerDialog
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExposedDropdownMenuBox
import androidx.compose.material3.ExposedDropdownMenuDefaults
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Snackbar
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.CenterAlignedTopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.material3.rememberDatePickerState
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
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.capstone.sigve.domain.model.MaintenanceOrderDetail
import com.capstone.sigve.domain.model.MaintenanceOrderStatus
import com.capstone.sigve.domain.model.MaintenanceTask
import com.capstone.sigve.domain.model.MaintenanceType
import com.capstone.sigve.domain.model.Mechanic
import com.capstone.sigve.domain.model.TaskType
import com.capstone.sigve.domain.model.WorkshopInventoryItem
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun OrderDetailScreen(
    onNavigateBack: () -> Unit,
    viewModel: OrderDetailViewModel = hiltViewModel()
) {
    val uiState by remember { derivedStateOf { viewModel.uiState } }
    val snackbarHostState = remember { SnackbarHostState() }

    // Mostrar mensajes
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
        topBar = {
            CenterAlignedTopAppBar(
                title = { 
                    Text(
                        text = uiState.order?.let { "Orden #${it.id}" } ?: "Detalle de Orden",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                        color = Color.White
                    )
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(
                            Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Volver",
                            tint = Color.White
                        )
                    }
                },
                actions = {
                    if (!uiState.isLoading && uiState.order != null) {
                        IconButton(onClick = { viewModel.onRefresh() }) {
                            Icon(
                                Icons.Default.Refresh,
                                contentDescription = "Refrescar",
                                tint = Color.White
                            )
                        }
                    }
                },
                colors = TopAppBarDefaults.centerAlignedTopAppBarColors(
                    containerColor = Color(0xFFDF2532)
                )
            )
        },
        snackbarHost = { SnackbarHost(snackbarHostState) },
        floatingActionButton = {
            if (uiState.isEditable && uiState.hasChanges) {
                FloatingActionButton(
                    onClick = { viewModel.onSaveChanges() },
                    containerColor = MaterialTheme.colorScheme.primary
                ) {
                    if (uiState.isSaving) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(24.dp),
                            color = MaterialTheme.colorScheme.onPrimary
                        )
                    } else {
                        Icon(Icons.Default.Check, contentDescription = "Guardar")
                    }
                }
            }
        }
    ) { paddingValues ->
        when {
            uiState.isLoading -> {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(paddingValues),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            }

            uiState.order == null -> {
                ErrorContent(
                    message = uiState.error ?: "No se pudo cargar la orden",
                    onRetry = { viewModel.onRefresh() },
                    modifier = Modifier.padding(paddingValues)
                )
            }

            else -> {
                OrderDetailContent(
                    uiState = uiState,
                    onStatusChange = viewModel::onStatusChange,
                    onMaintenanceTypeChange = viewModel::onMaintenanceTypeChange,
                    onMechanicChange = viewModel::onMechanicChange,
                    onObservationsChange = viewModel::onObservationsChange,
                    onExitDateChange = viewModel::onExitDateChange,
                    onShowAddTaskDialog = viewModel::onShowAddTaskDialog,
                    onShowAddPartDialog = viewModel::onShowAddPartDialog,
                    onDeleteTask = viewModel::onDeleteTask,
                    onRemovePart = viewModel::onRemovePart,
                    modifier = Modifier.padding(paddingValues)
                )
            }
        }
    }

    // Diálogos
    if (uiState.showAddTaskDialog) {
        AddTaskDialog(
            taskTypes = uiState.availableTaskTypes,
            selectedTypeId = uiState.newTaskTypeId,
            description = uiState.newTaskDescription,
            cost = uiState.newTaskCost,
            isSaving = uiState.isSaving,
            onTypeChange = viewModel::onNewTaskTypeChange,
            onDescriptionChange = viewModel::onNewTaskDescriptionChange,
            onCostChange = viewModel::onNewTaskCostChange,
            onConfirm = viewModel::onConfirmAddTask,
            onDismiss = viewModel::onDismissAddTaskDialog
        )
    }

    if (uiState.showAddPartDialog) {
        AddPartDialog(
            inventory = uiState.availableInventory,
            selectedInventoryId = uiState.newPartInventoryId,
            quantity = uiState.newPartQuantity,
            isSaving = uiState.isSaving,
            onInventoryChange = viewModel::onNewPartInventoryChange,
            onQuantityChange = viewModel::onNewPartQuantityChange,
            onConfirm = viewModel::onConfirmAddPart,
            onDismiss = viewModel::onDismissAddPartDialog
        )
    }

    if (uiState.showExitDatePicker) {
        ExitDatePickerDialog(
            onDateSelected = viewModel::onExitDateChange,
            onDismiss = viewModel::onDismissExitDatePicker
        )
    }
}

@Composable
private fun OrderDetailContent(
    uiState: OrderDetailUiState,
    onStatusChange: (Int) -> Unit,
    onMaintenanceTypeChange: (Int) -> Unit,
    onMechanicChange: (String?) -> Unit,
    onObservationsChange: (String) -> Unit,
    onExitDateChange: (String) -> Unit,
    onShowAddTaskDialog: () -> Unit,
    onShowAddPartDialog: (Int) -> Unit,
    onDeleteTask: (Int) -> Unit,
    onRemovePart: (Int) -> Unit,
    modifier: Modifier = Modifier
) {
    val order = uiState.order ?: return

    LazyColumn(
        modifier = modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Banner de orden completada
        if (order.isCompleted) {
            item {
                CompletedOrderBanner()
            }
        }

        // Sección: Información del Vehículo
        item {
            VehicleInfoCard(order = order)
        }

        // Sección: Información de la Orden (editable)
        item {
            OrderInfoCard(
                order = order,
                uiState = uiState,
                onStatusChange = onStatusChange,
                onMaintenanceTypeChange = onMaintenanceTypeChange,
                onMechanicChange = onMechanicChange,
                onExitDateChange = onExitDateChange
            )
        }

        // Sección: Observaciones
        item {
            ObservationsCard(
                observations = uiState.observations,
                isEditable = uiState.isEditable,
                onObservationsChange = onObservationsChange
            )
        }

        // Sección: Tareas realizadas
        item {
            TasksHeader(
                taskCount = order.taskCount,
                isEditable = uiState.isEditable,
                onAddTask = onShowAddTaskDialog
            )
        }

        if (order.tasks.isEmpty()) {
            item {
                EmptyTasksMessage()
            }
        } else {
            items(order.tasks, key = { it.id }) { task ->
                TaskCard(
                    task = task,
                    isEditable = uiState.isEditable,
                    onAddPart = { onShowAddPartDialog(task.id) },
                    onDeleteTask = { onDeleteTask(task.id) },
                    onRemovePart = onRemovePart
                )
            }
        }

        // Resumen de costos
        item {
            CostSummaryCard(order = order)
        }

        // Espacio para el FAB
        item {
            Spacer(modifier = Modifier.height(80.dp))
        }
    }
}

@Composable
private fun CompletedOrderBanner() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = Color(0xFF4CAF50).copy(alpha = 0.1f)
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = Icons.Default.Lock,
                contentDescription = null,
                tint = Color(0xFF4CAF50),
                modifier = Modifier.size(24.dp)
            )
            Spacer(modifier = Modifier.width(12.dp))
            Column {
                Text(
                    text = "Orden Completada",
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF4CAF50)
                )
                Text(
                    text = "Esta orden ha sido cerrada y no puede ser modificada",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun VehicleInfoCard(order: MaintenanceOrderDetail) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            SectionHeader(
                icon = Icons.Default.DirectionsCar,
                title = "Información del Vehículo"
            )

            Spacer(modifier = Modifier.height(12.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .size(56.dp)
                        .clip(RoundedCornerShape(8.dp))
                        .background(MaterialTheme.colorScheme.secondaryContainer),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Default.DirectionsCar,
                        contentDescription = null,
                        modifier = Modifier.size(32.dp),
                        tint = MaterialTheme.colorScheme.onSecondaryContainer
                    )
                }

                Spacer(modifier = Modifier.width(16.dp))

                Column {
                    Text(
                        text = order.vehicle.licensePlate,
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = order.vehicle.displayName,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                InfoChip(
                    icon = Icons.Default.LocalFireDepartment,
                    text = order.vehicle.fireStationName,
                    iconTint = Color(0xFFDF2532)
                )
                InfoChip(
                    icon = Icons.Default.Speed,
                    text = "${order.mileage} km"
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun OrderInfoCard(
    order: MaintenanceOrderDetail,
    uiState: OrderDetailUiState,
    onStatusChange: (Int) -> Unit,
    onMaintenanceTypeChange: (Int) -> Unit,
    onMechanicChange: (String?) -> Unit,
    onExitDateChange: (String) -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            SectionHeader(
                icon = Icons.Default.Edit,
                title = "Información de la Orden"
            )

            Spacer(modifier = Modifier.height(16.dp))

            // Fecha de ingreso (solo lectura)
            InfoRow(label = "Fecha de Ingreso", value = order.entryDate)

            Spacer(modifier = Modifier.height(12.dp))

            // Estado (dropdown)
            DropdownField(
                label = "Estado",
                selectedValue = uiState.availableStatuses.find { it.id == uiState.selectedStatusId }?.name ?: "",
                options = uiState.availableStatuses.map { it.id to it.name },
                enabled = uiState.isEditable,
                onOptionSelected = { onStatusChange(it) }
            )

            // Fecha de salida (si es completada)
            AnimatedVisibility(visible = uiState.showExitDateField) {
                Column {
                    Spacer(modifier = Modifier.height(12.dp))
                    OutlinedTextField(
                        value = uiState.exitDate ?: "",
                        onValueChange = { },
                        label = { Text("Fecha de Salida *") },
                        modifier = Modifier.fillMaxWidth(),
                        enabled = uiState.isEditable,
                        readOnly = true,
                        isError = uiState.isExitDateRequired,
                        supportingText = if (uiState.isExitDateRequired) {
                            { Text("La fecha de salida es obligatoria para cerrar la orden") }
                        } else null,
                        trailingIcon = {
                            IconButton(
                                onClick = { onExitDateChange("") },
                                enabled = uiState.isEditable
                            ) {
                                Icon(Icons.Default.CalendarMonth, contentDescription = "Seleccionar fecha")
                            }
                        }
                    )
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Tipo de mantención (dropdown)
            DropdownField(
                label = "Tipo de Mantención",
                selectedValue = uiState.availableMaintenanceTypes.find { it.id == uiState.selectedMaintenanceTypeId }?.name ?: "",
                options = uiState.availableMaintenanceTypes.map { it.id to it.name },
                enabled = uiState.isEditable,
                onOptionSelected = { onMaintenanceTypeChange(it) }
            )

            Spacer(modifier = Modifier.height(12.dp))

            // Mecánico asignado (dropdown)
            DropdownField(
                label = "Mecánico Asignado",
                selectedValue = uiState.availableMechanics.find { it.id == uiState.selectedMechanicId }?.fullName ?: "Sin asignar",
                options = listOf(null to "Sin asignar") + uiState.availableMechanics.map { it.id to it.fullName },
                enabled = uiState.isEditable,
                onOptionSelected = { id -> onMechanicChange(id as? String) }
            )
        }
    }
}

@Composable
private fun ObservationsCard(
    observations: String,
    isEditable: Boolean,
    onObservationsChange: (String) -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            SectionHeader(
                icon = Icons.Default.Info,
                title = "Observaciones"
            )

            Spacer(modifier = Modifier.height(12.dp))

            OutlinedTextField(
                value = observations,
                onValueChange = onObservationsChange,
                modifier = Modifier.fillMaxWidth(),
                enabled = isEditable,
                placeholder = { Text("Notas generales sobre la mantención...") },
                minLines = 3,
                maxLines = 5
            )
        }
    }
}

@Composable
private fun TasksHeader(
    taskCount: Int,
    isEditable: Boolean,
    onAddTask: () -> Unit
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(
                imageVector = Icons.Default.Build,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.width(8.dp))
            Text(
                text = "Tareas Realizadas ($taskCount)",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
        }

        if (isEditable) {
            Button(
                onClick = onAddTask,
                contentPadding = PaddingValues(horizontal = 12.dp, vertical = 8.dp)
            ) {
                Icon(Icons.Default.Add, contentDescription = null, modifier = Modifier.size(18.dp))
                Spacer(modifier = Modifier.width(4.dp))
                Text("Agregar")
            }
        }
    }
}

@Composable
private fun EmptyTasksMessage() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(32.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                imageVector = Icons.Default.Build,
                contentDescription = null,
                modifier = Modifier.size(48.dp),
                tint = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f)
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "No hay tareas registradas",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
private fun TaskCard(
    task: MaintenanceTask,
    isEditable: Boolean,
    onAddPart: () -> Unit,
    onDeleteTask: () -> Unit,
    onRemovePart: (Int) -> Unit
) {
    var isExpanded by remember { mutableStateOf(true) }

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            // Header de la tarea
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.weight(1f)
                ) {
                    Box(
                        modifier = Modifier
                            .size(40.dp)
                            .clip(RoundedCornerShape(8.dp))
                            .background(MaterialTheme.colorScheme.primaryContainer),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Default.Settings,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.onPrimaryContainer
                        )
                    }
                    Spacer(modifier = Modifier.width(12.dp))
                    Column {
                        Text(
                            text = task.taskType.name,
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold
                        )
                        if (!task.description.isNullOrBlank()) {
                            Text(
                                text = task.description,
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                }

                Row {
                    IconButton(onClick = { isExpanded = !isExpanded }) {
                        Icon(
                            imageVector = if (isExpanded) Icons.Default.ExpandLess else Icons.Default.ExpandMore,
                            contentDescription = if (isExpanded) "Contraer" else "Expandir"
                        )
                    }
                    if (isEditable) {
                        IconButton(onClick = onDeleteTask) {
                            Icon(
                                imageVector = Icons.Default.Delete,
                                contentDescription = "Eliminar tarea",
                                tint = MaterialTheme.colorScheme.error
                            )
                        }
                    }
                }
            }

            AnimatedVisibility(visible = isExpanded) {
                Column {
                    Spacer(modifier = Modifier.height(12.dp))
                    HorizontalDivider()
                    Spacer(modifier = Modifier.height(12.dp))

                    // Costo de mano de obra
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(
                            text = "Mano de obra:",
                            style = MaterialTheme.typography.bodyMedium
                        )
                        Text(
                            text = "$${String.format("%.0f", task.cost)}",
                            style = MaterialTheme.typography.bodyMedium,
                            fontWeight = FontWeight.Medium
                        )
                    }

                    Spacer(modifier = Modifier.height(8.dp))

                    // Repuestos
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "Repuestos (${task.parts.size}):",
                            style = MaterialTheme.typography.bodyMedium,
                            fontWeight = FontWeight.Medium
                        )
                        if (isEditable) {
                            TextButton(onClick = onAddPart) {
                                Icon(Icons.Default.Add, contentDescription = null, modifier = Modifier.size(16.dp))
                                Spacer(modifier = Modifier.width(4.dp))
                                Text("Agregar")
                            }
                        }
                    }

                    if (task.parts.isEmpty()) {
                        Text(
                            text = "Sin repuestos",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier.padding(start = 8.dp)
                        )
                    } else {
                        task.parts.forEach { part ->
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(vertical = 4.dp),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Column(modifier = Modifier.weight(1f)) {
                                    Text(
                                        text = part.inventoryItem.displayName,
                                        style = MaterialTheme.typography.bodySmall
                                    )
                                    Text(
                                        text = "Cantidad: ${part.quantityUsed} × $${String.format("%.0f", part.costPerUnit ?: part.inventoryItem.currentCost)}",
                                        style = MaterialTheme.typography.labelSmall,
                                        color = MaterialTheme.colorScheme.onSurfaceVariant
                                    )
                                }
                                Text(
                                    text = "$${String.format("%.0f", part.totalCost)}",
                                    style = MaterialTheme.typography.bodySmall,
                                    fontWeight = FontWeight.Medium
                                )
                                if (isEditable) {
                                    IconButton(
                                        onClick = { onRemovePart(part.id) },
                                        modifier = Modifier.size(32.dp)
                                    ) {
                                        Icon(
                                            imageVector = Icons.Default.Close,
                                            contentDescription = "Eliminar repuesto",
                                            modifier = Modifier.size(16.dp),
                                            tint = MaterialTheme.colorScheme.error
                                        )
                                    }
                                }
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(8.dp))
                    HorizontalDivider()
                    Spacer(modifier = Modifier.height(8.dp))

                    // Total de la tarea
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(
                            text = "Subtotal tarea:",
                            style = MaterialTheme.typography.bodyMedium,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = "$${String.format("%.0f", task.totalCost)}",
                            style = MaterialTheme.typography.bodyMedium,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.primary
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun CostSummaryCard(order: MaintenanceOrderDetail) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.3f)
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Text(
                text = "Resumen de Costos",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )

            Spacer(modifier = Modifier.height(12.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text("Tareas realizadas:")
                Text("${order.taskCount}")
            }

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text("Repuestos utilizados:")
                Text("${order.partsCount}")
            }

            Spacer(modifier = Modifier.height(8.dp))
            HorizontalDivider()
            Spacer(modifier = Modifier.height(8.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "COSTO TOTAL:",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "$${String.format("%.0f", order.calculatedTotalCost)}",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.primary
                )
            }
        }
    }
}

// ========== Componentes auxiliares ==========

@Composable
private fun SectionHeader(icon: ImageVector, title: String) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.primary,
            modifier = Modifier.size(20.dp)
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(
            text = title,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold
        )
    }
}

@Composable
private fun InfoRow(label: String, value: String) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            fontWeight = FontWeight.Medium
        )
    }
}

@Composable
private fun InfoChip(icon: ImageVector, text: String, iconTint: Color = MaterialTheme.colorScheme.primary) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        modifier = Modifier
            .clip(RoundedCornerShape(8.dp))
            .background(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f))
            .padding(horizontal = 8.dp, vertical = 4.dp)
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            modifier = Modifier.size(16.dp),
            tint = iconTint
        )
        Spacer(modifier = Modifier.width(4.dp))
        Text(
            text = text,
            style = MaterialTheme.typography.labelMedium
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun <T> DropdownField(
    label: String,
    selectedValue: String,
    options: List<Pair<T, String>>,
    enabled: Boolean,
    onOptionSelected: (T) -> Unit
) {
    var expanded by remember { mutableStateOf(false) }

    ExposedDropdownMenuBox(
        expanded = expanded && enabled,
        onExpandedChange = { if (enabled) expanded = it }
    ) {
        OutlinedTextField(
            value = selectedValue,
            onValueChange = {},
            label = { Text(label) },
            readOnly = true,
            enabled = enabled,
            trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded) },
            modifier = Modifier
                .fillMaxWidth()
                .menuAnchor()
        )

        ExposedDropdownMenu(
            expanded = expanded && enabled,
            onDismissRequest = { expanded = false }
        ) {
            options.forEach { (id, name) ->
                DropdownMenuItem(
                    text = { Text(name) },
                    onClick = {
                        onOptionSelected(id)
                        expanded = false
                    }
                )
            }
        }
    }
}

@Composable
private fun ErrorContent(
    message: String,
    onRetry: () -> Unit,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                imageVector = Icons.Default.Error,
                contentDescription = null,
                modifier = Modifier.size(64.dp),
                tint = MaterialTheme.colorScheme.error
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = message,
                style = MaterialTheme.typography.bodyLarge,
                textAlign = TextAlign.Center
            )
            Spacer(modifier = Modifier.height(16.dp))
            Button(onClick = onRetry) {
                Text("Reintentar")
            }
        }
    }
}

// ========== Diálogos ==========

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun AddTaskDialog(
    taskTypes: List<TaskType>,
    selectedTypeId: Int?,
    description: String,
    cost: String,
    isSaving: Boolean,
    onTypeChange: (Int) -> Unit,
    onDescriptionChange: (String) -> Unit,
    onCostChange: (String) -> Unit,
    onConfirm: () -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Agregar Tarea") },
        text = {
            Column(
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                DropdownField(
                    label = "Tipo de Tarea *",
                    selectedValue = taskTypes.find { it.id == selectedTypeId }?.name ?: "Seleccionar...",
                    options = taskTypes.map { it.id to it.name },
                    enabled = !isSaving,
                    onOptionSelected = onTypeChange
                )

                OutlinedTextField(
                    value = description,
                    onValueChange = onDescriptionChange,
                    label = { Text("Descripción (opcional)") },
                    modifier = Modifier.fillMaxWidth(),
                    enabled = !isSaving,
                    minLines = 2
                )

                OutlinedTextField(
                    value = cost,
                    onValueChange = onCostChange,
                    label = { Text("Costo mano de obra") },
                    modifier = Modifier.fillMaxWidth(),
                    enabled = !isSaving,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                    prefix = { Text("$") }
                )
            }
        },
        confirmButton = {
            Button(
                onClick = onConfirm,
                enabled = selectedTypeId != null && !isSaving
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
private fun AddPartDialog(
    inventory: List<WorkshopInventoryItem>,
    selectedInventoryId: Int?,
    quantity: String,
    isSaving: Boolean,
    onInventoryChange: (Int) -> Unit,
    onQuantityChange: (String) -> Unit,
    onConfirm: () -> Unit,
    onDismiss: () -> Unit
) {
    val selectedItem = inventory.find { it.id == selectedInventoryId }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Agregar Repuesto") },
        text = {
            Column(
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                DropdownField(
                    label = "Repuesto *",
                    selectedValue = selectedItem?.displayName ?: "Seleccionar...",
                    options = inventory.map { it.id to "${it.displayName} (${it.quantity} disp.)" },
                    enabled = !isSaving,
                    onOptionSelected = onInventoryChange
                )

                if (selectedItem != null) {
                    Text(
                        text = "Precio unitario: $${String.format("%.0f", selectedItem.currentCost)}",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }

                OutlinedTextField(
                    value = quantity,
                    onValueChange = onQuantityChange,
                    label = { Text("Cantidad") },
                    modifier = Modifier.fillMaxWidth(),
                    enabled = !isSaving,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
                )

                if (selectedItem != null && quantity.isNotEmpty()) {
                    val qty = quantity.toIntOrNull() ?: 0
                    Text(
                        text = "Subtotal: $${String.format("%.0f", selectedItem.currentCost * qty)}",
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Medium
                    )
                }
            }
        },
        confirmButton = {
            Button(
                onClick = onConfirm,
                enabled = selectedInventoryId != null && quantity.isNotEmpty() && !isSaving
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
private fun ExitDatePickerDialog(
    onDateSelected: (String) -> Unit,
    onDismiss: () -> Unit
) {
    val datePickerState = rememberDatePickerState()
    
    DatePickerDialog(
        onDismissRequest = onDismiss,
        confirmButton = {
            TextButton(
                onClick = {
                    datePickerState.selectedDateMillis?.let { millis ->
                        val sdf = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
                        val date = sdf.format(Date(millis))
                        onDateSelected(date)
                    }
                }
            ) {
                Text("Confirmar")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancelar")
            }
        }
    ) {
        DatePicker(state = datePickerState)
    }
}

