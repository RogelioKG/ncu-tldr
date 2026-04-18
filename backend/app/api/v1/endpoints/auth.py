from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.deps import get_db
from app.deps.auth import get_current_user
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    ResendVerificationRequest,
    TokenResponse,
    UserOut,
)
from app.schemas.review import MyReviewOut
from app.services.auth_service import auth_service
from app.services.review_service import review_service

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=MessageResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.register(db, req)


@router.get("/verify-email", response_model=TokenResponse)
async def verify_email(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    return await auth_service.verify_email(db, token)


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(
    req: ResendVerificationRequest, db: AsyncSession = Depends(get_db)
):
    return await auth_service.resend_verification(db, req)


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.login(db, req)


@router.get("/me/reviews", response_model=list[MyReviewOut])
async def my_reviews(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await review_service.list_my_reviews(db, current_user)


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return UserOut(
        id=str(current_user.id),
        email=current_user.email,
        display_name=current_user.display_name,
        is_active=current_user.is_active,
        email_verified=current_user.email_verified,
    )
