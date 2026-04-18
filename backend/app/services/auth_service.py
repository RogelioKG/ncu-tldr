import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.email_verification_token_repo import email_verification_token_repo
from app.repositories.user_repo import user_repo
from app.schemas.auth import (
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    ResendVerificationRequest,
    TokenResponse,
    UserOut,
)
from app.services.email_service import send_verification_email


class AuthService:
    def _build_token_response(
        self, user: User, remember_me: bool = False
    ) -> TokenResponse:
        token = create_access_token(str(user.id), remember_me=remember_me)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserOut(
                id=str(user.id),
                email=user.email,
                display_name=user.display_name,
                is_active=user.is_active,
                email_verified=user.email_verified,
            ),
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

    async def verify_email(self, db: AsyncSession, token: str) -> TokenResponse:
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

        return self._build_token_response(user)

    async def login(self, db: AsyncSession, req: LoginRequest) -> TokenResponse:
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
        return self._build_token_response(user, remember_me=req.remember_me)

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
