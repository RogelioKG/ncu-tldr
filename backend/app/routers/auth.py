from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.auth import (
    AuthTokenResponse,
    LoginRequest,
    RegisterRequest,
    UserResponse,
)
from app.services.mock_db import mock_db

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer(auto_error=True)


@router.post("/login", response_model=AuthTokenResponse)
async def login(payload: LoginRequest) -> AuthTokenResponse:
    token, user = mock_db.login(email=payload.email, password=payload.password)
    return AuthTokenResponse(accessToken=token, user=user)


@router.post("/register", response_model=AuthTokenResponse)
async def register(payload: RegisterRequest) -> AuthTokenResponse:
    token, user = mock_db.register(
        email=payload.email,
        password=payload.password,
        display_name=payload.displayName,
    )
    return AuthTokenResponse(accessToken=token, user=user)


@router.get("/me", response_model=UserResponse)
async def get_me(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UserResponse:
    return mock_db.get_user_by_token(credentials.credentials)
