from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Music Recommendation System"
    DEBUG: bool = True
    API_PREFIX: str = "/api"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database
    # Set USE_DATABASE=true in .env to enable SQLite persistence
    # Set USE_DATABASE=false (default) to use in-memory mode
    USE_DATABASE: bool = False
    DATABASE_URL: str = "sqlite:///./data/music_app.db"

    class Config:
        env_file = ".env"


settings = Settings()
