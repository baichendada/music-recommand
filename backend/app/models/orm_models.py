from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserORM(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class InteractionORM(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    music_id = Column(Integer, nullable=False)
    interaction_type = Column(String, nullable=False)  # play/like/skip/complete
    play_duration = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)


class FavoriteORM(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    music_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    __table_args__ = (
        UniqueConstraint("user_id", "music_id", name="uq_user_music"),
    )


class EmotionORM(Base):
    __tablename__ = "emotions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    emotion_type = Column(String, nullable=False)
    intensity = Column(Float, default=1.0)
    source = Column(String, default="explicit")
    created_at = Column(DateTime, default=datetime.now)
