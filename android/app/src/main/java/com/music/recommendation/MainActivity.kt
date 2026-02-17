package com.music.recommendation

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.music.recommendation.api.MusicRepository
import com.music.recommendation.components.AudioPlayer
import com.music.recommendation.components.MiniPlayer
import com.music.recommendation.models.Music
import com.music.recommendation.screens.*

class MainActivity : ComponentActivity() {

    private var audioPlayer: AudioPlayer? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        audioPlayer = AudioPlayer(applicationContext)

        setContent {
            MaterialTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    MusicApp(audioPlayer!!)
                }
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        audioPlayer?.release()
    }
}

sealed class Screen {
    object Login : Screen()
    object Home : Screen()
    object Profile : Screen()
    object Player : Screen()
}

@Composable
fun MusicApp(audioPlayer: AudioPlayer) {
    var currentScreen by remember { mutableStateOf<Screen>(Screen.Login) }
    val authViewModel = remember { AuthViewModel() }
    val homeViewModel = remember { HomeViewModel() }
    val profileViewModel = remember { ProfileViewModel() }

    // Collect player state
    val currentMusic by audioPlayer.currentMusic.collectAsStateWithLifecycle()
    val isPlaying by audioPlayer.isPlaying.collectAsStateWithLifecycle()
    val playProgress by audioPlayer.progress.collectAsStateWithLifecycle()

    // Player state
    var isLiked by remember { mutableStateOf(false) }
    var currentQueue by remember { mutableStateOf(listOf<Music>()) }
    var currentIndex by remember { mutableIntStateOf(0) }

    // Update queue when recommendations load
    LaunchedEffect(homeViewModel.recommendations) {
        homeViewModel.recommendations?.recommendations?.let { music ->
            if (currentQueue.isEmpty()) {
                currentQueue = music
            }
        }
    }

    // Update progress periodically
    LaunchedEffect(isPlaying) {
        while (isPlaying) {
            audioPlayer.updateProgress()
            kotlinx.coroutines.delay(500)
        }
    }

    when (val screen = currentScreen) {
        Screen.Login -> {
            LoginScreen(
                viewModel = authViewModel,
                onLoginSuccess = {
                    currentScreen = Screen.Home
                }
            )
        }

        Screen.Home -> {
            Scaffold(
                bottomBar = {
                    Column {
                        // Mini player
                        MiniPlayer(
                            music = currentMusic,
                            isPlaying = isPlaying,
                            onPlayPause = {
                                audioPlayer.playPause()
                            },
                            onNext = {
                                audioPlayer.playNext()
                            },
                            onClick = {
                                if (currentMusic != null) {
                                    currentScreen = Screen.Player
                                }
                            }
                        )

                        // Navigation bar
                        NavigationBar {
                            NavigationBarItem(
                                icon = { Icon(Icons.Default.Home, contentDescription = null) },
                                label = { Text("Home") },
                                selected = true,
                                onClick = { currentScreen = Screen.Home }
                            )
                            NavigationBarItem(
                                icon = { Icon(Icons.Default.Person, contentDescription = null) },
                                label = { Text("Profile") },
                                selected = false,
                                onClick = {
                                    profileViewModel.loadProfile()
                                    profileViewModel.loadEmotionHistory()
                                    currentScreen = Screen.Profile
                                }
                            )
                        }
                    }
                }
            ) { paddingValues ->
                Box(modifier = Modifier.padding(paddingValues)) {
                    HomeScreen(
                        viewModel = homeViewModel,
                        onLogout = {
                            authViewModel.logout()
                            currentScreen = Screen.Login
                        },
                        onMusicSelected = { music ->
                            // Play the selected music
                            currentQueue = homeViewModel.recommendations?.recommendations ?: listOf(music)
                            currentIndex = currentQueue.indexOf(music).coerceAtLeast(0)
                            audioPlayer.playPlaylist(currentQueue, currentIndex)
                        }
                    )
                }
            }
        }

        Screen.Profile -> {
            Scaffold(
                bottomBar = {
                    NavigationBar {
                        NavigationBarItem(
                            icon = { Icon(Icons.Default.Home, contentDescription = null) },
                            label = { Text("Home") },
                            selected = false,
                            onClick = { currentScreen = Screen.Home }
                        )
                        NavigationBarItem(
                            icon = { Icon(Icons.Default.Person, contentDescription = null) },
                            label = { Text("Profile") },
                            selected = true,
                            onClick = { currentScreen = Screen.Profile }
                        )
                    }
                }
            ) { paddingValues ->
                ProfileScreen(
                    viewModel = profileViewModel,
                    onLogout = {
                        authViewModel.logout()
                        currentScreen = Screen.Login
                    },
                    modifier = Modifier.padding(paddingValues)
                )
            }
        }

        Screen.Player -> {
            currentMusic?.let { music ->
                com.music.recommendation.components.FullPlayerScreen(
                    music = music,
                    isPlaying = isPlaying,
                    progress = playProgress,
                    onPlayPause = { audioPlayer.playPause() },
                    onSeek = { progress -> audioPlayer.seekToProgress(progress) },
                    onPrevious = { audioPlayer.playPrevious() },
                    onNext = { audioPlayer.playNext() },
                    onLike = { isLiked = !isLiked },
                    onBack = { currentScreen = Screen.Home },
                    isLiked = isLiked
                )
            }
        }
    }
}
