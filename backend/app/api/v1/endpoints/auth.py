from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.deps import get_db
from app.deps.auth import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut
from app.schemas.review import MyReviewOut
from app.services.auth_service import auth_service
from app.services.review_service import review_service

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.login(db, req)


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.register(db, req)


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
        display_name=current_user.display_name,
        email=current_user.email,
        is_active=current_user.is_active,
    )
