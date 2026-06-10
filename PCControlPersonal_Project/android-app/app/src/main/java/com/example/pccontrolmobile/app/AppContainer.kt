package com.example.pccontrolmobile.app

import android.content.Context
import com.example.pccontrolmobile.core.network.ApiService
import com.example.pccontrolmobile.data.local.AppDatabase
import com.example.pccontrolmobile.data.local.SettingsDataStore
import com.example.pccontrolmobile.data.remote.ws.RealtimeGateway
import com.example.pccontrolmobile.data.repository.PcControlRepository
import com.example.pccontrolmobile.data.repository.PcControlRepositoryImpl

class AppContainer(context: Context) {
    private val database = AppDatabase.create(context)
    private val apiService = ApiService()
    private val settingsStore = SettingsDataStore(context)
    private val realtimeGateway = RealtimeGateway(apiService.httpClient())

    val repository: PcControlRepository = PcControlRepositoryImpl(
        settingsStore = settingsStore,
        apiService = apiService,
        realtimeGateway = realtimeGateway,
        metricsDao = database.metricsHistoryDao(),
        logDao = database.logDao(),
        actionHistoryDao = database.actionHistoryDao()
    )
}
