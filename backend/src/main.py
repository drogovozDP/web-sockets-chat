from fastapi import FastAPI, Depends
from fastapi_users import FastAPIUsers

from backend.src.auth.models import User
from backend.src.auth.manager import get_user_manager
from backend.src.auth.config import auth_backend
from backend.src.auth.schemas import UserRead, UserCreate


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

app = FastAPI(
    title="Tutorial FastAPI"
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

current_user = fastapi_users.current_user()


@app.get("/protected-route")
def protected_route(user: User = Depends(current_user)):
    return f"Hello, {user.username}"


@app.get("/unprotected-route")
def unprotected_route():
    return f"Hello, anonim"


@app.get("/api/test")
def test():
    return "Hello from backend!"
