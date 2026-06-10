package com.example.pccontrolmobile.feature.settings

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewModelScope
import com.example.pccontrolmobile.core.network.ApiConfig
import com.example.pccontrolmobile.core.ui.DashboardCard
import com.example.pccontrolmobile.core.ui.InlineStatusBanner
import com.example.pccontrolmobile.core.ui.SectionTitle
import com.example.pccontrolmobile.data.repository.PcControlRepository
import com.example.pccontrolmobile.domain.model.AppSettings
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class SettingsUiState(
    val accessKey: String = "",

    val notificationsEnabled: Boolean = true,
    val darkModeEnabled: Boolean = true,
    val isSaving: Boolean = false,
    val testMessage: String? = null
)

class SettingsViewModel(private val repository: PcControlRepository) : ViewModel() {
    private val _uiState = MutableStateFlow(SettingsUiState())
    val uiState = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            val settings = repository.settings.first()
            _uiState.value = SettingsUiState(
                accessKey = settings.accessKey,

                notificationsEnabled = settings.notificationsEnabled,
                darkModeEnabled = settings.darkModeEnabled
            )
        }
    }

    fun updateAccessKey(value: String) = _uiState.update { it.copy(accessKey = value) }

    fun updateNotifications(value: Boolean) = _uiState.update { it.copy(notificationsEnabled = value) }
    fun updateDarkMode(value: Boolean) = _uiState.update { it.copy(darkModeEnabled = value) }

    fun save() {
        viewModelScope.launch {
            _uiState.update { it.copy(isSaving = true, testMessage = null) }
            val current = uiState.value
            repository.updateSettings(
                AppSettings(
                    baseUrl = ApiConfig.BASE_URL,
                    webSocketUrl = ApiConfig.WEBSOCKET_URL,
                    accessKey = current.accessKey.trim(),
                    refreshIntervalSeconds = 10,
                    notificationsEnabled = current.notificationsEnabled,
                    darkModeEnabled = current.darkModeEnabled
                )
            )
            _uiState.update { it.copy(isSaving = false, testMessage = "✅ Сохранено!") }
        }
    }

    fun testConnection() {
        viewModelScope.launch {
            _uiState.update { it.copy(testMessage = "⏳ Проверяю соединение...") }
            val message = repository.testConnection(ApiConfig.BASE_URL).fold(
                onSuccess = { "✅ Соединение установлено!" },
                onFailure = { "❌ Ошибка: ${it.message}" }
            )
            _uiState.update { it.copy(testMessage = message) }
        }
    }
}

@Composable
fun SettingsRoute(viewModel: SettingsViewModel) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item {
            DashboardCard {
                SectionTitle("⚙️ Настройки", "Введите ключ доступа из Telegram-бота")
            }
        }



        item {
            DashboardCard {
                Text("🔑 Ключ активации", style = MaterialTheme.typography.titleMedium)
                Spacer(Modifier.height(8.dp))
                Text(
                    "Получите ключ командой /key в Telegram-боте PC Manager",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(Modifier.height(12.dp))
                OutlinedTextField(
                    value = uiState.accessKey,
                    onValueChange = viewModel::updateAccessKey,
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("Ключ доступа") },
                    placeholder = { Text("TG-XXXX-XXXX-XXXX") },
                    visualTransformation = PasswordVisualTransformation(),
                    singleLine = true
                )
            }
        }

        item {
            DashboardCard {
                Text("🎨 Внешний вид", style = MaterialTheme.typography.titleMedium)
                Spacer(Modifier.height(10.dp))
                Row(
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Уведомления")
                    Switch(checked = uiState.notificationsEnabled, onCheckedChange = viewModel::updateNotifications)
                }
                Row(
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Тёмная тема")
                    Switch(checked = uiState.darkModeEnabled, onCheckedChange = viewModel::updateDarkMode)
                }
            }
        }

        item {
            Button(onClick = viewModel::testConnection, modifier = Modifier.fillMaxWidth()) {
                Text("🔗 Проверить соединение")
            }
        }

        item {
            Button(onClick = viewModel::save, modifier = Modifier.fillMaxWidth()) {
                Text(if (uiState.isSaving) "Сохраняю..." else "💾 Сохранить")
            }
        }

        uiState.testMessage?.let { message ->
            item {
                DashboardCard {
                    InlineStatusBanner(
                        title = "Статус",
                        message = message,
                        accent = if (message.startsWith("✅")) MaterialTheme.colorScheme.tertiary
                                 else MaterialTheme.colorScheme.error
                    )
                }
            }
        }
    }
}
