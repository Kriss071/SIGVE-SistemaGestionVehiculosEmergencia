package com.capstone.sigve.ui.vehicles

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
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
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp

private data class DummyVehicle(val patente: String, val details: String)

private val dummyList = listOf(
    DummyVehicle("QL-RN 27", "Mercedes-Benz Atego 1529"),
    DummyVehicle("PM-HW 03", "MAN TGM 13.290"),
    DummyVehicle("CD-TF 88", "Iveco Eurocargo Magirus"),
    DummyVehicle("JK-RX 19", "Scania P320"),
    DummyVehicle("NV-ZB 41", "Renault Midlum 280"),
    DummyVehicle("RS-GM 75", "Freightliner M2 / Rosenbauer"),
    DummyVehicle("BC-FG 55", "Volkswagen Constellation")
)

@Composable
fun VehiclesScreen() {
    // Estado para la barra de búsqueda (sin lógica real aún)
    var searchQuery by remember { mutableStateOf("") }

    Scaffold(
        topBar = {
            TopBar()
        },
        floatingActionButton = {
            FloatingActionButton(
                onClick = { /* Lógica de navegación se agregará aquí */ }
            ) {
                Icon(Icons.Default.Add, contentDescription = "Añadir Vehículo")
            }
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .padding(paddingValues)
                .fillMaxSize()
        ) {
            // --- Barra de Búsqueda ---
            OutlinedTextField(
                value = searchQuery,
                onValueChange = { searchQuery = it },
                label = { Text("Buscar por patente, marca...") },
                leadingIcon = { Icon(Icons.Default.Search, contentDescription = null) },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp)
            )

            // --- Lista de Vehículos ---
            LazyColumn(
                contentPadding = PaddingValues(start = 16.dp, end = 16.dp, bottom = 80.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(dummyList) { vehicle ->
                    VehicleListItem(
                        patente = vehicle.patente,
                        details = vehicle.details,
                        onClick = { /* Lógica de navegación se agregará aquí */ }
                    )
                }
            }
        }
    }
}

@Composable
fun TopBar() {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .height(64.dp),
        shadowElevation = 4.dp,
        color = Color(0xFFDF2532)
    ) {
        Row(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 16.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(
                "Vehículos del Taller",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )
            IconButton(onClick = { /* Lógica de opciones */ }) {
                Icon(
                    imageVector = Icons.Default.MoreVert,
                    contentDescription = "Opciones",
                    tint = MaterialTheme.colorScheme.onPrimaryContainer
                )
            }
        }
    }
}

// --- Ítem Individual de la Lista ---

@Composable
fun VehicleListItem(
    patente: String,
    details: String,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() },
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Icono (placeholder como en la imagen)
            Icon(
                imageVector = Icons.Filled.Settings,
                contentDescription = "Icono de vehículo",
                modifier = Modifier.size(40.dp),
                tint = MaterialTheme.colorScheme.secondary
            )

            Spacer(Modifier.width(16.dp))

            // Textos
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = patente,
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = details,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            // Icono de flecha
            Icon(
                imageVector = Icons.Default.LocationOn,
                contentDescription = "Ver detalle",
                modifier = Modifier.size(32.dp),
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Preview()
@Composable
fun PreviewVehicleScreen() {
    VehiclesScreen()
}