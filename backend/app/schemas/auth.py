import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

_NCU_EMAIL_RE = re.compile(r"^[0-9]+@cc\.ncu\.edu\.tw$")


class RegisterRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    email: str
    password: str
    display_name: str = Field(alias="displayName")

    @field_validator("email")
    @classmethod
    def must_be_ncu_email(cls, v: str) -> str:
        if not _NCU_EMAIL_RE.match(v):
            raise ValueError("必須是 NCU 學生信箱（學號@cc.ncu.edu.tw）")
        return v.lower()


class LoginRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    email: EmailStr
    password: str
    remember_me: bool = Field(alias="rememberMe", default=False)


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class MessageResponse(BaseModel):
    message: str


class UserOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: str
    email: str
    display_name: str = Field(alias="displayName")
    is_active: bool = Field(alias="isActive")
    email_verified: bool = Field(alias="emailVerified")
