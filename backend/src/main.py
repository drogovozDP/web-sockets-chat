from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from backend.src.auth.models import User
from backend.src.auth.config import fastapi_users, auth_backend, current_user
from backend.src.auth.schemas import UserRead, UserCreate
from backend.src.chat.router import router as router_chat


app = FastAPI(
    title="Chat FastAPI"
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

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/protected-route")
def protected_route(user: User = Depends(current_user)):
    return f"Hello, {user.username}"


@app.get("/unprotected-route")
def unprotected_route():
    return f"Hello, anonim"


@app.get("/api/test")
async def test():
    return "Hello from backend!"


app.include_router(router_chat)
