package com.example.pccontrolmobile.feature.control

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewModelScope
import com.example.pccontrolmobile.core.designsystem.theme.OrangeAccent
import com.example.pccontrolmobile.core.designsystem.theme.RedAccent
import com.example.pccontrolmobile.core.ui.DashboardCard
import com.example.pccontrolmobile.core.ui.EmptyState
import com.example.pccontrolmobile.core.ui.InlineStatusBanner
import com.example.pccontrolmobile.core.ui.SectionTitle
import com.example.pccontrolmobile.data.repository.PcControlRepository
import com.example.pccontrolmobile.domain.model.ActionHistoryItem
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

enum class ControlAction(
    val title: String,
    val risky: Boolean,
    val summary: String
) {
    RefreshStatus("Refresh status", false, "Pull fresh machine status from the server"),
    QuickCleanup("Run quick cleanup", false, "Fast maintenance without disruptive operations"),
    DeepCleanup("Run deep cleanup", false, "Longer maintenance with broader cleanup scope"),
    TempCleanup("Temporary files cleanup", false, "Remove cached temporary files through the backend"),
    RestartAgent("Restart agent", true, "Restart the remote PC agent service"),
    RestartPc("Restart PC", true, "Reboot the remote machine"),
    ShutdownPc("Shutdown PC", true, "Power off the remote machine")
}

data class ControlUiState(
    val busyAction: ControlAction? = null,
    val lastMessage: String? = null,
    val history: List<ActionHistoryItem> = emptyList()
) {
    val isBusy: Boolean = busyAction != null
}

class ControlViewModel(private val repository: PcControlRepository) : ViewModel() {
    private val _uiState = MutableStateFlow(ControlUiState())
    val uiState = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            repository.observeActionHistory().collect { history ->
                _uiState.update { it.copy(history = history) }
            }
        }
    }

    fun run(action: ControlAction) {
        if (_uiState.value.isBusy) return

        viewModelScope.launch {
            _uiState.update { it.copy(busyAction = action, lastMessage = null) }
            val message = when (action) {
                ControlAction.RefreshStatus -> repository.refreshStatus().fold(
                    onSuccess = { "Status refreshed successfully." },
                    onFailure = { it.message ?: "Failed to refresh status." }
                )
                ControlAction.QuickCleanup -> repository.quickCleanup().fold(
                    onSuccess = { it.message },
                    onFailure = { it.message ?: "Quick cleanup failed." }
                )
                ControlAction.DeepCleanup -> repository.deepCleanup().fold(
                    onSuccess = { it.message },
                    onFailure = { it.message ?: "Deep cleanup failed." }
                )
                ControlAction.TempCleanup -> repository.tempCleanup().fold(
                    onSuccess = { it.message },
                    onFailure = { it.message ?: "Temporary cleanup failed." }
                )
                ControlAction.RestartAgent -> repository.restartAgent().fold(
                    onSuccess = { it.message },
                    onFailure = { it.message ?: "Restart agent failed." }
                )
                ControlAction.RestartPc -> repository.restartPc().fold(
                    onSuccess = { it.message },
                    onFailure = { it.message ?: "Restart PC failed." }
                )
                ControlAction.ShutdownPc -> repository.shutdownPc().fold(
                    onSuccess = { it.message },
                    onFailure = { it.message ?: "Shutdown PC failed." }
                )
            }
            _uiState.update { it.copy(busyAction = null, lastMessage = message) }
        }
    }
}

@Composable
fun ControlRoute(
    viewModel: ControlViewModel,
    onOpenScreen: () -> Unit = {}
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    var pendingAction by remember { mutableStateOf<ControlAction?>(null) }

    pendingAction?.let { action ->
        AlertDialog(
            onDismissRequest = { pendingAction = null },
            confirmButton = {
                Button(
                    onClick = {
                        viewModel.run(action)
                        pendingAction = null
                    }
                ) {
                    Text("Confirm")
                }
            },
            dismissButton = {
                OutlinedButton(onClick = { pendingAction = null }) {
                    Text("Cancel")
                }
            },
            title = { Text("Confirm action") },
            text = { Text("Are you sure you want to ${action.title.lowercase()}?") }
        )
    }

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            DashboardCard {
                SectionTitle("Remote control", "Safe backend-powered actions for your PC")
                androidx.compose.foundation.layout.Spacer(modifier = Modifier.height(14.dp))
                InlineStatusBanner(
                    title = if (uiState.isBusy) "Action in progress" else "Ready",
                    message = uiState.lastMessage ?: "Select an action below. Risky operations always require confirmation.",
                    accent = when {
                        uiState.busyAction?.risky == true -> OrangeAccent
                        uiState.isBusy -> MaterialTheme.colorScheme.primary
                        else -> MaterialTheme.colorScheme.tertiary
                    }
                )
                androidx.compose.foundation.layout.Spacer(modifier = Modifier.height(12.dp))
                OutlinedButton(
                    onClick = onOpenScreen,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Open server screen")
                }
            }
        }

        item {
            SectionTitle(
                title = "Available actions",
                subtitle = "Buttons are disabled during active requests to prevent duplicate execution"
            )
        }

        items(ControlAction.values().toList(), key = { it.name }) { action ->
            DashboardCard {
                Text(action.title, style = MaterialTheme.typography.titleMedium)
                androidx.compose.foundation.layout.Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = action.summary,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                androidx.compose.foundation.layout.Spacer(modifier = Modifier.height(12.dp))
                Button(
                    onClick = {
                        if (action.risky) {
                            pendingAction = action
                        } else {
                            viewModel.run(action)
                        }
                    },
                    enabled = !uiState.isBusy,
                    modifier = Modifier.fillMaxWidth(),
                    colors = if (action == ControlAction.ShutdownPc) {
                        ButtonDefaults.buttonColors(
                            containerColor = RedAccent,
                            contentColor = MaterialTheme.colorScheme.onPrimary
                        )
                    } else {
                        ButtonDefaults.buttonColors()
                    }
                ) {
                    val label = if (uiState.busyAction == action) {
                        "Working..."
                    } else {
                        action.title
                    }
                    Text(label)
                }
            }
        }

        item {
            DashboardCard {
                SectionTitle("Recent action history", "Latest backend-confirmed operations")
                androidx.compose.foundation.layout.Spacer(modifier = Modifier.height(10.dp))
                if (uiState.history.isEmpty()) {
                    EmptyState(
                        title = "No control history yet",
                        subtitle = "Executed actions will appear here with their backend responses."
                    )
                } else {
                    uiState.history.take(8).forEach { item ->
                        InlineStatusBanner(
                            title = item.title,
                            message = item.summary,
                            accent = if (item.success) MaterialTheme.colorScheme.tertiary else OrangeAccent,
                            modifier = Modifier.padding(vertical = 4.dp)
                        )
                    }
                }
            }
        }
    }
}
