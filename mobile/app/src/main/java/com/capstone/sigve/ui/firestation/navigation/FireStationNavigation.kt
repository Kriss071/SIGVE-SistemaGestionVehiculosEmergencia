package com.capstone.sigve.ui.firestation.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ExitToApp
import androidx.compose.material.icons.filled.DateRange
import androidx.compose.material.icons.filled.DirectionsCar
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.capstone.sigve.ui.common.SigveTopAppBar
import com.capstone.sigve.ui.firestation.FireStationHomeScreen
import com.capstone.sigve.ui.firestation.FireStationVehiclesScreen
import com.capstone.sigve.ui.firestation.VehicleHistoryScreen
import com.capstone.sigve.ui.settings.SettingsScreen

sealed class FireStationNavRoute(val route: String, val title: String, val icon: ImageVector) {
    data object Home : FireStationNavRoute("firestation_home", "Dashboard", Icons.Default.Home)
    data object Vehicles : FireStationNavRoute("firestation_vehicles", "Vehículos", Icons.Default.DirectionsCar)
    data object History : FireStationNavRoute("firestation_history", "Historial", Icons.Default.DateRange) {
        // Ruta base sin parámetros
        const val baseRoute = "firestation_history"
        // Ruta con parámetro opcional para vehicleId
        const val routeWithParam = "firestation_history/{vehicleId}"
        fun createRoute(vehicleId: Int? = null) = 
            if (vehicleId != null) "firestation_history/$vehicleId" else baseRoute
    }
    data object Settings : FireStationNavRoute("firestation_settings", "Ajustes", Icons.Default.Settings)

    companion object {
        // Items que aparecen en el bottom navigation (sin History)
        val bottomNavItems = listOf(Home, Vehicles, Settings)
        // Todos los items (incluyendo History para otras referencias)
        val items = listOf(Home, Vehicles, History, Settings)
    }
}

@Composable
fun FireStationNavigation(
    onLogout: () -> Unit
) {
    val navController = rememberNavController()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry?.destination

    val currentScreen = remember(currentDestination) {
        FireStationNavRoute.items.find { 
            currentDestination?.route?.startsWith(it.route) == true
        }
    }
    
    // Determinar si estamos en una pantalla de historial (con parámetro)
    val isHistoryScreen = currentDestination?.route?.startsWith(FireStationNavRoute.History.baseRoute) == true
    
    val currentTitle = if (isHistoryScreen) {
        "Historial del Vehículo"
    } else {
        currentScreen?.title ?: "Cuartel"
    }

    var showMenu by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            SigveTopAppBar(
                title = currentTitle,
                showBackButton = isHistoryScreen,
                onBackClick = if (isHistoryScreen) { { navController.navigateUp() } } else null
            ) {
                if (!isHistoryScreen) {
                    IconButton(onClick = { showMenu = true }) {
                        Icon(
                            imageVector = Icons.Default.MoreVert,
                            contentDescription = "Opciones",
                            tint = MaterialTheme.colorScheme.onPrimary
                        )
                    }
                    DropdownMenu(
                        expanded = showMenu,
                        onDismissRequest = { showMenu = false }
                    ) {
                        DropdownMenuItem(
                            text = { Text("Cerrar Sesión") },
                            onClick = {
                                showMenu = false
                                onLogout()
                            },
                            leadingIcon = {
                                Icon(Icons.AutoMirrored.Filled.ExitToApp, contentDescription = null)
                            }
                        )
                    }
                }
            }
        },
        bottomBar = {
            // Solo mostrar bottom nav si no estamos en historial
            if (!isHistoryScreen) {
                NavigationBar {
                    FireStationNavRoute.bottomNavItems.forEach { screen ->
                        NavigationBarItem(
                            icon = { Icon(screen.icon, contentDescription = screen.title) },
                            label = { Text(screen.title) },
                            selected = currentDestination?.hierarchy?.any { it.route == screen.route } == true,
                            onClick = {
                                navController.navigate(screen.route) {
                                    popUpTo(navController.graph.findStartDestination().id) {
                                        saveState = true
                                    }
                                    launchSingleTop = true
                                    restoreState = true
                                }
                            }
                        )
                    }
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = FireStationNavRoute.Home.route,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(FireStationNavRoute.Home.route) {
                FireStationHomeScreen()
            }
            composable(FireStationNavRoute.Vehicles.route) {
                FireStationVehiclesScreen(navController = navController)
            }
            // Ruta base de historial (sin parámetros)
            composable(FireStationNavRoute.History.baseRoute) {
                VehicleHistoryScreen(vehicleId = null)
            }
            // Ruta de historial con vehicleId
            composable(
                route = FireStationNavRoute.History.routeWithParam,
                arguments = listOf(
                    navArgument("vehicleId") {
                        type = NavType.IntType
                    }
                )
            ) { backStackEntry ->
                val vehicleId = backStackEntry.arguments?.getInt("vehicleId")
                VehicleHistoryScreen(vehicleId = vehicleId)
            }
            composable(FireStationNavRoute.Settings.route) {
                SettingsScreen()
            }
        }
    }
}


