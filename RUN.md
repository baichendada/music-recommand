# Quick Start Guide - Run the Project on PC

This guide explains how to run the Music Recommendation System on your PC.

---

## Prerequisites

### Required Software
- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Android Studio** - [Download](https://developer.android.com/studio)
- **Git** (optional) - [Download](https://git-scm.com)

---

## Part 1: Run Backend

### Step 1: Open Terminal
```bash
cd /Users/baichen/Project/music-project/backend
```

### Step 2: Install & Start (choose one)

**Option A — macOS + Anaconda (recommended):**
```bash
/opt/anaconda3/bin/pip install -r requirements.txt
/opt/anaconda3/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**Option B — Standard venv:**
```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**You should see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8001
[db] USE_DATABASE=false — running in memory mode
[+] Using GTZAN dataset: 999 songs
```

### Step 3 (Optional): Enable SQLite Persistence

By default data is lost on restart. To keep user data across restarts:

```bash
# Edit backend/.env
USE_DATABASE=true
```

The database file `backend/data/music_app.db` is created automatically.

---

## Part 2: Run Android App

### Option A: Android Studio (Recommended)

1. **Open Android Studio**
2. **File → Open**
3. Select `/Users/baichen/Project/music-project/android`
4. **Wait** for Gradle sync to complete
5. **Build → Build Bundle(s) / APK(s) → Build APK**
6. **Run → Run 'app'** (or install the APK on emulator/device)

### Option B: Command Line

```bash
cd /Users/baichen/Project/music-project/android

# Check Gradle wrapper
chmod +x gradlew

# Build debug APK
./gradlew assembleDebug

# APK location: app/build/outputs/apk/debug/app-debug.apk
```

---

## Part 3: Connect App to Backend

### For Android Emulator
The app is already configured to use `10.0.2.2` (maps to host machine)

### For Physical Device
1. Find your PC's IP address:
   - **Mac**: System Preferences → Network → Wi-Fi → IP Address
   - **Windows**: Open CMD → `ipconfig`

2. Update the IP in Android:
   - File: `android/app/src/main/java/com/music/recommendation/api/ApiClient.kt`
   - Change: `const val BASE_URL = "http://YOUR_IP:8001/"`
   - Rebuild APK

3. **Important**: Both PC and phone must be on the same WiFi

---

## Part 4: Using the App

### 1. Register
- Open app → Enter username, email, password
- Tap "Register"

### 2. Login
- Enter credentials → Tap "Login"

### 3. Select Your Mood
- On home screen, tap an emotion button:
  - 😊 Happy
  - 😢 Sad
  - 😌 Calm
  - 🎉 Excited
  - 😠 Angry
  - 😌 Relaxed

### 4. Get Recommendations
- Music matching your mood will appear
- Tap any song to play

### 5. Browse All Music
- Switch to "All Music" tab

### 6. Use Player
- Tap song → Full player opens
- Play/Pause, Next/Previous
- Seek bar, Like button

### 7. View Profile
- Tap Profile icon
- See emotion history, stats

---

## Quick Test Without Android

You can test the API using curl:

### Health Check
```bash
curl http://localhost:8001/health
```

### Register User
```bash
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"123456"}'
```

### Login
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"123456"}'
```

### Get Recommendations (replace TOKEN with actual token)
```bash
curl http://localhost:8001/api/recommend \
  -H "Authorization: Bearer TOKEN"
```

### Test AI Lyrics Analysis
```bash
curl -X POST http://localhost:8001/api/ai/analyze/emotion \
  -H "Content-Type: application/json" \
  -d '{"lyrics": "亲爱的 爱上你 从那天起 甜蜜的很轻易"}'
```

---

## Troubleshooting

### Backend Won't Start
- Check Python version: `python3 --version` (must be 3.10+)
- If using Anaconda on macOS, use `/opt/anaconda3/bin/python` instead of venv (venv's sklearn may conflict with Anaconda Python 3.13)
- Reinstall deps: `pip install -r requirements.txt`

### Audio Won't Play (UnrecognizedInputFormatException)
- Ensure `media3-extractor:1.3.1` is in `android/app/build.gradle.kts`
- Do **Gradle Sync** in Android Studio after any dependency change

### App Can't Connect
- Make sure backend is running (check terminal)
- Use correct IP (10.0.2.2 for emulator)
- Check firewall allows port 8001

### Build Errors
- Open Android Studio → File → Invalidate Caches → Invalidate and Restart

---

## Project Structure

```
music-project/
├── backend/              # Python FastAPI
│   ├── app/
│   │   ├── api/        # API endpoints
│   │   ├── ai/         # AI modules
│   │   └── services/   # Business logic
│   ├── tests/          # Unit tests
│   └── requirements.txt
│
├── android/             # Kotlin Android
│   ├── app/src/main/
│   │   ├── java/       # Kotlin code
│   │   └── res/        # Resources
│   └── build.gradle
│
├── docs/               # Documentation
├── plan.md             # Architecture
└── todo.md             # Task list
```

---

## Need Help?

- API Docs: See `docs/api.md`
- User Manual: See `docs/manual.md`
