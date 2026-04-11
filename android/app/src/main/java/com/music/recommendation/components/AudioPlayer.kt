package com.music.recommendation.components

import android.content.Context
import android.util.Log
import androidx.media3.common.MediaItem
import androidx.media3.common.Player
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.exoplayer.source.DefaultMediaSourceFactory
import androidx.media3.datasource.DefaultHttpDataSource
import androidx.media3.datasource.DefaultDataSource
import com.music.recommendation.api.ApiClient
import com.music.recommendation.models.Music
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class AudioPlayer(private val context: Context) {

    private var exoPlayer: ExoPlayer? = null

    private val _isPlaying = MutableStateFlow(false)
    val isPlaying: StateFlow<Boolean> = _isPlaying.asStateFlow()

    private val _currentMusic = MutableStateFlow<Music?>(null)
    val currentMusic: StateFlow<Music?> = _currentMusic.asStateFlow()

    private val _progress = MutableStateFlow(0f)
    val progress: StateFlow<Float> = _progress.asStateFlow()

    private val _duration = MutableStateFlow(0)
    val duration: StateFlow<Int> = _duration.asStateFlow()

    private var playlist: List<Music> = emptyList()
    private var currentIndex: Int = 0

    private val playerListener = object : Player.Listener {
        override fun onPlaybackStateChanged(playbackState: Int) {
            Log.d("AudioPlayer", "Playback state changed: $playbackState")
            when (playbackState) {
                Player.STATE_ENDED -> {
                    Log.d("AudioPlayer", "Playback ended, playing next")
                    playNext()
                }
                Player.STATE_READY -> {
                    _duration.value = exoPlayer?.duration?.toInt() ?: 0
                    Log.d("AudioPlayer", "Player ready, duration: ${_duration.value}")
                }
                Player.STATE_BUFFERING -> {
                    Log.d("AudioPlayer", "Player buffering")
                }
                Player.STATE_IDLE -> {
                    Log.d("AudioPlayer", "Player idle")
                }
            }
        }

        override fun onIsPlayingChanged(isPlaying: Boolean) {
            Log.d("AudioPlayer", "Is playing changed: $isPlaying")
            _isPlaying.value = isPlaying
        }

        override fun onPlayerError(error: androidx.media3.common.PlaybackException) {
            Log.e("AudioPlayer", "Player error: ${error.message}", error)
        }
    }

    init {
        initializePlayer()
    }

    private fun initializePlayer() {
        Log.d("AudioPlayer", "Initializing ExoPlayer")
        val httpDataSourceFactory = DefaultHttpDataSource.Factory()
            .setAllowCrossProtocolRedirects(true)  // 允许跟随 302 重定向
        val dataSourceFactory = DefaultDataSource.Factory(context, httpDataSourceFactory)
        val mediaSourceFactory = DefaultMediaSourceFactory(dataSourceFactory)
        exoPlayer = ExoPlayer.Builder(context)
            .setMediaSourceFactory(mediaSourceFactory)
            .build().apply {
                addListener(playerListener)
            }
        Log.d("AudioPlayer", "ExoPlayer initialized: $exoPlayer")
    }

    fun playMusic(music: Music) {
        _currentMusic.value = music
        _progress.value = 0f

        // Get audio URL from backend API
        val audioUrl = getAudioUrl(music.id)
        Log.d("AudioPlayer", "Playing music: ${music.title}, id: ${music.id}, audioUrl: $audioUrl")

        if (audioUrl != null) {
            exoPlayer?.apply {
                Log.d("AudioPlayer", "Setting media item and preparing player")
                setMediaItem(MediaItem.fromUri(audioUrl))
                prepare()
                play()
                Log.d("AudioPlayer", "Player state - isPlaying: $isPlaying")
            }
        } else {
            Log.e("AudioPlayer", "Failed to get audio URL for music: ${music.title}")
        }
    }

    private fun getAudioUrl(musicId: Int): String? {
        // Use the audio streaming endpoint directly
        return "${ApiClient.BASE_URL}api/music/audio/$musicId"
    }

    fun playPlaylist(musicList: List<Music>, startIndex: Int = 0) {
        playlist = musicList
        currentIndex = startIndex
        if (musicList.isNotEmpty()) {
            playMusic(musicList[startIndex])
        }
    }

    fun play() {
        exoPlayer?.play()
    }

    fun pause() {
        exoPlayer?.pause()
    }

    fun playPause() {
        if (_isPlaying.value) {
            pause()
        } else {
            play()
        }
    }

    fun seekTo(position: Long) {
        exoPlayer?.seekTo(position)
    }

    fun seekToProgress(progress: Float) {
        val duration = exoPlayer?.duration ?: return
        if (duration > 0) {
            val position = (progress * duration).toLong()
            seekTo(position)
        }
    }

    fun playNext() {
        if (playlist.isEmpty()) return
        currentIndex = (currentIndex + 1) % playlist.size
        playMusic(playlist[currentIndex])
    }

    fun playPrevious() {
        if (playlist.isEmpty()) return
        currentIndex = if (currentIndex > 0) currentIndex - 1 else playlist.size - 1
        playMusic(playlist[currentIndex])
    }

    fun updateProgress() {
        val player = exoPlayer ?: return
        val currentPosition = player.currentPosition
        val totalDuration = player.duration
        if (totalDuration > 0) {
            _progress.value = currentPosition.toFloat() / totalDuration.toFloat()
        }
    }

    fun release() {
        exoPlayer?.apply {
            removeListener(playerListener)
            release()
        }
        exoPlayer = null
    }
}
