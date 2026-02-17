# Mobile Music Recommendation System - Task List

## Phase 1: Infrastructure & Quick Prototype

- [x] Initialize Git repository with proper .gitignore
- [x] Create Python FastAPI project structure
- [x] Setup Python virtual environment
- [x] Install core dependencies (fastapi, uvicorn, pydantic)
- [x] Create in-memory data store (dict/list)
- [x] Create basic FastAPI endpoints (health check, echo)
- [x] Test API runs locally
- [x] Create Android project with Jetpack Compose
- [x] Configure Android build dependencies
- [x] Verify Android connects to local API

## Phase 2: Core Features (In-Memory)

- [x] Implement in-memory User storage
- [x] Implement in-memory Music storage
- [x] Implement User authentication (JWT) endpoints
- [x] Implement Music CRUD API endpoints
- [x] Implement basic recommendation endpoint
- [x] Create Android login/registration screens
- [x] Create basic music list display
- [x] Test full basic flow (login → browse → recommend)

## Phase 3: AI Core

- [x] Install audio processing libraries (librosa)
- [x] Install NLP libraries (jieba, snownlp, transformers)
- [x] Implement audio feature extraction module
- [x] Implement lyrics preprocessing (tokenization, stopwords)
- [x] Implement lyrics sentiment analysis
- [x] Create emotion tagging system
- [x] Build multi-dimensional emotion label system
- [x] Integrate AI with API endpoints
- [x] Create emotion input UI in Android
- [x] Download real music data (Bensound)
- [x] Extract real audio features with Librosa
- [x] Generate emotion tags automatically
- [x] Persist processed data to JSON
- [x] Download and process GTZAN dataset (1000 songs)
- [x] Genre to emotion mapping (rock→angry, jazz→calm, etc.)

## Phase 4: Backend Logic Enhancement

- [x] Implement emotion recording API
- [x] Implement content-based recommendation module
- [x] Implement collaborative filtering module
- [x] Create hybrid recommendation engine
- [x] Implement user preference learning
- [x] Add user feedback handling (like/skip/play)
- [x] Implement User-Item matrix construction
- [x] Implement SVD + cosine similarity for CF
- [x] Add matrix persistence (pickle)

## Phase 5: Android UI

- [x] Create app navigation structure
- [x] Implement emotion input interface
- [x] Create music player UI with playback controls
- [x] Implement recommendation list display
- [x] Create user profile screen
- [x] Add music playback controls (play/pause/next/prev)
- [x] Implement feedback mechanism (like/skip)
- [x] Polish UI/UX
- [x] Connect to backend on port 8001
- [x] Implement audio streaming playback (ExoPlayer + HTTP)
- [x] Add audio streaming endpoint in backend

## Phase 6: Persistence Upgrade (SQLite)

- [ ] Install SQLAlchemy
- [ ] Migrate in-memory storage to SQLite
- [ ] Add data migration scripts
- [ ] Test data persists after restart

## Phase 7: Production Ready (MySQL + Redis)

- [ ] Setup MySQL database and create schema
- [ ] Migrate SQLite to MySQL
- [ ] Setup Redis for caching
- [ ] Add Redis caching layer
- [ ] Performance optimization

## Phase 8: Testing & Documentation

- [x] Write unit tests for backend
- [x] Write unit tests for AI module
- [x] Perform API integration testing
- [x] Conduct UI/UX testing
- [x] Create API documentation
- [x] Write user manual
- [x] Create algorithm evaluation script (Precision, Recall, F1, NDCG, Coverage)
- [x] Compare Content-Based vs Collaborative vs Hybrid
- [x] Test audio streaming playback
- [ ] Final testing and bug fixes
- [ ] Prepare thesis/closing report
