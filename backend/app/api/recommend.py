from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.models.schemas import (
    MusicResponse, RecommendResponse, EmotionType,
    InteractionCreate, InteractionResponse
)
from app.services import auth_service, music_service, recommendation_service, data_store

router = APIRouter(prefix="/recommend", tags=["Recommendation"])
security = HTTPBearer()


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Get current user ID from token"""
    user = auth_service.get_current_user(credentials.credentials)
    return user.id


@router.get("", response_model=RecommendResponse)
async def get_recommendations(
    user_id: int = Depends(get_current_user_id),
    emotion: Optional[EmotionType] = Query(None),
    limit: int = Query(10, ge=1, le=50)
):
    """Get personalized recommendations"""
    return recommendation_service.get_recommendations(
        user_id=user_id,
        emotion=emotion,
        limit=limit
    )


@router.get("/by-favorites", response_model=RecommendResponse)
async def get_recommendations_by_favorites(
    user_id: int = Depends(get_current_user_id),
    limit: int = Query(10, ge=1, le=50)
):
    """Get music recommendations based on user's favorites"""
    # Get user's favorites
    favorites = data_store.get_user_favorites(user_id)

    if not favorites:
        # No favorites yet, return popular/recent music
        return recommendation_service.get_recommendations(
            user_id=user_id,
            emotion=None,
            limit=limit
        )

    # Get recommendations based on favorites
    recommendations = recommendation_service.get_recommendations_based_on_favorites(
        user_id=user_id,
        favorite_music=favorites,
        limit=limit
    )

    return RecommendResponse(
        recommendations=recommendations,
        algorithm="based-on-favorites"
    )


@router.get("/by-emotion/{emotion}", response_model=List[MusicResponse])
async def get_by_emotion(
    emotion: EmotionType,
    limit: int = Query(10, ge=1, le=50)
):
    """Get music recommendations by emotion"""
    return music_service.get_music_by_emotion(emotion.value, limit=limit)


@router.post("/interact", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
async def record_interaction(
    interaction: InteractionCreate,
    user_id: int = Depends(get_current_user_id)
):
    """Record user interaction with music (play, like, skip)"""
    result = recommendation_service.record_interaction(
        user_id=user_id,
        music_id=interaction.music_id,
        interaction_type=interaction.interaction_type,
        play_duration=interaction.play_duration or 0
    )

    # Also add to favorites if interaction is "like"
    if interaction.interaction_type.value == "like":
        data_store.add_favorite(user_id, interaction.music_id)

    return result
