# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Emotion-based music recommendation system with two components:
- **Backend**: FastAPI (Python) REST API at `backend/`
- **Android**: Jetpack Compose app at `android/`

## Backend Commands

```bash
# Setup (from backend/)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the server (port 8001)
cd backend
uvicorn app.main:app --reload --port 8001

# API docs available at http://localhost:8001/docs
```

There are no backend tests currently. The `requirements.txt` only lists core dependencies; the venv contains additional ML packages (librosa, numpy, scipy, sklearn, snownlp, jieba) installed separately.

## Android Commands

```bash
# Build debug APK (from android/)
./gradlew assembleDebug

# Run tests
./gradlew test

# Install on connected device/emulator
./gradlew installDebug
```

The Android app targets API 24+ (compileSdk 34) and uses Kotlin + Jetpack Compose.

## Architecture

### Backend (`backend/app/`)

**Data layer** — `services/data_store.py`: All data is stored in-memory Python dicts (`users_db`, `music_db`, `interactions_db`, `favorites_db`). On startup, it loads music from `backend/data/music_gtzan.json` → `music_processed.json` → hardcoded Bensound samples (priority order). No database is used; user/session data resets on server restart.

**API routes** (`api/`): `auth`, `music`, `emotion`, `recommend`, `ai`, `favorites` — all mounted under `/api` prefix.

**Recommendation engine** — `services/hybrid_recommender.py`: `HybridRecommender` combines:
1. Content-based: emotion tag matching against `music_db`
2. Collaborative filtering: `UserItemMatrix` (sparse CSR matrix + TruncatedSVD + cosine similarity)

The matrix is persisted to `backend/data/user_item_matrix.pkl` and loaded on startup via a global singleton (`get_recommender()`).

**AI pipeline** — `ai/`:
- `audio_extractor.py`: Uses librosa to extract tempo, energy, MFCCs, chroma, etc. Falls back to demo features for HTTP URLs.
- `lyrics_analyzer.py`: Chinese lyrics sentiment analysis using jieba tokenization + hardcoded sentiment/emotion lexicons.
- `emotion_service.py`: Combines audio + lyrics results into unified emotion tags.

**Auth** — JWT tokens (python-jose), passwords hashed with passlib/bcrypt. Tokens stored in `data_store.tokens_db` dict (not Redis).

**Config** — `core/config.py` reads from `.env` file. Key: `SECRET_KEY` must be changed for production.

### Android (`android/app/src/main/java/com/music/recommendation/`)

**Navigation** — `MainActivity.kt` uses a sealed `Screen` class (Login, Home, Profile, Player) with manual `currentScreen` state — no Jetpack Navigation component.

**API client** — `api/ApiClient.kt` + `api/MusicRepository.kt`: Retrofit2 with Gson. Base URL is `http://10.0.2.2:8001/` (Android emulator loopback to host). For physical devices, change `BASE_URL` in `ApiClient.kt` to the host machine's LAN IP.

**Audio playback** — `components/AudioPlayer.kt`: Wraps Media3 ExoPlayer. Exposes `currentMusic`, `isPlaying`, `progress` as `StateFlow`. Playlist queue managed in `MainActivity`. Exposes `onTrackStopped: (musicId, playedSeconds) -> Unit` callback — fired whenever a track is switched or finishes, used by `MainActivity` to record `play` interactions with real duration.

**ViewModels** — Defined inline in screen files (e.g., `HomeViewModel` in `HomeScreen.kt`, `AuthViewModel` in `LoginScreen.kt`).

**Emotion flow**: User selects an emotion chip → `HomeViewModel.recordEmotion()` → POST `/api/emotion` → GET `/api/recommend?emotion=<type>` → updates recommendations list.

## Key Data Contracts

Emotion types: `happy | sad | angry | calm | excited | relaxed`

Interaction types: `play | like | skip | complete`

Music objects carry `emotion_tags: List[str]` and `audio_features: Dict` used by both the recommendation engine and Android display.
