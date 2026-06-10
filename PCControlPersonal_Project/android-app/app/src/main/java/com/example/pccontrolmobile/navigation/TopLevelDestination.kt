package com.example.pccontrolmobile.navigation

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.ListAlt
import androidx.compose.material.icons.filled.Memory
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Tune
import androidx.compose.ui.graphics.vector.ImageVector

sealed class TopLevelDestination(
    val route: String,
    val label: String,
    val icon: ImageVector
) {
    object Home : TopLevelDestination("home", "Home", Icons.Default.Home)
    object Monitor : TopLevelDestination("monitor", "Monitor", Icons.Default.Memory)
    object Control : TopLevelDestination("control", "Control", Icons.Default.Tune)
    object Logs : TopLevelDestination("logs", "Logs", Icons.Default.ListAlt)
    object Settings : TopLevelDestination("settings", "Settings", Icons.Default.Settings)
}

object ExtraDestination {
    const val Optimizer = "optimizer"
    const val Chat = "chat"
    const val Files = "files"
    const val Screen = "screen"
    const val Agents = "agents"
    const val Tasks = "tasks"
    const val RemotePattern = "remote/{agentId}"
    fun remote(agentId: String) = "remote/$agentId"
}

val topLevelDestinations = listOf(
    TopLevelDestination.Home,
    TopLevelDestination.Monitor,
    TopLevelDestination.Control,
    TopLevelDestination.Logs,
    TopLevelDestination.Settings
)
