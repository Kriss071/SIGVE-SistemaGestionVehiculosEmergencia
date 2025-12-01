package com.capstone.sigve

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.hilt.navigation.compose.hiltViewModel
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
            val isSystemDark = isSystemInDarkTheme()

            val isDarkTheme = when (theme) {
                AppTheme.DARK -> true
                AppTheme.LIGHT -> false
                AppTheme.SYSTEM -> isSystemDark
            }

            SIGVETheme(darkTheme = isDarkTheme) {
                AppNavigation()
            }
        }
    }
}
