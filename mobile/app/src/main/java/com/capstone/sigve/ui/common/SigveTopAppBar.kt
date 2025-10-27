package com.capstone.sigve.ui.common

import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.material3.CenterAlignedTopAppBar
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight

@OptIn(ExperimentalMaterial3Api::class) // Necesario para CenterAlignedTopAppBar
@Composable
fun SigveTopAppBar(
    title: String,
    actions: @Composable RowScope.() -> Unit = {} // Por defecto, sin acciones
) {
    CenterAlignedTopAppBar(
        title = {
            Text(
                text = title,
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onPrimary // Color de texto sobre el primario
            )
        },
        modifier = Modifier.fillMaxWidth(),
        actions = actions, // Coloca aquí los iconos de acción
        colors = TopAppBarDefaults.centerAlignedTopAppBarColors(
            containerColor = Color(0xFFDF2532) // Color de fondo rojo característico
            // Puedes ajustar otros colores si es necesario (ej: color de iconos)
        )
    )
}