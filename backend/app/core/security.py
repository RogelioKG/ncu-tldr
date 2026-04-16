from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from app.config import get_settings

_settings = get_settings()
_SECRET_KEY: str = _settings.jwt_secret_key
_ALGORITHM = "HS256"
_ACCESS_TOKEN_EXPIRE_MINUTES = _settings.access_token_expire_minutes


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(sub: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": sub, "exp": expire}
    return jwt.encode(payload, _SECRET_KEY, algorithm=_ALGORITHM)


def decode_access_token(token: str) -> str:
    payload = jwt.decode(token, _SECRET_KEY, algorithms=[_ALGORITHM])
    return str(payload["sub"])
