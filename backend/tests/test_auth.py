import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "demo@cc.ncu.edu.tw", "password": "password123"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["tokenType"] == "bearer"
    assert payload["accessToken"].startswith("mock-")


@pytest.mark.asyncio
async def test_login_invalid(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "demo@cc.ncu.edu.tw", "password": "wrong-password"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_register_and_get_me(client: AsyncClient) -> None:
    register = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "new-user@cc.ncu.edu.tw",
            "password": "new-password-123",
            "displayName": "New User",
        },
    )
    assert register.status_code == 200
    token = register.json()["accessToken"]

    me = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me.status_code == 200
    assert me.json()["email"] == "new-user@cc.ncu.edu.tw"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient) -> None:
    first = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "dup-user@cc.ncu.edu.tw",
            "password": "new-password-123",
            "displayName": "Dup User",
        },
    )
    assert first.status_code == 200

    second = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "dup-user@cc.ncu.edu.tw",
            "password": "new-password-123",
            "displayName": "Dup User",
        },
    )
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_get_me_with_invalid_token(client: AsyncClient) -> None:
    me = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer bad-token"},
    )
    assert me.status_code == 401
