from typing import Optional

from fastapi_users import schemas


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
