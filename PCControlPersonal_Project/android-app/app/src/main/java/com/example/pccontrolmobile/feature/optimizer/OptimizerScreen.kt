package com.example.pccontrolmobile.feature.optimizer

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewModelScope
import com.example.pccontrolmobile.core.ui.DashboardCard
import com.example.pccontrolmobile.core.ui.SectionTitle
import com.example.pccontrolmobile.data.repository.PcControlRepository
import com.example.pccontrolmobile.domain.model.ActionHistoryItem
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class OptimizerUiState(
    val isRunning: Boolean = false,
    val lastSummary: String? = null,
    val history: List<ActionHistoryItem> = emptyList()
)

class OptimizerViewModel(private val repository: PcControlRepository) : ViewModel() {
    private val _uiState = MutableStateFlow(OptimizerUiState())
    val uiState = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            repository.observeActionHistory().collect { history ->
                _uiState.update { it.copy(history = history) }
            }
        }
    }

    fun runQuick() = runAction { repository.quickCleanup().getOrNull()?.message ?: "Quick cleanup failed" }
    fun runDeep() = runAction { repository.deepCleanup().getOrNull()?.message ?: "Deep cleanup failed" }
    fun runTemp() = runAction { repository.tempCleanup().getOrNull()?.message ?: "Temp cleanup failed" }

    private fun runAction(block: suspend () -> String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isRunning = true) }
            val summary = block()
            _uiState.update { it.copy(isRunning = false, lastSummary = summary) }
        }
    }
}

@Composable
fun OptimizerRoute(viewModel: OptimizerViewModel) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            DashboardCard {
                SectionTitle("Optimizer", "Safe backend actions with history")
                androidx.compose.foundation.layout.Spacer(modifier = Modifier.height(8.dp))
                Text(
                    uiState.lastSummary ?: "Choose an optimization task",
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
        item {
            Button(onClick = viewModel::runQuick, enabled = !uiState.isRunning, modifier = Modifier.fillMaxWidth()) {
                Text(if (uiState.isRunning) "Working..." else "Quick cleanup")
            }
        }
        item {
            Button(onClick = viewModel::runDeep, enabled = !uiState.isRunning, modifier = Modifier.fillMaxWidth()) {
                Text(if (uiState.isRunning) "Working..." else "Deep cleanup")
            }
        }
        item {
            Button(onClick = viewModel::runTemp, enabled = !uiState.isRunning, modifier = Modifier.fillMaxWidth()) {
                Text(if (uiState.isRunning) "Working..." else "Temporary files cleanup")
            }
        }
        item {
            DashboardCard {
                SectionTitle("Recent optimizer history")
                androidx.compose.foundation.layout.Spacer(modifier = Modifier.height(8.dp))
                if (uiState.history.isEmpty()) {
                    Text("No optimization history yet", color = MaterialTheme.colorScheme.onSurfaceVariant)
                } else {
                    uiState.history.take(10).forEach {
                        Text("${it.title}: ${it.summary}")
                    }
                }
            }
        }
    }
}
