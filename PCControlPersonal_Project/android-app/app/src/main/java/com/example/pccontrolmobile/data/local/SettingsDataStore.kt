package com.example.pccontrolmobile.data.local

import android.content.Context
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.intPreferencesKey
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.example.pccontrolmobile.domain.model.AppSettings
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map

private val Context.settingsDataStore by preferencesDataStore(name = "pc_control_mobile_settings")

class SettingsDataStore(private val context: Context) {

    private object Keys {
        val baseUrl = stringPreferencesKey("base_url")
        val webSocketUrl = stringPreferencesKey("websocket_url")
        val accessKey = stringPreferencesKey("access_key")
        val refreshInterval = intPreferencesKey("refresh_interval_seconds")
        val notificationsEnabled = booleanPreferencesKey("notifications_enabled")
        val darkModeEnabled = booleanPreferencesKey("dark_mode_enabled")
    }

    val settingsFlow: Flow<AppSettings> = context.settingsDataStore.data.map(::mapSettings)

    suspend fun getSettings(): AppSettings = settingsFlow.first()

    suspend fun updateSettings(settings: AppSettings) {
        context.settingsDataStore.edit { prefs ->
            prefs[Keys.baseUrl] = settings.baseUrl
            prefs[Keys.webSocketUrl] = settings.webSocketUrl
            prefs[Keys.accessKey] = settings.accessKey
            prefs[Keys.refreshInterval] = settings.refreshIntervalSeconds
            prefs[Keys.notificationsEnabled] = settings.notificationsEnabled
            prefs[Keys.darkModeEnabled] = settings.darkModeEnabled
        }
    }

    private fun mapSettings(preferences: Preferences): AppSettings = AppSettings(
        baseUrl = preferences[Keys.baseUrl] ?: AppSettings().baseUrl,
        webSocketUrl = preferences[Keys.webSocketUrl] ?: AppSettings().webSocketUrl,
        accessKey = preferences[Keys.accessKey] ?: AppSettings().accessKey,
        refreshIntervalSeconds = preferences[Keys.refreshInterval] ?: AppSettings().refreshIntervalSeconds,
        notificationsEnabled = preferences[Keys.notificationsEnabled] ?: AppSettings().notificationsEnabled,
        darkModeEnabled = preferences[Keys.darkModeEnabled] ?: AppSettings().darkModeEnabled
    )
}
