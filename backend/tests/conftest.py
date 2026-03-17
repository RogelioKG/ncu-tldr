import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.services.mock_db import mock_db
from main import app


@pytest.fixture(autouse=True)
def reset_mock_db() -> None:
    mock_db.reset()


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
