package com.example.pccontrolmobile.data.remote.dto

import com.example.pccontrolmobile.domain.model.ActionResult
import com.example.pccontrolmobile.domain.model.ChatAuthor
import com.example.pccontrolmobile.domain.model.ChatMessage
import com.example.pccontrolmobile.domain.model.LogEntry
import com.example.pccontrolmobile.domain.model.LogLevel
import com.example.pccontrolmobile.domain.model.MobileAgent
import com.example.pccontrolmobile.domain.model.MobileTask
import com.example.pccontrolmobile.domain.model.OptimizationResult
import com.example.pccontrolmobile.domain.model.OptimizationType
import com.example.pccontrolmobile.domain.model.RemoteFile
import com.example.pccontrolmobile.domain.model.SystemMetrics
import com.example.pccontrolmobile.domain.model.SystemStatus
import com.squareup.moshi.Json

data class StatusDto(
    @Json(name = "online") val online: Boolean? = null,
    @Json(name = "hostName") val hostName: String? = null,
    @Json(name = "lastUpdate") val lastUpdate: Long? = null,
    @Json(name = "agentVersion") val agentVersion: String? = null,
    @Json(name = "cpu") val cpu: Float? = null,
    @Json(name = "ram") val ram: Float? = null,
    @Json(name = "disk") val disk: Float? = null,
    @Json(name = "temperature") val temperature: Float? = null,
    @Json(name = "fps") val fps: Float? = null,
    @Json(name = "uptime") val uptime: String? = null,
    @Json(name = "networkStatus") val networkStatus: String? = null,
    @Json(name = "runningTask") val runningTask: String? = null
)

data class MetricsDto(
    @Json(name = "cpu") val cpu: Float? = null,
    @Json(name = "ram") val ram: Float? = null,
    @Json(name = "disk") val disk: Float? = null,
    @Json(name = "temperature") val temperature: Float? = null,
    @Json(name = "fps") val fps: Float? = null,
    @Json(name = "uptime") val uptime: String? = null,
    @Json(name = "networkStatus") val networkStatus: String? = null,
    @Json(name = "runningTask") val runningTask: String? = null,
    @Json(name = "timestamp") val timestamp: Long? = null
)

data class LogDto(
    @Json(name = "id") val id: String? = null,
    @Json(name = "level") val level: String? = null,
    @Json(name = "message") val message: String? = null,
    @Json(name = "source") val source: String? = null,
    @Json(name = "timestamp") val timestamp: Long? = null
)

data class ActionResponseDto(
    @Json(name = "success") val success: Boolean? = null,
    @Json(name = "message") val message: String? = null,
    @Json(name = "cleanedMb") val cleanedMb: Double? = null,
    @Json(name = "durationMs") val durationMs: Long? = null
)

data class FileDto(
    @Json(name = "id") val id: Long? = null,
    @Json(name = "filename") val filename: String? = null,
    @Json(name = "original_filename") val originalFilename: String? = null,
    @Json(name = "name") val name: String? = null,
    @Json(name = "size_bytes") val sizeBytesSnake: Long? = null,
    @Json(name = "sizeBytes") val sizeBytes: Long? = null,
    @Json(name = "created_at") val createdAt: String? = null,
    @Json(name = "updatedAt") val updatedAt: Long? = null,
    @Json(name = "public_type") val publicType: String? = null,
    @Json(name = "type") val type: String? = null,
    @Json(name = "downloadUrl") val downloadUrl: String? = null,
    @Json(name = "details") val details: String? = null
)

data class ServerInfoDto(
    @Json(name = "server_name") val serverName: String? = null,
    @Json(name = "hostname") val hostname: String? = null,
    @Json(name = "local_ip") val localIp: String? = null,
    @Json(name = "public_url") val publicUrl: String? = null,
    @Json(name = "server_port") val serverPort: Int? = null,
    @Json(name = "base_url") val baseUrl: String? = null,
    @Json(name = "websocket_url") val websocketUrl: String? = null,
    @Json(name = "uptime") val uptime: Long? = null,
    @Json(name = "version") val version: String? = null
)

data class ChatMessageDto(
    @Json(name = "id") val id: String? = null,
    @Json(name = "author") val author: String? = null,
    @Json(name = "message") val message: String? = null,
    @Json(name = "timestamp") val timestamp: Long? = null
)

data class LoginRequestDto(
    @Json(name = "admin_token") val adminToken: String
)

data class LoginResponseDto(
    @Json(name = "access_token") val accessToken: String,
    @Json(name = "token_type") val tokenType: String? = null,
    @Json(name = "expires_in") val expiresIn: Long? = null
)

data class MobileAgentDto(
    @Json(name = "agent_id") val agentId: String? = null,
    @Json(name = "name") val name: String? = null,
    @Json(name = "status") val status: String? = null,
    @Json(name = "last_seen") val lastSeen: String? = null,
    @Json(name = "latency") val latency: Int? = null,
    @Json(name = "version") val version: String? = null,
    @Json(name = "platform") val platform: String? = null,
    @Json(name = "hostname") val hostname: String? = null,
    @Json(name = "username") val username: String? = null,
    @Json(name = "os") val os: String? = null,
    @Json(name = "local_ip") val localIp: String? = null,
    @Json(name = "public_ip") val publicIp: String? = null,
    @Json(name = "connection_ip") val connectionIp: String? = null,
    @Json(name = "camera_enabled") val cameraEnabled: Boolean? = null,
    @Json(name = "video_enabled") val videoEnabled: Boolean? = null,
    @Json(name = "current_task") val currentTask: String? = null,
    @Json(name = "last_error") val lastError: String? = null
)

data class MobileTaskDto(
    @Json(name = "task_id") val taskId: String? = null,
    @Json(name = "agent_id") val agentId: String? = null,
    @Json(name = "action") val action: String? = null,
    @Json(name = "status") val status: String? = null,
    @Json(name = "result") val result: String? = null,
    @Json(name = "error") val error: String? = null
)

data class MobileTaskCreateDto(
    @Json(name = "agent_id") val agentId: String,
    @Json(name = "action") val action: String,
    @Json(name = "payload") val payload: Map<String, String> = emptyMap(),
    @Json(name = "confirmed") val confirmed: Boolean = false
)

fun StatusDto.toSystemStatus() = SystemStatus(
    online = online ?: false,
    hostName = hostName ?: "PC",
    lastUpdate = lastUpdate ?: System.currentTimeMillis(),
    agentVersion = agentVersion
)

fun StatusDto.toMetrics() = SystemMetrics(
    cpuUsage = cpu,
    ramUsage = ram,
    diskUsage = disk,
    temperatureC = temperature,
    fps = fps,
    uptime = uptime,
    networkStatus = networkStatus,
    runningTask = runningTask,
    timestamp = lastUpdate ?: System.currentTimeMillis()
)

fun MetricsDto.toModel() = SystemMetrics(
    cpuUsage = cpu,
    ramUsage = ram,
    diskUsage = disk,
    temperatureC = temperature,
    fps = fps,
    uptime = uptime,
    networkStatus = networkStatus,
    runningTask = runningTask,
    timestamp = timestamp ?: System.currentTimeMillis()
)

fun LogDto.toModel() = LogEntry(
    id = id ?: "${timestamp ?: System.currentTimeMillis()}_${message.orEmpty()}",
    level = when (level?.lowercase()) {
        "warning", "warn" -> LogLevel.WARNING
        "error" -> LogLevel.ERROR
        "success", "ok" -> LogLevel.SUCCESS
        else -> LogLevel.INFO
    },
    message = message ?: "",
    source = source ?: "server",
    timestamp = timestamp ?: System.currentTimeMillis()
)

fun ActionResponseDto.toActionResult() = ActionResult(
    success = success ?: false,
    message = message ?: "Unknown action result"
)

fun ActionResponseDto.toOptimizationResult(type: OptimizationType) = OptimizationResult(
    type = type,
    success = success ?: false,
    cleanedMb = cleanedMb,
    durationMs = durationMs,
    message = message ?: "No details"
)

fun FileDto.toModel() = RemoteFile(
    id = id?.toString() ?: filename ?: name.orEmpty(),
    name = originalFilename ?: name ?: filename ?: "Unknown file",
    sizeBytes = sizeBytesSnake ?: sizeBytes ?: 0L,
    updatedAt = updatedAt ?: System.currentTimeMillis(),
    type = publicType ?: type,
    downloadUrl = downloadUrl,
    details = details
)

fun ChatMessageDto.toModel() = ChatMessage(
    id = id ?: "${timestamp ?: System.currentTimeMillis()}_${message.orEmpty()}",
    author = when (author?.lowercase()) {
        "user" -> ChatAuthor.USER
        "system" -> ChatAuthor.SYSTEM
        else -> ChatAuthor.SERVER
    },
    text = message ?: "",
    timestamp = timestamp ?: System.currentTimeMillis()
)

fun MobileAgentDto.toModel() = MobileAgent(
    agentId = agentId.orEmpty(),
    name = name ?: "Agent",
    status = status ?: "offline",
    lastSeen = lastSeen,
    latency = latency ?: 0,
    version = version ?: "unknown",
    platform = platform ?: "Windows",
    currentTask = currentTask,
    lastError = lastError
)

fun MobileTaskDto.toModel() = MobileTask(
    taskId = taskId.orEmpty(),
    agentId = agentId.orEmpty(),
    action = action.orEmpty(),
    status = status ?: "unknown",
    result = result,
    error = error
)
