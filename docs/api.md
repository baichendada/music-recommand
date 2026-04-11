# Music Recommendation System - API Documentation

## Base URL
```
http://localhost:8001
```

## Authentication

All endpoints except health check and public music endpoints require authentication.

### Bearer Token
Include in headers:
```
Authorization: Bearer <token>
```

---

## Endpoints

### Health Check

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "app": "Music Recommendation System",
  "version": "1.0.0"
}
```

---

### Authentication

#### POST /api/auth/register
Register a new user.

**Request:**
```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string"
}
```

**Response (201):**
```json
{
  "id": 1,
  "username": "string",
  "email": "user@example.com",
  "created_at": "2024-01-01T00:00:00"
}
```

#### POST /api/auth/login
Login and get access token.

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

#### GET /api/auth/me
Get current user info.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": 1,
  "username": "string",
  "email": "user@example.com",
  "created_at": "2024-01-01T00:00:00"
}
```

#### GET /api/auth/stats
Get user interaction statistics.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "plays": 42,
  "likes": 10
}
```

---

### Music

#### GET /api/music
Get all music.

**Query Parameters:**
- `limit` (int): Max results (default 50)
- `offset` (int): Pagination offset (default 0)

**Response:**
```json
[
  {
    "id": 1,
    "title": "晴天",
    "artist": "周杰伦",
    "album": "叶惠美",
    "duration": 269,
    "audio_url": "https://...",
    "cover_url": "https://...",
    "lyrics": "...",
    "emotion_tags": ["happy", "calm"],
    "audio_features": {"tempo": 120, "energy": 0.6},
    "created_at": "2024-01-01T00:00:00"
  }
]
```

#### GET /api/music/{id}
Get music by ID.

#### GET /api/music/search?q={query}
Search music by title or artist.

#### GET /api/music/audio/{id}
Stream audio file for a music track.

**Response:** Audio file (WAV/MP3)

**Headers:**
- `Content-Type`: audio/wav or audio/mpeg
- `Accept-Ranges`: bytes

---

### Emotion

#### POST /api/emotion
Record user emotion.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "emotion_type": "happy",
  "intensity": 1.0,
  "source": "explicit"
}
```

**Emotion Types:** `happy`, `sad`, `calm`, `excited`, `angry`, `relaxed`

#### GET /api/emotion/history
Get emotion history.

**Headers:** `Authorization: Bearer <token>`

---

### Recommendation

#### GET /api/recommend
Get personalized recommendations.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `emotion` (str): Filter by emotion (optional)
- `limit` (int): Max results (default 10)

**Response:**
```json
{
  "recommendations": [...],
  "algorithm": "content-based"
}
```

#### GET /api/recommend/by-emotion/{emotion}
Get music by emotion tag.

#### POST /api/recommend/interact
Record user interaction with music.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "music_id": 1,
  "interaction_type": "play",
  "play_duration": 30
}
```

**Interaction Types:** `play`, `like`, `skip`, `complete`

**Note:** Using `interaction_type: "like"` automatically adds the music to favorites.

#### GET /api/recommend/by-favorites
Get music recommendations based on user's favorites.

Uses audio feature similarity (tempo, energy, danceability) and emotion tags from favorited music to find similar songs.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `limit` (int): Max results (default 10)

**Response:**
```json
{
  "recommendations": [...],
  "algorithm": "based-on-favorites"
}
```

---

### Favorites

#### GET /api/favorites
Get user's favorite music list.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `limit` (int): Max results (default 50)
- `offset` (int): Pagination offset (default 0)

**Response:**
```json
[
  {
    "id": 1,
    "title": "Blues 00093",
    "artist": "GTZAN Blues",
    ...
  }
]
```

#### POST /api/favorites/{music_id}
Add music to favorites.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "music_id": 1,
  "created_at": "2026-02-18T00:00:00"
}
```

#### DELETE /api/favorites/{music_id}
Remove music from favorites.

**Headers:** `Authorization: Bearer <token>`

#### GET /api/favorites/check/{music_id}
Check if music is favorited.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "is_favorited": true
}
```

#### GET /api/favorites/count
Get count of user's favorites.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "count": 10
}
```

---

### AI Analysis

#### POST /api/ai/analyze/emotion
Analyze music emotion from lyrics/audio.

**Request:**
```json
{
  "lyrics": "亲爱的 爱上你...",
  "audio_url": "https://..."
}
```

**Response:**
```json
{
  "lyrics_analysis": {
    "sentiment": {"sentiment_label": "positive"},
    "emotions": {"primary_emotion": "happy"}
  },
  "primary_emotion": "happy",
  "confidence": 0.5
}
```

#### POST /api/ai/analyze/lyrics
Analyze lyrics sentiment.

**Request:**
```json
{
  "lyrics": "歌词内容"
}
```

---

## Error Responses

**401 Unauthorized:** Invalid or missing token
**404 Not Found:** Resource not found
**400 Bad Request:** Invalid request data
