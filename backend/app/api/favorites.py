from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List

from app.models.schemas import MusicResponse, FavoriteCreate, FavoriteResponse
from app.services import auth_service, data_store

router = APIRouter(prefix="/favorites", tags=["Favorites"])
security = HTTPBearer()


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Get current user ID from token"""
    user = auth_service.get_current_user(credentials.credentials)
    return user.id


@router.get("", response_model=List[MusicResponse])
async def get_favorites(
    user_id: int = Depends(get_current_user_id),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get user's favorite music list"""
    favorites = data_store.get_user_favorites(user_id)
    # Apply pagination
    return favorites[offset:offset + limit]


@router.post("/{music_id}", response_model=FavoriteResponse)
async def add_favorite(
    music_id: int,
    user_id: int = Depends(get_current_user_id)
):
    """Add music to favorites"""
    # Check if music exists
    music = data_store.music_db.get(music_id)
    if not music:
        raise HTTPException(status_code=404, detail="Music not found")

    # Add to favorites
    favorite = data_store.add_favorite(user_id, music_id)
    return favorite


@router.delete("/{music_id}")
async def remove_favorite(
    music_id: int,
    user_id: int = Depends(get_current_user_id)
):
    """Remove music from favorites"""
    success = data_store.remove_favorite(user_id, music_id)
    if not success:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return {"message": "Removed from favorites"}


@router.get("/check/{music_id}")
async def check_favorite(
    music_id: int,
    user_id: int = Depends(get_current_user_id)
):
    """Check if music is in favorites"""
    is_favorited = data_store.is_favorited(user_id, music_id)
    return {"is_favorited": is_favorited}


@router.get("/count")
async def get_favorites_count(
    user_id: int = Depends(get_current_user_id)
):
    """Get count of user's favorites"""
    count = data_store.get_favorite_count(user_id)
    return {"count": count}
