package com.capstone.sigve.ui.settings

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.capstone.sigve.domain.model.AppColor
import com.capstone.sigve.domain.model.AppTheme

@Composable
fun SettingsScreen(viewModel: SettingsViewModel) {
    val theme by viewModel.theme.collectAsState()
    val color by viewModel.color.collectAsState()

    Column(
        modifier = Modifier.fillMaxSize().padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("Tema actual: $theme")
        Spacer(modifier = Modifier.height(8.dp))
        Row {
            Button(onClick = { viewModel.setTheme(AppTheme.LIGHT) }) { Text("Claro") }
            Spacer(modifier = Modifier.width(8.dp))
            Button(onClick = { viewModel.setTheme(AppTheme.DARK) }) { Text("Oscuro") }
            Spacer(modifier = Modifier.width(8.dp))
            Button(onClick = { viewModel.setTheme(AppTheme.SYSTEM) }) { Text("Sistema") }
        }

        Spacer(modifier = Modifier.height(16.dp))
        Text("Color actual: ${color.displayName}")
        Row {
            AppColor.entries.forEach { c ->
                Spacer(modifier = Modifier.width(4.dp))
                Button(onClick = { viewModel.setColor(c) }) { Text(c.displayName) }
            }
        }
    }
}