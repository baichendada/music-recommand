"""
Database connection management.

When USE_DATABASE=true in .env, uses SQLite via SQLAlchemy.
When USE_DATABASE=false (default), all operations are no-ops and
the existing in-memory data_store continues to work unchanged.
"""

from app.core.config import settings

engine = None
SessionLocal = None


def init_db():
    """Initialize database if USE_DATABASE is enabled."""
    global engine, SessionLocal

    if not settings.USE_DATABASE:
        print("[db] USE_DATABASE=false — running in memory mode")
        return

    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.models.orm_models import Base
        import os

        # Ensure data directory exists
        db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

        engine = create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False}
        )
        SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

        # Create all tables
        Base.metadata.create_all(bind=engine)
        print(f"[db] SQLite database initialized: {settings.DATABASE_URL}")

    except Exception as e:
        print(f"[db] Failed to initialize database: {e}")
        print("[db] Falling back to memory mode")
        engine = None
        SessionLocal = None


def get_session():
    """Get a database session. Returns None if database is disabled."""
    if SessionLocal is None:
        return None
    return SessionLocal()


def is_db_enabled() -> bool:
    """Check if database mode is active."""
    return engine is not None and SessionLocal is not None
