package com.capstone.sigve.ui.settings

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Slider
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.unit.dp
import androidx.hilt.lifecycle.viewmodel.compose.hiltViewModel
import com.capstone.sigve.domain.model.AppColor
import com.capstone.sigve.domain.model.AppTheme
import com.capstone.sigve.domain.model.CustomColors
import com.capstone.sigve.ui.theme.DarkBlueColors
import com.capstone.sigve.ui.theme.DarkDefaultColors
import com.capstone.sigve.ui.theme.DarkGreenColors
import com.capstone.sigve.ui.theme.DarkRedColors
import com.capstone.sigve.ui.theme.LightBlueColors
import com.capstone.sigve.ui.theme.LightDefaultColors
import com.capstone.sigve.ui.theme.LightGreenColors
import com.capstone.sigve.ui.theme.LightRedColors

@Composable
fun SettingsScreen(
    viewModel: SettingsViewModel = hiltViewModel(),
    innerPadding: PaddingValues
) {
    val theme by viewModel.theme.collectAsState()
    val color by viewModel.color.collectAsState()
    val customColors by viewModel.customColors.collectAsState()

    val themes =
        listOf(AppColor.DEFAULT, AppColor.BLUE, AppColor.GREEN, AppColor.RED, AppColor.CUSTOM)

    var selectedColor by remember { mutableStateOf(Color.White) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .padding(innerPadding)
            .padding(top = 28.dp, start = 16.dp, end = 16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Top
    ) {
        Text(
            text = "Ajustes · Colores actuales",
            style = MaterialTheme.typography.titleLarge,
            modifier = Modifier.padding(bottom = 12.dp)
        )

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 8.dp),
            horizontalArrangement = Arrangement.spacedBy(16.dp, Alignment.CenterHorizontally)
        ) {
            val colorList = listOf(
                "Primario" to MaterialTheme.colorScheme.primary,
                "Secundario" to MaterialTheme.colorScheme.secondary,
                "Terciario" to MaterialTheme.colorScheme.tertiary,
                "Fondo" to MaterialTheme.colorScheme.background
            )

            colorList.forEach { (label, color) ->
                ColorCard(label = label, color = color)
            }
        }

        Spacer(modifier = Modifier.height(18.dp))

        Text(text = "Tema: ${theme.name}", style = MaterialTheme.typography.bodyMedium)
        Text(text = "Paleta: ${color.name}", style = MaterialTheme.typography.bodySmall)

        Spacer(modifier = Modifier.height(18.dp))
        HorizontalDivider()
        Spacer(modifier = Modifier.height(18.dp))



        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp, Alignment.CenterHorizontally)
        ) {
            themes.forEach { appColor ->
                val colors = getThemeColors(
                    appColor = appColor,
                    customColors = customColors,
                    darkTheme = (theme == AppTheme.DARK)
                )
                MiniThemeCard(
                    colors = colors,
                    selected = (appColor == color),
                    onClick = { viewModel.setColor(appColor) }
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))
        Button(onClick = {
            val newTheme = if (theme == AppTheme.DARK) AppTheme.LIGHT else AppTheme.DARK
            viewModel.setTheme(newTheme)
        }) {
            Text(if (theme == AppTheme.DARK) "Tema Claro" else "Tema Oscuro")
        }

        if (color == AppColor.CUSTOM) {
            Spacer(modifier = Modifier.height(16.dp))
            Text("Colores personalizados", style = MaterialTheme.typography.titleMedium)

            Spacer(modifier = Modifier.height(8.dp))

            CustomColorPickerSection(
                currentColors = customColors,
                onColorChange = { newColors -> viewModel.setCustomColors(newColors) },
                defaultColor = customColors
            )
        }
    }
}

@Composable
private fun ColorCard(label: String, color: Color) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center,
        modifier = Modifier.widthIn(min = 80.dp)
    ) {
        Card(
            modifier = Modifier.size(100.dp),
            shape = RoundedCornerShape(12.dp),
            colors = CardDefaults.cardColors(containerColor = color),
            elevation = CardDefaults.cardElevation(defaultElevation = 6.dp)
        ) {}

        Spacer(modifier = Modifier.height(8.dp))

        Text(text = label, style = MaterialTheme.typography.bodyMedium)

        Spacer(modifier = Modifier.height(4.dp))

        Text(text = colorToHex(color), style = MaterialTheme.typography.bodySmall)
    }
}

private fun colorToHex(color: Color): String = String.format("#%08X", color.toArgb())

@Composable
fun MiniThemeCard(
    colors: List<Color>,
    selected: Boolean,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .size(width = 60.dp, height = 60.dp)
            .clickable { onClick() },
        shape = RoundedCornerShape(8.dp),
        border = if (selected) BorderStroke(2.dp, MaterialTheme.colorScheme.primary) else null,
        elevation = CardDefaults.cardElevation(4.dp)
    ) {
        Column(
            verticalArrangement = Arrangement.SpaceEvenly,
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier.padding(4.dp)
        ) {
            colors.forEach { color ->
                Box(
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxWidth()
                        .background(color, shape = RoundedCornerShape(4.dp))
                )
            }
        }
    }
}

@Composable
fun getThemeColors(
    appColor: AppColor,
    customColors: CustomColors,
    darkTheme: Boolean
): List<Color> {
    return when (appColor) {
        AppColor.DEFAULT -> listOf(
            if (darkTheme) DarkDefaultColors.primary else LightDefaultColors.primary,
            if (darkTheme) DarkDefaultColors.secondary else LightDefaultColors.secondary,
            if (darkTheme) DarkDefaultColors.tertiary else LightDefaultColors.tertiary,
            if (darkTheme) DarkDefaultColors.background else LightDefaultColors.background
        )

        AppColor.BLUE -> listOf(
            if (darkTheme) DarkBlueColors.primary else LightBlueColors.primary,
            if (darkTheme) DarkBlueColors.secondary else LightBlueColors.secondary,
            if (darkTheme) DarkBlueColors.tertiary else LightBlueColors.tertiary,
            if (darkTheme) DarkBlueColors.background else LightBlueColors.background
        )

        AppColor.GREEN -> listOf(
            if (darkTheme) DarkGreenColors.primary else LightGreenColors.primary,
            if (darkTheme) DarkGreenColors.secondary else LightGreenColors.secondary,
            if (darkTheme) DarkGreenColors.tertiary else LightGreenColors.tertiary,
            if (darkTheme) DarkGreenColors.background else LightGreenColors.background
        )

        AppColor.RED -> listOf(
            if (darkTheme) DarkRedColors.primary else LightRedColors.primary,
            if (darkTheme) DarkRedColors.secondary else LightRedColors.secondary,
            if (darkTheme) DarkRedColors.tertiary else LightRedColors.tertiary,
            if (darkTheme) DarkRedColors.background else LightRedColors.background
        )

        AppColor.CUSTOM -> listOf(
            Color(customColors.primary),
            Color(customColors.secondary),
            Color(customColors.tertiary),
            Color(customColors.background)
        )
    }
}

@Composable
fun CustomColorPickerSection(
    currentColors: CustomColors,
    onColorChange: (CustomColors) -> Unit,
    defaultColor: CustomColors
) {
    val scrollState = rememberScrollState()
    val labels = listOf("Primario", "Secundario", "Terciario", "Fondo")
    val values = listOf(
        Color(currentColors.primary),
        Color(currentColors.secondary),
        Color(currentColors.tertiary),
        Color(currentColors.background)
    )

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(12.dp)
            .verticalScroll(scrollState),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        labels.zip(values).forEachIndexed { index, pair ->
            val (label, initial) = pair
            Column {
                Text(label, style = MaterialTheme.typography.bodyMedium)
                Spacer(modifier = Modifier.height(8.dp))

                // HSV picker para este color
                HSVInlinePicker(
                    initialColor = initial,
                    onColorSelected = { newColor ->
                        // Convertir a Long y propagar el nuevo CustomColors
                        val newLong = newColor.toArgb().toLong()
                        val updated = when (index) {
                            0 -> currentColors.copy(primary = newLong)
                            1 -> currentColors.copy(secondary = newLong)
                            2 -> currentColors.copy(tertiary = newLong)
                            3 -> currentColors.copy(background = newLong)
                            else -> currentColors
                        }
                        onColorChange(updated)
                    }
                )
            }
        }
    }
}


@Composable
fun CustomColorCard(
    label: String,
    color: Color,
    onColorSelected: (Color) -> Unit
) {
    val options = listOf(
        Color(0xFF2196F3), // azul
        Color(0xFF4CAF50), // verde
        Color(0xFFF44336), // rojo
        Color(0xFFFF9800), // naranjo
        Color(0xFF9C27B0), // violeta
    )

    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(label, style = MaterialTheme.typography.bodyMedium)
        Row(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            modifier = Modifier.padding(vertical = 4.dp)
        ) {
            options.forEach { c ->
                Box(
                    modifier = Modifier
                        .size(36.dp)
                        .background(c, RoundedCornerShape(8.dp))
                        .clickable { onColorSelected(c) }
                        .then(
                            if (c == color) Modifier.background(Color.Black.copy(alpha = 0.2f))
                            else Modifier
                        )
                )
            }
        }
    }
}

@Composable
fun HSVInlinePicker(
    initialColor: Color,
    onColorSelected: (Color) -> Unit
) {
    // convierte initialColor a HSV para inicializar sliders
    val tmp = FloatArray(3)
    android.graphics.Color.colorToHSV(initialColor.toArgb(), tmp)

    var hue by remember { mutableStateOf(tmp[0]) }            // 0..360
    var saturation by remember { mutableStateOf(tmp[1]) }     // 0..1
    var value by remember { mutableStateOf(tmp[2]) }          // 0..1

    // si cambia initialColor desde afuera, actualizamos sliders
    LaunchedEffect(initialColor) {
        android.graphics.Color.colorToHSV(initialColor.toArgb(), tmp)
        hue = tmp[0]
        saturation = tmp[1]
        value = tmp[2]
    }

    val preview = Color.hsv(hue, saturation, value)

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        verticalArrangement = Arrangement.spacedBy(6.dp)
    ) {
        // preview
        Box(
            modifier = Modifier
                .height(40.dp)
                .fillMaxWidth()
                .background(preview, RoundedCornerShape(8.dp))
                .border(
                    1.dp,
                    MaterialTheme.colorScheme.onSurface.copy(alpha = 0.08f),
                    RoundedCornerShape(8.dp)
                )
        )

        // Hue slider 0..360
        Text("Tono: ${hue.toInt()}°", style = MaterialTheme.typography.bodySmall)
        Slider(
            value = hue,
            onValueChange = {
                hue = it
                onColorSelected(Color.hsv(hue, saturation, value))
            },
            valueRange = 0f..360f,
            modifier = Modifier.fillMaxWidth(),
            colors = androidx.compose.material3.SliderDefaults.colors(thumbColor = preview)
        )

        // Saturation 0..1
        Text(
            "Saturación: ${(saturation * 100).toInt()}%",
            style = MaterialTheme.typography.bodySmall
        )
        Slider(
            value = saturation,
            onValueChange = {
                saturation = it
                onColorSelected(Color.hsv(hue, saturation, value))
            },
            valueRange = 0f..1f,
            modifier = Modifier.fillMaxWidth(),
            colors = androidx.compose.material3.SliderDefaults.colors(thumbColor = preview)
        )

        // Value / Brightness 0..1
        Text("Brillo: ${(value * 100).toInt()}%", style = MaterialTheme.typography.bodySmall)
        Slider(
            value = value,
            onValueChange = {
                value = it
                onColorSelected(Color.hsv(hue, saturation, value))
            },
            valueRange = 0f..1f,
            modifier = Modifier.fillMaxWidth(),
            colors = androidx.compose.material3.SliderDefaults.colors(thumbColor = preview)
        )
    }
}