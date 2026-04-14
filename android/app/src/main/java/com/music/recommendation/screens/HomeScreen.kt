package com.music.recommendation.screens

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import coil.compose.AsyncImage
import com.music.recommendation.api.MusicRepository
import com.music.recommendation.api.Result
import com.music.recommendation.models.Music
import com.music.recommendation.models.RecommendationResponse
import kotlinx.coroutines.launch

class HomeViewModel : ViewModel() {
    private val repository = MusicRepository()

    var musicList by mutableStateOf<List<Music>>(emptyList())
    var recommendations by mutableStateOf<RecommendationResponse?>(null)
    var favorites by mutableStateOf<List<Music>>(emptyList())
    var favoriteRecommendations by mutableStateOf<RecommendationResponse?>(null)
    var favoriteIds by mutableStateOf<Set<Int>>(emptySet())
    var isLoading by mutableStateOf(false)
    var error by mutableStateOf<String?>(null)
    var selectedEmotion by mutableStateOf<String?>(null)

    // Emotion options
    val emotions = listOf("happy", "sad", "calm", "excited", "angry", "relaxed")

    fun loadMusicList() {
        viewModelScope.launch {
            isLoading = true
            when (val result = repository.getMusicList()) {
                is Result.Success -> musicList = result.data
                is Result.Error -> error = result.message
                is Result.Loading -> {}
            }
            isLoading = false
        }
    }

    fun loadRecommendations(emotion: String? = null) {
        viewModelScope.launch {
            isLoading = true
            selectedEmotion = emotion
            when (val result = repository.getRecommendations(emotion)) {
                is Result.Success -> recommendations = result.data
                is Result.Error -> error = result.message
                is Result.Loading -> {}
            }
            isLoading = false
        }
    }

    // Load favorites
    fun loadFavorites() {
        viewModelScope.launch {
            isLoading = true
            when (val result = repository.getFavorites()) {
                is Result.Success -> {
                    favorites = result.data
                    favoriteIds = result.data.map { it.id }.toSet()
                }
                is Result.Error -> error = result.message
                is Result.Loading -> {}
            }
            isLoading = false
        }
    }

    // Load recommendations based on favorites
    fun loadFavoriteRecommendations() {
        viewModelScope.launch {
            isLoading = true
            when (val result = repository.getRecommendationsByFavorites()) {
                is Result.Success -> favoriteRecommendations = result.data
                is Result.Error -> error = result.message
                is Result.Loading -> {}
            }
            isLoading = false
        }
    }

    // Toggle favorite
    fun toggleFavorite(musicId: Int) {
        viewModelScope.launch {
            val isFavorited = favoriteIds.contains(musicId)
            if (isFavorited) {
                when (repository.removeFavorite(musicId)) {
                    is Result.Success -> {
                        favoriteIds = favoriteIds - musicId
                        favorites = favorites.filter { it.id != musicId }
                    }
                    else -> {}
                }
            } else {
                when (repository.addFavorite(musicId)) {
                    is Result.Success -> {
                        favoriteIds = favoriteIds + musicId
                        // Reload favorites to get full music data
                        loadFavorites()
                    }
                    else -> {}
                }
            }
        }
    }

    fun recordEmotion(emotion: String) {
        viewModelScope.launch {
            repository.recordEmotion(emotion)
            // Reload recommendations with this emotion
            loadRecommendations(emotion)
        }
    }

    fun recordInteraction(musicId: Int, interactionType: String) {
        viewModelScope.launch {
            repository.recordInteraction(musicId, interactionType)
            // Also add to favorites if "like"
            if (interactionType == "like") {
                favoriteIds = favoriteIds + musicId
                loadFavorites()
            }
        }
    }

    fun clearError() {
        error = null
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    viewModel: HomeViewModel,
    onLogout: () -> Unit,
    onMusicSelected: (Music) -> Unit = {}
) {
    var selectedTab by remember { mutableIntStateOf(0) }

    LaunchedEffect(Unit) {
        viewModel.loadMusicList()
        viewModel.loadRecommendations()
        viewModel.loadFavorites()
        viewModel.loadFavoriteRecommendations()
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Music Recommendation") },
                actions = {
                    IconButton(onClick = onLogout) {
                        Icon(Icons.Default.Logout, contentDescription = "Logout")
                    }
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            TabRow(selectedTabIndex = selectedTab) {
                Tab(
                    selected = selectedTab == 0,
                    onClick = { selectedTab = 0 },
                    text = { Text("For You") },
                    icon = { Icon(Icons.Default.Recommend, contentDescription = null) }
                )
                Tab(
                    selected = selectedTab == 1,
                    onClick = { selectedTab = 1 },
                    text = { Text("Favorites") },
                    icon = { Icon(Icons.Default.Favorite, contentDescription = null) }
                )
                Tab(
                    selected = selectedTab == 2,
                    onClick = { selectedTab = 2 },
                    text = { Text("All Music") },
                    icon = { Icon(Icons.Default.MusicNote, contentDescription = null) }
                )
            }

            when (selectedTab) {
                0 -> RecommendationsTab(viewModel, onMusicSelected)
                1 -> FavoritesTab(viewModel, onMusicSelected)
                2 -> MusicListTab(viewModel, onMusicSelected)
            }
        }
    }
}

@Composable
fun RecommendationsTab(
    viewModel: HomeViewModel,
    onMusicSelected: (Music) -> Unit = {}
) {
    Column(modifier = Modifier.fillMaxSize()) {
        // Emotion selector
        Text(
            text = "How are you feeling?",
            style = MaterialTheme.typography.titleMedium,
            modifier = Modifier.padding(16.dp)
        )

        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            viewModel.emotions.forEach { emotion ->
                FilterChip(
                    selected = viewModel.selectedEmotion == emotion,
                    onClick = { viewModel.recordEmotion(emotion) },
                    label = { Text(emotion.replaceFirstChar { it.uppercase() }) }
                )
            }
        }

        Spacer(modifier = Modifier.height(8.dp))

        // Algorithm info
        viewModel.recommendations?.let { rec ->
            Text(
                text = "Algorithm: ${rec.algorithm}",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(horizontal = 16.dp)
            )
        }

        Spacer(modifier = Modifier.height(8.dp))

        if (viewModel.isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(viewModel.recommendations?.recommendations ?: emptyList()) { music ->
                    MusicItem(
                        music = music,
                        isFavorited = viewModel.favoriteIds.contains(music.id),
                        onPlay = { viewModel.recordInteraction(music.id, "play") },
                        onLike = { viewModel.toggleFavorite(music.id) },
                        onMusicSelected = onMusicSelected
                    )
                }
            }
        }
    }
}

@Composable
fun MusicListTab(
    viewModel: HomeViewModel,
    onMusicSelected: (Music) -> Unit = {}
) {
    Column(modifier = Modifier.fillMaxSize()) {
        if (viewModel.isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(viewModel.musicList) { music ->
                    MusicItem(
                        music = music,
                        isFavorited = viewModel.favoriteIds.contains(music.id),
                        onPlay = { viewModel.recordInteraction(music.id, "play") },
                        onLike = { viewModel.toggleFavorite(music.id) },
                        onMusicSelected = onMusicSelected
                    )
                }
            }
        }
    }
}

@Composable
fun FavoritesTab(
    viewModel: HomeViewModel,
    onMusicSelected: (Music) -> Unit = {}
) {
    Column(modifier = Modifier.fillMaxSize()) {
        // Show favorite-based recommendations first
        viewModel.favoriteRecommendations?.let { rec ->
            if (rec.recommendations.isNotEmpty()) {
                Text(
                    text = "Based on your favorites",
                    style = MaterialTheme.typography.titleMedium,
                    modifier = Modifier.padding(16.dp)
                )

                LazyColumn(
                    modifier = Modifier
                        .fillMaxWidth()
                        .weight(1f),
                    contentPadding = PaddingValues(horizontal = 16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    items(rec.recommendations) { music ->
                        MusicItem(
                            music = music,
                            isFavorited = viewModel.favoriteIds.contains(music.id),
                            onPlay = { viewModel.recordInteraction(music.id, "play") },
                            onLike = { viewModel.toggleFavorite(music.id) },
                            onMusicSelected = onMusicSelected
                        )
                    }
                }
            }
        }

        // Show user's favorites list
        if (viewModel.favorites.isNotEmpty()) {
            Text(
                text = "Your favorites (${viewModel.favorites.size})",
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.padding(16.dp)
            )

            LazyColumn(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f),
                contentPadding = PaddingValues(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(viewModel.favorites) { music ->
                    MusicItem(
                        music = music,
                        isFavorited = true,
                        onPlay = { viewModel.recordInteraction(music.id, "play") },
                        onLike = { viewModel.toggleFavorite(music.id) },
                        onMusicSelected = onMusicSelected
                    )
                }
            }
        } else if (!viewModel.isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f),
                contentAlignment = Alignment.Center
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Icon(
                        Icons.Default.FavoriteBorder,
                        contentDescription = null,
                        modifier = Modifier.size(64.dp),
                        tint = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = "No favorites yet",
                        style = MaterialTheme.typography.bodyLarge,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = "Tap the heart icon to add favorites",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
    }
}

@Composable
fun MusicItem(
    music: Music,
    isFavorited: Boolean = false,
    onPlay: () -> Unit,
    onLike: () -> Unit,
    onMusicSelected: (Music) -> Unit = {}
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable {
                onPlay()
                onMusicSelected(music)
            }
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Cover image
            if (music.coverUrl != null) {
                AsyncImage(
                    model = music.coverUrl,
                    contentDescription = null,
                    modifier = Modifier.size(56.dp)
                )
            } else {
                Surface(
                    modifier = Modifier.size(56.dp),
                    color = MaterialTheme.colorScheme.primaryContainer
                ) {
                    Icon(
                        Icons.Default.MusicNote,
                        contentDescription = null,
                        modifier = Modifier.padding(16.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.width(12.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = music.title,
                    style = MaterialTheme.typography.titleMedium,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
                Text(
                    text = music.artist,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                music.emotionTags?.let { tags ->
                    Text(
                        text = tags.joinToString(", "),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
            }

            IconButton(onClick = onLike) {
                Icon(
                    if (isFavorited) Icons.Default.Favorite else Icons.Default.FavoriteBorder,
                    contentDescription = "Like",
                    tint = if (isFavorited) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}
