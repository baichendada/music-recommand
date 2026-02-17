from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class EmotionType(str, Enum):
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    CALM = "calm"
    EXCITED = "excited"
    RELAXED = "relaxed"


class InteractionType(str, Enum):
    PLAY = "play"
    LIKE = "like"
    SKIP = "skip"
    COMPLETE = "complete"


# User schemas
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Music schemas
class MusicCreate(BaseModel):
    title: str
    artist: str
    album: Optional[str] = None
    duration: int  # seconds
    audio_url: str
    cover_url: Optional[str] = None
    lyrics: Optional[str] = None
    emotion_tags: Optional[List[str]] = None
    audio_features: Optional[Dict[str, Any]] = None


class MusicResponse(BaseModel):
    id: int
    title: str
    artist: str
    album: Optional[str]
    duration: int
    audio_url: str
    cover_url: Optional[str]
    lyrics: Optional[str]
    emotion_tags: Optional[List[str]]
    audio_features: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


# Emotion schemas
class EmotionCreate(BaseModel):
    emotion_type: EmotionType
    intensity: float = 1.0  # 0.0 to 1.0
    source: str = "explicit"  # "explicit" or "inferred"


class EmotionResponse(BaseModel):
    id: int
    user_id: int
    emotion_type: EmotionType
    intensity: float
    source: str
    created_at: datetime

    class Config:
        from_attributes = True


# Interaction schemas
class InteractionCreate(BaseModel):
    music_id: int
    interaction_type: InteractionType
    play_duration: Optional[int] = 0  # seconds played


class InteractionResponse(BaseModel):
    id: int
    user_id: int
    music_id: int
    interaction_type: InteractionType
    play_duration: int
    created_at: datetime

    class Config:
        from_attributes = True


# Recommendation schemas
class RecommendRequest(BaseModel):
    emotion: Optional[EmotionType] = None
    limit: int = 10


class RecommendResponse(BaseModel):
    recommendations: List[MusicResponse]
    algorithm: str = "hybrid"


# Favorite/Playlist schemas
class FavoriteCreate(BaseModel):
    music_id: int


class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    music_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PlaylistCreate(BaseModel):
    name: str
    description: Optional[str] = None


class PlaylistResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PlaylistWithMusic(PlaylistResponse):
    music: List[MusicResponse] = []
