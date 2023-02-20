from fastapi import APIRouter, Depends

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.auth.models import User
from backend.src.chat.models import chat, message, user_chat
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
    query = select(chat).filter(chat.c.id.in_(
        select(user_chat.c.chat_id).where(user_chat.c.user_id == user.id).subquery()
    ))
    result = await session.execute(query)
    return result.all()


@router.get("/{chat_id}")
async def get_specific_chat(
        chat_id: int,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user)
):
    subquery = select(user_chat.c.chat_id).where(
        and_(user_chat.c.user_id == user.id, user_chat.c.chat_id == chat_id)
    ).subquery()
    query = select(message).where(message.c.chat_id == subquery)
    result = await session.execute(query)
    return result.all()
