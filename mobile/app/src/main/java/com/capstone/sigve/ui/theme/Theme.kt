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
import com.capstone.sigve.domain.model.CustomColors

/* Other default colors to override
background = Color(0xFFFFFBFE),
surface = Color(0xFFFFFBFE),
onPrimary = Color.White,
onSecondary = Color.White,
onTertiary = Color.White,
onBackground = Color(0xFF1C1B1F),
onSurface = Color(0xFF1C1B1F),
*/

val LightDefaultColors = lightColorScheme(
    primary = Color(0xFF6200EE),
    secondary = Color(0xFF03DAC6),
    tertiary = Color(0xFFBB86FC),
    background = Color(0xFFE7E7E7)
)

val DarkDefaultColors = darkColorScheme(
    primary = Color(0xFFBB86FC),
    secondary = Color(0xFF03DAC6),
    tertiary = Color(0xFF6200EE),
    background = Color(0xFF343434)
)

val LightBlueColors = lightColorScheme(
    primary = Color(0xFF0D47A1),
    secondary = Color(0xFF1976D2),
    tertiary = Color(0xFF64B5F6),
    background = Color(0xFFE7E7E7)
)

val DarkBlueColors = darkColorScheme(
    primary = Color(0xFF64B5F6),
    secondary = Color(0xFF1976D2),
    tertiary = Color(0xFF0D47A1),
    background = Color(0xFF343434)
)

val LightGreenColors = lightColorScheme(
    primary = Color(0xFF4CAF50),
    secondary = Color(0xFF5500FF),
    tertiary = Color(0xFF7D5260),
    background = Color(0xFFE7E7E7)
)

val DarkGreenColors = darkColorScheme(
    primary = Color(0xFF7D5260),
    secondary = Color(0xFF625B71),
    tertiary = Color(0xFF4CAF50),
    background = Color(0xFF343434)
)

val LightRedColors = lightColorScheme(
    primary = Color(0xFFF44336),
    secondary = Color(0xFF625B71),
    tertiary = Color(0xFF7D5260),
    background = Color(0xFFE7E7E7)
)

val DarkRedColors = darkColorScheme(
    primary = Color(0xFF7D5260),
    secondary = Color(0xFF625B71),
    tertiary = Color(0xFFF44336),
    background = Color(0xFF343434)
)

@Composable
fun SIGVETheme(
    darkTheme: Boolean,
    appColor: AppColor,
    customColors: CustomColors,
    content: @Composable () -> Unit
) {

    val colorScheme = when (appColor) {
        AppColor.DEFAULT -> if (darkTheme) DarkDefaultColors else LightDefaultColors
        AppColor.BLUE -> if (darkTheme) DarkBlueColors else LightBlueColors
        AppColor.GREEN -> if (darkTheme) DarkGreenColors else LightGreenColors
        AppColor.RED -> if (darkTheme) DarkRedColors else LightRedColors

        AppColor.CUSTOM -> if (darkTheme) {
            darkColorScheme(
                primary = Color(customColors.primary),
                secondary = Color(customColors.secondary),
                tertiary = Color(customColors.tertiary),
                background = Color(customColors.background)
            )
        } else {
            lightColorScheme(
                primary = Color(customColors.primary),
                secondary = Color(customColors.secondary),
                tertiary = Color(customColors.tertiary),
                background = Color(customColors.background)
            )
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}