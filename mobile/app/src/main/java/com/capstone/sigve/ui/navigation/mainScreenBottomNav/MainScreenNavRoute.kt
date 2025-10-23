package com.capstone.sigve.ui.navigation.mainScreenBottomNav

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ShoppingCart
import androidx.compose.ui.graphics.vector.ImageVector

sealed class MainScreenNavRoute(
    val route: String,
    val title: String,
    val icon: ImageVector
) {
    data object Vehicles : MainScreenNavRoute(
        route = "vehicles_screen",
        title = "Vehículos",
        icon = Icons.Default.ShoppingCart
    )
    data object SEGUNDO : MainScreenNavRoute(
        route = "2",
        title = "Mantenciones",
        icon = Icons.Default.ShoppingCart
    )
    data object TERCERO : MainScreenNavRoute(
        route = "3",
        title = "Taller",
        icon = Icons.Default.ShoppingCart
    )
    data object CUARTO : MainScreenNavRoute(
        route = "settings_screen",
        title = "Configuración",
        icon = Icons.Default.ShoppingCart
    )

}