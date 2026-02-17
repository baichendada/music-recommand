from datetime import datetime
from typing import Dict, List, Optional, Set
import uuid
import os
import json

# Data file for persistence
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
MUSIC_DATA_FILE = os.path.join(DATA_DIR, 'music_processed.json')
GTZAN_DATA_FILE = os.path.join(DATA_DIR, 'music_gtzan.json')

# In-memory data storage
# In production, replace with database

users_db: Dict[int, dict] = {}
users_by_username: Dict[str, int] = {}
users_by_email: Dict[str, int] = {}

music_db: Dict[int, dict] = {}
music_counter = 0

emotions_db: Dict[int, dict] = {}
emotions_counter = 0

interactions_db: Dict[int, dict] = {}
interactions_counter = 0

# Favorites storage
favorites_db: Dict[int, dict] = {}
favorites_counter = 0
# Index: user_id -> set of music_ids
favorites_by_user: Dict[int, set] = {}

# Token storage (in production, use Redis)
tokens_db: Dict[str, int] = {}  # token -> user_id


def save_music_data():
    """Save music data to JSON file for persistence"""
    os.makedirs(DATA_DIR, exist_ok=True)
    # Convert datetime to string for JSON serialization
    data_to_save = {}
    for k, v in music_db.items():
        item = v.copy()
        if 'created_at' in item and isinstance(item['created_at'], datetime):
            item['created_at'] = item['created_at'].isoformat()
        if 'updated_at' in item and isinstance(item['updated_at'], datetime):
            item['updated_at'] = item['updated_at'].isoformat()
        data_to_save[k] = item

    with open(MUSIC_DATA_FILE, 'w') as f:
        json.dump(data_to_save, f, indent=2)


def load_music_data() -> bool:
    """Load processed music data from JSON file. Returns True if loaded successfully."""
    global music_counter
    if not os.path.exists(MUSIC_DATA_FILE):
        return False

    try:
        with open(MUSIC_DATA_FILE, 'r') as f:
            data = json.load(f)

        music_db.clear()
        for k, v in data.items():
            # Convert string back to datetime
            if 'created_at' in v and isinstance(v['created_at'], str):
                v['created_at'] = datetime.fromisoformat(v['created_at'])
            if 'updated_at' in v and isinstance(v['updated_at'], str):
                v['updated_at'] = datetime.fromisoformat(v['updated_at'])
            music_db[int(k)] = v

        music_counter = max(music_db.keys()) if music_db else 0
        return True
    except Exception as e:
        print(f"Failed to load music data: {e}")
        return False


def load_gtzan_data() -> bool:
    """Load GTZAN music data. Returns True if loaded successfully."""
    global music_counter
    if not os.path.exists(GTZAN_DATA_FILE):
        return False

    try:
        with open(GTZAN_DATA_FILE, 'r') as f:
            data = json.load(f)

        music_db.clear()
        for k, v in data.items():
            # Convert string back to datetime
            if 'created_at' in v and isinstance(v['created_at'], str):
                v['created_at'] = datetime.fromisoformat(v['created_at'])
            if 'updated_at' in v and isinstance(v['updated_at'], str):
                v['updated_at'] = datetime.fromisoformat(v['updated_at'])
            # Add created_at if not present
            if 'created_at' not in v:
                v['created_at'] = datetime.now()
            if 'updated_at' not in v:
                v['updated_at'] = datetime.now()
            music_db[int(k)] = v

        music_counter = max(music_db.keys()) if music_db else 0
        print(f"Loaded {len(music_db)} GTZAN music items")
        return True
    except Exception as e:
        print(f"Failed to load GTZAN data: {e}")
        return False


def generate_id(counter_dict: dict) -> int:
    """Generate unique ID"""
    counter_dict['current'] = counter_dict.get('current', 0) + 1
    return counter_dict['current']


# Initialize with sample music data (using GTZAN or Bensound)
def init_sample_data():
    global music_counter

    # Priority: GTZAN > processed Bensound > default sample
    if load_gtzan_data():
        print(f"[+] Using GTZAN dataset: {len(music_db)} songs")
        return

    # Try to load processed Bensound data
    if load_music_data():
        print(f"[+] Using processed Bensound data: {len(music_db)} songs")
        return

    sample_music = [
        {
            "title": "Happy Day",
            "artist": "Bensound",
            "album": "Free Music",
            "duration": 177,
            "audio_url": "https://cdn.bensound.com/bensound-theascension.mp3",
            "cover_url": "https://picsum.photos/seed/happy/300/300",
            "lyrics": "Feeling so happy today, sunshine and smiles everywhere",
            "emotion_tags": ["happy", "excited"],
            "audio_features": {"tempo": 140, "energy": 0.9}
        },
        {
            "title": "Sunny Day",
            "artist": "Bensound",
            "album": "Free Music",
            "duration": 194,
            "audio_url": "https://cdn.bensound.com/bensound-coloroflight.mp3",
            "cover_url": "https://picsum.photos/seed/sunny/300/300",
            "lyrics": "Walking in the sunshine, feeling warm and bright",
            "emotion_tags": ["happy", "relaxed"],
            "audio_features": {"tempo": 120, "energy": 0.6}
        },
        {
            "title": "Night Stars",
            "artist": "Bensound",
            "album": "Free Music",
            "duration": 206,
            "audio_url": "https://cdn.bensound.com/bensound-starlit.mp3",
            "cover_url": "https://picsum.photos/seed/stars/300/300",
            "lyrics": "Under the starlit sky, dreaming of tomorrow",
            "emotion_tags": ["calm", "relaxed"],
            "audio_features": {"tempo": 80, "energy": 0.4}
        },
        {
            "title": "Energetic Beat",
            "artist": "Bensound",
            "album": "Free Music",
            "duration": 158,
            "audio_url": "https://cdn.bensound.com/bensound-stayalert.mp3",
            "cover_url": "https://picsum.photos/seed/energy/300/300",
            "lyrics": "Stay alert, stay awake, the energy is calling",
            "emotion_tags": ["excited", "angry"],
            "audio_features": {"tempo": 150, "energy": 0.95}
        },
        {
            "title": "Tender Moments",
            "artist": "Bensound",
            "album": "Free Music",
            "duration": 182,
            "audio_url": "https://cdn.bensound.com/bensound-endo.mp3",
            "cover_url": "https://picsum.photos/seed/tender/300/300",
            "lyrics": "Tender moments shared with you, forever in my heart",
            "emotion_tags": ["calm", "relaxed"],
            "audio_features": {"tempo": 70, "energy": 0.3}
        },
        {
            "title": "Joyful Spirit",
            "artist": "Bensound",
            "album": "Free Music",
            "duration": 191,
            "audio_url": "https://cdn.bensound.com/bensound-thetriumphoflife.mp3",
            "cover_url": "https://picsum.photos/seed/joy/300/300",
            "lyrics": "Triumph of life, celebration of joy and hope",
            "emotion_tags": ["happy", "excited"],
            "audio_features": {"tempo": 135, "energy": 0.85}
        },
        {
            "title": "Melancholy",
            "artist": "Bensound",
            "album": "Free Music",
            "duration": 223,
            "audio_url": "https://cdn.bensound.com/bensound-north.mp3",
            "cover_url": "https://picsum.photos/seed/sad/300/300",
            "lyrics": "In the cold north wind, memories fade away",
            "emotion_tags": ["sad", "calm"],
            "audio_features": {"tempo": 65, "energy": 0.25}
        },
        {
            "title": "Dreamy Child",
            "artist": "Bensound",
            "album": "Free Music",
            "duration": 215,
            "audio_url": "https://cdn.bensound.com/bensound-curiouschild.mp3",
            "cover_url": "https://picsum.photos/seed/dream/300/300",
            "lyrics": "Curious child dreaming of wonders unknown",
            "emotion_tags": ["happy", "calm"],
            "audio_features": {"tempo": 90, "energy": 0.5}
        },
    ]

    for m in sample_music:
        music_counter += 1
        music_db[music_counter] = {
            "id": music_counter,
            **m,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }


# Initialize sample data on module load
init_sample_data()


# Favorites helper functions
def add_favorite(user_id: int, music_id: int) -> dict:
    """Add a music to user's favorites"""
    global favorites_counter

    # Check if already favorited
    if user_id in favorites_by_user and music_id in favorites_by_user[user_id]:
        # Already favorited, return existing
        for fav_id, fav in favorites_db.items():
            if fav['user_id'] == user_id and fav['music_id'] == music_id:
                return fav

    # Create new favorite
    favorites_counter += 1
    favorite = {
        "id": favorites_counter,
        "user_id": user_id,
        "music_id": music_id,
        "created_at": datetime.now()
    }
    favorites_db[favorites_counter] = favorite

    # Update index
    if user_id not in favorites_by_user:
        favorites_by_user[user_id] = set()
    favorites_by_user[user_id].add(music_id)

    return favorite


def remove_favorite(user_id: int, music_id: int) -> bool:
    """Remove a music from user's favorites"""
    if user_id not in favorites_by_user or music_id not in favorites_by_user[user_id]:
        return False

    # Remove from index
    favorites_by_user[user_id].discard(music_id)

    # Remove from database
    for fav_id, fav in list(favorites_db.items()):
        if fav['user_id'] == user_id and fav['music_id'] == music_id:
            del favorites_db[fav_id]
            return True

    return False


def get_user_favorites(user_id: int) -> List[dict]:
    """Get all favorites for a user"""
    if user_id not in favorites_by_user:
        return []

    favorites = []
    for music_id in favorites_by_user[user_id]:
        if music_id in music_db:
            favorites.append(music_db[music_id])
    return favorites


def is_favorited(user_id: int, music_id: int) -> bool:
    """Check if a music is favorited by user"""
    return user_id in favorites_by_user and music_id in favorites_by_user[user_id]


def get_favorite_count(user_id: int) -> int:
    """Get count of user's favorites"""
    if user_id not in favorites_by_user:
        return 0
    return len(favorites_by_user[user_id])
