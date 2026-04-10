import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_courses_empty(client: AsyncClient) -> None:
    response = await client.get("/api/v1/courses")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)


@pytest.mark.asyncio
async def test_get_course_pairs(client: AsyncClient) -> None:
    response = await client.get("/api/v1/courses/pairs")
    assert response.status_code == 200
    payload = response.json()
    assert "pairs" in payload
    assert isinstance(payload["pairs"], list)


@pytest.mark.asyncio
async def test_get_course_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/v1/courses/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_courses_with_query(client: AsyncClient) -> None:
    response = await client.get("/api/v1/courses", params={"q": "nonexistent_xyz"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
