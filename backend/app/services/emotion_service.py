from datetime import datetime
from typing import List
from fastapi import HTTPException, status

from app.models.schemas import EmotionCreate, EmotionResponse, EmotionType
from app.services import data_store
from app.core.config import settings


def record_emotion(user_id: int, emotion_data: EmotionCreate) -> EmotionResponse:
    """Record user emotion"""
    emotion_id = len(data_store.emotions_db) + 1

    emotion = {
        "id": emotion_id,
        "user_id": user_id,
        "emotion_type": emotion_data.emotion_type,
        "intensity": emotion_data.intensity,
        "source": emotion_data.source,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

    data_store.emotions_db[emotion_id] = emotion

    # Sync to database
    if settings.USE_DATABASE:
        from app.core.database import is_db_enabled
        from app.services.db_store import db_create_emotion
        if is_db_enabled():
            db_create_emotion(
                emotion_id=emotion_id,
                user_id=user_id,
                emotion_type=emotion_data.emotion_type.value if hasattr(emotion_data.emotion_type, 'value') else str(emotion_data.emotion_type),
                intensity=emotion_data.intensity,
                source=emotion_data.source,
            )

    return EmotionResponse(**emotion)


def get_emotion_history(user_id: int, limit: int = 20) -> List[EmotionResponse]:
    """Get user emotion history"""
    user_emotions = []

    for emotion in data_store.emotions_db.values():
        if emotion['user_id'] == user_id:
            user_emotions.append(EmotionResponse(**emotion))

    # Sort by creation time (newest first)
    user_emotions.sort(key=lambda x: x.created_at, reverse=True)
    return user_emotions[:limit]


def get_latest_emotion(user_id: int) -> EmotionResponse:
    """Get user's latest emotion"""
    user_emotions = get_emotion_history(user_id, limit=1)
    if not user_emotions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No emotion history found"
        )
    return user_emotions[0]
