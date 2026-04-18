import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.security import (
    create_access_token,
    generate_refresh_token_str,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.user import User
from app.repositories.email_verification_token_repo import email_verification_token_repo
from app.repositories.refresh_token_repo import refresh_token_repo
from app.repositories.user_repo import user_repo
from app.schemas.auth import (
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    ResendVerificationRequest,
    UserOut,
)
from app.services.email_service import send_verification_email

_settings = get_settings()


@dataclass
class AuthTokens:
    user: UserOut
    access_token: str
    refresh_token: str
    remember_me: bool = False


class AuthService:
    def _build_user_out(self, user: User) -> UserOut:
        return UserOut(
            id=str(user.id),
            email=user.email,
            display_name=user.display_name,
            is_active=user.is_active,
            email_verified=user.email_verified,
        )

    async def _issue_tokens(
        self, db: AsyncSession, user: User, remember_me: bool = False
    ) -> AuthTokens:
        access_token = create_access_token(str(user.id))
        raw_refresh = generate_refresh_token_str()
        token_hash = hash_token(raw_refresh)
        days = (
            _settings.refresh_token_remember_me_expire_days
            if remember_me
            else _settings.refresh_token_expire_days
        )
        expires_at = datetime.now(timezone.utc) + timedelta(days=days)
        await refresh_token_repo.create(
            db, user_id=user.id, token_hash=token_hash, expires_at=expires_at
        )
        return AuthTokens(
            user=self._build_user_out(user),
            access_token=access_token,
            refresh_token=raw_refresh,
            remember_me=remember_me,
        )

    async def register(self, db: AsyncSession, req: RegisterRequest) -> MessageResponse:
        existing = await user_repo.get_by_email(db, req.email)
        if existing:
            raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")

        user = await user_repo.create(
            db,
            email=req.email,
            hashed_password=hash_password(req.password),
            display_name=req.display_name,
        )

        token_str = str(uuid.uuid4())
        await email_verification_token_repo.create(db, user_id=user.id, token=token_str)

        sent = send_verification_email(req.email, token_str)
        if not sent:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="無法寄送驗證信，請稍後再試",
            )
        return MessageResponse(message="驗證信已寄出，請確認您的 NCU 學生信箱")

    async def verify_email(self, db: AsyncSession, token: str) -> AuthTokens:
        record = await email_verification_token_repo.get_by_token(db, token)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="無效的驗證連結"
            )
        if record.used_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="驗證連結已使用過"
            )
        if datetime.now(timezone.utc) > record.expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="驗證連結已過期"
            )

        user = await user_repo.get_by_id(db, record.user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="使用者不存在"
            )

        await email_verification_token_repo.mark_used(db, record)

        if not user.email_verified:
            user.email_verified = True
            await db.flush()

        return await self._issue_tokens(db, user)

    async def login(self, db: AsyncSession, req: LoginRequest) -> AuthTokens:
        user = await user_repo.get_by_email(db, req.email)
        if not user or not verify_password(req.password, user.hashed_password):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, "Invalid email or password"
            )
        if not user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="請先驗證您的電子信箱",
            )
        return await self._issue_tokens(db, user, remember_me=req.remember_me)

    async def refresh(self, db: AsyncSession, raw_refresh_token: str) -> AuthTokens:
        token_hash = hash_token(raw_refresh_token)
        record = await refresh_token_repo.get_by_hash(db, token_hash)

        if record is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")

        if record.revoked_at is not None:
            # Token was already used — possible theft. Revoke all tokens for this user.
            await refresh_token_repo.revoke_all_for_user(db, record.user_id)
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, "Refresh token reuse detected"
            )

        if datetime.now(timezone.utc) > record.expires_at:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token expired")

        user = await user_repo.get_by_id(db, record.user_id)
        if user is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")

        # Rotate: revoke old token, issue new one
        await refresh_token_repo.revoke(db, record)

        # Preserve remember_me semantics: if old token had >1 day expiry, keep it
        days_remaining = (record.expires_at - datetime.now(timezone.utc)).days
        remember_me = days_remaining > _settings.refresh_token_expire_days

        return await self._issue_tokens(db, user, remember_me=remember_me)

    async def logout(self, db: AsyncSession, raw_refresh_token: str | None) -> None:
        if raw_refresh_token is None:
            return
        token_hash = hash_token(raw_refresh_token)
        record = await refresh_token_repo.get_by_hash(db, token_hash)
        if record and record.revoked_at is None:
            await refresh_token_repo.revoke(db, record)

    async def resend_verification(
        self, db: AsyncSession, req: ResendVerificationRequest
    ) -> MessageResponse:
        user = await user_repo.get_by_email(db, str(req.email))
        if user is not None and not user.email_verified:
            token_str = str(uuid.uuid4())
            await email_verification_token_repo.create(
                db, user_id=user.id, token=token_str
            )
            send_verification_email(user.email, token_str)
        return MessageResponse(message="若此信箱已註冊且尚未驗證，驗證信已重新寄出")


auth_service = AuthService()
