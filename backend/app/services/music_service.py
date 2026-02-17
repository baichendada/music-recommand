from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status

from app.models.schemas import MusicCreate, MusicResponse
from app.services import data_store


def get_all_music(limit: int = 50, offset: int = 0) -> List[MusicResponse]:
    """Get all music"""
    music_list = list(data_store.music_db.values())
    music_list.sort(key=lambda x: x['created_at'], reverse=True)
    return [MusicResponse(**m) for m in music_list[offset:offset + limit]]


def get_music_by_id(music_id: int) -> MusicResponse:
    """Get music by ID"""
    music = data_store.music_db.get(music_id)
    if not music:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Music not found"
        )
    return MusicResponse(**music)


def search_music(query: str) -> List[MusicResponse]:
    """Search music by title or artist"""
    results = []
    query_lower = query.lower()

    for music in data_store.music_db.values():
        if (query_lower in music['title'].lower() or
            query_lower in music['artist'].lower() or
            (music.get('album') and query_lower in music['album'].lower())):
            results.append(MusicResponse(**music))

    return results


def create_music(music_data: MusicCreate) -> MusicResponse:
    """Create new music entry"""
    music_id = len(data_store.music_db) + 1

    music = {
        "id": music_id,
        "title": music_data.title,
        "artist": music_data.artist,
        "album": music_data.album,
        "duration": music_data.duration,
        "audio_url": music_data.audio_url,
        "cover_url": music_data.cover_url,
        "lyrics": music_data.lyrics,
        "emotion_tags": music_data.emotion_tags or [],
        "audio_features": music_data.audio_features or {},
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

    data_store.music_db[music_id] = music
    return MusicResponse(**music)


def get_music_by_emotion(emotion: str, limit: int = 10) -> List[MusicResponse]:
    """Get music by emotion tag"""
    results = []

    for music in data_store.music_db.values():
        emotion_tags = music.get('emotion_tags', [])
        if emotion.lower() in [tag.lower() for tag in emotion_tags]:
            results.append(MusicResponse(**music))

    # Limit results
    return results[:limit]
