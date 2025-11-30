package com.capstone.sigve.ui.admin.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ExitToApp
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
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.capstone.sigve.ui.admin.AdminHomeScreen
import com.capstone.sigve.ui.common.SigveTopAppBar
import com.capstone.sigve.ui.settings.SettingsScreen

sealed class AdminNavRoute(val route: String, val title: String, val icon: ImageVector) {
    data object Home : AdminNavRoute("admin_home", "Inicio", Icons.Default.Home)
    data object Settings : AdminNavRoute("admin_settings", "Ajustes", Icons.Default.Settings)

    companion object {
        val items = listOf(Home, Settings)
    }
}

@Composable
fun AdminNavigation(
    onLogout: () -> Unit
) {
    val navController = rememberNavController()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry?.destination

    val currentScreen = remember(currentDestination) {
        AdminNavRoute.items.find { it.route == currentDestination?.route }
    }
    val currentTitle = currentScreen?.title ?: "Admin SIGVE"

    var showMenu by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
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
        },
        bottomBar = {
            NavigationBar {
                AdminNavRoute.items.forEach { screen ->
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
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = AdminNavRoute.Home.route,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(AdminNavRoute.Home.route) {
                AdminHomeScreen()
            }
            composable(AdminNavRoute.Settings.route) {
                SettingsScreen()
            }
        }
    }
}


