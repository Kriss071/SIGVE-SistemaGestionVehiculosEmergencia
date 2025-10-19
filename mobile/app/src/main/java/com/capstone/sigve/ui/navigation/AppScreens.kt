package com.capstone.sigve.ui.navigation

sealed class AppScreens(val route: String) {
    data object LoginScreen: AppScreens("login_screen")
    data object SettingsScreen: AppScreens("settings_screen")
}