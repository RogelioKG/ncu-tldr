import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_comments_empty(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/courses/1/comments")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_list_comments_invalid_course_returns_empty(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/courses/99999/comments")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_comment_unauthenticated(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/courses/1/comments",
        json={"content": "Nice course"},
    )
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_create_comment_requires_auth(client: AsyncClient) -> None:
    """Unauthenticated requests are rejected before any DB work."""
    resp = await client.post(
        "/api/v1/courses/1/comments",
        json={"content": "Hello world"},
    )
    assert resp.status_code in (401, 403)
