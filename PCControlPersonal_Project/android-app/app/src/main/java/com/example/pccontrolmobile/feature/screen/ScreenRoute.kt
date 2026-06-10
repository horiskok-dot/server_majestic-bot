package com.example.pccontrolmobile.feature.screen

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewModelScope
import com.example.pccontrolmobile.core.ui.DashboardCard
import com.example.pccontrolmobile.core.ui.EmptyState
import com.example.pccontrolmobile.core.ui.InlineStatusBanner
import com.example.pccontrolmobile.core.ui.SectionTitle
import com.example.pccontrolmobile.data.repository.PcControlRepository
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class ScreenUiState(
    val bitmap: Bitmap? = null,
    val isLoading: Boolean = false,
    val autoRefresh: Boolean = false,
    val lastMessage: String = "Press refresh to load the server screen.",
    val lastUpdatedAt: Long? = null
)

class ScreenViewModel(private val repository: PcControlRepository) : ViewModel() {
    private val _uiState = MutableStateFlow(ScreenUiState())
    val uiState = _uiState.asStateFlow()

    fun refresh() {
        if (_uiState.value.isLoading) return
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, lastMessage = "Loading screen...") }
            val result = repository.loadServerScreen()
            _uiState.update { current ->
                result.fold(
                    onSuccess = { bytes ->
                        val bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
                        if (bitmap != null) {
                            current.copy(
                                bitmap = bitmap,
                                isLoading = false,
                                lastMessage = "Screen updated.",
                                lastUpdatedAt = System.currentTimeMillis()
                            )
                        } else {
                            current.copy(isLoading = false, lastMessage = "Server returned an invalid image.")
                        }
                    },
                    onFailure = { error ->
                        current.copy(isLoading = false, lastMessage = error.message ?: "Failed to load screen.")
                    }
                )
            }
        }
    }

    fun setAutoRefresh(enabled: Boolean) {
        _uiState.update { it.copy(autoRefresh = enabled) }
        if (enabled) refresh()
    }
}

@Composable
fun ScreenRoute(viewModel: ScreenViewModel) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val bitmap = uiState.bitmap

    LaunchedEffect(uiState.autoRefresh) {
        while (uiState.autoRefresh) {
            viewModel.refresh()
            delay(3_000)
        }
    }

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            DashboardCard {
                SectionTitle("Server screen", "Protected screenshot stream from your PC server")
                Spacer(modifier = Modifier.height(12.dp))
                InlineStatusBanner(
                    title = if (uiState.autoRefresh) "Live refresh enabled" else "Manual mode",
                    message = uiState.lastMessage,
                    accent = if (uiState.autoRefresh) MaterialTheme.colorScheme.tertiary else MaterialTheme.colorScheme.primary
                )
            }
        }

        item {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(260.dp)
                    .background(
                        color = MaterialTheme.colorScheme.surface,
                        shape = RoundedCornerShape(24.dp)
                    )
                    .padding(10.dp),
                contentAlignment = Alignment.Center
            ) {
                when {
                    uiState.isLoading && uiState.bitmap == null -> CircularProgressIndicator()
                    bitmap != null -> Image(
                        bitmap = bitmap.asImageBitmap(),
                        contentDescription = "Server screen",
                        modifier = Modifier.fillMaxSize(),
                        contentScale = ContentScale.Fit
                    )
                    else -> EmptyState(
                        title = "No screen yet",
                        subtitle = "Tap Refresh screen. If it fails, check Server Base URL and Access key."
                    )
                }
            }
        }

        item {
            Button(
                onClick = viewModel::refresh,
                enabled = !uiState.isLoading,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(if (uiState.isLoading) "Loading..." else "Refresh screen")
            }
        }

        item {
            OutlinedButton(
                onClick = { viewModel.setAutoRefresh(!uiState.autoRefresh) },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(if (uiState.autoRefresh) "Stop live refresh" else "Start live refresh")
            }
        }
    }
}
