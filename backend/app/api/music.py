from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException

from app.models.schemas import MusicCreate, MusicResponse
from app.services import auth_service, music_service
import os

router = APIRouter(prefix="/music", tags=["Music"])
security = HTTPBearer()


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Get current user ID from token"""
    user = auth_service.get_current_user(credentials.credentials)
    return user.id


@router.get("", response_model=List[MusicResponse])
async def get_music_list(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get all music"""
    return music_service.get_all_music(limit=limit, offset=offset)


@router.get("/search", response_model=List[MusicResponse])
async def search_music(q: str = Query(..., min_length=1)):
    """Search music by title or artist"""
    return music_service.search_music(q)


@router.get("/audio/{music_id}")
async def get_audio_stream(music_id: int):
    """Stream audio file for a music track"""
    music = music_service.get_music_by_id(music_id)
    if not music:
        raise HTTPException(status_code=404, detail="Music not found")

    audio_url = music.audio_url
    if not audio_url:
        raise HTTPException(status_code=404, detail="Audio file not found")

    # If it's already a URL, redirect to it so media players can stream directly
    if audio_url.startswith('http'):
        return RedirectResponse(url=audio_url, status_code=302)

    # If it's a local file, stream it
    if os.path.exists(audio_url):
        ext = os.path.splitext(audio_url)[1].lower()
        media_type = "audio/wav"
        if ext == ".mp3":
            media_type = "audio/mpeg"

        return FileResponse(
            audio_url,
            media_type=media_type,
            headers={
                "Accept-Ranges": "bytes",
                "Content-Disposition": f'inline; filename="{os.path.basename(audio_url)}"'
            }
        )
    else:
        raise HTTPException(status_code=404, detail="Audio file not found")


@router.get("/{music_id}", response_model=MusicResponse)
async def get_music(music_id: int):
    """Get music details by ID"""
    return music_service.get_music_by_id(music_id)


@router.post("", response_model=MusicResponse, status_code=status.HTTP_201_CREATED)
async def create_music(
    music_data: MusicCreate,
    user_id: int = Depends(get_current_user_id)
):
    """Create new music (admin only in production)"""
    return music_service.create_music(music_data)
