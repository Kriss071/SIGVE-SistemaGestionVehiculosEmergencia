package com.capstone.sigve.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.capstone.sigve.ui.auth.LoginScreen
import com.capstone.sigve.ui.navigation.mainScreenBottomNav.MainScreenNavigation

@Composable
fun AppNavigation() {
    val navController = rememberNavController()
    NavHost(navController = navController, startDestination = RootNavRoute.LoginScreen.route) {

        composable(RootNavRoute.LoginScreen.route) {
            LoginScreen(navController = navController)
        }

        composable(RootNavRoute.MainScreen.route){
            MainScreenNavigation()
        }
    }
}