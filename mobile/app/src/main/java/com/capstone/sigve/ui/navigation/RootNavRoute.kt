package com.capstone.sigve.ui.navigation

sealed class RootNavRoute(val route: String) {
    data object Login : RootNavRoute("login_screen")
    data object AdminModule : RootNavRoute("admin_module")
    data object WorkshopModule : RootNavRoute("workshop_module")
    data object FireStationModule : RootNavRoute("fire_station_module")
}