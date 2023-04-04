from typing import Optional

from fastapi_users import schemas
from pydantic import BaseModel


class UserRead(schemas.BaseUser[int]):
    """
    Schema for user reading.
    """
    id: int
    email: str
    name: str
    surname: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserResponse(schemas.BaseUser[int]):
    """
    Schema for user responding.
    """
    id: int
    email: str
    name: str
    surname: str


class UserCreate(schemas.BaseUserCreate):
    """
    Schema for user creations.
    """
    name: str
    surname: str
    email: str
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class RegistrationResponse(BaseModel):
    """
    Schema for registration response.
    """
    status: str
    details: str


class TokenResponse(BaseModel):
    """
    Schema for authentication response.
    """
    access_token: str
    token_type: str
