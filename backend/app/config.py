from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
        case_sensitive=False,
    )

    app_name: str = Field(default="NCU-TLDR Backend")
    app_version: str = Field(default="0.1.0")
    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173"],
    )

    x_sync_secret_key: str = Field(default="change-me-in-production")
    jwt_secret_key: str = Field(default="insecure-dev-secret-change-in-prod")
    access_token_expire_minutes: int = Field(default=60)

    database_url: str = Field(...)

    # AWS SES
    aws_access_key_id: str = Field(default="")
    aws_secret_access_key: str = Field(default="")
    aws_region: str = Field(default="ap-southeast-1")
    email_from: str = Field(default="noreply@ncutldr.com")
    verify_base_url: str = Field(default="https://ncutldr.com")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore
