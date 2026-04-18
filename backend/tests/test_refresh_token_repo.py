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
    assert cols == {
        "id",
        "user_id",
        "token_hash",
        "expires_at",
        "revoked_at",
        "created_at",
    }


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

    created = await refresh_token_repo.create(
        db, user_id=test_user.id, token_hash=token_hash, expires_at=expires
    )
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
    token = await refresh_token_repo.create(
        db, user_id=test_user.id, token_hash=token_hash, expires_at=expires
    )

    await refresh_token_repo.revoke(db, token)

    fetched = await refresh_token_repo.get_by_hash(db, token_hash)
    assert fetched is not None
    assert fetched.revoked_at is not None


async def test_revoke_all_for_user(db: AsyncSession, test_user: User) -> None:
    expires = datetime.now(timezone.utc) + timedelta(days=1)
    for _ in range(3):
        raw = generate_refresh_token_str()
        await refresh_token_repo.create(
            db, user_id=test_user.id, token_hash=hash_token(raw), expires_at=expires
        )

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
    await refresh_token_repo.create(
        db, user_id=other_user.id, token_hash=other_token_hash, expires_at=expires
    )

    other_fetched = await refresh_token_repo.get_by_hash(db, other_token_hash)
    assert other_fetched is not None
    assert other_fetched.revoked_at is None
