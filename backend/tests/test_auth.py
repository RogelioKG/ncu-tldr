from unittest.mock import patch

from httpx import AsyncClient


# ── Register ──────────────────────────────────────────────────────────────


async def test_register_invalid_email(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "student@gmail.com", "password": "pw", "displayName": "T"},
    )
    assert resp.status_code == 422


async def test_register_non_numeric_id(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "abc@cc.ncu.edu.tw", "password": "pw", "displayName": "T"},
    )
    assert resp.status_code == 422


async def test_register_success(client: AsyncClient) -> None:
    with patch("app.services.auth_service.send_verification_email", return_value=True):
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "109999001@cc.ncu.edu.tw",
                "password": "secret123",
                "displayName": "Test User",
            },
        )
    assert resp.status_code == 200
    assert resp.json()["message"] == "驗證信已寄出，請確認您的 NCU 學生信箱"


async def test_register_duplicate(client: AsyncClient) -> None:
    with patch("app.services.auth_service.send_verification_email", return_value=True):
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "109999010@cc.ncu.edu.tw",
                "password": "pw",
                "displayName": "T",
            },
        )
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "109999010@cc.ncu.edu.tw",
                "password": "pw2",
                "displayName": "T2",
            },
        )
    assert resp.status_code == 409


async def test_register_ses_failure(client: AsyncClient) -> None:
    with patch("app.services.auth_service.send_verification_email", return_value=False):
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "109999011@cc.ncu.edu.tw",
                "password": "pw",
                "displayName": "T",
            },
        )
    assert resp.status_code == 503


# ── Verify email ───────────────────────────────────────────────────────────


async def test_verify_email_invalid_token(client: AsyncClient) -> None:
    resp = await client.get(
        "/api/v1/auth/verify-email",
        params={"token": "00000000-0000-0000-0000-000000000000"},
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "無效的驗證連結"


async def test_verify_email_full_flow(client: AsyncClient) -> None:
    """Register → capture token → verify → receive JWT."""
    captured: dict = {}

    def capture(email, token):
        captured["token"] = token
        return True

    with patch(
        "app.services.auth_service.send_verification_email", side_effect=capture
    ):
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "109999020@cc.ncu.edu.tw",
                "password": "mypassword",
                "displayName": "User20",
            },
        )

    assert "token" in captured

    resp = await client.get(
        "/api/v1/auth/verify-email", params={"token": captured["token"]}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "accessToken" in data
    assert data["tokenType"] == "bearer"
    assert data["user"]["email"] == "109999020@cc.ncu.edu.tw"
    assert data["user"]["emailVerified"] is True


async def test_verify_email_token_reuse(client: AsyncClient) -> None:
    captured: dict = {}

    def capture(email, token):
        captured["token"] = token
        return True

    with patch(
        "app.services.auth_service.send_verification_email", side_effect=capture
    ):
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "109999021@cc.ncu.edu.tw",
                "password": "pw",
                "displayName": "U21",
            },
        )

    token = captured["token"]
    await client.get("/api/v1/auth/verify-email", params={"token": token})
    resp = await client.get("/api/v1/auth/verify-email", params={"token": token})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "驗證連結已使用過"


# ── Login ──────────────────────────────────────────────────────────────────


async def test_login_before_verification_returns_403(client: AsyncClient) -> None:
    with patch("app.services.auth_service.send_verification_email", return_value=True):
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "109999030@cc.ncu.edu.tw",
                "password": "pw",
                "displayName": "U30",
            },
        )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "109999030@cc.ncu.edu.tw", "password": "pw"},
    )
    assert resp.status_code == 403
    assert resp.json()["detail"] == "請先驗證您的電子信箱"


async def test_login_after_verification_succeeds(client: AsyncClient) -> None:
    captured: dict = {}

    def capture(email, token):
        captured["token"] = token
        return True

    with patch(
        "app.services.auth_service.send_verification_email", side_effect=capture
    ):
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "109999031@cc.ncu.edu.tw",
                "password": "mypassword",
                "displayName": "U31",
            },
        )

    await client.get("/api/v1/auth/verify-email", params={"token": captured["token"]})

    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "109999031@cc.ncu.edu.tw", "password": "mypassword"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "accessToken" in data
    assert data["user"]["emailVerified"] is True


async def test_login_wrong_password(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "109999031@cc.ncu.edu.tw", "password": "wrongpassword"},
    )
    assert resp.status_code == 401


# ── /me ────────────────────────────────────────────────────────────────────


async def test_me_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


async def test_me_returns_current_user(client: AsyncClient) -> None:
    captured: dict = {}

    def capture(email, token):
        captured["token"] = token
        return True

    with patch(
        "app.services.auth_service.send_verification_email", side_effect=capture
    ):
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "109999040@cc.ncu.edu.tw",
                "password": "pw",
                "displayName": "U40",
            },
        )

    verify_resp = await client.get(
        "/api/v1/auth/verify-email", params={"token": captured["token"]}
    )
    access_token = verify_resp.json()["accessToken"]

    me_resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert me_resp.status_code == 200
    me = me_resp.json()
    assert me["email"] == "109999040@cc.ncu.edu.tw"
    assert me["emailVerified"] is True
