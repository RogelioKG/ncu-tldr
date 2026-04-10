import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test_register@example.com",
            "password": "password123",
            "displayName": "Test User",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "accessToken" in data
    assert data["tokenType"] == "bearer"
    assert data["user"]["email"] == "test_register@example.com"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient) -> None:
    payload = {
        "email": "dup_test@example.com",
        "password": "pass123",
        "displayName": "First User",
    }
    await client.post("/api/v1/auth/register", json=payload)
    resp = await client.post(
        "/api/v1/auth/register",
        json={**payload, "displayName": "Second User"},
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "login_test@example.com",
            "password": "mypassword",
            "displayName": "Login User",
        },
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "login_test@example.com", "password": "mypassword"},
    )
    assert resp.status_code == 200
    assert "accessToken" in resp.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrongpw_test@example.com",
            "password": "correctpassword",
            "displayName": "User",
        },
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrongpw_test@example.com", "password": "wrongpassword"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "ghost@example.com", "password": "anything"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_authenticated(client: AsyncClient) -> None:
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "me_test@example.com",
            "password": "pass123",
            "displayName": "Me User",
        },
    )
    assert reg.status_code == 201
    token = reg.json()["accessToken"]
    resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["email"] == "me_test@example.com"


@pytest.mark.asyncio
async def test_me_unauthenticated(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_me_invalid_token(client: AsyncClient) -> None:
    resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert resp.status_code == 401
