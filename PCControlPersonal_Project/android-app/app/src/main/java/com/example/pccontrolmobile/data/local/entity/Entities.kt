package com.example.pccontrolmobile.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "metrics_history")
data class MetricsHistoryEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val cpuUsage: Float?,
    val ramUsage: Float?,
    val diskUsage: Float?,
    val temperatureC: Float?,
    val fps: Float?,
    val uptime: String?,
    val networkStatus: String?,
    val runningTask: String?,
    val timestamp: Long
)

@Entity(tableName = "logs")
data class LogEntity(
    @PrimaryKey val id: String,
    val level: String,
    val message: String,
    val source: String,
    val timestamp: Long
)

@Entity(tableName = "action_history")
data class ActionHistoryEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val title: String,
    val summary: String,
    val success: Boolean,
    val timestamp: Long
)

