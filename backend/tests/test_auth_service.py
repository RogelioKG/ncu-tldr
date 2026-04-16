from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth_service import AuthService


@pytest.fixture
def service() -> AuthService:
    return AuthService()


@pytest.fixture
def mock_db() -> AsyncMock:
    return AsyncMock(spec=AsyncSession)


async def test_register_sends_email_and_returns_message(
    service: AuthService, mock_db: AsyncMock
) -> None:
    with (
        patch("app.services.auth_service.user_repo") as mock_user_repo,
        patch(
            "app.services.auth_service.email_verification_token_repo"
        ) as mock_token_repo,
        patch("app.services.auth_service.send_verification_email", return_value=True),
    ):
        mock_user_repo.get_by_email = AsyncMock(return_value=None)
        mock_user_repo.create = AsyncMock(
            return_value=MagicMock(id="uuid-1", email="109999001@cc.ncu.edu.tw")
        )
        mock_token_repo.create = AsyncMock(return_value=MagicMock(token="tok-abc"))

        req = RegisterRequest(
            email="109999001@cc.ncu.edu.tw",
            password="secret",
            **{"displayName": "Test"},
        )
        result = await service.register(mock_db, req)

        assert result.message == "驗證信已寄出，請確認您的 NCU 學生信箱"


async def test_register_duplicate_email_raises_409(
    service: AuthService, mock_db: AsyncMock
) -> None:
    with patch("app.services.auth_service.user_repo") as mock_user_repo:
        mock_user_repo.get_by_email = AsyncMock(
            return_value=MagicMock(email="109999001@cc.ncu.edu.tw")
        )
        req = RegisterRequest(
            email="109999001@cc.ncu.edu.tw",
            password="secret",
            **{"displayName": "Test"},
        )
        with pytest.raises(HTTPException) as exc:
            await service.register(mock_db, req)
        assert exc.value.status_code == 409


async def test_register_ses_failure_raises_503(
    service: AuthService, mock_db: AsyncMock
) -> None:
    with (
        patch("app.services.auth_service.user_repo") as mock_user_repo,
        patch(
            "app.services.auth_service.email_verification_token_repo"
        ) as mock_token_repo,
        patch("app.services.auth_service.send_verification_email", return_value=False),
    ):
        mock_user_repo.get_by_email = AsyncMock(return_value=None)
        mock_user_repo.create = AsyncMock(
            return_value=MagicMock(id="uuid-1", email="109999001@cc.ncu.edu.tw")
        )
        mock_token_repo.create = AsyncMock(return_value=MagicMock(token="tok-abc"))

        req = RegisterRequest(
            email="109999001@cc.ncu.edu.tw",
            password="secret",
            **{"displayName": "Test"},
        )
        with pytest.raises(HTTPException) as exc:
            await service.register(mock_db, req)
        assert exc.value.status_code == 503


async def test_login_unverified_raises_403(
    service: AuthService, mock_db: AsyncMock
) -> None:
    with patch("app.services.auth_service.user_repo") as mock_user_repo:
        mock_user = MagicMock(email_verified=False, hashed_password="$2b$hash")
        mock_user_repo.get_by_email = AsyncMock(return_value=mock_user)

        with (
            patch("app.services.auth_service.verify_password", return_value=True),
            pytest.raises(HTTPException) as exc,
        ):
            await service.login(mock_db, LoginRequest(email="a@b.com", password="pw"))

        assert exc.value.status_code == 403


async def test_login_wrong_password_raises_401(
    service: AuthService, mock_db: AsyncMock
) -> None:
    with patch("app.services.auth_service.user_repo") as mock_user_repo:
        mock_user = MagicMock(email_verified=True, hashed_password="$2b$hash")
        mock_user_repo.get_by_email = AsyncMock(return_value=mock_user)

        with (
            patch("app.services.auth_service.verify_password", return_value=False),
            pytest.raises(HTTPException) as exc,
        ):
            await service.login(
                mock_db, LoginRequest(email="a@b.com", password="wrong")
            )

        assert exc.value.status_code == 401
