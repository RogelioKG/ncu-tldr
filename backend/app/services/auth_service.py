from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repo import user_repo
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut


class AuthService:
    def _build_token_response(self, user: User) -> TokenResponse:
        token = create_access_token(str(user.id))
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserOut(
                id=str(user.id),
                email=user.email,
                display_name=user.display_name,
                is_active=user.is_active,
            ),
        )

    async def register(self, db: AsyncSession, req: RegisterRequest) -> TokenResponse:
        existing = await user_repo.get_by_email(db, req.email)
        if existing:
            raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
        user = await user_repo.create(
            db,
            email=req.email,
            hashed_password=hash_password(req.password),
            display_name=req.display_name,
        )
        return self._build_token_response(user)

    async def login(self, db: AsyncSession, req: LoginRequest) -> TokenResponse:
        user = await user_repo.get_by_email(db, req.email)
        if not user or not verify_password(req.password, user.hashed_password):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, "Invalid email or password"
            )
        return self._build_token_response(user)


auth_service = AuthService()
