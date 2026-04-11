"""
Database-backed storage operations.

Each function mirrors its counterpart in data_store.py but reads/writes
to SQLite via SQLAlchemy. Called only when is_db_enabled() is True.
"""

from datetime import datetime
from typing import Dict, List, Optional, Set

from app.core.database import get_session
from app.models.orm_models import UserORM, InteractionORM, FavoriteORM, EmotionORM


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def db_create_user(user_id: int, username: str, email: str, password_hash: str) -> dict:
    session = get_session()
    try:
        user = UserORM(
            id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return _user_to_dict(user)
    finally:
        session.close()


def db_load_all_users() -> List[dict]:
    """Load all users from DB into memory on startup."""
    session = get_session()
    try:
        users = session.query(UserORM).all()
        return [_user_to_dict(u) for u in users]
    finally:
        session.close()


def _user_to_dict(u: UserORM) -> dict:
    return {
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "password_hash": u.password_hash,
        "created_at": u.created_at,
        "updated_at": u.updated_at,
    }


# ---------------------------------------------------------------------------
# Interactions
# ---------------------------------------------------------------------------

def db_create_interaction(
    interaction_id: int,
    user_id: int,
    music_id: int,
    interaction_type: str,
    play_duration: int = 0,
) -> dict:
    session = get_session()
    try:
        row = InteractionORM(
            id=interaction_id,
            user_id=user_id,
            music_id=music_id,
            interaction_type=interaction_type,
            play_duration=play_duration,
            created_at=datetime.now(),
        )
        session.add(row)
        session.commit()
        return _interaction_to_dict(row)
    finally:
        session.close()


def db_load_all_interactions() -> List[dict]:
    session = get_session()
    try:
        rows = session.query(InteractionORM).all()
        return [_interaction_to_dict(r) for r in rows]
    finally:
        session.close()


def _interaction_to_dict(r: InteractionORM) -> dict:
    return {
        "id": r.id,
        "user_id": r.user_id,
        "music_id": r.music_id,
        "interaction_type": r.interaction_type,
        "play_duration": r.play_duration,
        "created_at": r.created_at,
        "updated_at": r.created_at,
    }


# ---------------------------------------------------------------------------
# Favorites
# ---------------------------------------------------------------------------

def db_add_favorite(favorite_id: int, user_id: int, music_id: int) -> dict:
    session = get_session()
    try:
        # Check if already exists
        existing = session.query(FavoriteORM).filter_by(
            user_id=user_id, music_id=music_id
        ).first()
        if existing:
            return _favorite_to_dict(existing)

        row = FavoriteORM(
            id=favorite_id,
            user_id=user_id,
            music_id=music_id,
            created_at=datetime.now(),
        )
        session.add(row)
        session.commit()
        session.refresh(row)
        return _favorite_to_dict(row)
    finally:
        session.close()


def db_remove_favorite(user_id: int, music_id: int) -> bool:
    session = get_session()
    try:
        row = session.query(FavoriteORM).filter_by(
            user_id=user_id, music_id=music_id
        ).first()
        if not row:
            return False
        session.delete(row)
        session.commit()
        return True
    finally:
        session.close()


def db_load_all_favorites() -> List[dict]:
    session = get_session()
    try:
        rows = session.query(FavoriteORM).all()
        return [_favorite_to_dict(r) for r in rows]
    finally:
        session.close()


def _favorite_to_dict(r: FavoriteORM) -> dict:
    return {
        "id": r.id,
        "user_id": r.user_id,
        "music_id": r.music_id,
        "created_at": r.created_at,
    }


# ---------------------------------------------------------------------------
# Emotions
# ---------------------------------------------------------------------------

def db_create_emotion(
    emotion_id: int,
    user_id: int,
    emotion_type: str,
    intensity: float = 1.0,
    source: str = "explicit",
) -> dict:
    session = get_session()
    try:
        row = EmotionORM(
            id=emotion_id,
            user_id=user_id,
            emotion_type=emotion_type,
            intensity=intensity,
            source=source,
            created_at=datetime.now(),
        )
        session.add(row)
        session.commit()
        return _emotion_to_dict(row)
    finally:
        session.close()


def db_load_all_emotions() -> List[dict]:
    session = get_session()
    try:
        rows = session.query(EmotionORM).all()
        return [_emotion_to_dict(r) for r in rows]
    finally:
        session.close()


def _emotion_to_dict(r: EmotionORM) -> dict:
    return {
        "id": r.id,
        "user_id": r.user_id,
        "emotion_type": r.emotion_type,
        "intensity": r.intensity,
        "source": r.source,
        "created_at": r.created_at,
    }
