"""
AI Analysis API Endpoints
"""

from typing import Optional
from fastapi import APIRouter, File, UploadFile, Form, status
from pydantic import BaseModel

from app.ai.emotion_service import (
    analyze_music_emotion,
    get_recommended_emotions,
    match_music_to_emotion
)
from app.ai.audio_extractor import extract_audio_features
from app.ai.lyrics_analyzer import analyze_lyrics

router = APIRouter(prefix="/ai", tags=["AI Analysis"])


class LyricsAnalysisRequest(BaseModel):
    lyrics: str


class EmotionAnalysisRequest(BaseModel):
    audio_url: Optional[str] = None
    lyrics: Optional[str] = None


class EmotionAnalysisResponse(BaseModel):
    audio_analysis: Optional[dict] = None
    lyrics_analysis: Optional[dict] = None
    combined_tags: list
    primary_emotion: str
    confidence: float


@router.post("/analyze/emotion", response_model=EmotionAnalysisResponse)
async def analyze_emotion(request: EmotionAnalysisRequest):
    """
    Analyze music emotion from audio and/or lyrics

    - **audio_url**: URL or path to audio file
    - **lyrics**: Lyrics text (supports Chinese)
    """
    result = analyze_music_emotion(audio_url=request.audio_url, lyrics=request.lyrics)
    return EmotionAnalysisResponse(**result)


@router.post("/analyze/lyrics")
async def analyze_lyrics_text(request: LyricsAnalysisRequest):
    """
    Analyze lyrics sentiment and emotion

    - **lyrics**: Chinese lyrics text
    """
    result = analyze_lyrics(request.lyrics)
    return result


@router.get("/analyze/audio/{music_id}")
async def analyze_audio_features(audio_url: str):
    """
    Extract audio features from music file

    - **audio_url**: URL or path to audio file
    """
    features = extract_audio_features(audio_url)
    return features


@router.get("/recommend/emotions/{emotion}")
async def get_emotion_recommendations(emotion: str):
    """
    Get related emotions for recommendation

    - **emotion**: Primary emotion
    """
    related = get_recommended_emotions(emotion)
    return {
        "emotion": emotion,
        "related_emotions": related
    }


@router.post("/match")
async def match_music(
    emotion: str = Form(...),
    audio_features: dict = Form(...)
):
    """
    Calculate how well music matches an emotion

    - **emotion**: Target emotion
    - **audio_features**: Audio features dictionary
    """
    score = match_music_to_emotion(emotion, audio_features)
    return {
        "emotion": emotion,
        "match_score": score,
        "match_level": "high" if score > 0.7 else "medium" if score > 0.4 else "low"
    }
