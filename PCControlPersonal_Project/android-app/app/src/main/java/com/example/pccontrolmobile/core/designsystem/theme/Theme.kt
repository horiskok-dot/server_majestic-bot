package com.example.pccontrolmobile.core.designsystem.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable

private val DarkColors = darkColorScheme(
    primary = BlueAccent,
    secondary = CyanAccent,
    tertiary = GreenAccent,
    background = Slate950,
    surface = SurfaceRaised,
    surfaceVariant = SurfaceMuted,
    onPrimary = Slate950,
    onSecondary = Slate950,
    onBackground = TextPrimary,
    onSurface = TextPrimary,
    onSurfaceVariant = TextSecondary,
    error = RedAccent,
    outline = CardBorder,
    outlineVariant = CardBorderStrong,
    secondaryContainer = SurfaceOverlay,
    tertiaryContainer = SurfaceOverlay
)

@Composable
fun PcControlMobileTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = DarkColors,
        typography = AppTypography,
        content = content
    )
}
