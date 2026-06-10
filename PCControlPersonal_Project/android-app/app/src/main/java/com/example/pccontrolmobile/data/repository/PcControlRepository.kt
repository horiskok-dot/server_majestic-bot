package com.example.pccontrolmobile.data.repository

import com.example.pccontrolmobile.domain.model.ActionHistoryItem
import com.example.pccontrolmobile.domain.model.ActionResult
import com.example.pccontrolmobile.domain.model.AppSettings
import com.example.pccontrolmobile.domain.model.ChatMessage
import com.example.pccontrolmobile.domain.model.LogEntry
import com.example.pccontrolmobile.domain.model.MobileAgent
import com.example.pccontrolmobile.domain.model.MobileTask
import com.example.pccontrolmobile.domain.model.OptimizationResult
import com.example.pccontrolmobile.domain.model.RemoteFile
import com.example.pccontrolmobile.domain.model.SocketConnectionState
import com.example.pccontrolmobile.domain.model.SystemMetrics
import com.example.pccontrolmobile.domain.model.SystemStatus
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.StateFlow

interface PcControlRepository {
    val settings: Flow<AppSettings>
    val chatMessages: Flow<ChatMessage>
    val chatConnectionState: StateFlow<SocketConnectionState>

    fun observeMetricsHistory(limit: Int = 24): Flow<List<SystemMetrics>>
    fun observeLogs(limit: Int = 200): Flow<List<LogEntry>>
    fun observeActionHistory(limit: Int = 50): Flow<List<ActionHistoryItem>>

    suspend fun refreshStatus(): Result<SystemStatus>
    suspend fun refreshMetrics(): Result<SystemMetrics>
    suspend fun refreshLogs(): Result<List<LogEntry>>
    suspend fun loadFiles(): Result<List<RemoteFile>>
    suspend fun getFileDetails(id: String): Result<RemoteFile>
    suspend fun loadAgents(): Result<List<MobileAgent>>
    suspend fun loadTasks(): Result<List<MobileTask>>
    suspend fun createAgentTask(agentId: String, action: String): Result<MobileTask>
    suspend fun sendRemoteInput(agentId: String, payload: Map<String, String>): Result<MobileTask>
    suspend fun cancelTask(taskId: String): Result<MobileTask>
    suspend fun retryTask(taskId: String): Result<MobileTask>

    suspend fun quickCleanup(): Result<OptimizationResult>
    suspend fun deepCleanup(): Result<OptimizationResult>
    suspend fun tempCleanup(): Result<OptimizationResult>
    suspend fun restartAgent(): Result<ActionResult>
    suspend fun restartPc(): Result<ActionResult>
    suspend fun shutdownPc(): Result<ActionResult>
    suspend fun loadServerScreen(): Result<ByteArray>
    suspend fun testConnection(baseUrl: String): Result<Unit>

    fun connectSockets()
    fun disconnectSockets()
    fun sendChatMessage(text: String)

    suspend fun updateSettings(settings: AppSettings)
    suspend fun getCurrentSettings(): AppSettings
}
