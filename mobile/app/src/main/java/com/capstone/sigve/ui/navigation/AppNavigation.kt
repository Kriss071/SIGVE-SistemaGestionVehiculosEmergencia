package com.capstone.sigve.ui.navigation

import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.runtime.Composable
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.capstone.sigve.ui.auth.LoginScreen
import com.capstone.sigve.ui.settings.SettingsScreen
import com.capstone.sigve.ui.settings.SettingsViewModel

@Composable
fun AppNavigation(settingsViewModel: SettingsViewModel, innerPadding: PaddingValues) {
    val navController = rememberNavController()
    NavHost(navController = navController, startDestination = AppScreens.LoginScreen.route) {
        composable(AppScreens.LoginScreen.route) {
            LoginScreen(navController)
        }

        composable(AppScreens.SettingsScreen.route) {
            SettingsScreen(viewModel = settingsViewModel, innerPadding = innerPadding)
        }
    }
}