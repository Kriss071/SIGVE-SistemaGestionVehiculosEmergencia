package com.capstone.sigve.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

/**
 * Esquema de colores para tema claro
 * Diseñado para SIGVE - Sistema de Gestión de Vehículos de Emergencia
 */
private val LightColorScheme = lightColorScheme(
    // Colores primarios - Rojo bomberos
    primary = FireRed,
    onPrimary = OnPrimaryLight,
    primaryContainer = FireRedLight,
    onPrimaryContainer = OnPrimaryContainerLight,
    
    // Colores secundarios - Gris profesional
    secondary = SlateGray,
    onSecondary = OnSecondaryLight,
    secondaryContainer = SlateGrayLight,
    onSecondaryContainer = OnSecondaryContainerLight,
    
    // Colores terciarios - Verde éxito
    tertiary = SuccessGreen,
    onTertiary = OnTertiaryLight,
    tertiaryContainer = SuccessGreenLight,
    onTertiaryContainer = OnTertiaryContainerLight,
    
    // Error
    error = ErrorRed,
    onError = OnErrorLight,
    errorContainer = ErrorRedContainer,
    onErrorContainer = OnErrorContainerLight,
    
    // Fondos y superficies
    background = BackgroundLight,
    onBackground = OnBackgroundLight,
    surface = SurfaceLight,
    onSurface = OnSurfaceLight,
    surfaceVariant = SurfaceVariantLight,
    onSurfaceVariant = OnSurfaceVariantLight,
    
    // Bordes
    outline = OutlineLight,
    outlineVariant = OutlineVariantLight,
    
    // Otros
    inverseSurface = SurfaceDark,
    inverseOnSurface = OnSurfaceDark,
    inversePrimary = FireRedDark,
    scrim = OnBackgroundLight
)

/**
 * Esquema de colores para tema oscuro
 */
private val DarkColorScheme = darkColorScheme(
    // Colores primarios - Rojo bomberos (ajustado para oscuro)
    primary = FireRedDark,
    onPrimary = OnPrimaryDark,
    primaryContainer = FireRedDarkContainer,
    onPrimaryContainer = OnPrimaryContainerDark,
    
    // Colores secundarios - Gris profesional
    secondary = SlateGrayDark,
    onSecondary = OnSecondaryDark,
    secondaryContainer = SlateGrayDarkContainer,
    onSecondaryContainer = OnSecondaryContainerDark,
    
    // Colores terciarios - Verde éxito
    tertiary = SuccessGreenDark,
    onTertiary = OnTertiaryDark,
    tertiaryContainer = SuccessGreenDarkContainer,
    onTertiaryContainer = OnTertiaryContainerDark,
    
    // Error
    error = ErrorRedDark,
    onError = OnErrorDark,
    errorContainer = ErrorRedDarkContainer,
    onErrorContainer = OnErrorContainerDark,
    
    // Fondos y superficies
    background = BackgroundDark,
    onBackground = OnBackgroundDark,
    surface = SurfaceDark,
    onSurface = OnSurfaceDark,
    surfaceVariant = SurfaceVariantDark,
    onSurfaceVariant = OnSurfaceVariantDark,
    
    // Bordes
    outline = OutlineDark,
    outlineVariant = OutlineVariantDark,
    
    // Otros
    inverseSurface = SurfaceLight,
    inverseOnSurface = OnSurfaceLight,
    inversePrimary = FireRed,
    scrim = OnBackgroundDark
)

/**
 * Tema principal de SIGVE
 * 
 * @param darkTheme Si es true, usa el tema oscuro
 * @param content Contenido de la aplicación
 */
@Composable
fun SIGVETheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
