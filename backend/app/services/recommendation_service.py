from datetime import datetime
from typing import List, Optional
import random

from app.models.schemas import (
    MusicResponse, RecommendResponse, EmotionType, InteractionType
)
from app.services import data_store, emotion_service, music_service
from app.services.hybrid_recommender import get_recommender, rebuild_recommender


def get_recommendations(
    user_id: int,
    emotion: Optional[EmotionType] = None,
    limit: int = 10
) -> RecommendResponse:
    """
    Get personalized recommendations using hybrid algorithm:
    1. Content-based: match emotion tags
    2. Collaborative filtering: based on user interactions (matrix + cosine similarity)
    3. Fallback: random popular music
    """
    try:
        # Use new hybrid recommender with cosine similarity
        recommender = get_recommender()
        results, algorithm = recommender.get_recommendations(
            user_id=user_id,
            emotion=emotion,
            limit=limit,
            content_weight=0.5  # Equal weight for content and CF
        )

        # Convert to MusicResponse
        recommendations = [
            MusicResponse(**r['music']) for r in results
        ]

        # If we got valid recommendations, return them
        if recommendations:
            return RecommendResponse(
                recommendations=recommendations,
                algorithm=algorithm
            )
    except Exception as e:
        print(f"[!] Hybrid recommendation failed: {e}")

    # Fallback: use original simple method
    return _get_recommendations_fallback(user_id, emotion, limit)


def _get_recommendations_fallback(
    user_id: int,
    emotion: Optional[EmotionType] = None,
    limit: int = 10
) -> RecommendResponse:
    """Fallback recommendation method if hybrid fails"""

    # If emotion provided, use content-based
    if emotion:
        content_based = get_content_based_recommendations(emotion, limit)
        if content_based:
            return RecommendResponse(
                recommendations=content_based,
                algorithm="content-based"
            )

    # Try collaborative filtering
    collab_recommendations = get_collaborative_recommendations(user_id, limit)
    if collab_recommendations:
        return RecommendResponse(
            recommendations=collab_recommendations,
            algorithm="collaborative"
        )

    # Fallback: random music
    all_music = list(data_store.music_db.values())
    random.shuffle(all_music)
    recommendations = [MusicResponse(**m) for m in all_music[:limit]]

    return RecommendResponse(
        recommendations=recommendations,
        algorithm="random"
    )


def get_content_based_recommendations(
    emotion: EmotionType,
    limit: int = 10
) -> List[MusicResponse]:
    """Content-based recommendations based on emotion tags"""
    emotion_str = emotion.value
    matched_music = []

    for music in data_store.music_db.values():
        emotion_tags = music.get('emotion_tags', [])
        if emotion_str in [tag.lower() for tag in emotion_tags]:
            matched_music.append(music)

    # If exact match found, return them
    if matched_music:
        # Sort by energy level (for better match)
        matched_music.sort(
            key=lambda x: x.get('audio_features', {}).get('energy', 0.5),
            reverse=True
        )
        return [MusicResponse(**m) for m in matched_music[:limit]]

    # Partial match - include music with related emotions
    related_emotions = get_related_emotions(emotion_str)
    for music in data_store.music_db.values():
        if music in matched_music:
            continue
        emotion_tags = music.get('emotion_tags', [])
        if any(related in [tag.lower() for tag in emotion_tags] for related in related_emotions):
            matched_music.append(music)

    return [MusicResponse(**m) for m in matched_music[:limit]]


def get_collaborative_recommendations(
    user_id: int,
    limit: int = 10
) -> List[MusicResponse]:
    """Collaborative filtering based on user interactions"""

    # Get user's liked music
    user_liked_music = set()
    for interaction in data_store.interactions_db.values():
        if (interaction['user_id'] == user_id and
            interaction['interaction_type'] == InteractionType.LIKE):
            user_liked_music.add(interaction['music_id'])

    if not user_liked_music:
        return []

    # Find similar users (users who liked same music)
    similar_users = {}
    for interaction in data_store.interactions_db.values():
        if (interaction['interaction_type'] == InteractionType.LIKE and
            interaction['music_id'] in user_liked_music and
            interaction['user_id'] != user_id):
            similar_users[interaction['user_id']] = similar_users.get(
                interaction['user_id'], 0
            ) + 1

    if not similar_users:
        return []

    # Get music liked by similar users
    recommended_music = []
    for interaction in data_store.interactions_db.values():
        if (interaction['user_id'] in similar_users and
            interaction['music_id'] not in user_liked_music and
            interaction['interaction_type'] == InteractionType.LIKE):
            music = data_store.music_db.get(interaction['music_id'])
            if music:
                recommended_music.append(music)

    # Remove duplicates and return
    seen = set()
    unique_music = []
    for m in recommended_music:
        if m['id'] not in seen:
            seen.add(m['id'])
            unique_music.append(m)

    return [MusicResponse(**m) for m in unique_music[:limit]]


def get_related_emotions(emotion: str) -> List[str]:
    """Get emotion-related emotions for partial matching"""
    emotion_map = {
        'happy': ['happy', 'excited', 'relaxed'],
        'sad': ['sad', 'calm', 'relaxed'],
        'angry': ['angry', 'excited'],
        'calm': ['calm', 'relaxed', 'sad'],
        'excited': ['excited', 'happy', 'angry'],
        'relaxed': ['relaxed', 'calm', 'happy']
    }
    return emotion_map.get(emotion, [emotion])


def record_interaction(
    user_id: int,
    music_id: int,
    interaction_type: InteractionType,
    play_duration: int = 0
):
    """Record user-music interaction"""
    interaction_id = len(data_store.interactions_db) + 1

    interaction = {
        "id": interaction_id,
        "user_id": user_id,
        "music_id": music_id,
        "interaction_type": interaction_type,
        "play_duration": play_duration,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

    data_store.interactions_db[interaction_id] = interaction

    # Rebuild recommendation matrix with new interaction
    try:
        rebuild_recommender()
    except Exception as e:
        print(f"[!] Failed to rebuild recommendation matrix: {e}")

    return interaction


def get_recommendations_based_on_favorites(
    user_id: int,
    favorite_music: List[dict],
    limit: int = 10
) -> List[MusicResponse]:
    """
    Get recommendations based on user's favorite music.
    Uses audio features similarity to find similar songs.
    """
    if not favorite_music:
        return []

    # Get favorite music IDs (exclude from recommendations)
    favorite_ids = {m['id'] for m in favorite_music}

    # Collect audio features from favorites
    favorite_features = []
    for music in favorite_music:
        features = music.get('audio_features', {})
        if features:
            favorite_features.append(features)

    if not favorite_features:
        # No audio features, fall back to emotion-based
        return _get_recommendations_by_favorite_emotions(favorite_music, favorite_ids, limit)

    # Calculate average features
    avg_tempo = sum(f.get('tempo', 120) for f in favorite_features) / len(favorite_features)
    avg_energy = sum(f.get('energy', 0.5) for f in favorite_features) / len(favorite_features)
    avg_danceability = sum(f.get('danceability', 0.5) for f in favorite_features) / len(favorite_features)

    # Get favorite emotion tags
    favorite_emotions = set()
    for music in favorite_music:
        tags = music.get('emotion_tags', [])
        favorite_emotions.update([t.lower() for t in tags])

    # Find similar music
    candidates = []
    for music in data_store.music_db.values():
        music_id = music['id']

        # Skip if already favorited
        if music_id in favorite_ids:
            continue

        features = music.get('audio_features', {})

        # Calculate similarity score
        score = 0.0

        # Tempo similarity (closer is better)
        if features.get('tempo'):
            tempo_diff = abs(features['tempo'] - avg_tempo)
            tempo_score = max(0, 1 - tempo_diff / 100)  # Normalize
            score += tempo_score * 0.3

        # Energy similarity
        if features.get('energy'):
            energy_diff = abs(features['energy'] - avg_energy)
            energy_score = max(0, 1 - energy_diff)
            score += energy_score * 0.3

        # Danceability similarity
        if features.get('danceability'):
            dance_diff = abs(features.get('danceability', 0.5) - avg_danceability)
            dance_score = max(0, 1 - dance_diff)
            score += dance_score * 0.2

        # Emotion tag matching
        music_emotions = set([t.lower() for t in music.get('emotion_tags', [])])
        emotion_overlap = len(music_emotions & favorite_emotions)
        if favorite_emotions:
            emotion_score = emotion_overlap / len(favorite_emotions)
            score += emotion_score * 0.2

        if score > 0:
            candidates.append((music, score))

    # Sort by score (descending)
    candidates.sort(key=lambda x: x[1], reverse=True)

    # Return top recommendations
    recommendations = [MusicResponse(**m) for m, _ in candidates[:limit]]

    return recommendations


def _get_recommendations_by_favorite_emotions(
    favorite_music: List[dict],
    favorite_ids: set,
    limit: int = 10
) -> List[MusicResponse]:
    """Fallback: recommend based on favorite music's emotion tags"""
    # Get favorite emotion tags
    favorite_emotions = set()
    for music in favorite_music:
        tags = music.get('emotion_tags', [])
        favorite_emotions.update([t.lower() for t in tags])

    if not favorite_emotions:
        # No emotions, return random
        all_music = [m for m in data_store.music_db.values() if m['id'] not in favorite_ids]
        random.shuffle(all_music)
        return [MusicResponse(**m) for m in all_music[:limit]]

    # Find music with matching emotions
    candidates = []
    for music in data_store.music_db.values():
        if music['id'] in favorite_ids:
            continue

        music_emotions = set([t.lower() for t in music.get('emotion_tags', [])])
        overlap = len(music_emotions & favorite_emotions)

        if overlap > 0:
            candidates.append((music, overlap))

    candidates.sort(key=lambda x: x[1], reverse=True)
    return [MusicResponse(**m) for m, _ in candidates[:limit]]
