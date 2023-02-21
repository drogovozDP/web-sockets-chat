from fastapi import APIRouter, Depends

from backend.src.auth.models import User
from backend.src.auth.schemas import UserRead, UserCreate
from backend.src.auth.config import fastapi_users, auth_backend, current_user


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["Auth"],
)

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["Auth"],
)


@router.get("/protected-route")
def protected_route(user: User = Depends(current_user)):
    return f"Hello, {user.name} {user.surname}"


@router.get("/unprotected-route")
def unprotected_route():
    return f"Hello, anonim"


@router.get("/api/test")
async def test():
    return "Hello from backend!"
