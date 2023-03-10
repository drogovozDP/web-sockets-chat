from typing import List

from sqlalchemy import select, insert, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.auth.models import auth_user
from backend.src.auth.schemas import UserRead
from backend.src.chat.models import user_chat, chat, message
from backend.src.database import get_async_session


async def get_session():
    async_session = anext(get_async_session())
    return await async_session


async def get_user_chat_list(user_id: int, session: AsyncSession):
    subquery = select(user_chat).where(user_chat.c.user_id == user_id).subquery()
    query = select(chat).join(subquery).filter(subquery.c.chat_id == chat.c.id)
    result = await session.execute(query)
    return result.all()


async def create_chat(
        users: List[int],
        session: AsyncSession,
        user: UserRead
):
    query = select(auth_user).where(auth_user.c.id.in_(users))
    result = await session.execute(query)
    result = result.all()
    stmt = insert(chat).values(
        name=f"{user.name} {' '.join([user['name'] for user in result])}"
    ).returning(chat.c.id)
    result = await session.execute(stmt)
    chat_id = result.fetchone()[0]

    stmt = insert(user_chat).values([{"user_id": user.id, "chat_id": chat_id}] + [
        {"user_id": user, "chat_id": chat_id} for user in users
    ])
    await session.execute(stmt)
    await session.commit()
    return {"status": 200, "details": "Chat has been created."}


async def get_messages_from_specific_chat(
        chat_id: int,
        user_id: int,
        session: AsyncSession,
):
    subquery = select(user_chat.c.chat_id).where(
        and_(user_chat.c.user_id == user_id, user_chat.c.chat_id == chat_id)
    ).subquery()
    query = select(message).where(message.c.chat_id == subquery)
    result = await session.execute(query)
    return result.all()


async def get_users_in_chat(
        chat_id: int,
        session: AsyncSession,
):
    user_ids = select(user_chat.c.user_id).where(user_chat.c.chat_id == chat_id).subquery()
    query = select(
        auth_user.c.id,
        auth_user.c.name,
        auth_user.c.surname
    ).join(user_ids).filter(
        user_ids.c.user_id == auth_user.c.id
    )
    result = await session.execute(query)
    result = result.all()
    return result


async def save_message(user_id: int, user_message: dict):
    session = await get_session()
    stmt = insert(message).values(
        value=user_message["value"],
        sender=user_id,
        chat_id=user_message["chat_id"]
    )
    await session.execute(stmt)
    await session.commit()
