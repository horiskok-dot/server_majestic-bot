package com.example.pccontrolmobile.data.repository

import com.example.pccontrolmobile.core.network.ApiService
import com.example.pccontrolmobile.data.local.SettingsDataStore
import com.example.pccontrolmobile.data.local.dao.ActionHistoryDao
import com.example.pccontrolmobile.data.local.dao.LogDao
import com.example.pccontrolmobile.data.local.dao.MetricsHistoryDao
import com.example.pccontrolmobile.data.local.entity.ActionHistoryEntity
import com.example.pccontrolmobile.data.local.entity.LogEntity
import com.example.pccontrolmobile.data.local.entity.MetricsHistoryEntity
import com.example.pccontrolmobile.data.remote.dto.toActionResult
import com.example.pccontrolmobile.data.remote.dto.LoginRequestDto
import com.example.pccontrolmobile.data.remote.dto.MobileTaskCreateDto
import com.example.pccontrolmobile.data.remote.dto.toMetrics
import com.example.pccontrolmobile.data.remote.dto.toModel
import com.example.pccontrolmobile.data.remote.dto.toOptimizationResult
import com.example.pccontrolmobile.data.remote.dto.toSystemStatus
import com.example.pccontrolmobile.data.remote.ws.RealtimeGateway
import com.example.pccontrolmobile.domain.model.ActionHistoryItem
import com.example.pccontrolmobile.domain.model.ActionResult
import com.example.pccontrolmobile.domain.model.AppSettings
import com.example.pccontrolmobile.domain.model.ChatMessage
import com.example.pccontrolmobile.domain.model.LogEntry
import com.example.pccontrolmobile.domain.model.LogLevel
import com.example.pccontrolmobile.domain.model.MobileAgent
import com.example.pccontrolmobile.domain.model.MobileTask
import com.example.pccontrolmobile.domain.model.OptimizationResult
import com.example.pccontrolmobile.domain.model.OptimizationType
import com.example.pccontrolmobile.domain.model.RemoteFile
import com.example.pccontrolmobile.domain.model.SocketConnectionState
import com.example.pccontrolmobile.domain.model.SystemMetrics
import com.example.pccontrolmobile.domain.model.SystemStatus
import java.io.IOException
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.runBlocking
import okhttp3.Request
import retrofit2.HttpException

class PcControlRepositoryImpl(
    private val settingsStore: SettingsDataStore,
    private val apiService: ApiService,
    private val realtimeGateway: RealtimeGateway,
    private val metricsDao: MetricsHistoryDao,
    private val logDao: LogDao,
    private val actionHistoryDao: ActionHistoryDao
) : PcControlRepository {

    override val settings: Flow<AppSettings> = settingsStore.settingsFlow
    override val chatMessages: Flow<ChatMessage> = realtimeGateway.chatMessages
    override val chatConnectionState: StateFlow<SocketConnectionState> = realtimeGateway.chatConnection

    override fun observeMetricsHistory(limit: Int): Flow<List<SystemMetrics>> =
        metricsDao.observeRecent(limit).map { items ->
            items.sortedBy { it.timestamp }.map {
                SystemMetrics(
                    cpuUsage = it.cpuUsage,
                    ramUsage = it.ramUsage,
                    diskUsage = it.diskUsage,
                    temperatureC = it.temperatureC,
                    fps = it.fps,
                    uptime = it.uptime,
                    networkStatus = it.networkStatus,
                    runningTask = it.runningTask,
                    timestamp = it.timestamp
                )
            }
        }

    override fun observeLogs(limit: Int): Flow<List<LogEntry>> =
        logDao.observeRecent(limit).map { items ->
            items.map {
                LogEntry(
                    id = it.id,
                    level = when (it.level) {
                        "WARNING" -> LogLevel.WARNING
                        "ERROR" -> LogLevel.ERROR
                        "SUCCESS" -> LogLevel.SUCCESS
                        else -> LogLevel.INFO
                    },
                    message = it.message,
                    source = it.source,
                    timestamp = it.timestamp
                )
            }
        }

    override fun observeActionHistory(limit: Int): Flow<List<ActionHistoryItem>> =
        actionHistoryDao.observeRecent(limit).map { items ->
            items.map { ActionHistoryItem(it.id, it.title, it.summary, it.success, it.timestamp) }
        }

    override suspend fun refreshStatus(): Result<SystemStatus> = safeApiCall {
        val response = api().getSystemStatus(accessKey())
        cacheMetrics(response.toMetrics())
        response.toSystemStatus()
    }

    override suspend fun refreshMetrics(): Result<SystemMetrics> = safeApiCall {
        val metrics = api().getSystemMetrics(accessKey()).toModel()
        cacheMetrics(metrics)
        metrics
    }

    override suspend fun refreshLogs(): Result<List<LogEntry>> = safeApiCall {
        val logs = api().getSystemLogs(accessKey()).map { it.toModel() }
        logDao.clear()
        logDao.insertAll(logs.map { LogEntity(it.id, it.level.name, it.message, it.source, it.timestamp) })
        logs
    }

    override suspend fun loadFiles(): Result<List<RemoteFile>> = safeApiCall {
        api().getFiles(accessKey()).map { it.toModel() }
    }

    override suspend fun getFileDetails(id: String): Result<RemoteFile> = safeApiCall {
        api().getFileDetails(accessKey(), id).toModel()
    }

    override suspend fun loadAgents(): Result<List<MobileAgent>> = safeApiCall {
        api().getMobileAgents(mobileBearer()).map { it.toModel() }
    }

    override suspend fun loadTasks(): Result<List<MobileTask>> = safeApiCall {
        api().getMobileTasks(mobileBearer()).map { it.toModel() }
    }

    override suspend fun createAgentTask(agentId: String, action: String): Result<MobileTask> = safeApiCall {
        api().createMobileTask(mobileBearer(), MobileTaskCreateDto(agentId = agentId, action = action)).toModel()
    }

    override suspend fun sendRemoteInput(agentId: String, payload: Map<String, String>): Result<MobileTask> = safeApiCall {
        api().createMobileTask(
            mobileBearer(),
            MobileTaskCreateDto(
                agentId = agentId,
                action = "remote_input",
                payload = payload,
                confirmed = true
            )
        ).toModel()
    }

    override suspend fun cancelTask(taskId: String): Result<MobileTask> = safeApiCall {
        api().cancelMobileTask(mobileBearer(), taskId).toModel()
    }

    override suspend fun retryTask(taskId: String): Result<MobileTask> = safeApiCall {
        api().retryMobileTask(mobileBearer(), taskId).toModel()
    }

    override suspend fun quickCleanup(): Result<OptimizationResult> =
        runAction("Quick cleanup") { api().optimizeQuick(accessKey()).toOptimizationResult(OptimizationType.QUICK) }

    override suspend fun deepCleanup(): Result<OptimizationResult> =
        runAction("Deep cleanup") { api().optimizeDeep(accessKey()).toOptimizationResult(OptimizationType.DEEP) }

    override suspend fun tempCleanup(): Result<OptimizationResult> =
        runAction("Temporary cleanup") { api().optimizeTemp(accessKey()).toOptimizationResult(OptimizationType.TEMP) }

    override suspend fun restartAgent(): Result<ActionResult> =
        runSimpleAction("Restart agent") { api().restartAgent(accessKey()).toActionResult() }

    override suspend fun restartPc(): Result<ActionResult> =
        runSimpleAction("Restart PC") { api().restartPc(accessKey()).toActionResult() }

    override suspend fun shutdownPc(): Result<ActionResult> =
        runSimpleAction("Shutdown PC") { api().shutdownPc(accessKey()).toActionResult() }

    override suspend fun loadServerScreen(): Result<ByteArray> = safeApiCall {
        val settings = settingsStore.getSettings()
        if (settings.accessKey.isBlank()) {
            throw IllegalStateException("Access key is empty. Open /mobile in Telegram and paste the key in Settings.")
        }
        val url = settings.baseUrl.trimEnd('/') + "/api/mobile/screenshot"
        val request = Request.Builder()
            .url(url)
            .header("X-PCManager-Key", settings.accessKey)
            .get()
            .build()
        apiService.httpClient().newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw IllegalStateException("Screen request failed: HTTP ${response.code}")
            }
            response.body?.bytes() ?: throw IllegalStateException("Screen response is empty")
        }
    }

    override suspend fun testConnection(baseUrl: String): Result<Unit> = safeApiCall {
        apiService.create(baseUrl).getSystemStatus(settingsStore.getSettings().accessKey)
        Unit
    }

    override fun connectSockets() {
        val settings = runBlocking { settingsStore.getSettings() }
        realtimeGateway.connect(settings.webSocketUrl)
    }

    override fun disconnectSockets() {
        realtimeGateway.disconnect()
    }

    override fun sendChatMessage(text: String) {
        if (text.isBlank()) return
        val settings = runCatching { kotlinx.coroutines.runBlocking { settingsStore.getSettings() } }.getOrNull() ?: AppSettings()
        realtimeGateway.sendChatMessage(settings.webSocketUrl, text)
    }

    override suspend fun updateSettings(settings: AppSettings) {
        settingsStore.updateSettings(settings)
    }

    override suspend fun getCurrentSettings(): AppSettings = settingsStore.getSettings()

    fun connectSocketsNow(settings: AppSettings) {
        realtimeGateway.connect(settings.webSocketUrl)
    }

    private suspend fun api() = apiService.create(settingsStore.getSettings().baseUrl)

    private suspend fun accessKey() = settingsStore.getSettings().accessKey

    private suspend fun mobileBearer(): String {
        val token = api().login(LoginRequestDto(adminToken = accessKey())).accessToken
        return "Bearer $token"
    }

    private suspend fun <T> safeApiCall(block: suspend () -> T): Result<T> {
        return try {
            Result.success(block())
        } catch (error: Throwable) {
            Result.failure(error.toRepositoryError())
        }
    }

    private suspend fun cacheMetrics(metrics: SystemMetrics) {
        metricsDao.insert(
            MetricsHistoryEntity(
                cpuUsage = metrics.cpuUsage,
                ramUsage = metrics.ramUsage,
                diskUsage = metrics.diskUsage,
                temperatureC = metrics.temperatureC,
                fps = metrics.fps,
                uptime = metrics.uptime,
                networkStatus = metrics.networkStatus,
                runningTask = metrics.runningTask,
                timestamp = metrics.timestamp
            )
        )
        metricsDao.trim()
    }

    private suspend fun runSimpleAction(title: String, block: suspend () -> ActionResult): Result<ActionResult> =
        safeApiCall {
            val result = block()
            actionHistoryDao.insert(
                ActionHistoryEntity(
                    title = title,
                    summary = result.message,
                    success = result.success,
                    timestamp = result.timestamp
                )
            )
            result
        }

    private suspend fun runAction(
        title: String,
        block: suspend () -> OptimizationResult
    ): Result<OptimizationResult> = safeApiCall {
        val result = block()
        actionHistoryDao.insert(
            ActionHistoryEntity(
                title = title,
                summary = result.message,
                success = result.success,
                timestamp = result.timestamp
            )
        )
        result
    }
}

private fun Throwable.toRepositoryError(): Throwable {
    return when (this) {
        is IOException -> IllegalStateException("Cannot reach server. Check Wi‑Fi or BASE_URL.", this)
        is HttpException -> IllegalStateException("Server error ${code()}: ${message()}", this)
        is IllegalArgumentException -> IllegalStateException("Invalid server URL. Update BASE_URL in settings.", this)
        else -> this
    }
}
