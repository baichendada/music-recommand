from typing import List
from fastapi import APIRouter, Depends, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.models.schemas import EmotionCreate, EmotionResponse
from app.services import auth_service, emotion_service

router = APIRouter(prefix="/emotion", tags=["Emotion"])
security = HTTPBearer()


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Get current user ID from token"""
    user = auth_service.get_current_user(credentials.credentials)
    return user.id


@router.post("", response_model=EmotionResponse, status_code=status.HTTP_201_CREATED)
async def record_emotion(
    emotion_data: EmotionCreate,
    user_id: int = Depends(get_current_user_id)
):
    """Record user emotion"""
    return emotion_service.record_emotion(user_id, emotion_data)


@router.get("/history", response_model=List[EmotionResponse])
async def get_emotion_history(
    user_id: int = Depends(get_current_user_id),
    limit: int = Query(20, ge=1, le=100)
):
    """Get user emotion history"""
    return emotion_service.get_emotion_history(user_id, limit=limit)


@router.get("/latest", response_model=EmotionResponse)
async def get_latest_emotion(user_id: int = Depends(get_current_user_id)):
    """Get user's latest emotion"""
    return emotion_service.get_latest_emotion(user_id)
