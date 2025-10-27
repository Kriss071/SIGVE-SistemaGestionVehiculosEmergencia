package com.capstone.sigve.ui.navigation.mainScreenBottomNav

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.hilt.lifecycle.viewmodel.compose.hiltViewModel
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.capstone.sigve.ui.common.SigveTopAppBar
import com.capstone.sigve.ui.settings.SettingsScreen
import com.capstone.sigve.ui.vehicles.VehiclesScreen


@Composable
fun MainScreenNavigation() {
    val navController = rememberNavController()

    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry?.destination

    val currentScreen = remember(currentDestination) {
        BottomNavDestinations.items.find { it.route == currentDestination?.route }
    }
    val currentTitle = currentScreen?.title ?: "SIGVE"

    Scaffold(
        topBar = {
            SigveTopAppBar(title = currentTitle) {
                IconButton(onClick = { /* Lógica común o condicional */ }) {
                    Icon(
                        imageVector = Icons.Default.MoreVert,
                        contentDescription = "Opciones",
                        tint = MaterialTheme.colorScheme.onPrimary // Asegura visibilidad
                    )
                }
            }
        },
        bottomBar = {
            NavigationBar {
                BottomNavDestinations.items.forEach { screen ->
                    NavigationBarItem(
                        icon = { Icon(screen.icon, contentDescription = screen.title) },
                        label = { Text(screen.title) },
                        selected = currentDestination?.hierarchy?.any() { it.route == screen.route } == true,
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
        }) { innerPadding ->
        NavHost(navController, startDestination = BottomNavDestinations.Vehicles.route) {
            composable(BottomNavDestinations.Vehicles.route) {
                VehiclesScreen()
            }
            composable(BottomNavDestinations.Maintenance.route) {
                VehiclesScreen()
            }

            composable(BottomNavDestinations.Workshop.route) {
                VehiclesScreen()
            }

            composable(BottomNavDestinations.Settings.route) {
                SettingsScreen(
                    viewModel = hiltViewModel(),
                    innerPadding = innerPadding
                )
            }
        }
    }

}