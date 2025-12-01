package com.capstone.sigve.ui.workshop.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ExitToApp
import androidx.compose.material.icons.filled.Build
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.ShoppingCart
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
import com.capstone.sigve.ui.settings.SettingsScreen
import com.capstone.sigve.ui.workshop.InventoryScreen
import com.capstone.sigve.ui.workshop.MaintenanceScreen
import com.capstone.sigve.ui.workshop.OrderDetailScreen
import com.capstone.sigve.ui.workshop.WorkshopHomeScreen

sealed class WorkshopNavRoute(val route: String, val title: String, val icon: ImageVector) {
    data object Home : WorkshopNavRoute("workshop_home", "Inicio", Icons.Default.Home)
    data object Maintenance : WorkshopNavRoute("workshop_maintenance", "Mantenciones", Icons.Default.Build)
    data object Inventory : WorkshopNavRoute("workshop_inventory", "Inventario", Icons.Default.ShoppingCart)
    data object Settings : WorkshopNavRoute("workshop_settings", "Ajustes", Icons.Default.Settings)
    
    // Rutas sin ícono (no aparecen en bottom nav)
    data object OrderDetail : WorkshopNavRoute("workshop_order_detail/{orderId}", "Detalle de Orden", Icons.Default.Build) {
        fun createRoute(orderId: Int) = "workshop_order_detail/$orderId"
    }

    companion object {
        val items = listOf(Home, Maintenance, Inventory, Settings)
    }
}

@Composable
fun WorkshopNavigation(
    onLogout: () -> Unit
) {
    val navController = rememberNavController()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry?.destination

    val currentScreen = remember(currentDestination) {
        WorkshopNavRoute.items.find { it.route == currentDestination?.route }
    }
    val currentTitle = currentScreen?.title ?: "Taller"
    
    // Determinar si estamos en una pantalla con bottom nav
    val showBottomNav = currentDestination?.route in WorkshopNavRoute.items.map { it.route }
    val showTopBar = currentDestination?.route in WorkshopNavRoute.items.map { it.route }

    var showMenu by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            if (showTopBar) {
                SigveTopAppBar(title = currentTitle) {
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
            if (showBottomNav) {
                NavigationBar {
                    WorkshopNavRoute.items.forEach { screen ->
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
            startDestination = WorkshopNavRoute.Home.route,
            modifier = Modifier
        ) {
            composable(WorkshopNavRoute.Home.route) {
                androidx.compose.foundation.layout.Box(modifier = Modifier.padding(innerPadding)) {
                    WorkshopHomeScreen()
                }
            }
            composable(WorkshopNavRoute.Maintenance.route) {
                androidx.compose.foundation.layout.Box(modifier = Modifier.padding(innerPadding)) {
                    MaintenanceScreen(
                        onOrderClick = { orderId ->
                            navController.navigate(WorkshopNavRoute.OrderDetail.createRoute(orderId))
                        }
                    )
                }
            }
            composable(WorkshopNavRoute.Inventory.route) {
                androidx.compose.foundation.layout.Box(modifier = Modifier.padding(innerPadding)) {
                    InventoryScreen()
                }
            }
            composable(WorkshopNavRoute.Settings.route) {
                androidx.compose.foundation.layout.Box(modifier = Modifier.padding(innerPadding)) {
                    SettingsScreen()
                }
            }
            composable(
                route = WorkshopNavRoute.OrderDetail.route,
                arguments = listOf(
                    navArgument("orderId") { type = NavType.IntType }
                )
            ) {
                OrderDetailScreen(
                    onNavigateBack = { navController.popBackStack() }
                )
            }
        }
    }
}
