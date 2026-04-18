# JWT + HttpOnly Cookie + Refresh Token Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate from `localStorage` Bearer token to HttpOnly cookies with short-lived access tokens and rotating refresh tokens stored in DB.

**Architecture:** Login sets two HttpOnly cookies — `access_token` (15-min JWT) and `refresh_token` (raw token stored hashed in DB). On 401 the frontend silently calls `POST /refresh` to rotate both cookies. Frontend never touches localStorage or Authorization headers again — cookies are sent automatically.

**Tech Stack:** FastAPI (Cookie dep), python-jose JWT, bcrypt-style SHA-256 hash for refresh tokens, httpx test client (handles cookies), Vue 3 + Pinia, `fetch` with `credentials: 'include'`

---

## Background: What Currently Exists

| Layer | Current state |
|-------|--------------|
| Backend token creation | `core/security.py` — `create_access_token(sub, remember_me)` — 15 min or 3-day JWT |
| Backend auth dep | `deps/auth.py` — reads `Authorization: Bearer <token>` |
| Backend login response | `schemas/auth.py` `TokenResponse` — returns `{ accessToken, tokenType, user }` |
| Frontend storage | `useAuthStore` — stores token in `localStorage` key `ncu-tldr-token` |
| Frontend requests | `api/client.ts` — sets `Authorization: Bearer` header manually |
| Tests | `tests/test_auth.py` — asserts `accessToken` in response body, sends `Authorization` header |

Everything above changes. Nothing uses the Authorization header after this plan.

---

## File Map

### New files
- `backend/app/models/refresh_token.py` — SQLAlchemy ORM model
- `backend/app/repositories/refresh_token_repo.py` — DB operations for refresh tokens
- `backend/alembic/versions/v16__a1b2c3d4e5f6__add_refresh_tokens.py` — migration

### Modified backend files
- `backend/app/config.py` — add `access_token_expire_minutes=15`, `refresh_token_expire_days`, `cookie_secure`, `cookie_samesite`
- `backend/app/core/security.py` — add `hash_token()`, `generate_refresh_token_str()`
- `backend/app/schemas/auth.py` — remove `TokenResponse`, keep `UserOut`
- `backend/app/services/auth_service.py` — new internal `AuthTokens` dataclass, update login/verify_email, add `refresh`/`logout`
- `backend/app/deps/auth.py` — read from `Cookie` instead of Bearer
- `backend/app/api/v1/endpoints/auth.py` — inject `Response`, set cookies, add `/refresh` and `/logout`
- `backend/tests/test_auth.py` — update to assert cookies instead of body tokens, use cookie-based `/me`

### Modified frontend files
- `frontend/src/api/client.ts` — add `credentials: 'include'`, remove `token` option, add silent refresh on 401
- `frontend/src/api/auth.ts` — update `AuthResult`, add `logout()`, `refreshToken()`
- `frontend/src/stores/useAuthStore.ts` — remove `token`/localStorage, simplify `hydrateFromStorage`
- `frontend/src/router/index.ts` — add `beforeEach` guard for protected routes

---

## Task 1: Refresh Token Model + Migration

**Files:**
- Create: `backend/app/models/refresh_token.py`
- Create: `backend/alembic/versions/v16__a1b2c3d4e5f6__add_refresh_tokens.py`

The `refresh_tokens` table stores the SHA-256 hash of the raw token (never the raw token itself). `revoked_at` is NULL while valid.

- [ ] **Step 1: Write the failing test for the model import**

File: `backend/tests/test_refresh_token_repo.py` (new file)

```python
import pytest
from app.models.refresh_token import RefreshToken


def test_refresh_token_model_has_expected_columns() -> None:
    cols = {c.key for c in RefreshToken.__table__.columns}
    assert cols == {"id", "user_id", "token_hash", "expires_at", "revoked_at", "created_at"}
```

- [ ] **Step 2: Run to confirm it fails**

```bash
cd backend && python -m pytest tests/test_refresh_token_repo.py::test_refresh_token_model_has_expected_columns -v
```

Expected: `ModuleNotFoundError: No module named 'app.models.refresh_token'`

- [ ] **Step 3: Create `backend/app/models/refresh_token.py`**

```python
import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(sa.String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        nullable=False,
    )

    __table_args__ = (
        sa.Index("idx_refresh_tokens_token_hash", "token_hash", unique=True),
        sa.Index("idx_refresh_tokens_user_id", "user_id"),
    )
```

- [ ] **Step 4: Register the new model in `backend/app/models/__init__.py`**

Read the file first, then add the import. It should follow the same pattern as other model imports. Add:

```python
from app.models.refresh_token import RefreshToken  # noqa: F401
```

- [ ] **Step 5: Run test to confirm it passes**

```bash
cd backend && python -m pytest tests/test_refresh_token_repo.py::test_refresh_token_model_has_expected_columns -v
```

Expected: `PASSED`

- [ ] **Step 6: Create the Alembic migration `backend/alembic/versions/v16__a1b2c3d4e5f6__add_refresh_tokens.py`**

```python
"""add refresh tokens

Revision ID: a1b2c3d4e5f6
Revises: 5dc0a0a89f21
Create Date: 2026-04-19

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "5dc0a0a89f21"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "refresh_tokens",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"], unique=True
    )
    op.create_index("idx_refresh_tokens_user_id", "refresh_tokens", ["user_id"])


def downgrade() -> None:
    op.drop_index("idx_refresh_tokens_user_id", table_name="refresh_tokens")
    op.drop_index("idx_refresh_tokens_token_hash", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")
```

- [ ] **Step 7: Run migration against the dev DB**

```bash
cd backend && docker compose exec backend uv run alembic upgrade head
```

Expected: Migration `a1b2c3d4e5f6` runs without error.

- [ ] **Step 8: Commit**

```bash
git add backend/app/models/refresh_token.py backend/app/models/__init__.py backend/alembic/versions/v16__a1b2c3d4e5f6__add_refresh_tokens.py backend/tests/test_refresh_token_repo.py
git commit -m "feat(auth): add RefreshToken model and migration v16"
```

---

## Task 2: Config + Security Utilities

**Files:**
- Modify: `backend/app/config.py`
- Modify: `backend/app/core/security.py`

The access token shortens from 180 min to 15 min. Refresh token lifetime is 1 day (or 30 days for `remember_me`). `cookie_secure` is `False` in local dev (set via `.env`), `True` in production.

- [ ] **Step 1: Write the failing tests for security utilities**

File: `backend/tests/test_security.py` (new file)

```python
import hashlib
import secrets

from app.core.security import generate_refresh_token_str, hash_token


def test_generate_refresh_token_str_is_urlsafe_64_chars() -> None:
    token = generate_refresh_token_str()
    assert len(token) == 64
    assert token.isascii()


def test_generate_refresh_token_str_is_unique() -> None:
    assert generate_refresh_token_str() != generate_refresh_token_str()


def test_hash_token_returns_sha256_hex() -> None:
    raw = "some-random-token-string"
    result = hash_token(raw)
    expected = hashlib.sha256(raw.encode()).hexdigest()
    assert result == expected
    assert len(result) == 64


def test_hash_token_is_deterministic() -> None:
    raw = generate_refresh_token_str()
    assert hash_token(raw) == hash_token(raw)
```

- [ ] **Step 2: Run to confirm they fail**

```bash
cd backend && python -m pytest tests/test_security.py -v
```

Expected: `ImportError` — `generate_refresh_token_str` and `hash_token` do not exist yet.

- [ ] **Step 3: Update `backend/app/config.py`**

Replace the existing `Settings` class body to match (keep all existing fields, add the new ones):

```python
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="allow",
        case_sensitive=False,
    )

    app_name: str = Field(default="NCU-TLDR Backend")
    app_version: str = Field(default="0.1.0")
    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173"],
    )

    x_sync_secret_key: str = Field(..., min_length=1)
    jwt_secret_key: str = Field(..., min_length=1)
    access_token_expire_minutes: int = Field(default=15)
    refresh_token_expire_days: int = Field(default=1)
    refresh_token_remember_me_expire_days: int = Field(default=30)
    cookie_secure: bool = Field(default=True)
    cookie_samesite: str = Field(default="lax")

    database_url: str = Field(..., min_length=1)
    sqlalchemy_echo: bool = Field(default=False)

    # AWS SES
    aws_access_key_id: str = Field(..., min_length=1)
    aws_secret_access_key: str = Field(..., min_length=1)
    aws_region: str = Field(default="ap-southeast-1")
    email_from: str = Field(default="NCU-TLDR <noreply@ncutldr.com>")
    verify_base_url: str = Field(default="https://ncutldr.com")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore
```

Note: `remember_me_expire_minutes` is removed (no longer needed — `remember_me` now controls refresh token lifetime, not access token).

- [ ] **Step 4: Add `COOKIE_SECURE=false` to local `.env`**

Open `.env` (project root) and add this line if not already present:
```
COOKIE_SECURE=false
```

- [ ] **Step 5: Update `backend/app/core/security.py`**

Full replacement:

```python
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from app.config import get_settings

_settings = get_settings()
_SECRET_KEY: str = _settings.jwt_secret_key
_ALGORITHM = "HS256"
_ACCESS_TOKEN_EXPIRE_MINUTES = _settings.access_token_expire_minutes


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(sub: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": sub, "exp": expire}
    return jwt.encode(payload, _SECRET_KEY, algorithm=_ALGORITHM)


def decode_access_token(token: str) -> str:
    payload = jwt.decode(token, _SECRET_KEY, algorithms=[_ALGORITHM])
    return str(payload["sub"])


def generate_refresh_token_str() -> str:
    """Return a 64-char URL-safe random token (raw, not hashed)."""
    return secrets.token_urlsafe(48)[:64]


def hash_token(raw: str) -> str:
    """SHA-256 hex digest of a raw token. Store this in the DB, never the raw value."""
    return hashlib.sha256(raw.encode()).hexdigest()
```

Note: `create_access_token` no longer takes `remember_me` — access tokens are always 15 min. The `remember_me` parameter is removed.

- [ ] **Step 6: Run the new security tests**

```bash
cd backend && python -m pytest tests/test_security.py -v
```

Expected: All 4 tests `PASSED`.

- [ ] **Step 7: Commit**

```bash
git add backend/app/config.py backend/app/core/security.py backend/tests/test_security.py
git commit -m "feat(auth): add cookie config, hash_token, and generate_refresh_token_str"
```

---

## Task 3: Refresh Token Repository

**Files:**
- Create: `backend/app/repositories/refresh_token_repo.py`
- Modify: `backend/tests/test_refresh_token_repo.py`

- [ ] **Step 1: Add repository tests to `backend/tests/test_refresh_token_repo.py`**

Replace the entire file:

```python
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from app.core.security import generate_refresh_token_str, hash_token
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.refresh_token_repo import refresh_token_repo
from app.repositories.user_repo import user_repo
from sqlalchemy.ext.asyncio import AsyncSession


def test_refresh_token_model_has_expected_columns() -> None:
    cols = {c.key for c in RefreshToken.__table__.columns}
    assert cols == {"id", "user_id", "token_hash", "expires_at", "revoked_at", "created_at"}


@pytest.fixture
async def test_user(db: AsyncSession) -> User:
    return await user_repo.create(
        db,
        email="999000001@cc.ncu.edu.tw",
        hashed_password="hashed",
        display_name="Repo Test",
    )


async def test_create_and_get_by_hash(db: AsyncSession, test_user: User) -> None:
    raw = generate_refresh_token_str()
    token_hash = hash_token(raw)
    expires = datetime.now(timezone.utc) + timedelta(days=1)

    created = await refresh_token_repo.create(db, user_id=test_user.id, token_hash=token_hash, expires_at=expires)
    assert created.token_hash == token_hash

    fetched = await refresh_token_repo.get_by_hash(db, token_hash)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.revoked_at is None


async def test_get_by_hash_returns_none_for_missing(db: AsyncSession) -> None:
    result = await refresh_token_repo.get_by_hash(db, "nonexistent_hash")
    assert result is None


async def test_revoke(db: AsyncSession, test_user: User) -> None:
    raw = generate_refresh_token_str()
    token_hash = hash_token(raw)
    expires = datetime.now(timezone.utc) + timedelta(days=1)
    token = await refresh_token_repo.create(db, user_id=test_user.id, token_hash=token_hash, expires_at=expires)

    await refresh_token_repo.revoke(db, token)

    fetched = await refresh_token_repo.get_by_hash(db, token_hash)
    assert fetched is not None
    assert fetched.revoked_at is not None


async def test_revoke_all_for_user(db: AsyncSession, test_user: User) -> None:
    expires = datetime.now(timezone.utc) + timedelta(days=1)
    for _ in range(3):
        raw = generate_refresh_token_str()
        await refresh_token_repo.create(db, user_id=test_user.id, token_hash=hash_token(raw), expires_at=expires)

    await refresh_token_repo.revoke_all_for_user(db, test_user.id)

    # Create another user's token to ensure we don't revoke across users
    other_user = await user_repo.create(
        db,
        email="999000002@cc.ncu.edu.tw",
        hashed_password="hashed",
        display_name="Other",
    )
    raw = generate_refresh_token_str()
    other_token_hash = hash_token(raw)
    await refresh_token_repo.create(db, user_id=other_user.id, token_hash=other_token_hash, expires_at=expires)

    other_fetched = await refresh_token_repo.get_by_hash(db, other_token_hash)
    assert other_fetched is not None
    assert other_fetched.revoked_at is None
```

- [ ] **Step 2: Run to confirm tests fail**

```bash
cd backend && python -m pytest tests/test_refresh_token_repo.py -v -k "not model_has_expected"
```

Expected: `ImportError` — `refresh_token_repo` does not exist yet.

- [ ] **Step 3: Create `backend/app/repositories/refresh_token_repo.py`**

```python
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    async def create(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshToken:
        token = RefreshToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        db.add(token)
        await db.flush()
        await db.refresh(token)
        return token

    async def get_by_hash(self, db: AsyncSession, token_hash: str) -> RefreshToken | None:
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        return result.scalars().first()

    async def revoke(self, db: AsyncSession, token: RefreshToken) -> None:
        token.revoked_at = datetime.now(timezone.utc)
        await db.flush()

    async def revoke_all_for_user(self, db: AsyncSession, user_id: uuid.UUID) -> None:
        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=datetime.now(timezone.utc))
        )
        await db.flush()


refresh_token_repo = RefreshTokenRepository()
```

- [ ] **Step 4: Run repository tests**

```bash
cd backend && python -m pytest tests/test_refresh_token_repo.py -v
```

Expected: All tests `PASSED`.

- [ ] **Step 5: Commit**

```bash
git add backend/app/repositories/refresh_token_repo.py backend/tests/test_refresh_token_repo.py
git commit -m "feat(auth): add RefreshTokenRepository with create, get_by_hash, revoke, revoke_all_for_user"
```

---

## Task 4: Update Auth Schemas

**Files:**
- Modify: `backend/app/schemas/auth.py`

`TokenResponse` is replaced. Endpoints now return `UserOut` directly. `LoginRequest` removes `remember_me`'s effect on access token (still kept to control refresh token lifetime).

- [ ] **Step 1: Replace `backend/app/schemas/auth.py`**

```python
import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

_NCU_EMAIL_RE = re.compile(r"^[0-9]+@cc\.ncu\.edu\.tw$")


class RegisterRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    email: str
    password: str
    display_name: str = Field(alias="displayName")

    @field_validator("email")
    @classmethod
    def must_be_ncu_email(cls, v: str) -> str:
        if not _NCU_EMAIL_RE.match(v):
            raise ValueError("必須是 NCU 學生信箱（學號@cc.ncu.edu.tw）")
        return v.lower()


class LoginRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    email: EmailStr
    password: str
    remember_me: bool = Field(alias="rememberMe", default=False)


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class MessageResponse(BaseModel):
    message: str


class UserOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: str
    email: str
    display_name: str = Field(alias="displayName")
    is_active: bool = Field(alias="isActive")
    email_verified: bool = Field(alias="emailVerified")
```

Note: `TokenResponse` is completely removed. Endpoints that previously returned `TokenResponse` now return `UserOut`.

- [ ] **Step 2: Run the existing auth schema tests to ensure they still pass**

```bash
cd backend && python -m pytest tests/test_auth_schemas.py -v
```

Expected: All pass (the schema tests test `RegisterRequest`, `LoginRequest` etc., which are unchanged).

- [ ] **Step 3: Commit**

```bash
git add backend/app/schemas/auth.py
git commit -m "feat(auth): remove TokenResponse schema, endpoints return UserOut"
```

---

## Task 5: Update Auth Service

**Files:**
- Modify: `backend/app/services/auth_service.py`

The service introduces an internal `AuthTokens` dataclass. Cookie-setting is the endpoint's responsibility — the service returns `AuthTokens` containing all needed values. `remember_me` now controls refresh token lifetime only.

- [ ] **Step 1: Update `backend/app/services/auth_service.py`**

Full replacement:

```python
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
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="無效的驗證連結")
        if record.used_at is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="驗證連結已使用過")
        if datetime.now(timezone.utc) > record.expires_at:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="驗證連結已過期")

        user = await user_repo.get_by_id(db, record.user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="使用者不存在")

        await email_verification_token_repo.mark_used(db, record)

        if not user.email_verified:
            user.email_verified = True
            await db.flush()

        return await self._issue_tokens(db, user)

    async def login(self, db: AsyncSession, req: LoginRequest) -> AuthTokens:
        user = await user_repo.get_by_email(db, req.email)
        if not user or not verify_password(req.password, user.hashed_password):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
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
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token reuse detected")

        if datetime.now(timezone.utc) > record.expires_at:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token expired")

        user = await user_repo.get_by_id(db, record.user_id)
        if user is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")

        # Rotate: revoke old token, issue new one
        await refresh_token_repo.revoke(db, record)

        # Preserve remember_me semantics: if old token had 30-day expiry, keep it
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
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/services/auth_service.py
git commit -m "feat(auth): update AuthService to issue refresh tokens and rotate on /refresh"
```

---

## Task 6: Update Auth Dependency (Cookie-Based)

**Files:**
- Modify: `backend/app/deps/auth.py`

Replace `HTTPBearer` with `Cookie(...)`. FastAPI reads the `access_token` cookie automatically.

- [ ] **Step 1: Replace `backend/app/deps/auth.py`**

```python
from uuid import UUID

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.deps import get_db
from app.models.user import User
from app.repositories.user_repo import user_repo


async def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    if access_token is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    try:
        user_id = UUID(decode_access_token(access_token))
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    user = await user_repo.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    return user


async def get_optional_user(
    access_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    if access_token is None:
        return None
    try:
        user_id = UUID(decode_access_token(access_token))
        return await user_repo.get_by_id(db, user_id)
    except Exception:
        return None
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/deps/auth.py
git commit -m "feat(auth): read access_token from Cookie instead of Authorization header"
```

---

## Task 7: Update Auth Endpoints + Add /refresh and /logout

**Files:**
- Modify: `backend/app/api/v1/endpoints/auth.py`

Endpoints set/clear cookies via the injected `Response`. The cookie helper function lives here.

- [ ] **Step 1: Replace `backend/app/api/v1/endpoints/auth.py`**

```python
from fastapi import APIRouter, Cookie, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
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


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/api/v1/auth")


@router.post("/register", response_model=MessageResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.register(db, req)


@router.get("/verify-email", response_model=UserOut)
async def verify_email(
    response: Response,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    tokens = await auth_service.verify_email(db, token)
    _set_auth_cookies(response, tokens)
    return tokens.user


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(
    req: ResendVerificationRequest, db: AsyncSession = Depends(get_db)
):
    return await auth_service.resend_verification(db, req)


@router.post("/login", response_model=UserOut)
async def login(req: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
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
        from fastapi import HTTPException, status
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "No refresh token")
    tokens = await auth_service.refresh(db, refresh_token)
    _set_auth_cookies(response, tokens)
    return tokens.user


@router.post("/logout", response_model=MessageResponse)
async def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    await auth_service.logout(db, refresh_token)
    _clear_auth_cookies(response)
    return MessageResponse(message="已登出")


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
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/api/v1/endpoints/auth.py
git commit -m "feat(auth): endpoints set HttpOnly cookies, add /refresh and /logout"
```

---

## Task 8: Update Backend Tests

**Files:**
- Modify: `backend/tests/test_auth.py`

Tests now check cookies instead of `accessToken` in body, and use cookie-based `/me`.  
httpx `AsyncClient` preserves cookies between requests automatically.

- [ ] **Step 1: Replace `backend/tests/test_auth.py`**

```python
from unittest.mock import patch

from httpx import AsyncClient


# ── Register ──────────────────────────────────────────────────────────────


async def test_register_invalid_email(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "student@gmail.com", "password": "pw", "displayName": "T"},
    )
    assert resp.status_code == 422


async def test_register_non_numeric_id(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "abc@cc.ncu.edu.tw", "password": "pw", "displayName": "T"},
    )
    assert resp.status_code == 422


async def test_register_success(client: AsyncClient) -> None:
    with patch("app.services.auth_service.send_verification_email", return_value=True):
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "109999001@cc.ncu.edu.tw",
                "password": "secret123",
                "displayName": "Test User",
            },
        )
    assert resp.status_code == 200
    assert resp.json()["message"] == "驗證信已寄出，請確認您的 NCU 學生信箱"


async def test_register_duplicate(client: AsyncClient) -> None:
    with patch("app.services.auth_service.send_verification_email", return_value=True):
        await client.post(
            "/api/v1/auth/register",
            json={"email": "109999010@cc.ncu.edu.tw", "password": "pw", "displayName": "T"},
        )
        resp = await client.post(
            "/api/v1/auth/register",
            json={"email": "109999010@cc.ncu.edu.tw", "password": "pw2", "displayName": "T2"},
        )
    assert resp.status_code == 409


async def test_register_ses_failure(client: AsyncClient) -> None:
    with patch("app.services.auth_service.send_verification_email", return_value=False):
        resp = await client.post(
            "/api/v1/auth/register",
            json={"email": "109999011@cc.ncu.edu.tw", "password": "pw", "displayName": "T"},
        )
    assert resp.status_code == 503


# ── Verify email ───────────────────────────────────────────────────────────


async def test_verify_email_invalid_token(client: AsyncClient) -> None:
    resp = await client.get(
        "/api/v1/auth/verify-email",
        params={"token": "00000000-0000-0000-0000-000000000000"},
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "無效的驗證連結"


async def test_verify_email_full_flow(client: AsyncClient) -> None:
    """Register → capture token → verify → cookies are set, user returned."""
    captured: dict = {}

    def capture(email, token):
        captured["token"] = token
        return True

    with patch("app.services.auth_service.send_verification_email", side_effect=capture):
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "109999020@cc.ncu.edu.tw",
                "password": "mypassword",
                "displayName": "User20",
            },
        )

    assert "token" in captured

    resp = await client.get(
        "/api/v1/auth/verify-email", params={"token": captured["token"]}
    )
    assert resp.status_code == 200
    data = resp.json()
    # No accessToken in body anymore — it's in the cookie
    assert "accessToken" not in data
    assert data["email"] == "109999020@cc.ncu.edu.tw"
    assert data["emailVerified"] is True
    # Cookies are set
    assert "access_token" in resp.cookies
    assert "refresh_token" in resp.cookies


async def test_verify_email_token_reuse(client: AsyncClient) -> None:
    captured: dict = {}

    def capture(email, token):
        captured["token"] = token
        return True

    with patch("app.services.auth_service.send_verification_email", side_effect=capture):
        await client.post(
            "/api/v1/auth/register",
            json={"email": "109999021@cc.ncu.edu.tw", "password": "pw", "displayName": "U21"},
        )

    token = captured["token"]
    await client.get("/api/v1/auth/verify-email", params={"token": token})
    resp = await client.get("/api/v1/auth/verify-email", params={"token": token})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "驗證連結已使用過"


# ── Login ──────────────────────────────────────────────────────────────────


async def test_login_before_verification_returns_403(client: AsyncClient) -> None:
    with patch("app.services.auth_service.send_verification_email", return_value=True):
        await client.post(
            "/api/v1/auth/register",
            json={"email": "109999030@cc.ncu.edu.tw", "password": "pw", "displayName": "U30"},
        )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "109999030@cc.ncu.edu.tw", "password": "pw"},
    )
    assert resp.status_code == 403
    assert resp.json()["detail"] == "請先驗證您的電子信箱"


async def test_login_after_verification_succeeds(client: AsyncClient) -> None:
    captured: dict = {}

    def capture(email, token):
        captured["token"] = token
        return True

    with patch("app.services.auth_service.send_verification_email", side_effect=capture):
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "109999031@cc.ncu.edu.tw",
                "password": "mypassword",
                "displayName": "U31",
            },
        )

    await client.get("/api/v1/auth/verify-email", params={"token": captured["token"]})

    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "109999031@cc.ncu.edu.tw", "password": "mypassword"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "accessToken" not in data  # token is now a cookie
    assert data["emailVerified"] is True
    assert "access_token" in resp.cookies
    assert "refresh_token" in resp.cookies


async def test_login_wrong_password(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "109999031@cc.ncu.edu.tw", "password": "wrongpassword"},
    )
    assert resp.status_code == 401


# ── /me ────────────────────────────────────────────────────────────────────


async def test_me_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


async def test_me_returns_current_user(client: AsyncClient) -> None:
    captured: dict = {}

    def capture(email, token):
        captured["token"] = token
        return True

    with patch("app.services.auth_service.send_verification_email", side_effect=capture):
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "109999040@cc.ncu.edu.tw",
                "password": "pw",
                "displayName": "U40",
            },
        )

    # Verify email → cookies are set on the client
    await client.get("/api/v1/auth/verify-email", params={"token": captured["token"]})

    # httpx AsyncClient auto-sends cookies set by the previous response
    me_resp = await client.get("/api/v1/auth/me")
    assert me_resp.status_code == 200
    me = me_resp.json()
    assert me["email"] == "109999040@cc.ncu.edu.tw"
    assert me["emailVerified"] is True


# ── /refresh ──────────────────────────────────────────────────────────────


async def test_refresh_issues_new_tokens(client: AsyncClient) -> None:
    captured: dict = {}

    def capture(email, token):
        captured["token"] = token
        return True

    with patch("app.services.auth_service.send_verification_email", side_effect=capture):
        await client.post(
            "/api/v1/auth/register",
            json={"email": "109999050@cc.ncu.edu.tw", "password": "pw", "displayName": "U50"},
        )

    await client.get("/api/v1/auth/verify-email", params={"token": captured["token"]})

    old_access = client.cookies.get("access_token")
    old_refresh = client.cookies.get("refresh_token")

    resp = await client.post("/api/v1/auth/refresh")
    assert resp.status_code == 200
    assert "access_token" in resp.cookies
    assert "refresh_token" in resp.cookies
    assert resp.cookies["access_token"] != old_access
    assert resp.cookies["refresh_token"] != old_refresh


async def test_refresh_reuse_revokes_all_tokens(client: AsyncClient) -> None:
    captured: dict = {}

    def capture(email, token):
        captured["token"] = token
        return True

    with patch("app.services.auth_service.send_verification_email", side_effect=capture):
        await client.post(
            "/api/v1/auth/register",
            json={"email": "109999051@cc.ncu.edu.tw", "password": "pw", "displayName": "U51"},
        )

    await client.get("/api/v1/auth/verify-email", params={"token": captured["token"]})
    original_refresh = client.cookies.get("refresh_token")

    # First refresh — ok
    await client.post("/api/v1/auth/refresh")

    # Manually set cookie back to the original (simulating token theft replay)
    client.cookies.set("refresh_token", original_refresh)
    resp = await client.post("/api/v1/auth/refresh")
    assert resp.status_code == 401


# ── /logout ───────────────────────────────────────────────────────────────


async def test_logout_clears_cookies(client: AsyncClient) -> None:
    captured: dict = {}

    def capture(email, token):
        captured["token"] = token
        return True

    with patch("app.services.auth_service.send_verification_email", side_effect=capture):
        await client.post(
            "/api/v1/auth/register",
            json={"email": "109999060@cc.ncu.edu.tw", "password": "pw", "displayName": "U60"},
        )

    await client.get("/api/v1/auth/verify-email", params={"token": captured["token"]})

    resp = await client.post("/api/v1/auth/logout")
    assert resp.status_code == 200
    assert resp.json()["message"] == "已登出"

    # After logout, /me should return 401
    me_resp = await client.get("/api/v1/auth/me")
    assert me_resp.status_code == 401
```

- [ ] **Step 2: Run the full backend test suite**

```bash
cd backend && python -m pytest tests/ -v
```

Expected: All tests pass. Pay special attention to `test_auth.py`, `test_auth_service.py`, `test_refresh_token_repo.py`, `test_security.py`.

If `test_auth_service.py` fails because it calls `_build_token_response` (which is removed), update it to use the new `_build_user_out` method or just delete those specific unit tests — the service is now integration-tested via `test_auth.py`.

- [ ] **Step 3: Commit**

```bash
git add backend/tests/test_auth.py
git commit -m "test(auth): update tests for cookie-based auth, add refresh/logout flow tests"
```

---

## Task 9: Frontend — API Client

**Files:**
- Modify: `frontend/src/api/client.ts`

Remove `token` option from `RequestOptions`. Add `credentials: 'include'`. On 401, silently call `/api/v1/auth/refresh` once and retry — if refresh fails, logout and redirect.

- [ ] **Step 1: Replace `frontend/src/api/client.ts`**

```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.trim() || ''

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export function hasBackendApi(): boolean {
  return API_BASE_URL.length > 0
}

export function getDataSourceLabel(): 'API' {
  return 'API'
}

async function doFetch(path: string, options: RequestInit): Promise<Response> {
  return fetch(`${API_BASE_URL}${path}`, {
    ...options,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> | undefined),
    },
  })
}

export async function request<T>(path: string, options: RequestInit = {}, _isRetry = false): Promise<T> {
  if (!hasBackendApi()) {
    throw new ApiError('Backend API is not configured. Please set VITE_API_BASE_URL.', 500)
  }

  const response = await doFetch(path, options)

  if (response.status === 401 && !_isRetry && path !== '/api/v1/auth/refresh') {
    try {
      await doFetch('/api/v1/auth/refresh', { method: 'POST' })
      return request<T>(path, options, true)
    }
    catch {
      const { useAuthStore } = await import('@/stores/useAuthStore')
      useAuthStore().logout()
      const { default: router } = await import('@/router')
      router.push({ name: 'login' })
      throw new ApiError('Session expired', 401)
    }
  }

  if (!response.ok) {
    if (response.status === 401) {
      const { useAuthStore } = await import('@/stores/useAuthStore')
      useAuthStore().logout()
      const { default: router } = await import('@/router')
      router.push({ name: 'login' })
      throw new ApiError('Session expired', 401)
    }
    let message = `Request failed with status ${response.status}`
    try {
      const data = await response.json() as { detail?: string }
      if (data.detail) {
        message = data.detail
      }
    }
    catch {
      // ignore json parse errors
    }
    throw new ApiError(message, response.status)
  }

  if (response.status === 204) {
    return undefined as T
  }
  return await response.json() as T
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/api/client.ts
git commit -m "feat(auth): use credentials:include, remove Authorization header, add silent refresh on 401"
```

---

## Task 10: Frontend — Auth API + Auth Store

**Files:**
- Modify: `frontend/src/api/auth.ts`
- Modify: `frontend/src/stores/useAuthStore.ts`

No more `accessToken` in API responses. No more `localStorage`. The store only tracks `user` and loading state.

- [ ] **Step 1: Replace `frontend/src/api/auth.ts`**

```typescript
import { request } from './client'

export interface AuthUser {
  id: string
  email: string
  displayName: string
  isActive: boolean
  emailVerified: boolean
}

export interface MessageResponse {
  message: string
}

export interface LoginPayload {
  email: string
  password: string
  rememberMe?: boolean
}

export interface RegisterPayload {
  email: string
  password: string
  displayName: string
}

export async function login(payload: LoginPayload): Promise<AuthUser> {
  return await request<AuthUser>('/api/v1/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function register(payload: RegisterPayload): Promise<MessageResponse> {
  return await request<MessageResponse>('/api/v1/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function resendVerification(email: string): Promise<MessageResponse> {
  return await request<MessageResponse>('/api/v1/auth/resend-verification', {
    method: 'POST',
    body: JSON.stringify({ email }),
  })
}

export async function getMe(): Promise<AuthUser> {
  return await request<AuthUser>('/api/v1/auth/me')
}

export async function logoutApi(): Promise<void> {
  await request<MessageResponse>('/api/v1/auth/logout', { method: 'POST' })
}
```

- [ ] **Step 2: Replace `frontend/src/stores/useAuthStore.ts`**

```typescript
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { getMe, login, logoutApi, register } from '@/api/auth'

interface AuthUser {
  id: string
  email: string
  displayName: string
  isActive: boolean
  emailVerified: boolean
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<AuthUser | null>(null)
  const isLoading = ref(false)

  const isLoggedIn = computed(() => user.value !== null)
  const displayName = computed(() => user.value?.displayName ?? '')

  async function loginWithPassword(email: string, password: string, rememberMe = false): Promise<void> {
    isLoading.value = true
    try {
      user.value = await login({ email, password, rememberMe })
    }
    finally {
      isLoading.value = false
    }
  }

  async function registerWithPassword(
    email: string,
    password: string,
    displayNameValue: string,
  ): Promise<void> {
    isLoading.value = true
    try {
      await register({ email, password, displayName: displayNameValue })
    }
    finally {
      isLoading.value = false
    }
  }

  async function hydrateFromStorage(): Promise<void> {
    try {
      user.value = await getMe()
    }
    catch {
      user.value = null
    }
  }

  async function logout(): Promise<void> {
    try {
      await logoutApi()
    }
    catch {
      // ignore — clear local state regardless
    }
    user.value = null
  }

  return {
    displayName,
    hydrateFromStorage,
    isLoading,
    isLoggedIn,
    loginWithPassword,
    logout,
    registerWithPassword,
    user,
  }
})
```

Note: `token` ref and `localStorage` are completely gone. `logout()` is now async — it calls the backend to revoke the refresh token before clearing state.

- [ ] **Step 3: Search for any component that calls `logout()` without `await`**

```bash
grep -rn "\.logout()" frontend/src --include="*.vue" --include="*.ts"
```

For each match, confirm it either `await`s the call or the lack of `await` is intentional (e.g. fire-and-forget in a navigation handler).

- [ ] **Step 4: Search for any code that reads `authStore.token`**

```bash
grep -rn "authStore\.token\|\.token\.value\|store\.token" frontend/src --include="*.vue" --include="*.ts"
```

Remove any `token` references found (they no longer exist on the store).

- [ ] **Step 5: Search for any remaining `getMe(token)` calls with a token argument**

```bash
grep -rn "getMe(" frontend/src --include="*.ts"
```

`getMe` no longer takes a `token` argument. Fix any calls that still pass one.

- [ ] **Step 6: Run frontend tests**

```bash
cd frontend && pnpm test run
```

Expected: All tests pass. Fix any that reference `token` or `localStorage` from the store.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/api/auth.ts frontend/src/stores/useAuthStore.ts
git commit -m "feat(auth): remove localStorage token from store, cookies auto-sent by browser"
```

---

## Task 11: Frontend — Router Guard

**Files:**
- Modify: `frontend/src/router/index.ts`

Add a `beforeEach` navigation guard. Protected routes require `isLoggedIn`. The guard runs after `hydrateFromStorage` has completed (called in `main.ts` before mounting).

However, because `hydrateFromStorage` is async and `main.ts` does not `await` it, the guard needs to handle the case where hydration is still in progress. The cleanest approach: mark routes as `requiresAuth` in their `meta`, and redirect to `/login` if `!isLoggedIn`.

All existing routes except `login`, `register`, `about`, and `not-found` require auth.

- [ ] **Step 1: Replace `frontend/src/router/index.ts`**

```typescript
import type { RouteRecordRaw } from 'vue-router'
import { createRouter, createWebHistory } from 'vue-router'
import CourseDetailView from '../views/CourseDetailView.vue'
import HomeView from '../views/HomeView.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { requiresAuth: true },
  },
  {
    path: '/course/:id',
    name: 'course-detail',
    component: CourseDetailView,
    props: true,
    meta: { requiresAuth: true },
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/RegisterView.vue'),
  },
  {
    path: '/my-reviews',
    name: 'my-reviews',
    component: () => import('../views/MyReviewsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/my-level',
    name: 'my-level',
    component: () => import('../views/PointsShopView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/about',
    name: 'about',
    component: () => import('../views/AboutView.vue'),
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('../views/NotFoundView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0 }
  },
})

router.beforeEach(async (to) => {
  if (!to.meta.requiresAuth) {
    return true
  }

  const { useAuthStore } = await import('@/stores/useAuthStore')
  const auth = useAuthStore()

  if (!auth.isLoggedIn) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  return true
})

export default router
```

- [ ] **Step 2: Update `frontend/src/main.ts` to await hydration before mounting**

The router guard fires on navigation. If the app mounts and immediately navigates, hydration may not be complete and `isLoggedIn` returns false incorrectly. Await hydration before mounting:

```typescript
import { createPinia } from 'pinia'
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/useAuthStore'
import './style.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia).use(router)

const auth = useAuthStore()
auth.hydrateFromStorage().finally(() => {
  app.mount('#app')
})
```

This ensures the user's auth state is known before the first route is evaluated.

- [ ] **Step 3: Run frontend tests**

```bash
cd frontend && pnpm test run
```

Expected: All pass. Update `router/index.spec.ts` if it asserts specific navigation behavior without auth.

- [ ] **Step 4: Verify the login redirect works end-to-end**

Start the dev server and visit `http://localhost:5173/my-reviews` while not logged in. You should be redirected to `/login?redirect=%2Fmy-reviews`.

```bash
cd frontend && pnpm dev
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/router/index.ts frontend/src/main.ts
git commit -m "feat(auth): add router guard for requiresAuth routes, await hydration before mount"
```

---

## Task 12: Update Remaining Frontend Auth References

**Files:**
- Search all `.vue` and `.ts` files in `frontend/src`

Some components may call `authStore.token` directly or pass `token` to API functions. This task cleans those up.

- [ ] **Step 1: Search for stale token references**

```bash
grep -rn "token" frontend/src --include="*.vue" --include="*.ts" | grep -v "node_modules" | grep -v ".spec." | grep -v "refreshToken\|access_token\|refresh_token\|emit.*token\|tokenType"
```

- [ ] **Step 2: For each match, remove the `token` prop/parameter or update the call**

Common patterns to fix:
- `api.someCall(authStore.token)` → `api.someCall()` (token now sent as cookie)
- `headers: { Authorization: ... }` inside any fetch call → remove (client handles this)

- [ ] **Step 3: Run full frontend test suite**

```bash
cd frontend && pnpm test run
```

Expected: All pass.

- [ ] **Step 4: Commit**

```bash
git add frontend/src
git commit -m "fix(auth): remove all stale token references from frontend components"
```

---

## Self-Review Checklist

### Spec Coverage

| Requirement | Task |
|-------------|------|
| Access token in HttpOnly cookie | Task 7 (`_set_auth_cookies`) |
| Refresh token hashed in DB | Task 1 (model), Task 3 (repo), Task 5 (service `_issue_tokens`) |
| Refresh token rotation | Task 5 (`auth_service.refresh` revokes old + issues new) |
| Reuse detection → revoke all | Task 5 (`refresh` calls `revoke_all_for_user`) |
| Short-lived access token (15 min) | Task 2 (`config.py`) |
| `remember_me` → longer refresh token | Task 5 + Task 7 |
| Logout revokes refresh token | Task 5 (`auth_service.logout`) + Task 7 (`/logout` endpoint) |
| Frontend: no localStorage | Task 10 |
| Frontend: cookies auto-sent | Task 9 (`credentials: 'include'`) |
| Frontend: silent refresh on 401 | Task 9 (`client.ts` retry logic) |
| Frontend: route guard | Task 11 |
| Backend tests updated | Task 8 |

### Critical Notes for Implementors

1. **`remember_me` field removed from `create_access_token`** — if any other code calls `create_access_token(sub, remember_me=True)`, it will break. Search with: `grep -rn "create_access_token" backend/`

2. **`TokenResponse` schema removed** — if any other file imports it (e.g. `test_auth_schemas.py`), update those imports.

3. **`logout()` in store is now async** — components that call `authStore.logout()` inside `@click` handlers should either `await` it or use `.catch()`.

4. **`hydrateFromStorage` makes a network call on every page load** — if the server is down, the app will fail silently (user appears logged out). This is acceptable for a dev/student project.

5. **Cookie `Path=/api/v1/auth` for refresh token** — the browser will only send this cookie to `/api/v1/auth/...` URLs. This is intentional. The frontend `client.ts` refresh call must use the full path `/api/v1/auth/refresh`.

6. **Test DB for `test_refresh_token_repo.py`** — uses the same `conftest.py` fixtures. Ensure the `refresh_tokens` table is created in the test DB by running `alembic upgrade head` on the test DB, or (since tests use `Base.metadata.create_all`) just import the model.
