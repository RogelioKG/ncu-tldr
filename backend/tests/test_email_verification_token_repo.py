import uuid
from datetime import datetime, timezone

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.email_verification_token_repo import email_verification_token_repo


@pytest_asyncio.fixture
async def test_user(db: AsyncSession) -> User:
    from app.core.security import hash_password

    user = User(
        email=f"{uuid.uuid4().hex[:8]}@cc.ncu.edu.tw",
        hashed_password=hash_password("pw"),
        display_name="testuser",
        email_verified=False,
    )
    db.add(user)
    await db.flush()
    return user


async def test_create_token(db: AsyncSession, test_user: User) -> None:
    token_str = str(uuid.uuid4())
    record = await email_verification_token_repo.create(
        db, user_id=test_user.id, token=token_str
    )
    assert record.token == token_str
    assert record.user_id == test_user.id
    assert record.used_at is None
    assert record.expires_at > datetime.now(timezone.utc)


async def test_get_by_token_found(db: AsyncSession, test_user: User) -> None:
    token_str = str(uuid.uuid4())
    await email_verification_token_repo.create(
        db, user_id=test_user.id, token=token_str
    )
    result = await email_verification_token_repo.get_by_token(db, token_str)
    assert result is not None
    assert result.token == token_str


async def test_get_by_token_not_found(db: AsyncSession) -> None:
    result = await email_verification_token_repo.get_by_token(db, "nonexistent")
    assert result is None


async def test_mark_used(db: AsyncSession, test_user: User) -> None:
    token_str = str(uuid.uuid4())
    record = await email_verification_token_repo.create(
        db, user_id=test_user.id, token=token_str
    )
    await email_verification_token_repo.mark_used(db, record)
    assert record.used_at is not None
