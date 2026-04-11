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

### Database
- **Phase 1**: In-memory dict/list (fast iteration)
- **Phase 2**: SQLite (file-based, zero-config, **已实现** — 改一行 `.env` 即可启用)
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

> 音乐数据不入库，继续从 `music_gtzan.json` 启动时加载到内存。以下四张表已在 SQLite 模式下实现（`backend/app/models/orm_models.py`）。

### users（用户表）
```
users
├── id           INTEGER  PRIMARY KEY AUTOINCREMENT
├── username     TEXT     UNIQUE NOT NULL
├── email        TEXT     UNIQUE NOT NULL
├── password_hash TEXT    NOT NULL
├── created_at   DATETIME
└── updated_at   DATETIME
```

### interactions（交互记录表）
```
interactions
├── id               INTEGER  PRIMARY KEY AUTOINCREMENT
├── user_id          INTEGER  NOT NULL
├── music_id         INTEGER  NOT NULL
├── interaction_type TEXT     NOT NULL  -- play / like / skip / complete
├── play_duration    INTEGER  DEFAULT 0
└── created_at       DATETIME
```

### favorites（收藏表）
```
favorites
├── id         INTEGER  PRIMARY KEY AUTOINCREMENT
├── user_id    INTEGER  NOT NULL
├── music_id   INTEGER  NOT NULL
├── created_at DATETIME
└── UNIQUE(user_id, music_id)  -- 防止重复收藏
```

### emotions（情绪历史表）
```
emotions
├── id           INTEGER  PRIMARY KEY AUTOINCREMENT
├── user_id      INTEGER  NOT NULL
├── emotion_type TEXT     NOT NULL  -- happy/sad/angry/calm/excited/relaxed
├── intensity    REAL     DEFAULT 1.0
├── source       TEXT     DEFAULT 'explicit'
└── created_at   DATETIME
```

---

## 数据库模式切换

编辑 `backend/.env`，改一行即可：

```bash
# 内存模式（默认，重启后数据丢失）
USE_DATABASE=false

# SQLite 持久化模式（数据保存在 backend/data/music_app.db）
USE_DATABASE=true
```

启动时系统自动：
1. 创建 SQLite 文件和表结构（首次运行）
2. 将数据库中已有的用户、交互、收藏、情绪记录恢复到内存
3. 每次写操作同步到数据库

降级时只需将 `USE_DATABASE` 改回 `false`，无需任何其他操作。

---

## Storage Evolution

| Phase | Storage | Use Case | 状态 |
|-------|---------|----------|------|
| 1 | In-Memory (dict/list) | Rapid prototyping, basic API testing | ✅ 已实现 |
| 2 | SQLite | File-based, no setup needed, USE_DATABASE=true 启用 | ✅ 已实现 |
| 3 | MySQL 8.0 + Redis 7.x | Production-ready, caching, sessions | 待实现 |

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

### Phase 5: Persistence Upgrade ✅
- SQLite 接入完成（`USE_DATABASE=true` 启用）
- 持久化：users / interactions / favorites / emotions 四张表
- 支持一键降级回内存模式（`USE_DATABASE=false`）
- 启动时自动从数据库恢复数据到内存

### Phase 6: Production Ready
- Migrate to MySQL + Redis
- Performance optimization

---

## Version Control

- **Git**: Primary version control
- **Branch Strategy**: Git Flow (main, develop, feature/*)
