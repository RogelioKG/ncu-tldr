from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: str = Field(alias="displayName")
    model_config = ConfigDict(populate_by_name=True)


class UserOut(BaseModel):
    id: str  # UUID as string
    email: str
    display_name: str = Field(alias="displayName")
    is_active: bool = Field(alias="isActive")
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str = Field(alias="accessToken")
    token_type: str = Field(alias="tokenType", default="bearer")
    user: UserOut
    model_config = ConfigDict(populate_by_name=True)
