from app.models.refresh_token import RefreshToken


def test_refresh_token_model_has_expected_columns() -> None:
    cols = {c.key for c in RefreshToken.__table__.columns}
    assert cols == {
        "id",
        "user_id",
        "token_hash",
        "expires_at",
        "revoked_at",
        "created_at",
    }
