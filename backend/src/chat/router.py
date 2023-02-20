from fastapi import APIRouter, Depends

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.auth.models import User
from backend.src.auth.config import current_user
from backend.src.database import get_async_session

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.get("/")
async def get_list_chat(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user)
):
    query = select(User).where()
    result = await session.execute(query)
    return result.all()


@router.get("/{chat_id}")
async def get_specific_chat(
        chat_id: int,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user)
):
    query = select(User).where(User.c.id == chat_id)
    result = await session.execute(query)
    return result.all()

# select name from auth_user where auth_user.id in (select user_id from user_chat where chat_id = 1);
