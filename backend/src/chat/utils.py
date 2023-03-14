from typing import List
# from datetime import datetime
import datetime

from sqlalchemy import select, insert, update, delete, and_, func, asc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.auth.models import auth_user
from backend.src.auth.schemas import UserRead
from backend.src.chat.models import user_chat, chat, message, unchecked_message
from backend.src.database import get_async_session


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
    chat_name = f"{user.name} {' '.join([user['name'] for user in result])}"
    stmt = insert(chat).values(
        name=chat_name
    ).returning(chat.c.id)
    result = await session.execute(stmt)
    chat_id = result.fetchone()[0]

    stmt = insert(user_chat).values([{"user_id": user.id, "chat_id": chat_id}] + [
        {"user_id": user, "chat_id": chat_id} for user in users
    ])
    await session.execute(stmt)
    await session.commit()
    return {"chat_name": chat_name}


async def get_messages_from_specific_chat(
        chat_id: int,
        user_id: int,
        session: AsyncSession,
):
    subquery = select(user_chat.c.chat_id).where(
        and_(user_chat.c.user_id == user_id, user_chat.c.chat_id == chat_id)
    ).subquery()

    query = select(message, auth_user.c.name, auth_user.c.surname) \
        .where(message.c.chat_id == subquery) \
        .join(auth_user).filter(auth_user.c.id == message.c.sender) \
        .order_by(asc(message.c.timestamp))
    result = await session.execute(query)
    return result.all()


async def get_amount_of_unchecked_messages(
        user_id: int,
        chat_id: int,
        session: AsyncSession,
):
    unchecked = select(unchecked_message.c.message_id).where(unchecked_message.c.user_id == user_id).subquery()
    query = select(message.c.chat_id, func.count(message.c.value).label("unchecked_messages"))\
        .join(unchecked).filter(message.c.id == unchecked.c.message_id)\
        .where(message.c.chat_id == chat_id)\
        .group_by(message.c.chat_id)
    result = await session.execute(query)
    return result.all()


async def get_amount_of_unchecked_messages_in_one_chat(user_id: int, chat_id: int):
    async_session = anext(get_async_session())
    session = await async_session
    unchecked = select(unchecked_message.c.message_id).where(unchecked_message.c.user_id == user_id).subquery()
    query = select(func.count(message.c.id).label("message_amount"))\
        .join(unchecked).filter(unchecked.c.message_id == message.c.id)\
        .where(message.c.chat_id == chat_id)
    result = await session.execute(query)
    return result.all()[0][0]


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


async def get_online_users_in_chat(chat_id: int, online_user_ids):
    async_session = anext(get_async_session())
    session = await async_session
    chat_user_ids = select(user_chat.c.user_id).where(user_chat.c.chat_id == chat_id).subquery()
    query = select(chat_user_ids).where(chat_user_ids.c.user_id.in_(online_user_ids))
    result = await session.execute(query)
    result = result.all()
    return [user[0] for user in result]


async def get_sender_name_surname(user_id):
    async_session = anext(get_async_session())
    session = await async_session
    query = select(auth_user.c.name, auth_user.c.surname).where(auth_user.c.id == user_id)
    result = await session.execute(query)
    result = result.all()
    return result[0]


async def check_messages_in_the_chat(user_id: int, chat_id: int):
    async_session = anext(get_async_session())
    session = await async_session

    unchecked_ids = select(unchecked_message.c.message_id).where(unchecked_message.c.user_id == user_id).subquery()

    unchecked_messages = select(message.c.id).join(unchecked_ids) \
        .filter(and_(message.c.chat_id == chat_id, unchecked_ids.c.message_id == message.c.id)).subquery()

    to_delete = select(unchecked_message.c.id).join(unchecked_messages) \
        .filter(unchecked_messages.c.id == unchecked_message.c.message_id) \
        .where(unchecked_message.c.user_id == user_id).subquery()

    stmt = delete(unchecked_message).where(unchecked_message.c.id.in_(to_delete))

    await session.execute(stmt)
    await session.commit()


async def save_unchecked_message(message_id: int, chat_id: int):
    async_session = anext(get_async_session())
    session = await async_session
    users = await get_users_in_chat(chat_id, session)
    stmt = insert(unchecked_message).values([
        {"message_id": message_id, "user_id": user[0]} for user in users
    ])
    await session.execute(stmt)
    await session.commit()


async def save_message(user_id: int, chat_id: int, value: str):
    async_session = anext(get_async_session())
    session = await async_session
    stmt = insert(message).values(
        value=value,
        sender=user_id,
        chat_id=chat_id,
        timestamp=datetime.datetime.utcnow(),
    ).returning(message.c.id)
    result = await session.execute(stmt)
    await session.commit()
    message_id = result.fetchone()[0]
    await save_unchecked_message(message_id, chat_id)
    return message_id


async def edit_message(message_id: int, value: str):
    async_session = anext(get_async_session())
    session = await async_session
    query = select(message.c.timestamp).where(message.c.id == message_id)
    result = await session.execute(query)
    timestamp = result.fetchone()[0]  # TODO make sort
    stmt = update(message).where(message.c.id == message_id).values(value=value, timestamp=datetime.date(1995, 12, 1))
    await session.execute(stmt)
    await session.commit()
