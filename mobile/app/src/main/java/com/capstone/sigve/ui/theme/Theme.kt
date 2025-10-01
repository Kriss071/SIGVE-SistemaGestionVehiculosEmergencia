package com.capstone.sigve.ui.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import com.capstone.sigve.domain.model.AppColor

private val DarkColorScheme = darkColorScheme(
    primary = Purple80,
    secondary = PurpleGrey80,
    tertiary = Pink80
)

private val LightColorScheme = lightColorScheme(
    primary = Purple40,
    secondary = PurpleGrey40,
    tertiary = Pink40

    /* Other default colors to override
    background = Color(0xFFFFFBFE),
    surface = Color(0xFFFFFBFE),
    onPrimary = Color.White,
    onSecondary = Color.White,
    onTertiary = Color.White,
    onBackground = Color(0xFF1C1B1F),
    onSurface = Color(0xFF1C1B1F),
    */
)

private val LightDefaultColors = lightColorScheme(
    primary = Color(0xFF6200EE),
    secondary = Color(0xFF03DAC6),
    tertiary = Color(0xFFBB86FC)
)

private val DarkDefaultColors = darkColorScheme(
    primary = Color(0xFFBB86FC),
    secondary = Color(0xFF03DAC6),
    tertiary = Color(0xFF6200EE)
)

private val LightBlueColors = lightColorScheme(
    primary = Color(0xFF0D47A1),
    secondary = Color(0xFF1976D2),
    tertiary = Color(0xFF64B5F6)
)

private val DarkBlueColors = darkColorScheme(
    primary = Color(0xFF0D47A1),
    secondary = Color(0xFF1976D2),
    tertiary = Color(0xFF64B5F6)
)

@Composable
fun SIGVETheme(
    darkTheme: Boolean,
    dynamicColor: Boolean = true,
    appColor: AppColor,
    content: @Composable () -> Unit
) {

    val colorScheme = when (appColor) {
        AppColor.DEFAULT -> if (darkTheme) DarkDefaultColors else LightDefaultColors
        AppColor.BLUE -> if (darkTheme) DarkBlueColors else LightBlueColors
        AppColor.GREEN -> if (darkTheme) darkColorScheme(primary = Color(0xFF2E7D32)) else lightColorScheme(primary = Color(0xFF4CAF50))
        AppColor.RED -> if (darkTheme) darkColorScheme(primary = Color(0xFFC62828)) else lightColorScheme(primary = Color(0xFFF44336))
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}