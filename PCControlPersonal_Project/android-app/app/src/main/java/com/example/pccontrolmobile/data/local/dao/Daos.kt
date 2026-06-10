package com.example.pccontrolmobile.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.example.pccontrolmobile.data.local.entity.ActionHistoryEntity
import com.example.pccontrolmobile.data.local.entity.LogEntity
import com.example.pccontrolmobile.data.local.entity.MetricsHistoryEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface MetricsHistoryDao {
    @Query("SELECT * FROM metrics_history ORDER BY timestamp DESC LIMIT :limit")
    fun observeRecent(limit: Int = 24): Flow<List<MetricsHistoryEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(item: MetricsHistoryEntity)

    @Query("DELETE FROM metrics_history WHERE id NOT IN (SELECT id FROM metrics_history ORDER BY timestamp DESC LIMIT :keep)")
    suspend fun trim(keep: Int = 64)
}

@Dao
interface LogDao {
    @Query("SELECT * FROM logs ORDER BY timestamp DESC LIMIT :limit")
    fun observeRecent(limit: Int = 200): Flow<List<LogEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(items: List<LogEntity>)

    @Query("DELETE FROM logs")
    suspend fun clear()
}

@Dao
interface ActionHistoryDao {
    @Query("SELECT * FROM action_history ORDER BY timestamp DESC LIMIT :limit")
    fun observeRecent(limit: Int = 50): Flow<List<ActionHistoryEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(item: ActionHistoryEntity)
}

