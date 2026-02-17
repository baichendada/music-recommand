# Mobile Music Recommendation System - Architecture & Roadmap

## Project Overview

A mobile music recommendation system that leverages affective computing to analyze user emotions and provide personalized music recommendations. The system combines audio feature extraction, lyrics sentiment analysis, and hybrid recommendation algorithms to deliver emotionally intelligent music suggestions.

## Tech Stack

### Backend + AI (Python)
- **Python**: 3.10+ (Tested 3.13)
- **Framework**: FastAPI
- **Build Tool**: Uvicorn
- **Data Validation**: Pydantic
- **Audio Processing**: Librosa, scipy
- **NLP**: jieba, snownlp
- **ML**: Scikit-learn (SVD, cosine similarity for CF)

### Frontend (Android)
- **Language**: Kotlin 1.9.x
- **Min SDK**: 24 (Android 7.0)
- **Target SDK**: 34 (Android 14)
- **UI Framework**: Jetpack Compose
- **Architecture**: MVVM with Clean Architecture
- **Networking**: Retrofit, OkHttp

### Database (Phase 1: In-Memory → Phase 2: MySQL + Redis)
- **Phase 1**: In-memory dict/list (fast iteration)
- **Phase 2**: SQLite (file-based, simple migration)
- **Phase 3**: MySQL 8.0 + Redis 7.x (production-ready)

---

## Architecture

### 3-Tier Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Android App (Kotlin/Compose)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ Emotion  │  │  Music   │  │ Playlist │  │  User    │           │
│  │  Input   │  │  Player  │  │ Display  │  │ Profile  │           │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘           │
│       └──────────────┴──────────────┴──────────────┘               │
│                              │                                       │
│                    Retrofit / OkHttp                                │
└──────────────────────────────┼──────────────────────────────────────┘
                               │ HTTPS
┌──────────────────────────────┼──────────────────────────────────────┐
│                  Python FastAPI (Unified Backend)                   │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                        REST API Layer                         │  │
│  │   /api/auth/*   /api/music/*   /api/emotion/*   /api/rec/*   │  │
│  └───────────────────────────────┬───────────────────────────────┘  │
│                                  │                                   │
│  ┌───────────────────────────────▼───────────────────────────────┐  │
│  │                    Business Logic Layer                       │  │
│  │   Auth Service  │  Music Service  │  Emotion Service  │       │  │
│  │   Recommendation Engine (Content + CF + Hybrid)              │  │
│  └───────────────────────────────┬───────────────────────────────┘  │
│                                  │                                   │
│  ┌───────────────────────────────▼───────────────────────────────┐  │
│  │                      AI Service Layer                          │  │
│  │   Audio Feature Extractor  │  Lyrics Sentiment Analyzer        │  │
│  │   Emotion Tag Generator    │  Hybrid Recommender               │  │
│  └───────────────────────────────┬───────────────────────────────┘  │
│                                  │                                   │
│  ┌───────────────────────────────▼───────────────────────────────┐  │
│  │                    Data Access Layer                           │  │
│  │   Phase 1: In-Memory  │  Phase 2: SQLite  │  Phase 3: MySQL    │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Database Schema

### Users Table
```
users
├── id (INT, PK)
├── username (VARCHAR)
├── password_hash (VARCHAR)
├── email (VARCHAR)
├── created_at (DATETIME)
└── updated_at (DATETIME)
```

### Music Table
```
music
├── id (INT, PK)
├── title (VARCHAR)
├── artist (VARCHAR)
├── album (VARCHAR)
├── duration (INT)
├── audio_url (VARCHAR)
├── cover_url (VARCHAR)
├── lyrics (TEXT)
├── emotion_tags (JSON)
├── audio_features (JSON)
├── created_at (DATETIME)
└── updated_at (DATETIME)
```

### Emotions Table
```
emotions
├── id (INT, PK)
├── user_id (INT, FK)
├── emotion_type (VARCHAR)
├── intensity (FLOAT)
├── source (VARCHAR) -- 'explicit' or 'inferred'
├── created_at (DATETIME)
└── updated_at (DATETIME)
```

### User Music Interaction Table
```
user_music_interaction
├── id (INT, PK)
├── user_id (INT, FK)
├── music_id (INT, FK)
├── interaction_type (VARCHAR) -- 'play', 'like', 'skip', 'complete'
├── play_duration (INT)
├── created_at (DATETIME)
└── updated_at (DATETIME)
```

### User Preference Table
```
user_preferences
├── id (INT, PK)
├── user_id (INT, FK)
├── preferred_genres (JSON)
├── preferred_emotions (JSON)
├── listening_history_summary (JSON)
└── updated_at (DATETIME)
```

---

## Storage Evolution

| Phase | Storage | Use Case |
|-------|---------|----------|
| 1 | In-Memory (dict/list) | Rapid prototyping, basic API testing |
| 2 | SQLite | File-based, no setup needed, simple migration |
| 3 | MySQL 8.0 + Redis 7.x | Production-ready, caching, sessions |

---

## Key Modules

### 1. Audio Feature Extraction (Python)
- **Library**: Librosa
- **Features**: tempo, pitch, spectral centroid, MFCC, rhythm
- **Output**: JSON with extracted audio features

### 2. Lyrics Sentiment Analysis (Python)
- **Methods**: SnowNLP (sentiment), jieba (tokenization), custom emotion dictionary
- **Output**: Sentiment scores per dimension

### 3. Hybrid Recommendation Engine
- **Content-Based**: Emotion tag matching, audio feature similarity
- **Collaborative Filtering**: User-item matrix with SVD + cosine similarity
- **Implementation**: `hybrid_recommender.py` using scipy/sklearn
- **Note**: LightFM not compatible with Python 3.13, implemented equivalent with scipy

---

## Development Phases

### Phase 1: Infrastructure & Quick Prototype
- In-memory storage only
- Basic FastAPI endpoints
- Simple recommendation logic
- Test full flow quickly

### Phase 2: AI Core Enhancement
- Full audio feature extraction
- Complete lyrics sentiment analysis
- Emotion tagging system

### Phase 3: Backend Logic
- User authentication (JWT)
- Music CRUD
- Hybrid recommendation

### Phase 4: Android UI
- Emotion input interface
- Music player
- Recommendation display

### Phase 5: Persistence Upgrade
- Migrate to SQLite
- Add Redis caching

### Phase 6: Production Ready
- Migrate to MySQL + Redis
- Performance optimization

---

## Version Control

- **Git**: Primary version control
- **Branch Strategy**: Git Flow (main, develop, feature/*)
