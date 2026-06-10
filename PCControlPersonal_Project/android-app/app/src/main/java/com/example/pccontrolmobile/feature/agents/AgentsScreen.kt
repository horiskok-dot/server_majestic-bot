package com.example.pccontrolmobile.feature.agents

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewModelScope
import com.example.pccontrolmobile.core.ui.DashboardCard
import com.example.pccontrolmobile.core.ui.ErrorState
import com.example.pccontrolmobile.core.ui.LoadingState
import com.example.pccontrolmobile.core.ui.SectionTitle
import com.example.pccontrolmobile.data.repository.PcControlRepository
import com.example.pccontrolmobile.domain.model.MobileAgent
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class AgentsUiState(
    val loading: Boolean = true,
    val agents: List<MobileAgent> = emptyList(),
    val message: String? = null
)

class AgentsViewModel(private val repository: PcControlRepository) : ViewModel() {
    private val _uiState = MutableStateFlow(AgentsUiState())
    val uiState = _uiState.asStateFlow()

    init {
        refresh()
    }

    fun refresh() {
        viewModelScope.launch {
            _uiState.update { it.copy(loading = true, message = null) }
            val result = repository.loadAgents()
            _uiState.update { it.copy(loading = false, agents = result.getOrDefault(emptyList()), message = result.exceptionOrNull()?.message) }
        }
    }

    fun ping(agentId: String) {
        viewModelScope.launch {
            val result = repository.createAgentTask(agentId, "ping")
            _uiState.update { it.copy(message = result.fold({ "Ping task created: ${it.taskId}" }, { error -> error.message })) }
            refresh()
        }
    }
}

@Composable
fun AgentsRoute(
    viewModel: AgentsViewModel,
    onOpenRemote: (String) -> Unit = {}
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    if (state.loading && state.agents.isEmpty()) {
        LoadingState("Loading agents...")
        return
    }
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item {
            SectionTitle("Agents", "Connected personal PCs")
        }
        state.message?.let { item { ErrorState(message = it, onRetry = viewModel::refresh) } }
        if (state.agents.isEmpty()) {
            item { ErrorState(message = "No agents connected yet.", onRetry = viewModel::refresh) }
        }
        items(state.agents) { agent ->
            DashboardCard {
                Column {
                    Text(agent.name, style = MaterialTheme.typography.titleMedium)
                    Spacer(Modifier.height(6.dp))
                    Text("${agent.status} | ${agent.platform} | ${agent.version}", color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text("ID: ${agent.agentId}", color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text("Task: ${agent.currentTask ?: "-"}", color = MaterialTheme.colorScheme.onSurfaceVariant)
                    agent.lastError?.takeIf { it.isNotBlank() }?.let {
                        Text("Last error: $it", color = MaterialTheme.colorScheme.error)
                    }
                    Spacer(Modifier.height(12.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Button(
                            modifier = Modifier.weight(1f),
                            onClick = { viewModel.ping(agent.agentId) }
                        ) {
                            Text("Ping")
                        }
                        OutlinedButton(
                            modifier = Modifier.weight(1f),
                            onClick = { onOpenRemote(agent.agentId) }
                        ) {
                            Text("🛋️ Пульт")
                        }
                    }
                }
            }
        }
    }
}
