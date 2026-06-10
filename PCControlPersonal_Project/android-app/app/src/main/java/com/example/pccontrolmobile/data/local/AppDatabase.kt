package com.example.pccontrolmobile.data.local

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import com.example.pccontrolmobile.data.local.dao.ActionHistoryDao
import com.example.pccontrolmobile.data.local.dao.LogDao
import com.example.pccontrolmobile.data.local.dao.MetricsHistoryDao
import com.example.pccontrolmobile.data.local.entity.ActionHistoryEntity
import com.example.pccontrolmobile.data.local.entity.LogEntity
import com.example.pccontrolmobile.data.local.entity.MetricsHistoryEntity

@Database(
    entities = [MetricsHistoryEntity::class, LogEntity::class, ActionHistoryEntity::class],
    version = 1,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun metricsHistoryDao(): MetricsHistoryDao
    abstract fun logDao(): LogDao
    abstract fun actionHistoryDao(): ActionHistoryDao

    companion object {
        fun create(context: Context): AppDatabase =
            Room.databaseBuilder(context, AppDatabase::class.java, "pc_control_mobile.db").build()
    }
}

