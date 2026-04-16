import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import app.models  # noqa: F401 — register all ORM models with Base
from app.db.base import Base
from app.db.deps import get_db
from main import app

TEST_DATABASE_URL = (
    "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/ncu_tldr_test"
)

_ENUM_SETUP_SQL = """
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'course_type_enum') THEN
        CREATE TYPE course_type_enum AS ENUM ('REQUIRED', 'ELECTIVE');
    END IF;
END$$;
"""


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def engine():
    """Create tables once per test session and tear them down afterward."""
    eng = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with eng.begin() as conn:
        await conn.execute(text(_ENUM_SETUP_SQL))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture
async def db(engine):
    """Raw AsyncSession for repository-level tests — always rolls back after each test."""
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(engine) -> AsyncClient:
    """Each test gets fresh DB sessions (one per request) with auto-commit on success."""
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
    app.dependency_overrides.clear()
