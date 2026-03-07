import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_reviews(client: AsyncClient) -> None:
    response = await client.get("/api/courses/1/reviews")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) >= 1


@pytest.mark.asyncio
async def test_create_review(client: AsyncClient) -> None:
    response = await client.post(
        "/api/courses/1/reviews",
        json={
            "user": "Tester",
            "title": "有收穫",
            "content": "內容扎實。",
            "ratings": {
                "reward": 5,
                "score": 4,
                "easiness": 3,
                "teacherStyle": 4,
            },
        },
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["user"] == "Tester"

    reviews_response = await client.get("/api/courses/1/reviews")
    assert reviews_response.status_code == 200
    assert len(reviews_response.json()) == 3


@pytest.mark.asyncio
async def test_create_review_course_not_found(client: AsyncClient) -> None:
    response = await client.post(
        "/api/courses/999/reviews",
        json={
            "user": "Tester",
            "title": "測試",
            "content": "測試內容",
            "ratings": {
                "reward": 5,
                "score": 4,
                "easiness": 3,
                "teacherStyle": 4,
            },
        },
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_review_validation_error(client: AsyncClient) -> None:
    response = await client.post(
        "/api/courses/1/reviews",
        json={
            "user": "Tester",
            "title": "",
            "content": "測試內容",
            "ratings": {
                "reward": 5,
                "score": 4,
                "easiness": 3,
                "teacherStyle": 4,
            },
        },
    )
    assert response.status_code == 422
