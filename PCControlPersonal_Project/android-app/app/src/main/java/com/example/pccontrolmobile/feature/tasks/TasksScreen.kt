package com.example.pccontrolmobile.feature.tasks

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
import com.example.pccontrolmobile.domain.model.MobileTask
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class TasksUiState(
    val loading: Boolean = true,
    val tasks: List<MobileTask> = emptyList(),
    val message: String? = null
)

class TasksViewModel(private val repository: PcControlRepository) : ViewModel() {
    private val _uiState = MutableStateFlow(TasksUiState())
    val uiState = _uiState.asStateFlow()

    init {
        refresh()
    }

    fun refresh() {
        viewModelScope.launch {
            _uiState.update { it.copy(loading = true, message = null) }
            val result = repository.loadTasks()
            _uiState.update { it.copy(loading = false, tasks = result.getOrDefault(emptyList()), message = result.exceptionOrNull()?.message) }
        }
    }

    fun cancel(taskId: String) {
        viewModelScope.launch {
            val result = repository.cancelTask(taskId)
            _uiState.update { it.copy(message = result.fold({ "Cancelled: ${it.taskId}" }, { error -> error.message })) }
            refresh()
        }
    }

    fun retry(taskId: String) {
        viewModelScope.launch {
            val result = repository.retryTask(taskId)
            _uiState.update { it.copy(message = result.fold({ "Retry created: ${it.taskId}" }, { error -> error.message })) }
            refresh()
        }
    }
}

@Composable
fun TasksRoute(viewModel: TasksViewModel) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    if (state.loading && state.tasks.isEmpty()) {
        LoadingState("Loading tasks...")
        return
    }
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item {
            SectionTitle("Tasks", "Queue, results and retry controls")
        }
        state.message?.let { item { ErrorState(message = it, onRetry = viewModel::refresh) } }
        if (state.tasks.isEmpty()) {
            item { ErrorState(message = "No tasks yet.", onRetry = viewModel::refresh) }
        }
        items(state.tasks) { task ->
            DashboardCard {
                Column {
                    Text(task.action, style = MaterialTheme.typography.titleMedium)
                    Spacer(Modifier.height(6.dp))
                    Text("${task.status} | ${task.agentId}", color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text("ID: ${task.taskId}", color = MaterialTheme.colorScheme.onSurfaceVariant)
                    task.error?.takeIf { it.isNotBlank() }?.let { Text(it, color = MaterialTheme.colorScheme.error) }
                    task.result?.takeIf { it.isNotBlank() }?.let { Text(it.take(240), color = MaterialTheme.colorScheme.onSurfaceVariant) }
                    Spacer(Modifier.height(12.dp))
                    Row(horizontalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.fillMaxWidth()) {
                        OutlinedButton(modifier = Modifier.weight(1f), onClick = { viewModel.cancel(task.taskId) }) {
                            Text("Cancel")
                        }
                        Button(modifier = Modifier.weight(1f), onClick = { viewModel.retry(task.taskId) }) {
                            Text("Retry")
                        }
                    }
                }
            }
        }
    }
}
