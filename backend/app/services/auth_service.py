from datetime import datetime
import bcrypt
import hashlib
from jose import jwt
from fastapi import HTTPException, status
from typing import Optional

from app.core.config import settings
from app.models.schemas import UserCreate, UserResponse, Token
from app.services import data_store


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def get_password_hash(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')


def create_access_token(user_id: int) -> str:
    """Create JWT access token"""
    to_encode = {"sub": str(user_id)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def register_user(user_data: UserCreate) -> UserResponse:
    """Register a new user"""
    # Check if username exists
    if user_data.username in data_store.users_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email exists
    if user_data.email in data_store.users_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Generate user ID
    user_id = len(data_store.users_db) + 1

    # Create user
    user = {
        "id": user_id,
        "username": user_data.username,
        "email": user_data.email,
        "password_hash": get_password_hash(user_data.password),
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

    # Store user
    data_store.users_db[user_id] = user
    data_store.users_by_username[user_data.username] = user_id
    data_store.users_by_email[user_data.email] = user_id

    return UserResponse(**user)


def authenticate_user(username: str, password: str) -> Token:
    """Authenticate user and return token"""
    # Find user by username
    user_id = data_store.users_by_username.get(username)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    user = data_store.users_db.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    # Verify password
    if not verify_password(password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    # Create token
    access_token = create_access_token(user_id)

    # Store token
    data_store.tokens_db[access_token] = user_id

    return Token(access_token=access_token)


def get_current_user(token: str) -> UserResponse:
    """Get current user from token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = int(payload.get("sub"))
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user = data_store.users_db.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(**user)


def get_user_by_id(user_id: int) -> Optional[UserResponse]:
    """Get user by ID"""
    user = data_store.users_db.get(user_id)
    if not user:
        return None
    return UserResponse(**user)
