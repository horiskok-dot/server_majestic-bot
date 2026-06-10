package com.example.pccontrolmobile.core.network

object ApiConfig {
    const val BASE_URL = "http://192.168.0.193:8765/"
    const val WEBSOCKET_URL = "ws://192.168.0.193:8765/ws/status"

    fun normalizeBaseUrl(baseUrl: String): String {
        val trimmed = baseUrl.trim()
        val withScheme = when {
            trimmed.startsWith("http://") || trimmed.startsWith("https://") -> trimmed
            trimmed.isBlank() -> BASE_URL
            else -> "http://$trimmed"
        }
        return if (withScheme.endsWith("/")) withScheme else "$withScheme/"
    }
}
