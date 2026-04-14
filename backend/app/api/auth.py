from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.models.schemas import UserCreate, UserLogin, UserResponse, Token
from app.services import auth_service, data_store
from app.models.schemas import InteractionType

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user"""
    return auth_service.register_user(user_data)


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """Login and get access token"""
    return auth_service.authenticate_user(user_data.username, user_data.password)


@router.get("/me", response_model=UserResponse)
async def get_me(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user info"""
    token = credentials.credentials
    return auth_service.get_current_user(token)


@router.get("/stats")
async def get_user_stats(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get user interaction statistics"""
    token = credentials.credentials
    user = auth_service.get_current_user(token)
    user_id = user.id

    plays = sum(
        1 for i in data_store.interactions_db.values()
        if i["user_id"] == user_id and i["interaction_type"] == InteractionType.PLAY
    )
    # Use favorites count as likes (favorites are added via /favorites endpoint, not interactions)
    likes = len(data_store.get_user_favorites(user_id))

    return {"plays": plays, "likes": likes}
