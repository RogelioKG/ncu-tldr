import hashlib

from app.core.security import generate_refresh_token_str, hash_token


def test_generate_refresh_token_str_is_urlsafe_64_chars() -> None:
    token = generate_refresh_token_str()
    assert len(token) == 64
    assert token.isascii()


def test_generate_refresh_token_str_is_unique() -> None:
    assert generate_refresh_token_str() != generate_refresh_token_str()


def test_hash_token_returns_sha256_hex() -> None:
    raw = "some-random-token-string"
    result = hash_token(raw)
    expected = hashlib.sha256(raw.encode()).hexdigest()
    assert result == expected
    assert len(result) == 64


def test_hash_token_is_deterministic() -> None:
    raw = generate_refresh_token_str()
    assert hash_token(raw) == hash_token(raw)
