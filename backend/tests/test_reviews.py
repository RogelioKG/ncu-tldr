import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_reviews_empty(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/courses/1/reviews")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_create_review_unauthenticated(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/courses/1/reviews",
        json={
            "content": "Great course",
            "ratings": {"gain": 4, "highScore": 3, "easiness": 5, "teacherStyle": 4},
        },
    )
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_create_review_requires_auth(client: AsyncClient) -> None:
    """Unauthenticated requests are rejected before any DB work."""
    resp = await client.post(
        "/api/v1/courses/1/reviews",
        json={
            "title": "Good",
            "content": "Test",
            "ratings": {"gain": 4, "highScore": 4, "easiness": 3, "teacherStyle": 5},
        },
    )
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_list_reviews_invalid_course_returns_empty(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/courses/99999/reviews")
    assert resp.status_code == 200
    assert resp.json() == []
