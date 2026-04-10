import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_wishlist_empty(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/wishlist")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_add_to_wishlist(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/wishlist",
        json={"name": "Machine Learning", "teacher": "Dr. Smith"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Machine Learning"
    assert data["teacher"] == "Dr. Smith"
    assert data["voteCount"] >= 1


@pytest.mark.asyncio
async def test_add_to_wishlist_twice_increments_vote(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/wishlist",
        json={"name": "Vote Increment Course", "teacher": "Teacher X"},
    )
    resp = await client.post(
        "/api/v1/wishlist",
        json={"name": "Vote Increment Course", "teacher": "Teacher X"},
    )
    assert resp.status_code == 201
    assert resp.json()["voteCount"] == 2


@pytest.mark.asyncio
async def test_add_to_wishlist_different_teacher_creates_new(client: AsyncClient) -> None:
    resp1 = await client.post(
        "/api/v1/wishlist",
        json={"name": "Data Science", "teacher": "Prof. A"},
    )
    resp2 = await client.post(
        "/api/v1/wishlist",
        json={"name": "Data Science", "teacher": "Prof. B"},
    )
    assert resp1.status_code == 201
    assert resp2.status_code == 201
    assert resp1.json()["id"] != resp2.json()["id"]


@pytest.mark.asyncio
async def test_delete_wishlist_not_found(client: AsyncClient) -> None:
    resp = await client.delete("/api/v1/wishlist/99999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_wishlist_success(client: AsyncClient) -> None:
    create_resp = await client.post(
        "/api/v1/wishlist",
        json={"name": "Course To Delete", "teacher": "Teacher Z"},
    )
    assert create_resp.status_code == 201
    wish_id = create_resp.json()["id"]

    del_resp = await client.delete(f"/api/v1/wishlist/{wish_id}")
    assert del_resp.status_code == 204

    # Verify it's gone
    list_resp = await client.get("/api/v1/wishlist")
    ids = [item["id"] for item in list_resp.json()]
    assert wish_id not in ids
