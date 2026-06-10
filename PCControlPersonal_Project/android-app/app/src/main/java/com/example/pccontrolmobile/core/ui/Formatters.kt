package com.example.pccontrolmobile.core.ui

import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

fun percentText(value: Float?): String = value?.let { String.format(Locale.US, "%.0f%%", it) } ?: "--"

fun decimalText(value: Float?, suffix: String): String =
    value?.let { String.format(Locale.US, "%.1f %s", it, suffix) } ?: "--"

fun bytesText(bytes: Long): String {
    val kb = 1024.0
    val mb = kb * 1024.0
    val gb = mb * 1024.0
    return when {
        bytes >= gb -> String.format(Locale.US, "%.2f GB", bytes / gb)
        bytes >= mb -> String.format(Locale.US, "%.2f MB", bytes / mb)
        bytes >= kb -> String.format(Locale.US, "%.2f KB", bytes / kb)
        else -> "$bytes B"
    }
}

fun formatTime(timestamp: Long): String =
    SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(Date(timestamp))

