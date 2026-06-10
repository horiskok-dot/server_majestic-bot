package com.example.pccontrolmobile.data.remote.ws

import com.example.pccontrolmobile.domain.model.ChatAuthor
import com.example.pccontrolmobile.domain.model.ChatMessage
import com.example.pccontrolmobile.domain.model.SocketConnectionState
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.StateFlow
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener

class RealtimeGateway(
    private val client: OkHttpClient
) {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val _chatMessages = MutableSharedFlow<ChatMessage>(extraBufferCapacity = 32)
    private val _statusMessages = MutableSharedFlow<String>(extraBufferCapacity = 32)
    private val _chatConnection = MutableStateFlow(SocketConnectionState.DISCONNECTED)

    val chatMessages: SharedFlow<ChatMessage> = _chatMessages
    val statusMessages: SharedFlow<String> = _statusMessages
    val chatConnection: StateFlow<SocketConnectionState> = _chatConnection

    private var chatSocket: WebSocket? = null
    private var statusSocket: WebSocket? = null

    fun connect(baseWsUrl: String) {
        connectChat(baseWsUrl)
        connectStatus(baseWsUrl)
    }

    fun disconnect() {
        chatSocket?.close(1000, "manual_disconnect")
        statusSocket?.close(1000, "manual_disconnect")
        chatSocket = null
        statusSocket = null
        _chatConnection.value = SocketConnectionState.DISCONNECTED
    }

    fun sendChatMessage(baseWsUrl: String, message: String) {
        if (chatSocket == null) {
            connectChat(baseWsUrl)
        }
        chatSocket?.send("""{"message":"${message.replace("\"", "\\\"")}","author":"user"}""")
    }

    private fun connectChat(baseWsUrl: String) {
        _chatConnection.value = SocketConnectionState.CONNECTING
        val request = Request.Builder().url(joinWs(baseWsUrl, "ws/chat")).build()
        chatSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                _chatConnection.value = SocketConnectionState.CONNECTED
                _chatMessages.tryEmit(
                    ChatMessage(
                        id = "chat_open_${System.currentTimeMillis()}",
                        author = ChatAuthor.SYSTEM,
                        text = "Connected to chat",
                        timestamp = System.currentTimeMillis(),
                        connectionNotice = true
                    )
                )
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                _chatMessages.tryEmit(
                    ChatMessage(
                        id = "chat_${System.currentTimeMillis()}",
                        author = ChatAuthor.SERVER,
                        text = text,
                        timestamp = System.currentTimeMillis()
                    )
                )
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                _chatConnection.value = SocketConnectionState.ERROR
                _chatMessages.tryEmit(
                    ChatMessage(
                        id = "chat_error_${System.currentTimeMillis()}",
                        author = ChatAuthor.SYSTEM,
                        text = t.message ?: "Chat connection error",
                        timestamp = System.currentTimeMillis(),
                        connectionNotice = true
                    )
                )
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                _chatConnection.value = SocketConnectionState.DISCONNECTED
            }
        })
    }

    private fun connectStatus(baseWsUrl: String) {
        val request = Request.Builder().url(joinWs(baseWsUrl, "ws/status")).build()
        statusSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onMessage(webSocket: WebSocket, text: String) {
                _statusMessages.tryEmit(text)
            }
        })
    }

    private fun joinWs(base: String, path: String): String {
        val normalized = if (base.endsWith("/")) base else "$base/"
        return normalized + path.removePrefix("/")
    }
}
