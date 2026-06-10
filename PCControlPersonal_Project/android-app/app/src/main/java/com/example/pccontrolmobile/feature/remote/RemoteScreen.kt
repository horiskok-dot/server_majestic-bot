package com.example.pccontrolmobile.feature.remote

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewModelScope
import com.example.pccontrolmobile.core.ui.DashboardCard
import com.example.pccontrolmobile.core.ui.InlineStatusBanner
import com.example.pccontrolmobile.core.ui.SectionTitle
import com.example.pccontrolmobile.data.repository.PcControlRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

// ─── UiState ────────────────────────────────────────────────────────────────

data class RemoteUiState(
    val busy: Boolean = false,
    val lastMessage: String? = null
)

// ─── ViewModel ──────────────────────────────────────────────────────────────

class RemoteViewModel(
    private val agentId: String,
    private val repository: PcControlRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(RemoteUiState())
    val uiState = _uiState.asStateFlow()

    fun sendAction(payload: Map<String, String>) {
        if (_uiState.value.busy) return
        viewModelScope.launch {
            _uiState.update { it.copy(busy = true, lastMessage = null) }
            val result = repository.sendRemoteInput(agentId, payload)
            _uiState.update {
                it.copy(
                    busy = false,
                    lastMessage = result.fold(
                        onSuccess = { task -> "✅ Задача создана: ${task.taskId}" },
                        onFailure = { err -> "❌ ${err.message}" }
                    )
                )
            }
        }
    }
}

// ─── Dialogs ────────────────────────────────────────────────────────────────

private sealed interface RemoteDialog {
    object TextInput : RemoteDialog
    object TimerInput : RemoteDialog
    object AppLauncher : RemoteDialog
}

private val launcherOptions = listOf(
    "steam" to "Steam",
    "epic_games" to "Epic Games",
    "gta_5_rp" to "GTA 5 RP",
    "majestic_launcher" to "Majestic RP",
    "people_playground" to "People Playground"
)

// ─── Composable entry point ─────────────────────────────────────────────────

@Composable
fun RemoteRoute(viewModel: RemoteViewModel) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    var activeDialog by remember { mutableStateOf<RemoteDialog?>(null) }

    // ── Text-input dialog ────────────────────────────────────────────────────
    if (activeDialog == RemoteDialog.TextInput) {
        var inputText by remember { mutableStateOf("") }
        AlertDialog(
            onDismissRequest = { activeDialog = null },
            title = { Text("⌨️ Ввод текста") },
            text = {
                OutlinedTextField(
                    value = inputText,
                    onValueChange = { inputText = it },
                    label = { Text("Текст для ввода") },
                    singleLine = false,
                    keyboardOptions = KeyboardOptions(imeAction = ImeAction.Default),
                    modifier = Modifier.fillMaxWidth()
                )
            },
            confirmButton = {
                Button(onClick = {
                    viewModel.sendAction(mapOf("action" to "type_text", "text" to inputText))
                    activeDialog = null
                }) { Text("Отправить") }
            },
            dismissButton = {
                OutlinedButton(onClick = { activeDialog = null }) { Text("Отмена") }
            }
        )
    }

    // ── Timer dialog ─────────────────────────────────────────────────────────
    if (activeDialog == RemoteDialog.TimerInput) {
        var minutesText by remember { mutableStateOf("10") }
        AlertDialog(
            onDismissRequest = { activeDialog = null },
            title = { Text("⏰ Таймер выключения") },
            text = {
                OutlinedTextField(
                    value = minutesText,
                    onValueChange = { minutesText = it.filter { c -> c.isDigit() } },
                    label = { Text("Минут до выключения") },
                    singleLine = true,
                    keyboardOptions = KeyboardOptions(
                        keyboardType = KeyboardType.Number,
                        imeAction = ImeAction.Done
                    ),
                    modifier = Modifier.fillMaxWidth()
                )
            },
            confirmButton = {
                Button(onClick = {
                    val minutes = minutesText.ifBlank { "10" }
                    viewModel.sendAction(
                        mapOf(
                            "action" to "start_timer",
                            "duration" to minutes,
                            "timer_action" to "shutdown"
                        )
                    )
                    activeDialog = null
                }) { Text("Запустить") }
            },
            dismissButton = {
                OutlinedButton(onClick = { activeDialog = null }) { Text("Отмена") }
            }
        )
    }

    // ── App-launcher dialog ──────────────────────────────────────────────────
    if (activeDialog == RemoteDialog.AppLauncher) {
        AlertDialog(
            onDismissRequest = { activeDialog = null },
            title = { Text("🎮 Запустить игру") },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    launcherOptions.forEach { (key, label) ->
                        OutlinedButton(
                            onClick = {
                                viewModel.sendAction(
                                    mapOf("action" to "launch_allowed_app", "app_key" to key)
                                )
                                activeDialog = null
                            },
                            modifier = Modifier.fillMaxWidth()
                        ) { Text(label) }
                    }
                }
            },
            confirmButton = {},
            dismissButton = {
                OutlinedButton(onClick = { activeDialog = null }) { Text("Закрыть") }
            }
        )
    }

    // ── Main layout ──────────────────────────────────────────────────────────
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item {
            SectionTitle("🛋️ Пульт управления", "Управление ПК как с дивана")
        }

        // Status banner
        item {
            DashboardCard {
                InlineStatusBanner(
                    title = if (state.busy) "Выполняется..." else "Готов",
                    message = state.lastMessage ?: "Нажмите кнопку для отправки команды на ПК",
                    accent = if (state.busy)
                        MaterialTheme.colorScheme.primary
                    else
                        MaterialTheme.colorScheme.tertiary
                )
            }
        }

        // Mouse & scroll controls
        item {
            DashboardCard {
                Text("🖱️ Мышь и скролл", style = MaterialTheme.typography.titleMedium)
                Spacer(Modifier.height(10.dp))

                // Row 1: scroll up | move up | double click
                RemoteRow(enabled = !state.busy) {
                    RemoteButton("📜 Вверх", it) {
                        viewModel.sendAction(mapOf("action" to "scroll_up"))
                    }
                    RemoteButton("⬆️ Вверх", it) {
                        viewModel.sendAction(mapOf("action" to "move", "dx" to "0", "dy" to "-50"))
                    }
                    RemoteButton("🖱️ 2×ЛКМ", it) {
                        viewModel.sendAction(mapOf("action" to "click_double"))
                    }
                }

                Spacer(Modifier.height(6.dp))

                // Row 2: left | click left | click right | right
                RemoteRow(enabled = !state.busy) {
                    RemoteButton("◀️ Влево", it) {
                        viewModel.sendAction(mapOf("action" to "move", "dx" to "-50", "dy" to "0"))
                    }
                    RemoteButton("🖱️ ЛКМ", it) {
                        viewModel.sendAction(mapOf("action" to "click_left"))
                    }
                    RemoteButton("🖱️ ПКМ", it) {
                        viewModel.sendAction(mapOf("action" to "click_right"))
                    }
                    RemoteButton("▶️ Вправо", it) {
                        viewModel.sendAction(mapOf("action" to "move", "dx" to "50", "dy" to "0"))
                    }
                }

                Spacer(Modifier.height(6.dp))

                // Row 3: scroll down | move down | text input
                RemoteRow(enabled = !state.busy) {
                    RemoteButton("📜 Вниз", it) {
                        viewModel.sendAction(mapOf("action" to "scroll_down"))
                    }
                    RemoteButton("⬇️ Вниз", it) {
                        viewModel.sendAction(mapOf("action" to "move", "dx" to "0", "dy" to "50"))
                    }
                    RemoteButton("⌨️ Текст", it) {
                        activeDialog = RemoteDialog.TextInput
                    }
                }
            }
        }

        // Media controls
        item {
            DashboardCard {
                Text("🎵 Медиа и звук", style = MaterialTheme.typography.titleMedium)
                Spacer(Modifier.height(10.dp))

                // Row 4: play/pause | mute | vol down | vol up | desktop
                RemoteRow(enabled = !state.busy) {
                    RemoteButton("⏯️ Пауза", it) {
                        viewModel.sendAction(mapOf("action" to "media", "key" to "play_pause"))
                    }
                    RemoteButton("🔇 Мут", it) {
                        viewModel.sendAction(mapOf("action" to "media", "key" to "mute"))
                    }
                    RemoteButton("🔉 Тише", it) {
                        viewModel.sendAction(mapOf("action" to "media", "key" to "volume_down"))
                    }
                    RemoteButton("🔊 Громче", it) {
                        viewModel.sendAction(mapOf("action" to "media", "key" to "volume_up"))
                    }
                    RemoteButton("🖥️ Стол", it) {
                        viewModel.sendAction(mapOf("action" to "media", "key" to "show_desktop"))
                    }
                }
            }
        }

        // PC power controls
        item {
            DashboardCard {
                Text("⚡ Управление питанием", style = MaterialTheme.typography.titleMedium)
                Spacer(Modifier.height(10.dp))

                // Row 5: timer shutdown | sleep | lock
                RemoteRow(enabled = !state.busy) {
                    RemoteButton("⏰ Таймер", it) {
                        activeDialog = RemoteDialog.TimerInput
                    }
                    RemoteButton("💤 Сон", it) {
                        viewModel.sendAction(mapOf("action" to "sleep_pc"))
                    }
                    RemoteButton("🔒 Блок.", it) {
                        viewModel.sendAction(mapOf("action" to "lock_pc"))
                    }
                }
            }
        }

        // Game launcher
        item {
            DashboardCard {
                Text("🎮 Запуск приложений", style = MaterialTheme.typography.titleMedium)
                Spacer(Modifier.height(10.dp))
                Button(
                    onClick = { activeDialog = RemoteDialog.AppLauncher },
                    enabled = !state.busy,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("🎮 Запустить игру")
                }
            }
        }
    }
}

// ─── Helper composables ──────────────────────────────────────────────────────

@Composable
private fun RemoteRow(
    enabled: Boolean,
    content: @Composable RowScope.(Boolean) -> Unit
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(6.dp)
    ) {
        content(enabled)
    }
}

@Composable
private fun RowScope.RemoteButton(
    label: String,
    enabled: Boolean,
    onClick: () -> Unit
) {
    Button(
        onClick = onClick,
        enabled = enabled,
        modifier = Modifier
            .weight(1f)
            .height(52.dp),
        contentPadding = PaddingValues(horizontal = 4.dp, vertical = 4.dp),
        colors = ButtonDefaults.buttonColors(
            containerColor = MaterialTheme.colorScheme.secondaryContainer,
            contentColor = MaterialTheme.colorScheme.onSecondaryContainer,
            disabledContainerColor = MaterialTheme.colorScheme.secondaryContainer.copy(alpha = 0.4f),
            disabledContentColor = MaterialTheme.colorScheme.onSecondaryContainer.copy(alpha = 0.4f)
        )
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            maxLines = 2
        )
    }
}
