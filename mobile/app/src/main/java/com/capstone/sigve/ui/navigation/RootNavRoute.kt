package com.capstone.sigve.ui.navigation

sealed class RootNavRoute(val route: String) {
    data object LoginScreen: RootNavRoute("login_screen")
    data object MainScreen: RootNavRoute("main_screen")
}