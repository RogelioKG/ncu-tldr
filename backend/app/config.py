from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="allow",
        case_sensitive=False,
    )

    app_name: str = Field(default="NCU-TLDR Backend")
    app_version: str = Field(default="0.1.0")
    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173"],
    )

    x_sync_secret_key: str = Field(..., min_length=1)
    jwt_secret_key: str = Field(..., min_length=1)
    access_token_expire_minutes: int = Field(default=60 * 3)
    remember_me_expire_minutes: int = Field(default=60 * 24 * 3)  # 3 days

    database_url: str = Field(..., min_length=1)
    sqlalchemy_echo: bool = Field(default=False)

    # AWS SES
    aws_access_key_id: str = Field(..., min_length=1)
    aws_secret_access_key: str = Field(..., min_length=1)
    aws_region: str = Field(default="ap-southeast-1")
    email_from: str = Field(default="NCU-TLDR <noreply@ncutldr.com>")
    verify_base_url: str = Field(default="https://ncutldr.com")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore
