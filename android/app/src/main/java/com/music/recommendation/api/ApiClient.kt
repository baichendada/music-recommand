package com.music.recommendation.api

import com.music.recommendation.models.*
import retrofit2.Response
import retrofit2.http.*

object ApiClient {
    // Use 10.0.2.2 for Android Emulator (maps to host machine's localhost)
    // Use your computer's LAN IP for physical device
    const val BASE_URL = "http://10.0.2.2:8001/"

    private var _authToken: String? = null
    var authToken: String?
        get() = _authToken
        set(value) { _authToken = value }

    fun updateAuthToken(token: String?) {
        _authToken = token
    }

    fun clearAuthToken() {
        _authToken = null
    }
}

interface MusicApiService {
    // Auth
    @POST("api/auth/register")
    suspend fun register(@Body request: RegisterRequest): Response<User>

    @POST("api/auth/login")
    suspend fun login(@Body request: LoginRequest): Response<Token>

    @GET("api/auth/me")
    suspend fun getMe(): Response<User>

    @GET("api/auth/stats")
    suspend fun getUserStats(): Response<UserStats>

    // Music
    @GET("api/music")
    suspend fun getMusicList(
        @Query("limit") limit: Int = 50,
        @Query("offset") offset: Int = 0
    ): Response<List<Music>>

    @GET("api/music/{id}")
    suspend fun getMusic(@Path("id") id: Int): Response<Music>

    @GET("api/music/search")
    suspend fun searchMusic(@Query("q") query: String): Response<List<Music>>

    // Emotion
    @POST("api/emotion")
    suspend fun recordEmotion(@Body request: EmotionRequest): Response<Emotion>

    @GET("api/emotion/history")
    suspend fun getEmotionHistory(@Query("limit") limit: Int = 20): Response<List<Emotion>>

    @GET("api/emotion/latest")
    suspend fun getLatestEmotion(): Response<Emotion>

    // Recommendation
    @GET("api/recommend")
    suspend fun getRecommendations(
        @Query("emotion") emotion: String? = null,
        @Query("limit") limit: Int = 10
    ): Response<RecommendationResponse>

    @GET("api/recommend/by-emotion/{emotion}")
    suspend fun getByEmotion(
        @Path("emotion") emotion: String,
        @Query("limit") limit: Int = 10
    ): Response<List<Music>>

    @POST("api/recommend/interact")
    suspend fun recordInteraction(@Body request: InteractionRequest): Response<Unit>

    // Favorites
    @GET("api/favorites")
    suspend fun getFavorites(
        @Query("limit") limit: Int = 50,
        @Query("offset") offset: Int = 0
    ): Response<List<Music>>

    @POST("api/favorites/{musicId}")
    suspend fun addFavorite(@Path("musicId") musicId: Int): Response<Favorite>

    @DELETE("api/favorites/{musicId}")
    suspend fun removeFavorite(@Path("musicId") musicId: Int): Response<Unit>

    @GET("api/favorites/check/{musicId}")
    suspend fun checkFavorite(@Path("musicId") musicId: Int): Response<FavoriteCheck>

    @GET("api/favorites/count")
    suspend fun getFavoriteCount(): Response<FavoriteCount>

    // Recommendations based on favorites
    @GET("api/recommend/by-favorites")
    suspend fun getRecommendationsByFavorites(@Query("limit") limit: Int = 10): Response<RecommendationResponse>
}
