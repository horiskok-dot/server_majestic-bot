package com.example.pccontrolmobile.domain.model

import com.example.pccontrolmobile.core.network.ApiConfig

data class SystemStatus(
    val online: Boolean = false,
    val hostName: String = "PC",
    val lastUpdate: Long = 0L,
    val agentVersion: String? = null
)

data class SystemMetrics(
    val cpuUsage: Float? = null,
    val ramUsage: Float? = null,
    val diskUsage: Float? = null,
    val temperatureC: Float? = null,
    val fps: Float? = null,
    val uptime: String? = null,
    val networkStatus: String? = null,
    val runningTask: String? = null,
    val timestamp: Long = System.currentTimeMillis()
)

enum class LogLevel {
    INFO, WARNING, ERROR, SUCCESS
}

data class LogEntry(
    val id: String,
    val level: LogLevel,
    val message: String,
    val source: String,
    val timestamp: Long
)

enum class OptimizationType {
    QUICK, DEEP, TEMP, STARTUP, PROCESS
}

data class ActionResult(
    val success: Boolean,
    val message: String,
    val timestamp: Long = System.currentTimeMillis()
)

data class OptimizationResult(
    val type: OptimizationType,
    val success: Boolean,
    val cleanedMb: Double? = null,
    val durationMs: Long? = null,
    val message: String,
    val timestamp: Long = System.currentTimeMillis()
)

data class ActionHistoryItem(
    val id: Long,
    val title: String,
    val summary: String,
    val success: Boolean,
    val timestamp: Long
)

enum class ChatAuthor {
    USER, SERVER, SYSTEM
}

data class ChatMessage(
    val id: String,
    val author: ChatAuthor,
    val text: String,
    val timestamp: Long,
    val connectionNotice: Boolean = false
)

data class RemoteFile(
    val id: String,
    val name: String,
    val sizeBytes: Long,
    val updatedAt: Long,
    val type: String? = null,
    val downloadUrl: String? = null,
    val details: String? = null
)

data class MobileAgent(
    val agentId: String,
    val name: String,
    val status: String,
    val lastSeen: String?,
    val latency: Int,
    val version: String,
    val platform: String,
    val currentTask: String?,
    val lastError: String?
)

data class MobileTask(
    val taskId: String,
    val agentId: String,
    val action: String,
    val status: String,
    val result: String?,
    val error: String?
)

enum class SocketConnectionState {
    DISCONNECTED, CONNECTING, CONNECTED, ERROR
}

data class AppSettings(
    val baseUrl: String = ApiConfig.BASE_URL,
    val webSocketUrl: String = ApiConfig.WEBSOCKET_URL,
    val accessKey: String = "",
    val refreshIntervalSeconds: Int = 10,
    val notificationsEnabled: Boolean = true,
    val darkModeEnabled: Boolean = true
)
