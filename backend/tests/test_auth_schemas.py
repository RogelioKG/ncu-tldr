import pytest
from pydantic import ValidationError

from app.schemas.auth import RegisterRequest


def test_valid_ncu_email():
    req = RegisterRequest(
        email="109999001@cc.ncu.edu.tw",
        password="secret",
        **{"displayName": "Test"},
    )
    assert req.email == "109999001@cc.ncu.edu.tw"


def test_invalid_gmail():
    with pytest.raises(ValidationError) as exc:
        RegisterRequest(email="student@gmail.com", password="x", **{"displayName": "T"})
    assert "NCU" in str(exc.value)


def test_invalid_non_numeric_id():
    with pytest.raises(ValidationError) as exc:
        RegisterRequest(email="abc@cc.ncu.edu.tw", password="x", **{"displayName": "T"})
    assert "NCU" in str(exc.value)


def test_invalid_wrong_domain():
    with pytest.raises(ValidationError) as exc:
        RegisterRequest(
            email="109999001@ncu.edu.tw", password="x", **{"displayName": "T"}
        )
    assert "NCU" in str(exc.value)


def test_uppercase_domain_rejected():
    """Regex is case-sensitive — uppercase domain does not match."""
    with pytest.raises(ValidationError):
        RegisterRequest(
            email="109999001@CC.NCU.EDU.TW", password="x", **{"displayName": "T"}
        )
