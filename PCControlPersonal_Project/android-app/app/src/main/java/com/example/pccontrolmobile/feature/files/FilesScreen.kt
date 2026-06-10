package com.example.pccontrolmobile.feature.files

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewModelScope
import com.example.pccontrolmobile.core.ui.DashboardCard
import com.example.pccontrolmobile.core.ui.EmptyState
import com.example.pccontrolmobile.core.ui.ErrorState
import com.example.pccontrolmobile.core.ui.LoadingState
import com.example.pccontrolmobile.core.ui.SectionTitle
import com.example.pccontrolmobile.core.ui.bytesText
import com.example.pccontrolmobile.data.repository.PcControlRepository
import com.example.pccontrolmobile.domain.model.RemoteFile
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class FilesUiState(
    val isLoading: Boolean = false,
    val query: String = "",
    val files: List<RemoteFile> = emptyList(),
    val errorMessage: String? = null
) {
    val filteredFiles: List<RemoteFile>
        get() = files.filter { query.isBlank() || it.name.contains(query, true) || (it.type ?: "").contains(query, true) }
}

class FilesViewModel(private val repository: PcControlRepository) : ViewModel() {
    private val _uiState = MutableStateFlow(FilesUiState(isLoading = true))
    val uiState = _uiState.asStateFlow()

    init {
        refresh()
    }

    fun refresh() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            val result = repository.loadFiles()
            _uiState.update {
                it.copy(
                    isLoading = false,
                    files = result.getOrElse { emptyList() },
                    errorMessage = result.exceptionOrNull()?.message
                )
            }
        }
    }

    fun updateQuery(value: String) {
        _uiState.update { it.copy(query = value) }
    }
}

@Composable
fun FilesRoute(viewModel: FilesViewModel) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    var selectedFile by androidx.compose.runtime.remember { mutableStateOf<RemoteFile?>(null) }

    selectedFile?.let { file ->
        AlertDialog(
            onDismissRequest = { selectedFile = null },
            confirmButton = {},
            title = { Text(file.name) },
            text = {
                Text(
                    buildString {
                        appendLine("Size: ${bytesText(file.sizeBytes)}")
                        appendLine("Type: ${file.type ?: "Unknown"}")
                        appendLine("Updated: ${file.updatedAt}")
                        appendLine()
                        append(file.details ?: "Download/open/share flow is ready to connect once backend supports it.")
                    }
                )
            }
        )
    }

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item {
            DashboardCard {
                SectionTitle("Files", "Reports, logs and downloadable backend files")
                androidx.compose.foundation.layout.Spacer(modifier = Modifier.padding(4.dp))
                OutlinedTextField(
                    value = uiState.query,
                    onValueChange = viewModel::updateQuery,
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("Search files") }
                )
            }
        }
        uiState.errorMessage?.let { message ->
            item {
                ErrorState(message = message, onRetry = viewModel::refresh)
            }
        } ?: run {
            when {
                uiState.isLoading && uiState.files.isEmpty() -> item {
                    LoadingState("Loading backend files...")
                }

                uiState.filteredFiles.isEmpty() -> item {
                    EmptyState(
                        title = if (uiState.query.isBlank()) "No files available" else "No files matched",
                        subtitle = if (uiState.query.isBlank()) {
                            "Reports and logs will appear here when the backend exposes them."
                        } else {
                            "Try another query or clear the current search."
                        }
                    )
                }

                else -> items(uiState.filteredFiles, key = { it.id }) { file ->
                    DashboardCard(modifier = Modifier.clickable { selectedFile = file }) {
                        Text(file.name, style = androidx.compose.material3.MaterialTheme.typography.titleMedium)
                        Text(bytesText(file.sizeBytes))
                        Text(
                            file.type ?: "Unknown",
                            color = androidx.compose.material3.MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
        }
    }
}
