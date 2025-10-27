package com.capstone.sigve.ui.navigation.mainScreenBottomNav

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.ShoppingCart
import androidx.compose.material.icons.filled.ThumbUp
import androidx.compose.ui.graphics.vector.ImageVector

data class BottomNavItem(
    val route: String,
    val title: String,
    val icon: ImageVector
)

object BottomNavDestinations {
    val Vehicles = BottomNavItem("vehicles_screen", "Vehículos", Icons.Default.ShoppingCart)
    val Maintenance = BottomNavItem("maintenance_screen", "Mantenciones", Icons.Default.ThumbUp)
    val Workshop = BottomNavItem("workshop_screen", "Taller", Icons.Default.Home)
    val Settings = BottomNavItem("settings_screen", "Ajustes", Icons.Default.Settings)

    val items = listOf(Vehicles, Maintenance, Workshop, Settings)
}