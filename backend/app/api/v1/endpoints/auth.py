import logging

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.logging_utils import mask_email
from app.db.deps import get_db
from app.deps.auth import get_current_user
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    ResendVerificationRequest,
    UserOut,
)
from app.schemas.review import MyReviewOut
from app.services.auth_service import AuthTokens, auth_service
from app.services.review_service import review_service

router = APIRouter(tags=["auth"])
_settings = get_settings()
logger = logging.getLogger(__name__)


def _set_auth_cookies(response: Response, tokens: AuthTokens) -> None:
    days = (
        _settings.refresh_token_remember_me_expire_days
        if tokens.remember_me
        else _settings.refresh_token_expire_days
    )
    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        httponly=True,
        samesite=_settings.cookie_samesite,
        secure=_settings.cookie_secure,
        max_age=_settings.access_token_expire_minutes * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        samesite=_settings.cookie_samesite,
        secure=_settings.cookie_secure,
        max_age=days * 24 * 60 * 60,
        path="/api/v1/auth",
    )
    logger.debug("Authentication cookies set remember_me=%s", tokens.remember_me)


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/api/v1/auth")
    logger.debug("Authentication cookies cleared")


@router.post("/register", response_model=MessageResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    logger.debug("Register endpoint called email=%s", mask_email(req.email))
    return await auth_service.register(db, req)


@router.get("/verify-email", response_model=UserOut)
async def verify_email(
    response: Response,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    logger.info("Verify-email endpoint called")
    tokens = await auth_service.verify_email(db, token)
    _set_auth_cookies(response, tokens)
    return tokens.user


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(
    req: ResendVerificationRequest, db: AsyncSession = Depends(get_db)
):
    logger.debug(
        "Resend-verification endpoint called email=%s", mask_email(str(req.email))
    )
    return await auth_service.resend_verification(db, req)


@router.post("/login", response_model=UserOut)
async def login(
    req: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)
):
    logger.debug(
        "Login endpoint called email=%s remember_me=%s",
        mask_email(req.email),
        req.remember_me,
    )
    tokens = await auth_service.login(db, req)
    _set_auth_cookies(response, tokens)
    return tokens.user


@router.post("/refresh", response_model=UserOut)
async def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    if refresh_token is None:
        logger.info("Refresh endpoint failed: no refresh token cookie")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "No refresh token")
    logger.debug("Refresh endpoint called")
    tokens = await auth_service.refresh(db, refresh_token)
    _set_auth_cookies(response, tokens)
    return tokens.user


@router.post("/logout", response_model=MessageResponse)
async def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    logger.debug("Logout endpoint called")
    await auth_service.logout(db, refresh_token)
    _clear_auth_cookies(response)
    return MessageResponse(message="已登出")


@router.get("/me/reviews", response_model=list[MyReviewOut])
async def my_reviews(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.debug("My-reviews endpoint called user_id=%s", current_user.id)
    return await review_service.list_my_reviews(db, current_user)


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    logger.debug("Me endpoint called user_id=%s", current_user.id)
    return UserOut.model_validate(current_user)
