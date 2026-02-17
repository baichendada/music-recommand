# Mobile Music Recommendation System

A mobile music recommendation system based on affective computing. The system analyzes user emotions and provides personalized music recommendations using hybrid recommendation algorithms combining content-based and collaborative filtering.

## Project Structure

```
music-project/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── models/        # Data models (Pydantic)
│   │   ├── services/      # Business logic
│   │   ├── ai/           # AI modules (Librosa, jieba)
│   │   └── main.py        # Application entry
│   ├── scripts/           # Processing scripts
│   ├── tests/             # Unit tests
│   ├── data/              # Data storage (music_processed.json)
│   └── requirements.txt   # Python dependencies
│
├── android/                 # Android Kotlin app
│   ├── app/
│   │   ├── src/main/
│   │   │   ├── java/      # Kotlin source
│   │   │   └── res/       # Resources
│   └── build.gradle       # Dependencies
│
├── docs/                   # Documentation
├── plan.md                 # Architecture overview
├── todo.md                 # Task list
└── REVIEW.md               # Feature coverage analysis
```

---

## System Features

### AI-Powered Analysis
- **Audio Feature Extraction**: Real-time extraction using Librosa (tempo, MFCC, chroma, spectral features)
- **Lyrics Sentiment Analysis**: Chinese NLP using jieba + custom emotion dictionary
- **Emotion Tagging**: Multi-dimensional emotion tags (happy, sad, calm, excited, angry, relaxed)

### Data Sources
- **GTZAN Dataset** (Recommended for thesis): 1000 songs, 10 genres, academic standard
- **Bensound** (Demo): 8 songs, free music, immediate use

### Hybrid Recommendation Engine
- **Content-Based**: Emotion tag matching with audio feature similarity
- **Collaborative Filtering**: User-item matrix with SVD + cosine similarity
- **Hybrid**: Weighted combination with configurable weights

### Data Processing
- Downloads real music from Bensound CDN
- Extracts audio features using Librosa
- Generates emotion tags automatically
- Persists processed data to JSON

---

## Prerequisites

### Backend
- Python 3.10+ (Tested on 3.13)
- (Optional) MySQL 8.0 - for production
- (Optional) Redis 7.x - for production

### Android
- Android Studio (Koala+)
- JDK 17
- Android SDK 34

---

## Quick Start (In-Memory Mode)

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install additional AI dependencies (if not in requirements)
pip install librosa jieba scipy scikit-learn

# Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

The backend will start at `http://localhost:8001`

### 2. Process Music Data (Optional)

**Option A: Bensound Demo (8 songs)**
```bash
cd backend
PYTHONPATH=/Users/baichen/Project/music-project/backend python scripts/process_music.py
```

**Option B: GTZAN Dataset (1000 songs, recommended for thesis)**

1. Download GTZAN:
   - Kaggle: https://www.kaggle.com/datasets/andradaolteanu/gtzan-dataset-music-genre-classification
   - Or: https://archive.org/details/gtzan-dataset-music-genre-classification

2. Extract to: `backend/data/gtzan/`

3. Process:
```bash
cd backend
PYTHONPATH=/Users/baichen/Project/music-project/backend python scripts/download_gtzan.py
```

This will:
1. Extract audio features (tempo, MFCC, chroma, etc.)
2. Map genres to emotion tags (rock → angry, classical → calm, etc.)
3. Save to `backend/data/music_gtzan.json`

### 3. Android Setup

1. Open Android Studio
2. File → Open → Select `android/` directory
3. Wait for Gradle sync to complete
4. Build → Build APK

### 4. Connect Android to Backend

In `android/app/src/main/java/.../ApiClient.kt`:
```kotlin
object ApiClient {
    // For emulator: use 10.0.2.2 (maps to host machine's localhost)
    // For physical device: use your computer's LAN IP
    const val BASE_URL = "http://10.0.2.2:8001/"
}
```

---

## API Endpoints

### Health Check
```
GET /health
```

### Authentication
```
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
```

### Music
```
GET  /api/music              # List all music (with real audio features)
GET  /api/music/{id}         # Get music details
GET  /api/music/search?q=    # Search music
GET  /api/music/audio/{id}   # Stream audio file
```

### Emotion
```
POST /api/emotion            # Record user emotion
GET  /api/emotion/history    # Get emotion history
GET  /api/emotion/latest    # Get latest emotion
```

### Recommendation
```
GET /api/recommend           # Get personalized recommendations (hybrid)
GET /api/recommend/by-emotion/{emotion}  # Get by emotion
GET /api/recommend/by-favorites  # Get recommendations based on favorites
POST /api/recommend/interact # Record user interaction (like adds to favorites)
```

### Favorites
```
GET  /api/favorites              # Get user's favorite music list
POST /api/favorites/{music_id}  # Add music to favorites
DELETE /api/favorites/{music_id} # Remove music from favorites
GET  /api/favorites/check/{music_id}  # Check if favorited
GET  /api/favorites/count       # Get favorites count
```

### AI Analysis
```
POST /api/ai/analyze/emotion  # Analyze emotion from lyrics/audio
POST /api/ai/analyze/lyrics   # Analyze lyrics sentiment
POST /api/ai/analyze/audio   # Extract audio features
```

---

## Development Phases

### Phase 1-2: In-Memory Mode
- No database setup required
- All data stored in memory + JSON files
- Sample music with real Bensound URLs
- Real AI-extracted features

### Phase 3: SQLite Mode
```bash
cd backend
pip install sqlalchemy
# Database file created automatically
```

### Phase 4: MySQL + Redis Mode
See `docs/production-setup.md` for detailed instructions.

---

## Testing Recommendations

Run the evaluation script to compare algorithms:

```bash
cd backend
python tests/evaluate_recommender.py
```

This compares:
- Content-Based Filtering
- Collaborative Filtering
- Hybrid (Combined)

---

## Troubleshooting

### Backend won't start
- Ensure Python 3.10+ is installed: `python --version`
- Activate virtual environment: `source venv/bin/activate`
- Check dependencies: `pip list`

### Android can't connect to backend
- Use `10.0.2.2` for Android Emulator (not `localhost`)
- For physical device, both must be on same WiFi
- Check firewall allows port 8001
- Add internet permission in AndroidManifest.xml

### Audio feature extraction fails
- Install ffmpeg: `brew install ffmpeg` (Mac) or `apt install ffmpeg` (Linux)

---

## License

MIT License
