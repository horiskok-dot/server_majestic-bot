package com.example.pccontrolmobile.feature.monitor

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewModelScope
import com.example.pccontrolmobile.core.designsystem.theme.BlueAccent
import com.example.pccontrolmobile.core.designsystem.theme.CyanAccent
import com.example.pccontrolmobile.core.designsystem.theme.GreenAccent
import com.example.pccontrolmobile.core.designsystem.theme.OrangeAccent
import com.example.pccontrolmobile.core.ui.DashboardCard
import com.example.pccontrolmobile.core.ui.ErrorState
import com.example.pccontrolmobile.core.ui.MetricCard
import com.example.pccontrolmobile.core.ui.MetricHistoryChart
import com.example.pccontrolmobile.core.ui.SectionTitle
import com.example.pccontrolmobile.core.ui.decimalText
import com.example.pccontrolmobile.core.ui.percentText
import com.example.pccontrolmobile.data.repository.PcControlRepository
import com.example.pccontrolmobile.domain.model.SystemMetrics
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch

data class MonitorUiState(
    val isRefreshing: Boolean = false,
    val metrics: SystemMetrics = SystemMetrics(),
    val history: List<SystemMetrics> = emptyList(),
    val errorMessage: String? = null
)

class MonitorViewModel(private val repository: PcControlRepository) : ViewModel() {
    private val _uiState = MutableStateFlow(MonitorUiState())
    val uiState = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            repository.observeMetricsHistory(32).collect { history ->
                _uiState.update { it.copy(history = history) }
            }
        }
        viewModelScope.launch {
            while (isActive) {
                refresh()
                val interval = repository.getCurrentSettings().refreshIntervalSeconds.coerceAtLeast(5)
                delay(interval * 1000L)
            }
        }
    }

    fun refresh() {
        viewModelScope.launch {
            _uiState.update { it.copy(isRefreshing = true, errorMessage = null) }
            val result = repository.refreshMetrics()
            _uiState.update { current ->
                current.copy(
                    isRefreshing = false,
                    metrics = result.getOrElse { current.metrics },
                    errorMessage = result.exceptionOrNull()?.message
                )
            }
        }
    }
}

@Composable
fun MonitorRoute(viewModel: MonitorViewModel) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            DashboardCard {
                SectionTitle("PC Monitor", "Live telemetry from your backend")
                androidx.compose.foundation.layout.Spacer(modifier = Modifier.height(12.dp))
                Button(onClick = viewModel::refresh) {
                    Text(if (uiState.isRefreshing) "Refreshing..." else "Refresh now")
                }
            }
        }
        item {
            MetricCard(
                title = "CPU Usage",
                value = percentText(uiState.metrics.cpuUsage),
                caption = uiState.metrics.uptime ?: "Uptime unavailable",
                accent = BlueAccent
            )
        }
        item {
            MetricCard(
                title = "RAM Usage",
                value = percentText(uiState.metrics.ramUsage),
                caption = uiState.metrics.runningTask ?: "No active task",
                accent = GreenAccent
            )
        }
        item {
            MetricCard(
                title = "Disk Usage",
                value = percentText(uiState.metrics.diskUsage),
                caption = uiState.metrics.networkStatus ?: "Network unknown",
                accent = OrangeAccent
            )
        }
        item {
            MetricCard(
                title = "Temperature / FPS",
                value = "${decimalText(uiState.metrics.temperatureC, "°C")}  |  ${decimalText(uiState.metrics.fps, "fps")}",
                caption = "Gracefully handles missing values",
                accent = CyanAccent
            )
        }
        item {
            DashboardCard {
                SectionTitle("Metric History", "CPU trend")
                androidx.compose.foundation.layout.Spacer(modifier = Modifier.height(12.dp))
                MetricHistoryChart(
                    values = uiState.history.map { it.cpuUsage ?: 0f },
                    modifier = Modifier.fillMaxWidth()
                )
            }
        }
        uiState.errorMessage?.let { message ->
            item {
                ErrorState(message = message, onRetry = viewModel::refresh)
            }
        }
    }
}
