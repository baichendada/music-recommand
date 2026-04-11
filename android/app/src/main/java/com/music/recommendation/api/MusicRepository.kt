package com.music.recommendation.api

import com.music.recommendation.models.*

sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String, val code: Int = -1) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

class MusicRepository {

    private val api = RetrofitClient.apiService

    // Auth
    suspend fun register(username: String, email: String, password: String): Result<User> {
        return try {
            val response = api.register(RegisterRequest(username, email, password))
            if (response.isSuccessful) {
                response.body()?.let { Result.Success(it) }
                    ?: Result.Error("Empty response")
            } else {
                Result.Error(response.message(), response.code())
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "Unknown error")
        }
    }

    suspend fun login(username: String, password: String): Result<Token> {
        return try {
            val response = api.login(LoginRequest(username, password))
            if (response.isSuccessful) {
                response.body()?.let { token ->
                    ApiClient.updateAuthToken(token.accessToken)
                    Result.Success(token)
                } ?: Result.Error("Empty response")
            } else {
                Result.Error(response.message(), response.code())
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "Unknown error")
        }
    }

    suspend fun getCurrentUser(): Result<User> {
        return try {
            val response = api.getMe()
            if (response.isSuccessful) {
                response.body()?.let { Result.Success(it) }
                    ?: Result.Error("Empty response")
            } else {
                Result.Error(response.message(), response.code())
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "Unknown error")
        }
    }

    suspend fun getUserStats(): Result<UserStats> {
        return try {
            val response = api.getUserStats()
            if (response.isSuccessful) {
                response.body()?.let { Result.Success(it) }
                    ?: Result.Error("Empty response")
            } else {
                Result.Error(response.message(), response.code())
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "Unknown error")
        }
    }

    // Music
    suspend fun getMusicList(limit: Int = 50, offset: Int = 0): Result<List<Music>> {
        return try {
            val response = api.getMusicList(limit, offset)
            if (response.isSuccessful) {
                Result.Success(response.body() ?: emptyList())
            } else {
                Result.Error(response.message(), response.code())
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "Unknown error")
        }
    }

    suspend fun getMusic(id: Int): Result<Music> {
        return try {
            val response = api.getMusic(id)
            if (response.isSuccessful) {
                response.body()?.let { Result.Success(it) }
                    ?: Result.Error("Empty response")
            } else {
                Result.Error(response.message(), response.code())
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "Unknown error")
        }
    }

    suspend fun searchMusic(query: String): Result<List<Music>> {
        return try {
            val response = api.searchMusic(query)
            if (response.isSuccessful) {
                Result.Success(response.body() ?: emptyList())
            } else {
                Result.Error(response.message(), response.code())
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "Unknown error")
        }
    }

    // Emotion
    suspend fun recordEmotion(emotionType: String, intensity: Float = 1.0f): Result<Emotion> {
        return try {
            val response = api.recordEmotion(EmotionRequest(emotionType, intensity))
            if (response.isSuccessful) {
                response.body()?.let { Result.Success(it) }
                    ?: Result.Error("Empty response")
            } else {
                Result.Error(response.message(), response.code())
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "Unknown error")
        }
    }

    suspend fun getEmotionHistory(limit: Int = 20): Result<List<Emotion>> {
        return try {
            val response = api.getEmotionHistory(limit)
            if (response.isSuccessful) {
                Result.Success(response.body() ?: emptyList())
            } else {
                Result.Error(response.message(), response.code())
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "Unknown error")
        }
    }

    // Recommendation
    suspend fun getRecommendations(
        emotion: String? = null,
        limit: Int = 10
    ): Result<RecommendationResponse> {
        return try {
            val response = api.getRecommendations(emotion, limit)
            if (response.isSuccessful) {
                response.body()?.let { Result.Success(it) }
                    ?: Result.Error("Empty response")
            } else {
                Result.Error(response.message(), response.code())
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "Unknown error")
        }
    }

    suspend fun getByEmotion(emotion: String, limit: Int = 10): Result<List<Music>> {
        return try {
            val response = api.getByEmotion(emotion, limit)
            if (response.isSuccessful) {
                Result.Success(response.body() ?: emptyList())
            } else {
                Result.Error(response.message(), response.code())
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "Unknown error")
        }
    }

    suspend fun recordInteraction(
        musicId: Int,
        interactionType: String,
        playDuration: Int = 0
    ): Result<Unit> {
        return try {
            val response = api.recordInteraction(
                InteractionRequest(musicId, interactionType, playDuration)
            )
            if (response.isSuccessful) {
                Result.Success(Unit)
            } else {
                Result.Error(response.message(), response.code())
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "Unknown error")
        }
    }

    // Favorites
    suspend fun getFavorites(limit: Int = 50, offset: Int = 0): Result<List<Music>> {
        return try {
            val response = api.getFavorites(limit, offset)
            if (response.isSuccessful) {
                Result.Success(response.body() ?: emptyList())
            } else {
                Result.Error(response.message(), response.code())
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "Unknown error")
        }
    }

    suspend fun addFavorite(musicId: Int): Result<Favorite> {
        return try {
            val response = api.addFavorite(musicId)
            if (response.isSuccessful) {
                response.body()?.let { Result.Success(it) }
                    ?: Result.Error("Empty response")
            } else {
                Result.Error(response.message(), response.code())
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "Unknown error")
        }
    }

    suspend fun removeFavorite(musicId: Int): Result<Unit> {
        return try {
            val response = api.removeFavorite(musicId)
            if (response.isSuccessful) {
                Result.Success(Unit)
            } else {
                Result.Error(response.message(), response.code())
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "Unknown error")
        }
    }

    suspend fun checkFavorite(musicId: Int): Result<Boolean> {
        return try {
            val response = api.checkFavorite(musicId)
            if (response.isSuccessful) {
                response.body()?.let { Result.Success(it.isFavorited) }
                    ?: Result.Error("Empty response")
            } else {
                Result.Error(response.message(), response.code())
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "Unknown error")
        }
    }

    suspend fun getFavoriteCount(): Result<Int> {
        return try {
            val response = api.getFavoriteCount()
            if (response.isSuccessful) {
                response.body()?.let { Result.Success(it.count) }
                    ?: Result.Error("Empty response")
            } else {
                Result.Error(response.message(), response.code())
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "Unknown error")
        }
    }

    // Get recommendations based on favorites
    suspend fun getRecommendationsByFavorites(limit: Int = 10): Result<RecommendationResponse> {
        return try {
            val response = api.getRecommendationsByFavorites(limit)
            if (response.isSuccessful) {
                response.body()?.let { Result.Success(it) }
                    ?: Result.Error("Empty response")
            } else {
                Result.Error(response.message(), response.code())
            }
        } catch (e: Exception) {
            Result.Error(e.message ?: "Unknown error")
        }
    }

    fun logout() {
        ApiClient.clearAuthToken()
    }
}
