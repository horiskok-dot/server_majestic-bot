package com.example.pccontrolmobile.feature.dashboard

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
import androidx.compose.material.ExperimentalMaterialApi
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Bolt
import androidx.compose.material.icons.filled.ChatBubbleOutline
import androidx.compose.material.icons.filled.FolderOpen
import androidx.compose.material.icons.filled.Memory
import androidx.compose.material.icons.filled.Speed
import androidx.compose.material.icons.filled.Storage
import androidx.compose.material.icons.filled.Thermostat
import androidx.compose.material.icons.filled.Tune
import androidx.compose.material.icons.filled.Wifi
import androidx.compose.material.pullrefresh.PullRefreshIndicator
import androidx.compose.material.pullrefresh.PullRefreshState
import androidx.compose.material.pullrefresh.pullRefresh
import androidx.compose.material.pullrefresh.rememberPullRefreshState
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewModelScope
import com.example.pccontrolmobile.core.designsystem.theme.BlueAccent
import com.example.pccontrolmobile.core.designsystem.theme.CyanAccent
import com.example.pccontrolmobile.core.designsystem.theme.GreenAccent
import com.example.pccontrolmobile.core.designsystem.theme.OrangeAccent
import com.example.pccontrolmobile.core.designsystem.theme.PurpleAccent
import com.example.pccontrolmobile.core.ui.ActionTile
import com.example.pccontrolmobile.core.ui.DashboardCard
import com.example.pccontrolmobile.core.ui.ErrorState
import com.example.pccontrolmobile.core.ui.InlineStatusBanner
import com.example.pccontrolmobile.core.ui.LoadingState
import com.example.pccontrolmobile.core.ui.MetricCard
import com.example.pccontrolmobile.core.ui.MetricHistoryChart
import com.example.pccontrolmobile.core.ui.SectionTitle
import com.example.pccontrolmobile.core.ui.StatusChip
import com.example.pccontrolmobile.core.ui.decimalText
import com.example.pccontrolmobile.core.ui.formatTime
import com.example.pccontrolmobile.core.ui.percentText
import com.example.pccontrolmobile.data.repository.PcControlRepository
import com.example.pccontrolmobile.domain.model.SystemMetrics
import com.example.pccontrolmobile.domain.model.SystemStatus
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class DashboardUiState(
    val isLoading: Boolean = true,
    val status: SystemStatus = SystemStatus(),
    val metrics: SystemMetrics = SystemMetrics(),
    val history: List<SystemMetrics> = emptyList(),
    val errorMessage: String? = null
)

private data class DashboardMetricCard(
    val title: String,
    val value: String,
    val caption: String,
    val accent: androidx.compose.ui.graphics.Color,
    val icon: ImageVector
)

class DashboardViewModel(
    private val repository: PcControlRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow(DashboardUiState())
    val uiState = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            repository.observeMetricsHistory().collect { history ->
                _uiState.update { it.copy(history = history) }
            }
        }
        refresh()
    }

    fun refresh() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            val statusResult = repository.refreshStatus()
            val metricsResult = repository.refreshMetrics()
            _uiState.update { current ->
                current.copy(
                    isLoading = false,
                    status = statusResult.getOrElse { current.status },
                    metrics = metricsResult.getOrElse { current.metrics },
                    errorMessage = statusResult.exceptionOrNull()?.message
                        ?: metricsResult.exceptionOrNull()?.message
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterialApi::class)
@Composable
fun DashboardRoute(
    viewModel: DashboardViewModel,
    onOpenMonitor: () -> Unit,
    onOpenOptimizer: () -> Unit,
    onOpenChat: () -> Unit,
    onOpenFiles: () -> Unit,
    onOpenAgents: () -> Unit,
    onOpenTasks: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val pullRefreshState = rememberPullRefreshState(uiState.isLoading, viewModel::refresh)

    Column(
        modifier = Modifier
            .fillMaxSize()
            .pullRefresh(pullRefreshState)
    ) {
        BoxPullRefreshIndicator(uiState.isLoading, pullRefreshState)
        if (uiState.isLoading && uiState.history.isEmpty()) {
            LoadingState("Syncing your PC dashboard...")
        } else {
            DashboardScreen(
                state = uiState,
                onRefresh = viewModel::refresh,
                onOpenMonitor = onOpenMonitor,
                onOpenOptimizer = onOpenOptimizer,
                onOpenChat = onOpenChat,
                onOpenFiles = onOpenFiles,
                onOpenAgents = onOpenAgents,
                onOpenTasks = onOpenTasks
            )
        }
    }
}

@OptIn(ExperimentalMaterialApi::class)
@Composable
private fun BoxPullRefreshIndicator(
    refreshing: Boolean,
    pullRefreshState: PullRefreshState
) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .padding(top = 8.dp),
        contentAlignment = Alignment.TopCenter
    ) {
        PullRefreshIndicator(refreshing = refreshing, state = pullRefreshState)
    }
}

@Composable
private fun DashboardScreen(
    state: DashboardUiState,
    onRefresh: () -> Unit,
    onOpenMonitor: () -> Unit,
    onOpenOptimizer: () -> Unit,
    onOpenChat: () -> Unit,
    onOpenFiles: () -> Unit,
    onOpenAgents: () -> Unit,
    onOpenTasks: () -> Unit
) {
    val metrics = buildList {
        add(
            DashboardMetricCard(
                title = "CPU",
                value = percentText(state.metrics.cpuUsage),
                caption = state.metrics.runningTask ?: "Processor load",
                accent = BlueAccent,
                icon = Icons.Default.Memory
            )
        )
        add(
            DashboardMetricCard(
                title = "RAM",
                value = percentText(state.metrics.ramUsage),
                caption = state.metrics.uptime ?: "Memory pressure",
                accent = GreenAccent,
                icon = Icons.Default.Bolt
            )
        )
        add(
            DashboardMetricCard(
                title = "Disk",
                value = percentText(state.metrics.diskUsage),
                caption = state.metrics.networkStatus ?: "Storage pressure",
                accent = OrangeAccent,
                icon = Icons.Default.Storage
            )
        )
        add(
            DashboardMetricCard(
                title = "Temperature",
                value = decimalText(state.metrics.temperatureC, "°C"),
                caption = "Sensor telemetry",
                accent = CyanAccent,
                icon = Icons.Default.Thermostat
            )
        )
        if (state.metrics.fps != null) {
            add(
                DashboardMetricCard(
                    title = "FPS",
                    value = decimalText(state.metrics.fps, "fps"),
                    caption = "Realtime graphics data",
                    accent = PurpleAccent,
                    icon = Icons.Default.Speed
                )
            )
        }
    }

    androidx.compose.foundation.lazy.LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(start = 16.dp, end = 16.dp, top = 8.dp, bottom = 28.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            DashboardCard {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.Top
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = "PC Control Mobile",
                            style = MaterialTheme.typography.labelLarge,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = state.status.hostName,
                            style = MaterialTheme.typography.headlineMedium
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = "Last sync: ${formatTime(state.status.lastUpdate)}",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        state.status.agentVersion?.takeIf { it.isNotBlank() }?.let { version ->
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = "Agent version $version",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                    StatusChip(
                        online = state.status.online,
                        label = if (state.status.online) "Online" else "Offline"
                    )
                }
                Spacer(modifier = Modifier.height(18.dp))
                InlineStatusBanner(
                    title = if (state.status.online) "Connected to backend" else "Backend unavailable",
                    message = if (state.status.online) {
                        state.metrics.networkStatus ?: "Realtime telemetry is flowing"
                    } else {
                        "Pull to refresh or check the server connection in Settings"
                    },
                    accent = if (state.status.online) GreenAccent else OrangeAccent
                )
            }
        }

        item {
            SectionTitle(
                title = "System snapshot",
                subtitle = "Live overview of the most important machine metrics"
            )
        }

        items(metrics.chunked(2).size) { rowIndex ->
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                metrics.chunked(2)[rowIndex].forEach { metric ->
                    MetricCard(
                        title = metric.title,
                        value = metric.value,
                        caption = metric.caption,
                        accent = metric.accent,
                        icon = metric.icon,
                        modifier = Modifier.weight(1f)
                    )
                }
                if (metrics.chunked(2)[rowIndex].size == 1) {
                    Spacer(modifier = Modifier.weight(1f))
                }
            }
        }

        item {
            DashboardCard {
                SectionTitle("Performance trend", "Recent CPU samples from local cache")
                Spacer(modifier = Modifier.height(14.dp))
                MetricHistoryChart(
                    values = state.history.mapNotNull { it.cpuUsage ?: 0f },
                    modifier = Modifier.fillMaxWidth()
                )
            }
        }

        item {
            SectionTitle(
                title = "Quick actions",
                subtitle = "Jump straight into the tools you use most often"
            )
        }

        item {
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                ActionTile(
                    title = "Monitor",
                    subtitle = "Detailed live metrics and uptime",
                    modifier = Modifier.weight(1f),
                    onClick = onOpenMonitor
                )
                ActionTile(
                    title = "Optimizer",
                    subtitle = "Quick and deep maintenance actions",
                    modifier = Modifier.weight(1f),
                    onClick = onOpenOptimizer
                )
            }
        }

        item {
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                ActionTile(
                    title = "Agents",
                    subtitle = "Connected PCs and quick ping",
                    modifier = Modifier.weight(1f),
                    onClick = onOpenAgents
                )
                ActionTile(
                    title = "Tasks",
                    subtitle = "Queue, cancel and retry",
                    modifier = Modifier.weight(1f),
                    onClick = onOpenTasks
                )
            }
        }

        item {
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                ActionTile(
                    title = "Chat / Console",
                    subtitle = "Server messages, notices and command chat",
                    modifier = Modifier.weight(1f),
                    onClick = onOpenChat
                )
                ActionTile(
                    title = "Files",
                    subtitle = "Reports, logs and downloadable artifacts",
                    modifier = Modifier.weight(1f),
                    onClick = onOpenFiles
                )
            }
        }

        state.errorMessage?.let { message ->
            item {
                ErrorState(message = message, onRetry = onRefresh)
            }
        }
    }
}
