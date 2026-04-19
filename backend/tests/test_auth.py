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
    """Register → capture token → verify → cookies are set, user returned."""
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
    # No accessToken in body anymore — it's in the cookie
    assert "accessToken" not in data
    assert data["email"] == "109999020@cc.ncu.edu.tw"
    assert data["emailVerified"] is True
    # Cookies are set
    assert "access_token" in resp.cookies
    assert "refresh_token" in resp.cookies


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
    assert "accessToken" not in data  # token is now a cookie
    assert data["emailVerified"] is True
    assert "access_token" in resp.cookies
    assert "refresh_token" in resp.cookies


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

    # Verify email → cookies are set on the client automatically
    await client.get("/api/v1/auth/verify-email", params={"token": captured["token"]})

    # httpx AsyncClient auto-sends cookies set by the previous response
    me_resp = await client.get("/api/v1/auth/me")
    assert me_resp.status_code == 200
    me = me_resp.json()
    assert me["email"] == "109999040@cc.ncu.edu.tw"
    assert me["emailVerified"] is True


# ── /refresh ──────────────────────────────────────────────────────────────


async def test_refresh_issues_new_tokens(client: AsyncClient) -> None:
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
                "email": "109999050@cc.ncu.edu.tw",
                "password": "pw",
                "displayName": "U50",
            },
        )

    await client.get("/api/v1/auth/verify-email", params={"token": captured["token"]})

    old_refresh = client.cookies.get("refresh_token")

    resp = await client.post("/api/v1/auth/refresh")
    assert resp.status_code == 200
    assert "access_token" in resp.cookies
    assert "refresh_token" in resp.cookies
    # Refresh token is always a new random value after rotation
    assert resp.cookies["refresh_token"] != old_refresh


async def test_refresh_reuse_revokes_all_tokens(client: AsyncClient) -> None:
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
                "email": "109999051@cc.ncu.edu.tw",
                "password": "pw",
                "displayName": "U51",
            },
        )

    await client.get("/api/v1/auth/verify-email", params={"token": captured["token"]})
    original_refresh = client.cookies.get("refresh_token")

    # First refresh — ok
    await client.post("/api/v1/auth/refresh")

    # Manually set cookie back to the original (simulating token theft replay)
    client.cookies.set("refresh_token", original_refresh)
    resp = await client.post("/api/v1/auth/refresh")
    assert resp.status_code == 401


# ── /logout ───────────────────────────────────────────────────────────────


async def test_logout_clears_cookies(client: AsyncClient) -> None:
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
                "email": "109999060@cc.ncu.edu.tw",
                "password": "pw",
                "displayName": "U60",
            },
        )

    await client.get("/api/v1/auth/verify-email", params={"token": captured["token"]})

    resp = await client.post("/api/v1/auth/logout")
    assert resp.status_code == 200
    assert resp.json()["message"] == "已登出"

    # After logout, /me should return 401
    me_resp = await client.get("/api/v1/auth/me")
    assert me_resp.status_code == 401
