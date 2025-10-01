package com.capstone.sigve

import android.annotation.SuppressLint
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.viewModels
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import com.capstone.sigve.data.repository.SettingsRepository
import com.capstone.sigve.domain.model.AppTheme
import com.capstone.sigve.ui.settings.SettingsScreen
import com.capstone.sigve.ui.settings.SettingsViewModel
import com.capstone.sigve.ui.theme.SIGVETheme

class MainActivity : ComponentActivity() {

    private val settingsRepository by lazy { SettingsRepository(this) }

    // FACTORY VIEW MODEL - SACAR DE AQUI CUANDO SE AGREGUE INYECCIÓN DE DEPENDENCIAS
    private val settingsViewModel: SettingsViewModel by viewModels {
        object : ViewModelProvider.Factory {
            override fun <T : ViewModel> create(modelClass: Class<T>): T {
                if (modelClass.isAssignableFrom(SettingsViewModel::class.java)) {
                    @Suppress("UNCHECKED_CAST") return SettingsViewModel(settingsRepository) as T
                }
                throw IllegalArgumentException("Unknown ViewModel class")
            }
        }
    }

    // SACAR CUANDO SE USE INNERPADDING
    @SuppressLint("UnusedMaterial3ScaffoldPaddingParameter")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            val theme by settingsViewModel.theme.collectAsState()
            val color by settingsViewModel.color.collectAsState()

            SIGVETheme(
                darkTheme = (theme == AppTheme.DARK),
                appColor = color
            ) {
                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    SettingsScreen(viewModel = settingsViewModel)
                }
            }
        }
    }

}


