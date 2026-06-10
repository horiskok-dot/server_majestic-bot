package com.example.pccontrolmobile.navigation

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.CenterAlignedTopAppBar
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.example.pccontrolmobile.app.AppContainer
import com.example.pccontrolmobile.app.SimpleViewModelFactory
import com.example.pccontrolmobile.feature.agents.AgentsRoute
import com.example.pccontrolmobile.feature.agents.AgentsViewModel
import com.example.pccontrolmobile.feature.chat.ChatRoute
import com.example.pccontrolmobile.feature.chat.ChatViewModel
import com.example.pccontrolmobile.feature.control.ControlRoute
import com.example.pccontrolmobile.feature.control.ControlViewModel
import com.example.pccontrolmobile.feature.dashboard.DashboardRoute
import com.example.pccontrolmobile.feature.dashboard.DashboardViewModel
import com.example.pccontrolmobile.feature.files.FilesRoute
import com.example.pccontrolmobile.feature.files.FilesViewModel
import com.example.pccontrolmobile.feature.logs.LogsRoute
import com.example.pccontrolmobile.feature.logs.LogsViewModel
import com.example.pccontrolmobile.feature.monitor.MonitorRoute
import com.example.pccontrolmobile.feature.monitor.MonitorViewModel
import com.example.pccontrolmobile.feature.optimizer.OptimizerRoute
import com.example.pccontrolmobile.feature.optimizer.OptimizerViewModel
import com.example.pccontrolmobile.feature.remote.RemoteRoute
import com.example.pccontrolmobile.feature.remote.RemoteViewModel
import com.example.pccontrolmobile.feature.screen.ScreenRoute
import com.example.pccontrolmobile.feature.screen.ScreenViewModel
import com.example.pccontrolmobile.feature.settings.SettingsRoute
import com.example.pccontrolmobile.feature.settings.SettingsViewModel
import com.example.pccontrolmobile.feature.tasks.TasksRoute
import com.example.pccontrolmobile.feature.tasks.TasksViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PcControlNavHost(container: AppContainer) {
    val navController = rememberNavController()
    val backStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = backStackEntry?.destination
    val currentRoute = currentDestination?.route
    val isTopLevel = topLevelDestinations.any { it.route == currentRoute }

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        containerColor = androidx.compose.material3.MaterialTheme.colorScheme.background,
        topBar = {
            CenterAlignedTopAppBar(
                title = {
                    Text(routeTitle(currentRoute))
                },
                navigationIcon = {
                    if (!isTopLevel && currentRoute != null) {
                        IconButton(onClick = { navController.popBackStack() }) {
                            Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                        }
                    }
                },
                colors = TopAppBarDefaults.centerAlignedTopAppBarColors(
                    containerColor = androidx.compose.material3.MaterialTheme.colorScheme.background,
                    titleContentColor = androidx.compose.material3.MaterialTheme.colorScheme.onBackground
                )
            )
        },
        bottomBar = {
            if (isTopLevel) {
                NavigationBar(
                    containerColor = androidx.compose.material3.MaterialTheme.colorScheme.surface,
                    tonalElevation = 0.dp
                ) {
                    topLevelDestinations.forEach { destination ->
                        val selected = currentDestination?.hierarchy?.any { it.route == destination.route } == true
                        NavigationBarItem(
                            selected = selected,
                            onClick = {
                                navController.navigate(destination.route) {
                                    popUpTo(navController.graph.findStartDestination().id) {
                                        saveState = true
                                    }
                                    launchSingleTop = true
                                    restoreState = true
                                }
                            },
                            icon = { Icon(destination.icon, contentDescription = destination.label) },
                            label = { Text(destination.label) },
                            colors = NavigationBarItemDefaults.colors(
                                selectedIconColor = androidx.compose.material3.MaterialTheme.colorScheme.primary,
                                selectedTextColor = androidx.compose.material3.MaterialTheme.colorScheme.primary,
                                indicatorColor = androidx.compose.material3.MaterialTheme.colorScheme.primary.copy(alpha = 0.14f),
                                unselectedIconColor = androidx.compose.material3.MaterialTheme.colorScheme.onSurfaceVariant,
                                unselectedTextColor = androidx.compose.material3.MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        )
                    }
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = TopLevelDestination.Home.route,
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
            composable(TopLevelDestination.Home.route) {
                val vm: DashboardViewModel = viewModel(
                    factory = SimpleViewModelFactory { DashboardViewModel(container.repository) }
                )
                Box(modifier = Modifier.fillMaxSize()) {
                    DashboardRoute(
                        viewModel = vm,
                        onOpenMonitor = { navController.navigate(TopLevelDestination.Monitor.route) },
                        onOpenOptimizer = { navController.navigate(ExtraDestination.Optimizer) },
                        onOpenChat = { navController.navigate(ExtraDestination.Chat) },
                        onOpenFiles = { navController.navigate(ExtraDestination.Files) },
                        onOpenAgents = { navController.navigate(ExtraDestination.Agents) },
                        onOpenTasks = { navController.navigate(ExtraDestination.Tasks) }
                    )
                }
            }
            composable(TopLevelDestination.Monitor.route) {
                val vm: MonitorViewModel = viewModel(
                    factory = SimpleViewModelFactory { MonitorViewModel(container.repository) }
                )
                Box(modifier = Modifier.fillMaxSize()) {
                    MonitorRoute(vm)
                }
            }
            composable(TopLevelDestination.Control.route) {
                val vm: ControlViewModel = viewModel(
                    factory = SimpleViewModelFactory { ControlViewModel(container.repository) }
                )
                Box(modifier = Modifier.fillMaxSize()) {
                    ControlRoute(
                        viewModel = vm,
                        onOpenScreen = { navController.navigate(ExtraDestination.Screen) }
                    )
                }
            }
            composable(TopLevelDestination.Logs.route) {
                val vm: LogsViewModel = viewModel(
                    factory = SimpleViewModelFactory { LogsViewModel(container.repository) }
                )
                Box(modifier = Modifier.fillMaxSize()) {
                    LogsRoute(vm)
                }
            }
            composable(TopLevelDestination.Settings.route) {
                val vm: SettingsViewModel = viewModel(
                    factory = SimpleViewModelFactory { SettingsViewModel(container.repository) }
                )
                Box(modifier = Modifier.fillMaxSize()) {
                    SettingsRoute(vm)
                }
            }
            composable(ExtraDestination.Optimizer) {
                val vm: OptimizerViewModel = viewModel(
                    factory = SimpleViewModelFactory { OptimizerViewModel(container.repository) }
                )
                Box(modifier = Modifier.fillMaxSize()) {
                    OptimizerRoute(vm)
                }
            }
            composable(ExtraDestination.Chat) {
                val vm: ChatViewModel = viewModel(
                    factory = SimpleViewModelFactory { ChatViewModel(container.repository) }
                )
                Box(modifier = Modifier.fillMaxSize()) {
                    ChatRoute(vm)
                }
            }
            composable(ExtraDestination.Files) {
                val vm: FilesViewModel = viewModel(
                    factory = SimpleViewModelFactory { FilesViewModel(container.repository) }
                )
                Box(modifier = Modifier.fillMaxSize()) {
                    FilesRoute(vm)
                }
            }
            composable(ExtraDestination.Screen) {
                val vm: ScreenViewModel = viewModel(
                    factory = SimpleViewModelFactory { ScreenViewModel(container.repository) }
                )
                Box(modifier = Modifier.fillMaxSize()) {
                    ScreenRoute(vm)
                }
            }
            composable(ExtraDestination.Agents) {
                val vm: AgentsViewModel = viewModel(
                    factory = SimpleViewModelFactory { AgentsViewModel(container.repository) }
                )
                Box(modifier = Modifier.fillMaxSize()) {
                    AgentsRoute(
                        viewModel = vm,
                        onOpenRemote = { agentId -> navController.navigate(ExtraDestination.remote(agentId)) }
                    )
                }
            }
            composable(ExtraDestination.Tasks) {
                val vm: TasksViewModel = viewModel(
                    factory = SimpleViewModelFactory { TasksViewModel(container.repository) }
                )
                Box(modifier = Modifier.fillMaxSize()) {
                    TasksRoute(vm)
                }
            }
            composable(ExtraDestination.RemotePattern) { backStackEntry ->
                val agentId = backStackEntry.arguments?.getString("agentId") ?: return@composable
                val vm: RemoteViewModel = viewModel(
                    key = "remote_$agentId",
                    factory = SimpleViewModelFactory { RemoteViewModel(agentId, container.repository) }
                )
                Box(modifier = Modifier.fillMaxSize()) {
                    RemoteRoute(vm)
                }
            }
        }
    }
}

private fun routeTitle(route: String?): String {
    // remote/{agentId} pattern — check with startsWith
    if (route?.startsWith("remote/") == true) return "🛋️ Пульт управления"
    return when (route) {
        TopLevelDestination.Home.route -> "PC Control Mobile"
        TopLevelDestination.Monitor.route -> "PC Monitor"
        TopLevelDestination.Control.route -> "Remote Control"
        TopLevelDestination.Logs.route -> "Logs & Events"
        TopLevelDestination.Settings.route -> "Settings"
        ExtraDestination.Optimizer -> "Optimizer"
        ExtraDestination.Chat -> "Chat / Console"
        ExtraDestination.Files -> "Files"
        ExtraDestination.Screen -> "Server Screen"
        ExtraDestination.Agents -> "Agents"
        ExtraDestination.Tasks -> "Tasks"
        else -> "PC Control Mobile"
    }
}
