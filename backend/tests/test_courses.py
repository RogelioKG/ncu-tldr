import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_courses(client: AsyncClient) -> None:
    response = await client.get("/api/courses")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)


@pytest.mark.asyncio
async def test_get_course_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/courses/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_course_pairs(client: AsyncClient) -> None:
    response = await client.get("/api/courses/pairs")
    assert response.status_code == 200
    payload = response.json()
    assert "pairs" in payload
    assert isinstance(payload["pairs"], list)
