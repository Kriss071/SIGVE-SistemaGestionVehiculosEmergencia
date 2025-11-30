package com.capstone.sigve.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.capstone.sigve.ui.admin.navigation.AdminNavigation
import com.capstone.sigve.ui.auth.LoginScreen
import com.capstone.sigve.ui.firestation.navigation.FireStationNavigation
import com.capstone.sigve.ui.workshop.navigation.WorkshopNavigation

@Composable
fun AppNavigation() {
    val navController = rememberNavController()
    
    NavHost(
        navController = navController,
        startDestination = RootNavRoute.Login.route
    ) {
        // Pantalla de Login
        composable(RootNavRoute.Login.route) {
            LoginScreen(navController = navController)
        }

        // Módulo Admin SIGVE
        composable(RootNavRoute.AdminModule.route) {
            AdminNavigation(
                onLogout = {
                    navController.navigate(RootNavRoute.Login.route) {
                        popUpTo(0) { inclusive = true }
                    }
                }
            )
        }

        // Módulo Workshop (Admin Taller + Mecánico)
        composable(RootNavRoute.WorkshopModule.route) {
            WorkshopNavigation(
                onLogout = {
                    navController.navigate(RootNavRoute.Login.route) {
                        popUpTo(0) { inclusive = true }
                    }
                }
            )
        }

        // Módulo Fire Station (Jefe Cuartel)
        composable(RootNavRoute.FireStationModule.route) {
            FireStationNavigation(
                onLogout = {
                    navController.navigate(RootNavRoute.Login.route) {
                        popUpTo(0) { inclusive = true }
                    }
                }
            )
        }
    }
}