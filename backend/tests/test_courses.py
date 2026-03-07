import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_courses(client: AsyncClient) -> None:
    response = await client.get("/api/courses")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) >= 3


@pytest.mark.asyncio
async def test_get_courses_with_search(client: AsyncClient) -> None:
    response = await client.get("/api/courses", params={"q": "演算法"})
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["name"] == "演算法"


@pytest.mark.asyncio
async def test_get_course_by_id(client: AsyncClient) -> None:
    response = await client.get("/api/courses/1")
    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == 1
    assert "comments" in payload


@pytest.mark.asyncio
async def test_get_course_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/courses/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_courses_with_sort(client: AsyncClient) -> None:
    response = await client.get("/api/courses", params={"sort": "reward:desc"})
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) >= 2
    assert payload[0]["ratings"]["reward"] >= payload[1]["ratings"]["reward"]
