package com.capstone.sigve.ui.navigation

import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.runtime.Composable
import androidx.hilt.lifecycle.viewmodel.compose.hiltViewModel
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.capstone.sigve.ui.auth.LoginScreen
import com.capstone.sigve.ui.settings.SettingsScreen

@Composable
fun AppNavigation(
    innerPadding: PaddingValues
) {
    val navController = rememberNavController()
    NavHost(navController = navController, startDestination = AppScreens.LoginScreen.route) {
        composable(AppScreens.LoginScreen.route) {
            LoginScreen(navController = navController)
        }

        composable(AppScreens.SettingsScreen.route) {
            SettingsScreen(viewModel = hiltViewModel(), innerPadding = innerPadding)
        }
    }
}