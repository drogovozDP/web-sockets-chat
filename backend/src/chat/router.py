from fastapi import APIRouter, Depends

from backend.src.auth.models import User
from backend.src.auth.config import current_user


router = APIRouter(
    prefix="/chats",
    tags=["Chat"]
)


@router.get("/")
async def get_chat(user: User = Depends(current_user)):
    return {"statues": user.username}
