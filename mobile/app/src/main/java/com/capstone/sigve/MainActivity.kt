package com.capstone.sigve

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.hilt.lifecycle.viewmodel.compose.hiltViewModel
import com.capstone.sigve.domain.model.AppTheme
import com.capstone.sigve.ui.navigation.AppNavigation
import com.capstone.sigve.ui.settings.SettingsViewModel
import com.capstone.sigve.ui.theme.SIGVETheme
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            val settingsViewModel: SettingsViewModel = hiltViewModel()
            val theme by settingsViewModel.theme.collectAsState()
            val color by settingsViewModel.color.collectAsState()
            val customColors by settingsViewModel.customColors.collectAsState()

            SIGVETheme(
                darkTheme = (theme == AppTheme.DARK),
                appColor = color,
                customColors = customColors
            ) {
                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    AppNavigation(innerPadding = innerPadding)
                }
            }
        }
    }

}


