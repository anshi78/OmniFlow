from __future__ import annotations
"""Auth schemas — JWT authentication and user management."""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: str = Field(..., examples=["admin@omniflow.ai"])
    password: str = Field(..., min_length=8)
    full_name: str | None = None
    role: str = Field("viewer", pattern="^(admin|manager|viewer)$")


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str | None
    role: str
    is_active: bool
    created_at: datetime
    last_login: datetime | None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
