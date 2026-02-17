from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.models.schemas import UserCreate, UserLogin, UserResponse, Token
from app.services import auth_service

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
