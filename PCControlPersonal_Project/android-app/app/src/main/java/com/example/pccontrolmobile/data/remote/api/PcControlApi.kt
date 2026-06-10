package com.example.pccontrolmobile.data.remote.api

import com.example.pccontrolmobile.data.remote.dto.ActionResponseDto
import com.example.pccontrolmobile.data.remote.dto.FileDto
import com.example.pccontrolmobile.data.remote.dto.LoginRequestDto
import com.example.pccontrolmobile.data.remote.dto.LoginResponseDto
import com.example.pccontrolmobile.data.remote.dto.LogDto
import com.example.pccontrolmobile.data.remote.dto.MetricsDto
import com.example.pccontrolmobile.data.remote.dto.MobileAgentDto
import com.example.pccontrolmobile.data.remote.dto.MobileTaskCreateDto
import com.example.pccontrolmobile.data.remote.dto.MobileTaskDto
import com.example.pccontrolmobile.data.remote.dto.ServerInfoDto
import com.example.pccontrolmobile.data.remote.dto.StatusDto
import okhttp3.MultipartBody
import okhttp3.ResponseBody
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part
import retrofit2.http.Path
import retrofit2.http.Query
import retrofit2.http.Streaming

interface PcControlApi {
    @POST("api/auth/login")
    suspend fun login(@Body body: LoginRequestDto): LoginResponseDto

    @GET("api/system/status")
    suspend fun getSystemStatus(
        @Header("X-PCManager-Key") accessKey: String
    ): StatusDto

    @GET("api/system/metrics")
    suspend fun getSystemMetrics(
        @Header("X-PCManager-Key") accessKey: String
    ): MetricsDto

    @GET("api/system/logs")
    suspend fun getSystemLogs(
        @Header("X-PCManager-Key") accessKey: String
    ): List<LogDto>

    @POST("api/system/optimize/quick")
    suspend fun optimizeQuick(
        @Header("X-PCManager-Key") accessKey: String,
        @Body body: Map<String, String> = emptyMap()
    ): ActionResponseDto

    @POST("api/system/optimize/deep")
    suspend fun optimizeDeep(
        @Header("X-PCManager-Key") accessKey: String,
        @Body body: Map<String, String> = emptyMap()
    ): ActionResponseDto

    @POST("api/system/optimize/temp")
    suspend fun optimizeTemp(
        @Header("X-PCManager-Key") accessKey: String,
        @Body body: Map<String, String> = emptyMap()
    ): ActionResponseDto

    @POST("api/system/restart-agent")
    suspend fun restartAgent(
        @Header("X-PCManager-Key") accessKey: String,
        @Body body: Map<String, String> = emptyMap()
    ): ActionResponseDto

    @POST("api/system/restart-pc")
    suspend fun restartPc(
        @Header("X-PCManager-Key") accessKey: String,
        @Body body: Map<String, String> = emptyMap()
    ): ActionResponseDto

    @POST("api/system/shutdown-pc")
    suspend fun shutdownPc(
        @Header("X-PCManager-Key") accessKey: String,
        @Body body: Map<String, String> = emptyMap()
    ): ActionResponseDto

    @GET("api/files")
    suspend fun getFiles(
        @Header("X-PCManager-Key") accessKey: String
    ): List<FileDto>

    @GET("api/mobile/server-info")
    suspend fun getMobileServerInfo(
        @Header("Authorization") authorization: String
    ): ServerInfoDto

    @GET("api/mobile/connection-info")
    suspend fun getMobileConnectionInfo(
        @Header("Authorization") authorization: String
    ): ServerInfoDto

    @POST("api/mobile/server/screenshot")
    suspend fun takeServerScreenshot(
        @Header("Authorization") authorization: String
    ): FileDto

    @GET("api/mobile/server/screenshots")
    suspend fun getServerScreenshots(
        @Header("Authorization") authorization: String
    ): List<FileDto>

    @POST("api/mobile/server/webcam/photo")
    suspend fun takeServerWebcamPhoto(
        @Header("Authorization") authorization: String,
        @Query("confirmed") confirmed: Boolean = true
    ): FileDto

    @GET("api/mobile/server/webcam/photos")
    suspend fun getServerWebcamPhotos(
        @Header("Authorization") authorization: String
    ): List<FileDto>

    @POST("api/mobile/server/webcam/record")
    suspend fun recordServerWebcamVideo(
        @Header("Authorization") authorization: String,
        @Query("duration_seconds") durationSeconds: Int,
        @Query("confirmed") confirmed: Boolean = true
    ): FileDto

    @GET("api/mobile/server/webcam/videos")
    suspend fun getServerWebcamVideos(
        @Header("Authorization") authorization: String
    ): List<FileDto>

    @GET("api/files/{id}")
    suspend fun getFileDetails(
        @Header("X-PCManager-Key") accessKey: String,
        @Path("id") id: String
    ): FileDto

    @GET("api/mobile/agents")
    suspend fun getMobileAgents(
        @Header("Authorization") authorization: String
    ): List<MobileAgentDto>

    @GET("api/mobile/agents/{agentId}")
    suspend fun getMobileAgent(
        @Header("Authorization") authorization: String,
        @Path("agentId") agentId: String
    ): MobileAgentDto

    @GET("api/mobile/agents/{agentId}/processes")
    suspend fun getAgentProcesses(
        @Header("Authorization") authorization: String,
        @Path("agentId") agentId: String
    ): List<Map<String, Any>>

    @POST("api/mobile/agents/{agentId}/processes/refresh")
    suspend fun refreshAgentProcesses(
        @Header("Authorization") authorization: String,
        @Path("agentId") agentId: String
    ): MobileTaskDto

    @POST("api/mobile/agents/{agentId}/screenshot")
    suspend fun takeAgentScreenshot(
        @Header("Authorization") authorization: String,
        @Path("agentId") agentId: String
    ): MobileTaskDto

    @POST("api/mobile/agents/{agentId}/camera/photo")
    suspend fun takeAgentCameraPhoto(
        @Header("Authorization") authorization: String,
        @Path("agentId") agentId: String
    ): MobileTaskDto

    @POST("api/mobile/agents/{agentId}/camera/record")
    suspend fun recordAgentVideo(
        @Header("Authorization") authorization: String,
        @Path("agentId") agentId: String,
        @Query("duration_seconds") durationSeconds: Int
    ): MobileTaskDto

    @GET("api/mobile/tasks")
    suspend fun getMobileTasks(
        @Header("Authorization") authorization: String
    ): List<MobileTaskDto>

    @POST("api/mobile/tasks")
    suspend fun createMobileTask(
        @Header("Authorization") authorization: String,
        @Body body: MobileTaskCreateDto
    ): MobileTaskDto

    @POST("api/mobile/tasks/{taskId}/cancel")
    suspend fun cancelMobileTask(
        @Header("Authorization") authorization: String,
        @Path("taskId") taskId: String
    ): MobileTaskDto

    @POST("api/mobile/tasks/{taskId}/retry")
    suspend fun retryMobileTask(
        @Header("Authorization") authorization: String,
        @Path("taskId") taskId: String
    ): MobileTaskDto

    @GET("api/mobile/files")
    suspend fun getMobileFiles(
        @Header("Authorization") authorization: String
    ): List<FileDto>

    @GET("api/mobile/photos")
    suspend fun getMobilePhotos(
        @Header("Authorization") authorization: String
    ): List<FileDto>

    @GET("api/mobile/screenshots")
    suspend fun getMobileScreenshots(
        @Header("Authorization") authorization: String
    ): List<FileDto>

    @GET("api/mobile/videos")
    suspend fun getMobileVideos(
        @Header("Authorization") authorization: String
    ): List<FileDto>

    @Multipart
    @POST("api/mobile/files/upload")
    suspend fun uploadMobileFile(
        @Header("Authorization") authorization: String,
        @Query("public_type") publicType: String,
        @Part upload: MultipartBody.Part
    ): FileDto

    @Streaming
    @GET("api/mobile/files/{fileId}/download")
    suspend fun downloadMobileFile(
        @Header("Authorization") authorization: String,
        @Path("fileId") fileId: String
    ): ResponseBody

    @DELETE("api/mobile/files/{fileId}")
    suspend fun deleteMobileFile(
        @Header("Authorization") authorization: String,
        @Path("fileId") fileId: String
    ): Map<String, Boolean>
}
