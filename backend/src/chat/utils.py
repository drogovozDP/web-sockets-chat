import os
import shutil
from typing import List
import datetime
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import select, insert, update, delete, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.auth.models import auth_user
from backend.src.chat.models import user_chat, chat, message, unchecked_message
from backend.src.database import get_async_session
from backend.src.config import STATIC_FILES_PATH


async def get_user_chat_list(current_user_id: int, session: AsyncSession):
    """Gets from database user chat list.
    Args:
        user_id Database user id.
        session: A database async session.

    Returns:
         Chat list.
    """
    chat_ids = select(user_chat).where(user_chat.c.user_id == current_user_id).subquery()
    return (await session.execute(select(chat).join(chat_ids).filter(chat_ids.c.chat_id == chat.c.id))).all()


async def get_messages_from_specific_chat(
        chat_id: int,
        current_user_id: int,
        page: int,
        session: AsyncSession,
):
    """Gets from database messages from the specific chat.
    Args:
        chat_id: Database chat id.
        current_user_id: Database user id.
        page: Offset for messages.
        session: A database async session.

    Returns:
        Messages from the specific chat.
    """
    validated_chat_id = select(user_chat.c.chat_id).where(
        and_(user_chat.c.user_id == current_user_id, user_chat.c.chat_id == chat_id)
    ).subquery()

    messages = select(message, auth_user.c.name, auth_user.c.surname) \
        .where(message.c.chat_id == validated_chat_id) \
        .join(auth_user).filter(auth_user.c.id == message.c.sender) \
        .order_by(desc(message.c.timestamp))
    messages = messages.limit(10).offset(10 * page)
    return (await session.execute(messages)).all()[::-1]


async def get_amount_of_unchecked_messages(
        current_user_id: int,
        chat_id: int,
        session: AsyncSession,
):
    """Counts unchecked messages for the specific user in the specific chat.
    Args:
        current_user_id: Database user id.
        chat_id: Database chat id.
        session: A database async session.

    Returns:
        Amount of unchecked messages for the specific user.
    """
    unchecked = select(unchecked_message.c.message_id).where(unchecked_message.c.user_id == current_user_id).subquery()
    return (
        await session.execute(
            select(message.c.chat_id, func.count(message.c.value).label("unchecked_messages"))
            .join(unchecked).filter(message.c.id == unchecked.c.message_id)
            .where(message.c.chat_id == chat_id)
            .group_by(message.c.chat_id))
    ).fetchone()


async def create_chat(
        author_id: int,
        user_ids: List[int],
):
    """Creates new chat and saves it.
    Args:
        author_id: Initiator database user id.
        user_ids: Database user ids.

    Returns:
        Dictionary of chat name and chat id.
    """
    async_session = anext(get_async_session())
    session = await async_session

    users = (await session.execute(select(auth_user.c.id, auth_user.c.name).where(auth_user.c.id.in_(user_ids)))).all()
    author = (
        await session.execute(select(auth_user.c.id, auth_user.c.name).where(auth_user.c.id == author_id))).fetchone()

    chat_name = f"{author['name']} {' '.join([user['name'] for user in users])}"
    chat_id = (await session.execute(insert(chat).values(name=chat_name).returning(chat.c.id))).fetchone()[0]

    await session.execute(insert(user_chat).values([{"user_id": author["id"], "chat_id": chat_id}] + [
        {"user_id": user["id"], "chat_id": chat_id} for user in users
    ]))

    await session.commit()
    return {"chat_name": chat_name, "chat_id": chat_id}


async def get_users_in_chat(
        current_user_id: int,
        chat_id: int,
        session: AsyncSession,
):
    """Gets users in the specific chat.
    Args:
        current_user_id: Database user id.
        chat_id: Database chat id.
        session: A database async session.

    Returns:
        Users in the specific chat.
    """
    user_in_chat = await check_if_user_in_chat(current_user_id, chat_id, session)
    if not user_in_chat:
        return False

    user_ids = select(user_chat.c.user_id).where(user_chat.c.chat_id == chat_id).subquery()
    return (
        await session.execute(
            select(
                auth_user.c.id,
                auth_user.c.name,
                auth_user.c.surname
            ).join(user_ids).filter(
                user_ids.c.user_id == auth_user.c.id
            )
        )
    ).all()


async def _get_online_users_in_chat(chat_id: int, online_user_ids: List[int]):
    """Gets intersection between given list of user ids and user ids in the specific chat.
    This function is internal.
    Args:
        chat_id: Database chat id.
        online_user_ids: List of user ids.

    Returns:
        intersection between given list of user ids and user ids in the specific chat.
    """
    async_session = anext(get_async_session())
    session = await async_session
    chat_user_ids = select(user_chat.c.user_id).where(user_chat.c.chat_id == chat_id).subquery()
    query = select(chat_user_ids).where(chat_user_ids.c.user_id.in_(online_user_ids))
    result = await session.execute(query)
    result = result.all()
    return [user[0] for user in result]


async def get_sender_name_surname(user_id: int):
    """Gets from the database name and surname by id.
    Args:
        user_id: Database user id.

    Returns:
        Sender's name and surname.
    """
    async_session = anext(get_async_session())
    session = await async_session

    return (
        await session.execute(
            select(auth_user.c.name, auth_user.c.surname).where(auth_user.c.id == user_id)
        )
    ).all()[0]


async def check_messages_in_the_chat(current_user_id: int, chat_id: int):
    """Removes unchecked messages from the database for the specific user in the specific chat.
    Args:
        current_user_id: Database user id.
        chat_id: Database chat id.
    """
    async_session = anext(get_async_session())
    session = await async_session

    unchecked_ids = select(unchecked_message.c.message_id).where(unchecked_message.c.user_id == current_user_id).subquery()

    unchecked_messages = select(message.c.id).join(unchecked_ids) \
        .filter(and_(message.c.chat_id == chat_id, unchecked_ids.c.message_id == message.c.id)).subquery()

    to_delete = select(unchecked_message.c.id).join(unchecked_messages) \
        .filter(unchecked_messages.c.id == unchecked_message.c.message_id) \
        .where(unchecked_message.c.user_id == current_user_id).subquery()

    await session.execute(delete(unchecked_message).where(unchecked_message.c.id.in_(to_delete)))
    await session.commit()


async def save_unchecked_message(current_user_id: int, message_id: int, chat_id: int):
    """Saves unchecked messages from the database for the specific user in the specific chat.
    Args:
        current_user_id: Database user id.
        message_id: Database message id.
        chat_id: Database chat id.
    """
    async_session = anext(get_async_session())
    session = await async_session

    users = await get_users_in_chat(current_user_id, chat_id, session)

    await session.execute(
        insert(unchecked_message).values([
            {"message_id": message_id, "user_id": user[0]} for user in users
        ])
    )
    await session.commit()


async def save_message(current_user_id: int, chat_id: int, value: str, message_type: str):
    """Saves message to the database for the specific user in the specific chat.
    Args:
        current_user_id: Database user id.
        chat_id: Database chat id.
        value: Message content.
        message_type: Type of message.

    Returns:
        Saved message id.
    """
    async_session = anext(get_async_session())
    session = await async_session

    new_message_id = await session.execute(
        insert(message).values(
            type=message_type,
            value=value,
            sender=current_user_id,
            chat_id=chat_id,
            timestamp=datetime.datetime.utcnow(),
        ).returning(message.c.id)
    )
    await session.commit()

    new_message_id = new_message_id.fetchone()[0]
    await save_unchecked_message(current_user_id, new_message_id, chat_id)
    return new_message_id


async def check_if_user_in_chat(current_user_id, chat_id, session: AsyncSession):
    """Checks if the user in the chat.
    Args:
        current_user_id: Database user id.
        chat_id: Database chat id.

    Returns:
        Boolean (a user in the chat or not).
    """
    user_in_chat = (
        await session.execute(
            select(user_chat).where(and_(user_chat.c.user_id == current_user_id, user_chat.c.chat_id == chat_id))
        )
    ).fetchone()
    return user_in_chat is not None


async def save_file(file: UploadFile, chat_id: int, current_user_id: int, session: AsyncSession):
    """Saves the file in the specific chat.
    Args:
        file: File object.
        chat_id: Database chat id.
        current_user_id: Database user id.
        session: A database async session.

    Returns:
        Dictionary of saving status and details.
    """
    user_in_chat = await check_if_user_in_chat(current_user_id, chat_id, session)
    if not user_in_chat:
        return {"status": 400, "detail": "Bad credentials."}
    dir_name = STATIC_FILES_PATH / str(chat_id)
    os.mkdir(dir_name) if not os.path.exists(dir_name) else None
    file_name = f"{len(os.listdir(dir_name))}-{file.filename}"
    with open(dir_name / file_name, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"status": 200, "detail": Path(str(chat_id)) / file_name}


async def validate_message_author(message_id: int, current_user_id: int, chat_id: int):
    """Checks if user is message author.
    Args:
        message_id: Database message id.
        current_user_id: Database user id.
        chat_id: Database chat id.

    Returns:
        Boolean (user is author or not).
    """
    async_session = anext(get_async_session())
    session = await async_session

    msg = (
        await session.execute(
            select(message.c.sender, message.c.chat_id).where(message.c.id == message_id)
        )
    ).fetchone()

    return msg[0] == current_user_id and msg[1] == chat_id


async def validate_message_content(message_id: int):
    """Checks message type.
    Args:
        message_id: Database message id.

    Returns:
        True if message type equals to 'text'
    """
    async_session = anext(get_async_session())
    session = await async_session

    msg = (
        await session.execute(select(message.c.type).where(message.c.id == message_id))
    ).fetchone()
    return msg[0] == "text"


async def edit_message(message_id: int, value: str):
    """Updates message value in the database.
    Args:
        message_id: Database message id.
        value: New message value.
    """
    async_session = anext(get_async_session())
    session = await async_session

    timestamp = (
        await session.execute(
            select(message.c.timestamp).where(message.c.id == message_id)
        )
    ).fetchone()[0]

    await session.execute(
        update(message).where(message.c.id == message_id).values(
            value=value,
            timestamp=timestamp
        ).returning(message.c.value)
    )
    await session.commit()
