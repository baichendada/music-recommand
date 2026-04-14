package com.music.recommendation.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.music.recommendation.api.MusicRepository
import com.music.recommendation.api.Result
import com.music.recommendation.models.Emotion
import com.music.recommendation.models.Music
import kotlinx.coroutines.launch

class ProfileViewModel : ViewModel() {
    private val repository = MusicRepository()

    var username by mutableStateOf("")
    var email by mutableStateOf("")
    var likedMusic by mutableStateOf<List<Music>>(emptyList())
    var emotionHistory by mutableStateOf<List<Emotion>>(emptyList())
    var isLoading by mutableStateOf(false)
    var totalPlays by mutableStateOf(0)
    var totalLikes by mutableStateOf(0)

    fun loadProfile() {
        viewModelScope.launch {
            isLoading = true
            when (val result = repository.getCurrentUser()) {
                is Result.Success -> {
                    username = result.data.username
                    email = result.data.email
                }
                is Result.Error -> {}
                is Result.Loading -> {}
            }
            isLoading = false
        }
    }

    fun loadStats() {
        viewModelScope.launch {
            when (val result = repository.getUserStats()) {
                is Result.Success -> {
                    totalPlays = result.data.plays
                    totalLikes = result.data.likes
                }
                else -> {}
            }
        }
    }

    fun loadEmotionHistory() {
        viewModelScope.launch {
            when (val result = repository.getEmotionHistory(limit = 10)) {
                is Result.Success -> {
                    emotionHistory = result.data
                }
                is Result.Error -> {}
                is Result.Loading -> {}
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(
    viewModel: ProfileViewModel,
    onLogout: () -> Unit,
    modifier: Modifier = Modifier
) {
    // Settings local state
    var notificationsEnabled by remember { mutableStateOf(true) }
    var darkModeEnabled by remember { mutableStateOf(false) }
    var autoPlayEnabled by remember { mutableStateOf(true) }

    LaunchedEffect(Unit) {
        viewModel.loadProfile()
        viewModel.loadEmotionHistory()
        viewModel.loadStats()
    }

    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = { Text("Profile") },
                actions = {
                    IconButton(onClick = onLogout) {
                        Icon(Icons.Default.Logout, contentDescription = "Logout")
                    }
                }
            )
        }
    ) { paddingValues ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Profile header
            item {
                Card(
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(24.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        // Avatar
                        Surface(
                            modifier = Modifier.size(80.dp),
                            shape = androidx.compose.foundation.shape.CircleShape,
                            color = MaterialTheme.colorScheme.primaryContainer
                        ) {
                            Icon(
                                Icons.Default.Person,
                                contentDescription = null,
                                modifier = Modifier
                                    .padding(20.dp)
                                    .fillMaxSize(),
                                tint = MaterialTheme.colorScheme.onPrimaryContainer
                            )
                        }

                        Spacer(modifier = Modifier.height(16.dp))

                        Text(
                            text = viewModel.username.ifEmpty { "User" },
                            style = MaterialTheme.typography.headlineSmall
                        )

                        Text(
                            text = viewModel.email.ifEmpty { "user@example.com" },
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }

            // Stats row
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    StatCard(
                        icon = Icons.Default.Favorite,
                        value = "${viewModel.totalLikes}",
                        label = "Likes",
                        modifier = Modifier.weight(1f)
                    )
                    StatCard(
                        icon = Icons.Default.Mood,
                        value = "${viewModel.emotionHistory.size}",
                        label = "Emotions",
                        modifier = Modifier.weight(1f)
                    )
                }
            }

            // Current emotion
            item {
                Card(
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp)
                    ) {
                        Text(
                            text = "Current Mood",
                            style = MaterialTheme.typography.titleMedium
                        )
                        Spacer(modifier = Modifier.height(8.dp))

                        if (viewModel.emotionHistory.isNotEmpty()) {
                            val latestEmotion = viewModel.emotionHistory.first()
                            Row(
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(
                                    Icons.Default.Mood,
                                    contentDescription = null,
                                    tint = MaterialTheme.colorScheme.primary
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(
                                    text = latestEmotion.emotionType.replaceFirstChar { it.uppercase() },
                                    style = MaterialTheme.typography.bodyLarge
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(
                                    text = "Intensity: ${latestEmotion.intensity}",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                        } else {
                            Text(
                                text = "No emotion recorded yet",
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                }
            }

            // Emotion history
            if (viewModel.emotionHistory.isNotEmpty()) {
                item {
                    Text(
                        text = "Emotion History",
                        style = MaterialTheme.typography.titleMedium
                    )
                }

                items(viewModel.emotionHistory.take(5)) { emotion ->
                    Card(
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(12.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(
                                Icons.Default.Mood,
                                contentDescription = null,
                                tint = MaterialTheme.colorScheme.primary
                            )
                            Spacer(modifier = Modifier.width(12.dp))
                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    text = emotion.emotionType.replaceFirstChar { it.uppercase() },
                                    style = MaterialTheme.typography.bodyMedium
                                )
                                Text(
                                    text = emotion.createdAt.take(10),
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                            Text(
                                text = emotion.source,
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                            )
                        }
                    }
                }
            }

            // Settings section
            item {
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Settings",
                    style = MaterialTheme.typography.titleMedium
                )
            }

            item {
                Card(
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column {
                        ListItem(
                            headlineContent = { Text("Notifications") },
                            leadingContent = {
                                Icon(Icons.Default.Notifications, contentDescription = null)
                            },
                            trailingContent = {
                                Switch(
                                    checked = notificationsEnabled,
                                    onCheckedChange = { notificationsEnabled = it }
                                )
                            }
                        )
                        ListItem(
                            headlineContent = { Text("Dark Mode") },
                            leadingContent = {
                                Icon(Icons.Default.DarkMode, contentDescription = null)
                            },
                            trailingContent = {
                                Switch(
                                    checked = darkModeEnabled,
                                    onCheckedChange = { darkModeEnabled = it }
                                )
                            }
                        )
                        ListItem(
                            headlineContent = { Text("Auto-play Recommendations") },
                            leadingContent = {
                                Icon(Icons.Default.PlayCircle, contentDescription = null)
                            },
                            trailingContent = {
                                Switch(
                                    checked = autoPlayEnabled,
                                    onCheckedChange = { autoPlayEnabled = it }
                                )
                            }
                        )
                    }
                }
            }

            // App info
            item {
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "About",
                    style = MaterialTheme.typography.titleMedium
                )
            }

            item {
                Card(
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp)
                    ) {
                        Text(
                            text = "Music Recommendation System",
                            style = MaterialTheme.typography.bodyMedium
                        )
                        Text(
                            text = "Version 1.0.0",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Text(
                            text = "Based on Affective Computing",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun StatCard(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    value: String,
    label: String,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                icon,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = value,
                style = MaterialTheme.typography.headlineSmall
            )
            Text(
                text = label,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}
