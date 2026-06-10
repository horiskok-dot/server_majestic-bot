package com.example.pccontrolmobile.feature.chat

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewModelScope
import com.example.pccontrolmobile.core.ui.DashboardCard
import com.example.pccontrolmobile.core.ui.EmptyState
import com.example.pccontrolmobile.core.ui.InlineStatusBanner
import com.example.pccontrolmobile.core.ui.SectionTitle
import com.example.pccontrolmobile.core.ui.formatTime
import com.example.pccontrolmobile.data.repository.PcControlRepository
import com.example.pccontrolmobile.domain.model.ChatAuthor
import com.example.pccontrolmobile.domain.model.ChatMessage
import com.example.pccontrolmobile.domain.model.SocketConnectionState
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class ChatUiState(
    val input: String = "",
    val connectionState: SocketConnectionState = SocketConnectionState.DISCONNECTED,
    val messages: List<ChatMessage> = emptyList()
)

class ChatViewModel(private val repository: PcControlRepository) : ViewModel() {
    private val _uiState = MutableStateFlow(ChatUiState())
    val uiState = _uiState.asStateFlow()

    init {
        repository.connectSockets()
        viewModelScope.launch {
            repository.chatMessages.collect { message ->
                _uiState.update { it.copy(messages = (it.messages + message).takeLast(200)) }
            }
        }
        viewModelScope.launch {
            repository.chatConnectionState.collect { state ->
                _uiState.update { it.copy(connectionState = state) }
            }
        }
    }

    fun updateInput(value: String) {
        _uiState.update { it.copy(input = value) }
    }

    fun send() {
        val text = uiState.value.input.trim()
        if (text.isBlank()) return
        repository.sendChatMessage(text)
        _uiState.update {
            it.copy(
                input = "",
                messages = it.messages + ChatMessage(
                    id = "local_${System.currentTimeMillis()}",
                    author = ChatAuthor.USER,
                    text = text,
                    timestamp = System.currentTimeMillis()
                )
            )
        }
    }

    override fun onCleared() {
        repository.disconnectSockets()
    }
}

@Composable
fun ChatRoute(viewModel: ChatViewModel) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    androidx.compose.foundation.layout.Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        DashboardCard {
            SectionTitle("Chat / Console", "Live server messages and command exchange")
            androidx.compose.foundation.layout.Spacer(modifier = Modifier.padding(4.dp))
            InlineStatusBanner(
                title = when (uiState.connectionState) {
                    SocketConnectionState.CONNECTED -> "Connected"
                    SocketConnectionState.CONNECTING -> "Connecting"
                    SocketConnectionState.ERROR -> "Connection error"
                    SocketConnectionState.DISCONNECTED -> "Disconnected"
                },
                message = when (uiState.connectionState) {
                    SocketConnectionState.CONNECTED -> "WebSocket channel is ready for messages."
                    SocketConnectionState.CONNECTING -> "Trying to establish a live session with the server."
                    SocketConnectionState.ERROR -> "The backend did not accept the socket connection."
                    SocketConnectionState.DISCONNECTED -> "Open Settings to verify the WebSocket URL."
                },
                accent = when (uiState.connectionState) {
                    SocketConnectionState.CONNECTED -> com.example.pccontrolmobile.core.designsystem.theme.GreenAccent
                    SocketConnectionState.CONNECTING -> com.example.pccontrolmobile.core.designsystem.theme.BlueAccent
                    SocketConnectionState.ERROR -> com.example.pccontrolmobile.core.designsystem.theme.OrangeAccent
                    SocketConnectionState.DISCONNECTED -> com.example.pccontrolmobile.core.designsystem.theme.OrangeAccent
                }
            )
        }
        if (uiState.messages.isEmpty()) {
            EmptyState(
                title = "No messages yet",
                subtitle = "When the server sends system notices or replies, they will appear here."
            )
        } else {
            LazyColumn(
                modifier = Modifier.weight(1f, fill = true),
                contentPadding = PaddingValues(vertical = 8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(uiState.messages, key = { it.id }) { message ->
                    Surface(
                        color = when (message.author) {
                            ChatAuthor.USER -> MaterialTheme.colorScheme.primary.copy(alpha = 0.18f)
                            ChatAuthor.SERVER -> MaterialTheme.colorScheme.surfaceVariant
                            ChatAuthor.SYSTEM -> MaterialTheme.colorScheme.tertiary.copy(alpha = 0.18f)
                        },
                        shape = MaterialTheme.shapes.large
                    ) {
                        androidx.compose.foundation.layout.Column(Modifier.padding(12.dp)) {
                            Text(message.author.name, style = MaterialTheme.typography.labelLarge)
                            Text(message.text, modifier = Modifier.padding(top = 4.dp))
                            Text(
                                formatTime(message.timestamp),
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                }
            }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
            OutlinedTextField(
                value = uiState.input,
                onValueChange = viewModel::updateInput,
                modifier = Modifier.weight(1f),
                label = { Text("Message") }
            )
            Button(
                onClick = viewModel::send,
                enabled = uiState.input.isNotBlank() && uiState.connectionState != SocketConnectionState.CONNECTING,
                colors = ButtonDefaults.buttonColors()
            ) {
                Text("Send")
            }
        }
    }
}
