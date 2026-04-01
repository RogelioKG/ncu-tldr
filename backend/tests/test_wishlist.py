import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_wishlist(client: AsyncClient) -> None:
    response = await client.get("/api/v1/wishlist")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) >= 1
    assert "voteCount" in payload[0]


@pytest.mark.asyncio
async def test_create_wish_and_vote_up(client: AsyncClient) -> None:
    created = await client.post(
        "/api/v1/wishlist",
        json={"name": "新課程", "teacher": "新老師"},
    )
    assert created.status_code == 201
    assert created.json()["voteCount"] == 1

    voted = await client.post(
        "/api/v1/wishlist",
        json={"name": "新課程", "teacher": "新老師"},
    )
    assert voted.status_code == 201
    assert voted.json()["voteCount"] == 2


@pytest.mark.asyncio
async def test_delete_wish(client: AsyncClient) -> None:
    created = await client.post(
        "/api/v1/wishlist",
        json={"name": "待刪除課程", "teacher": "老師"},
    )
    wish_id = created.json()["id"]

    deleted = await client.delete(f"/api/v1/wishlist/{wish_id}")
    assert deleted.status_code == 204


@pytest.mark.asyncio
async def test_delete_missing_wish(client: AsyncClient) -> None:
    response = await client.delete("/api/v1/wishlist/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_wishlist_sorted_by_vote_count(client: AsyncClient) -> None:
    await client.post("/api/v1/wishlist", json={"name": "A課程", "teacher": "A老師"})
    await client.post("/api/v1/wishlist", json={"name": "A課程", "teacher": "A老師"})
    await client.post("/api/v1/wishlist", json={"name": "B課程", "teacher": "B老師"})

    response = await client.get("/api/v1/wishlist")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) >= 2
    assert payload[0]["voteCount"] >= payload[1]["voteCount"]
