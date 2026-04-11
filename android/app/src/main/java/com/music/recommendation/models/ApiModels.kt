package com.music.recommendation.models

import com.google.gson.annotations.SerializedName

// User models
data class User(
    val id: Int,
    val username: String,
    val email: String,
    @SerializedName("created_at") val createdAt: String
)

data class Token(
    @SerializedName("access_token") val accessToken: String,
    @SerializedName("token_type") val tokenType: String = "bearer"
)

data class LoginRequest(
    val username: String,
    val password: String
)

data class RegisterRequest(
    val username: String,
    val email: String,
    val password: String
)

// Music models
data class Music(
    val id: Int,
    val title: String,
    val artist: String,
    val album: String?,
    val duration: Int,
    @SerializedName("audio_url") val audioUrl: String,
    @SerializedName("cover_url") val coverUrl: String?,
    val lyrics: String?,
    @SerializedName("emotion_tags") val emotionTags: List<String>?,
    @SerializedName("audio_features") val audioFeatures: Map<String, Any>?,
    @SerializedName("created_at") val createdAt: String
)

// Emotion models
data class Emotion(
    val id: Int,
    @SerializedName("user_id") val userId: Int,
    @SerializedName("emotion_type") val emotionType: String,
    val intensity: Float,
    val source: String,
    @SerializedName("created_at") val createdAt: String
)

data class EmotionRequest(
    @SerializedName("emotion_type") val emotionType: String,
    val intensity: Float = 1.0f,
    val source: String = "explicit"
)

// Interaction models
data class InteractionRequest(
    @SerializedName("music_id") val musicId: Int,
    @SerializedName("interaction_type") val interactionType: String,
    @SerializedName("play_duration") val playDuration: Int = 0
)

// Recommendation models
data class RecommendationResponse(
    val recommendations: List<Music>,
    val algorithm: String
)

// Favorite models
data class Favorite(
    val id: Int,
    @SerializedName("user_id") val userId: Int,
    @SerializedName("music_id") val musicId: Int,
    @SerializedName("created_at") val createdAt: String
)

data class FavoriteCheck(
    @SerializedName("is_favorited") val isFavorited: Boolean
)

data class FavoriteCount(
    val count: Int
)

data class UserStats(
    val plays: Int,
    val likes: Int
)
