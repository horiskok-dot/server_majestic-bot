package com.example.pccontrolmobile.core.ui

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Bolt
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.AssistChip
import androidx.compose.material3.AssistChipDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Divider
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.example.pccontrolmobile.core.designsystem.theme.BlueAccent
import com.example.pccontrolmobile.core.designsystem.theme.CardBorder
import com.example.pccontrolmobile.core.designsystem.theme.CardBorderStrong
import com.example.pccontrolmobile.core.designsystem.theme.GreenAccent
import com.example.pccontrolmobile.core.designsystem.theme.OrangeAccent
import com.example.pccontrolmobile.core.designsystem.theme.RedAccent
import com.example.pccontrolmobile.core.designsystem.theme.SurfaceOverlay
import com.example.pccontrolmobile.core.designsystem.theme.TextSecondary
import com.example.pccontrolmobile.domain.model.LogEntry
import com.example.pccontrolmobile.domain.model.LogLevel

@Composable
fun DashboardCard(
    modifier: Modifier = Modifier,
    content: @Composable ColumnScope.() -> Unit
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        shape = RoundedCornerShape(28.dp),
        border = BorderStroke(1.dp, CardBorder),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(18.dp),
            content = content
        )
    }
}

@Composable
fun MetricCard(
    title: String,
    value: String,
    caption: String,
    accent: Color,
    icon: ImageVector = Icons.Default.Bolt,
    modifier: Modifier = Modifier
) {
    DashboardCard(modifier = modifier) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.Top
        ) {
            Column(modifier = Modifier.weight(1f, fill = false)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.labelLarge,
                    color = TextSecondary
                )
                Spacer(modifier = Modifier.height(12.dp))
                Text(
                    text = value,
                    style = MaterialTheme.typography.headlineSmall
                )
            }
            Surface(
                color = accent.copy(alpha = 0.14f),
                shape = RoundedCornerShape(18.dp)
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = accent,
                    modifier = Modifier.padding(10.dp)
                )
            }
        }
        Spacer(modifier = Modifier.height(14.dp))
        Text(
            text = caption,
            color = TextSecondary,
            style = MaterialTheme.typography.bodyMedium,
            maxLines = 2,
            overflow = TextOverflow.Ellipsis
        )
    }
}

@Composable
fun StatusChip(online: Boolean, label: String) {
    AssistChip(
        onClick = {},
        label = { Text(label) },
        colors = AssistChipDefaults.assistChipColors(
            containerColor = if (online) GreenAccent.copy(alpha = 0.18f) else RedAccent.copy(alpha = 0.18f),
            labelColor = if (online) GreenAccent else RedAccent
        ),
        border = AssistChipDefaults.assistChipBorder(
            borderColor = if (online) GreenAccent.copy(alpha = 0.35f) else RedAccent.copy(alpha = 0.35f)
        )
    )
}

@Composable
fun SectionTitle(title: String, subtitle: String? = null) {
    Column {
        Text(title, style = MaterialTheme.typography.titleLarge)
        if (!subtitle.isNullOrBlank()) {
            Spacer(modifier = Modifier.height(2.dp))
            Text(subtitle, color = TextSecondary, style = MaterialTheme.typography.bodyMedium)
        }
    }
}

@Composable
fun LoadingState(message: String = "Loading...") {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        CircularProgressIndicator()
        Spacer(modifier = Modifier.height(12.dp))
        Text(message, color = TextSecondary)
    }
}

@Composable
fun ErrorState(message: String, onRetry: (() -> Unit)? = null) {
    DashboardCard {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Default.Warning, contentDescription = null, tint = OrangeAccent)
            Spacer(modifier = Modifier.size(8.dp))
            Text("Something went wrong", fontWeight = FontWeight.SemiBold)
        }
        Spacer(modifier = Modifier.height(8.dp))
        Text(message, color = TextSecondary)
        if (onRetry != null) {
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "Tap to retry",
                color = BlueAccent,
                modifier = Modifier.clickable { onRetry() }
            )
        }
    }
}

@Composable
fun InlineStatusBanner(
    title: String,
    message: String,
    accent: Color,
    modifier: Modifier = Modifier
) {
    Surface(
        modifier = modifier.fillMaxWidth(),
        color = SurfaceOverlay,
        shape = RoundedCornerShape(22.dp),
        border = BorderStroke(1.dp, CardBorderStrong)
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 16.dp, vertical = 14.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(12.dp)
                    .background(accent, CircleShape)
            )
            Spacer(modifier = Modifier.size(12.dp))
            Column {
                Text(title, style = MaterialTheme.typography.labelLarge)
                Spacer(modifier = Modifier.height(2.dp))
                Text(message, style = MaterialTheme.typography.bodyMedium, color = TextSecondary)
            }
        }
    }
}

@Composable
fun EmptyState(title: String, subtitle: String) {
    DashboardCard {
        Text(title, style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(6.dp))
        Text(subtitle, color = TextSecondary)
    }
}

@Composable
fun MetricHistoryChart(values: List<Float>, modifier: Modifier = Modifier) {
    if (values.isEmpty()) {
        Box(modifier = modifier.height(60.dp))
        return
    }

    val max = (values.maxOrNull() ?: 100f).coerceAtLeast(1f)
    Canvas(modifier = modifier.height(72.dp).fillMaxWidth()) {
        val stepX = if (values.size > 1) size.width / (values.size - 1) else size.width
        val points = values.mapIndexed { index, value ->
            Offset(
                x = index * stepX,
                y = size.height - (value / max) * size.height
            )
        }

        for (i in 0 until points.lastIndex) {
            drawLine(
                color = BlueAccent,
                start = points[i],
                end = points[i + 1],
                strokeWidth = 6f,
                cap = StrokeCap.Round
            )
        }
    }
}

@Composable
fun ActionTile(
    title: String,
    subtitle: String,
    modifier: Modifier = Modifier,
    onClick: () -> Unit
) {
    DashboardCard(modifier = modifier.clickable { onClick() }) {
        Text(title, style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = subtitle,
            color = TextSecondary,
            maxLines = 2,
            overflow = TextOverflow.Ellipsis
        )
    }
}

@Composable
fun LogRow(item: LogEntry) {
    val accent = when (item.level) {
        LogLevel.INFO -> BlueAccent
        LogLevel.WARNING -> OrangeAccent
        LogLevel.ERROR -> RedAccent
        LogLevel.SUCCESS -> GreenAccent
    }

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(
                    modifier = Modifier
                        .size(10.dp)
                        .background(accent, CircleShape)
                )
                Spacer(modifier = Modifier.size(8.dp))
                Text(item.level.name, fontWeight = FontWeight.SemiBold)
            }
            Text(
                text = formatTime(item.timestamp),
                color = TextSecondary,
                style = MaterialTheme.typography.bodySmall
            )
        }
        Spacer(modifier = Modifier.height(6.dp))
        Text(item.message, style = MaterialTheme.typography.bodyLarge)
        Spacer(modifier = Modifier.height(4.dp))
        Text(item.source, color = TextSecondary, style = MaterialTheme.typography.bodySmall)
        Spacer(modifier = Modifier.height(8.dp))
        Divider(color = CardBorder)
    }
}

@Composable
fun LogsList(items: List<LogEntry>) {
    LazyColumn {
        items(items, key = { it.id }) { item ->
            LogRow(item)
        }
    }
}
