# User Manual - Music Recommendation System

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Features](#features)
5. [Troubleshooting](#troubleshooting)

---

## Introduction

Music Recommendation System is a mobile application that uses affective computing to analyze your emotions and provide personalized music recommendations. The system combines:
- **Lyrics Analysis**: Analyzes Chinese lyrics for sentiment
- **Audio Features**: Extracts music features (tempo, energy, mood)
- **Hybrid Recommendations**: Combines content-based and collaborative filtering

---

## Installation

### Backend (Python FastAPI)

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python3 -m venv venv
```

3. Activate virtual environment:
```bash
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

The backend runs at `http://localhost:8001`

### Android App

1. Open Android Studio
2. File → Open → Select `android/` folder
3. Wait for Gradle sync to complete
4. Build → Build APK
5. Install on emulator or device

**Network Setup:**
- Emulator: Uses `10.0.2.2` to connect to host machine
- Physical device: Must be on same WiFi, use your computer's LAN IP

---

## Getting Started

### 1. Register Account
- Open the app
- Enter username, email, password
- Tap "Register"

### 2. Login
- Enter credentials
- Tap "Login"

### 3. Select Mood
- On home screen, tap your current emotion (happy, sad, calm, excited, angry, relaxed)
- The system will recommend music matching your mood

### 4. Browse Music
- Switch between "Recommendations" and "All Music" tabs
- Tap any music to play

### 5. Player Controls
- Play/Pause
- Next/Previous
- Seek bar
- Like/Unlike

### 6. Profile
- View your emotion history
- See statistics (plays, likes)
- Adjust settings

---

## Features

### Emotion-Based Recommendations
The app analyzes your selected emotion and recommends music with matching emotional tags.

**Supported Emotions:**
- 😊 Happy - Upbeat, positive music
- 😢 Sad - Melancholic, emotional songs
- 😌 Calm - Peaceful, relaxing music
- 🎉 Excited - Energetic, upbeat tracks
- 😠 Angry - Intense, powerful music
- 😌 Relaxed - Easy-going, gentle songs

### Music Analysis (AI)
The backend automatically analyzes:
- **Lyrics**: Sentiment and emotion
- **Audio Features**: Tempo, energy, danceability

### Hybrid Recommendation Algorithm
- **Content-Based**: Matches emotion tags
- **Collaborative**: Based on similar users
- **Hybrid**: Combines both approaches

---

## Troubleshooting

### Backend Issues

**"Module not found" errors:**
```bash
pip install -r requirements.txt
```

**Port already in use:**
```bash
# Find and kill process
lsof -i :8001
kill -9 <PID>
```

**Database errors:** Data is in-memory, restart clears data (normal for development)

### Android Issues

**Can't connect to backend:**
- Check backend is running
- Use correct IP (10.0.2.2 for emulator)
- Check firewall allows port 8001
- Verify internet permission in manifest

**Build errors:**
- Update Android Studio
- Invalidate caches: File → Invalidate Caches
- Clean project: Build → Clean Project

**Login fails:**
- Check backend is running
- Verify network connectivity

---

## Architecture

```
┌─────────────┐     HTTP      ┌─────────────┐
│   Android   │ ◄──────────► │   FastAPI   │
│   (Kotlin) │              │  (Python)   │
└─────────────┘              └──────┬──────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
              ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐
              │  In-Mem   │  │    AI     │  │    API    │
              │  Storage  │  │  (Librosa)│  │  Routes   │
              └───────────┘  └───────────┘  └───────────┘
```

---

## API Documentation

See [docs/api.md](api.md) for full API reference.

---

## Version Info

- App Version: 1.0.0
- Backend: FastAPI
- Android: Kotlin + Jetpack Compose
- AI: Librosa, jieba, snownlp

---

## License

MIT License
