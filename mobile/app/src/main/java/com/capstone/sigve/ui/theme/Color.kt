package com.capstone.sigve.ui.theme

import androidx.compose.ui.graphics.Color

/**
 * Paleta de colores para SIGVE - Sistema de Gestión de Vehículos de Emergencia
 * 
 * Diseñada para reflejar la identidad de servicios de bomberos/emergencia:
 * - Rojo: Color principal (bomberos, urgencia, acción)
 * - Gris azulado: Profesionalismo y seriedad
 * - Verde: Estados positivos, completados, éxito
 */

// === COLORES PRIMARIOS (Rojo Bomberos) ===
val FireRed = Color(0xFFD32F2F)           // Primary Light
val FireRedLight = Color(0xFFFFCDD2)      // Primary Container Light
val FireRedDark = Color(0xFFFFB4AB)       // Primary Dark
val FireRedDarkContainer = Color(0xFF93000A)  // Primary Container Dark

// === COLORES SECUNDARIOS (Gris Azulado Profesional) ===
val SlateGray = Color(0xFF546E7A)         // Secondary Light
val SlateGrayLight = Color(0xFFCFD8DC)    // Secondary Container Light
val SlateGrayDark = Color(0xFFB0BEC5)     // Secondary Dark
val SlateGrayDarkContainer = Color(0xFF37474F)  // Secondary Container Dark

// === COLORES TERCIARIOS (Verde Éxito) ===
val SuccessGreen = Color(0xFF388E3C)      // Tertiary Light
val SuccessGreenLight = Color(0xFFC8E6C9) // Tertiary Container Light
val SuccessGreenDark = Color(0xFF81C784)  // Tertiary Dark
val SuccessGreenDarkContainer = Color(0xFF1B5E20)  // Tertiary Container Dark

// === COLORES DE ERROR ===
val ErrorRed = Color(0xFFBA1A1A)
val ErrorRedContainer = Color(0xFFFFDAD6)
val ErrorRedDark = Color(0xFFFFB4AB)
val ErrorRedDarkContainer = Color(0xFF93000A)

// === FONDOS Y SUPERFICIES ===
// Light Theme
val BackgroundLight = Color(0xFFF5F5F5)
val SurfaceLight = Color(0xFFFFFFFF)
val SurfaceVariantLight = Color(0xFFE7E0EC)
val OutlineLight = Color(0xFF79747E)
val OutlineVariantLight = Color(0xFFCAC4D0)

// Dark Theme
val BackgroundDark = Color(0xFF1C1B1F)
val SurfaceDark = Color(0xFF2B2930)
val SurfaceVariantDark = Color(0xFF49454F)
val OutlineDark = Color(0xFF938F99)
val OutlineVariantDark = Color(0xFF49454F)

// === COLORES SOBRE FONDOS ===
val OnPrimaryLight = Color.White
val OnSecondaryLight = Color.White
val OnTertiaryLight = Color.White
val OnBackgroundLight = Color(0xFF1C1B1F)
val OnSurfaceLight = Color(0xFF1C1B1F)
val OnSurfaceVariantLight = Color(0xFF49454F)

val OnPrimaryDark = Color(0xFF690005)
val OnSecondaryDark = Color(0xFF263238)
val OnTertiaryDark = Color(0xFF0D3711)
val OnBackgroundDark = Color(0xFFE6E1E5)
val OnSurfaceDark = Color(0xFFE6E1E5)
val OnSurfaceVariantDark = Color(0xFFCAC4D0)

val OnPrimaryContainerLight = Color(0xFF410002)
val OnSecondaryContainerLight = Color(0xFF1C313A)
val OnTertiaryContainerLight = Color(0xFF0D3711)

val OnPrimaryContainerDark = Color(0xFFFFDAD6)
val OnSecondaryContainerDark = Color(0xFFE0E0E0)
val OnTertiaryContainerDark = Color(0xFFC8E6C9)

val OnErrorLight = Color.White
val OnErrorDark = Color(0xFF690005)
val OnErrorContainerLight = Color(0xFF410002)
val OnErrorContainerDark = Color(0xFFFFDAD6)
