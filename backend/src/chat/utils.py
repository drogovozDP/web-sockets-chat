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


async def get_user_chat_list(user_id: int, session: AsyncSession):
    """Gets from database user chat list.
    Args:
        user_id Database user id.
        session: A database async session.

    Returns:
         Chat list.
    """
    subquery = select(user_chat).where(user_chat.c.user_id == user_id).subquery()
    query = select(chat).join(subquery).filter(subquery.c.chat_id == chat.c.id)
    result = await session.execute(query)
    return result.all()


async def get_messages_from_specific_chat(
        chat_id: int,
        user_id: int,
        page: int,
        session: AsyncSession,
):
    """Gets from database messages from the specific chat.
    Args:
        chat_id: Database chat id.
        user_id: Database user id.
        page: Offset for messages.
        session: A database async session.

    Returns:
        Messages from the specific chat.
    """
    subquery = select(user_chat.c.chat_id).where(
        and_(user_chat.c.user_id == user_id, user_chat.c.chat_id == chat_id)
    ).subquery()

    query = select(message, auth_user.c.name, auth_user.c.surname) \
        .where(message.c.chat_id == subquery) \
        .join(auth_user).filter(auth_user.c.id == message.c.sender) \
        .order_by(desc(message.c.timestamp))
    query = query.limit(10).offset(10 * page)
    result = await session.execute(query)
    return result.all()[::-1]


async def get_amount_of_unchecked_messages(
        user_id: int,
        chat_id: int,
        session: AsyncSession,
):
    """Counts unchecked messages for the specific user in the specific chat.
    Args:
        user_id: Database user id.
        chat_id: Database chat id.
        session: A database async session.

    Returns:
        Amount of unchecked messages for the specific user.
    """
    unchecked = select(unchecked_message.c.message_id).where(unchecked_message.c.user_id == user_id).subquery()
    query = select(message.c.chat_id, func.count(message.c.value).label("unchecked_messages"))\
        .join(unchecked).filter(message.c.id == unchecked.c.message_id)\
        .where(message.c.chat_id == chat_id)\
        .group_by(message.c.chat_id)
    result = await session.execute(query)
    return result.all()


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
    result = await session.execute(select(auth_user.c.id, auth_user.c.name).where(auth_user.c.id.in_(user_ids)))
    users = result.all()
    result = await session.execute(select(auth_user.c.id, auth_user.c.name).where(auth_user.c.id == author_id))
    author = result.fetchone()
    chat_name = f"{author['name']} {' '.join([user['name'] for user in users])}"
    stmt = insert(chat).values(
        name=chat_name
    ).returning(chat.c.id)
    result = await session.execute(stmt)
    chat_id = result.fetchone()[0]

    stmt = insert(user_chat).values([{"user_id": author["id"], "chat_id": chat_id}] + [
        {"user_id": user["id"], "chat_id": chat_id} for user in users
    ])
    await session.execute(stmt)
    await session.commit()
    return {"chat_name": chat_name, "chat_id": chat_id}


async def get_amount_of_unchecked_messages_in_one_chat(user_id: int, chat_id: int):
    """Gets amount of unchecked messages in the specific chat for the specific user.
    Args:
        user_id: Database user id.
        chat_id: Database chat id.

    Returns:
        Amount of unchecked messages for the specific user in the specific chat.
    """
    async_session = anext(get_async_session())
    session = await async_session
    unchecked = select(unchecked_message.c.message_id).where(unchecked_message.c.user_id == user_id).subquery()
    query = select(func.count(message.c.id).label("message_amount"))\
        .join(unchecked).filter(unchecked.c.message_id == message.c.id)\
        .where(message.c.chat_id == chat_id)
    result = await session.execute(query)
    return result.all()[0][0]


async def get_users_in_chat(
        user_id: int,
        chat_id: int,
        session: AsyncSession,
):
    """Gets users in the specific chat.
    Args:
        user_id: Database user id.
        chat_id: Database chat id.
        session: A database async session.

    Returns:
        Users in the specific chat.
    """
    user_in_chat = await check_if_user_in_chat(user_id, chat_id, session)
    if not user_in_chat:
        return False
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


async def get_online_users_in_chat(chat_id: int, online_user_ids: List[int]):
    """Gets intersection between given list of user ids and user ids in the specific chat.
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


async def get_sender_name_surname(user_id):
    """Gets from the database name and surname by id.
    Args:
        user_id: Database user id.

    Returns:
        Sender's name and surname.
    """
    async_session = anext(get_async_session())
    session = await async_session
    query = select(auth_user.c.name, auth_user.c.surname).where(auth_user.c.id == user_id)
    result = await session.execute(query)
    result = result.all()
    return result[0]


async def check_messages_in_the_chat(user_id: int, chat_id: int):
    """Removes unchecked messages from the database for the specific user in the specific chat.
    Args:
        user_id: Database user id.
        chat_id: Database chat id.
    """
    async_session = anext(get_async_session())
    session = await async_session

    unchecked_ids = select(unchecked_message.c.message_id).where(unchecked_message.c.user_id == user_id).subquery()

    unchecked_messages = select(message.c.id).join(unchecked_ids) \
        .filter(and_(message.c.chat_id == chat_id, unchecked_ids.c.message_id == message.c.id)).subquery()

    to_delete = select(unchecked_message.c.id).join(unchecked_messages) \
        .filter(unchecked_messages.c.id == unchecked_message.c.message_id) \
        .where(unchecked_message.c.user_id == user_id)

    to_delete = await session.execute(to_delete)
    to_delete = to_delete.all()

    stmt = delete(unchecked_message).where(or_(unchecked_message.c.id == del_id[0] for del_id in to_delete))
    await session.execute(stmt)
    await session.commit()


async def save_unchecked_message(user_id: int, message_id: int, chat_id: int):
    """Saves unchecked messages from the database for the specific user in the specific chat.
    Args:
        user_id: Database user id.
        message_id: Database message id.
        chat_id: Database chat id.
    """
    async_session = anext(get_async_session())
    session = await async_session
    users = await get_users_in_chat(user_id, chat_id, session)
    stmt = insert(unchecked_message).values([
        {"message_id": message_id, "user_id": user[0]} for user in users
    ])
    await session.execute(stmt)
    await session.commit()


async def save_message(user_id: int, chat_id: int, value: str, message_type: str):
    """Saves message to the database for the specific user in the specific chat.
    Args:
        user_id: Database user id.
        chat_id: Database chat id.
        value: Message content.
        message_type: Type of message.

    Returns:
        Saved message id.
    """
    async_session = anext(get_async_session())
    session = await async_session
    stmt = insert(message).values(
        type=message_type,
        value=value,
        sender=user_id,
        chat_id=chat_id,
        timestamp=datetime.datetime.utcnow(),
    ).returning(message.c.id)
    result = await session.execute(stmt)
    await session.commit()
    message_id = result.fetchone()[0]
    await save_unchecked_message(user_id, message_id, chat_id)
    return message_id


async def check_if_user_in_chat(user_id, chat_id, session: AsyncSession):
    """Checks if the user in the chat.
    Args:
        user_id: Database user id.
        chat_id: Database chat id.

    Returns:
        Boolean (a user in the chat or not).
    """
    query = select(user_chat).where(and_(user_chat.c.user_id == user_id, user_chat.c.chat_id == chat_id))
    result = await session.execute(query)
    user_in_chat = result.fetchone()
    return True if user_in_chat is not None else False


async def save_file(file: UploadFile, chat_id: int, user_id: int, session: AsyncSession):
    """Saves the file in the specific chat.
    Args:
        file: File object.
        chat_id: Database chat id.
        user_id: Database user id.
        session: A database async session.

    Returns:
        Dictionary of saving status and details.
    """
    user_in_chat = await check_if_user_in_chat(user_id, chat_id, session)
    if not user_in_chat:
        return {"status": 400, "detail": "Bad credentials."}
    dir_name = STATIC_FILES_PATH / str(chat_id)
    os.mkdir(dir_name) if not os.path.exists(dir_name) else None
    file_name = f"{len(os.listdir(dir_name))}-{file.filename}"
    with open(dir_name / file_name, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"status": 200, "detail": f"File {file.filename} saved!", "file_path": Path(str(chat_id)) / file_name}


async def validate_message_author(message_id: int, user_id: int, chat_id: int):
    """Checks if user is message author.
    Args:
        message_id: Database message id.
        user_id: Database user id.
        chat_id: Database chat id.

    Returns:
        Boolean (user is author or not).
    """
    async_session = anext(get_async_session())
    session = await async_session
    query = select(message.c.sender, message.c.chat_id).where(message.c.id == message_id)
    result = await session.execute(query)
    msg = result.fetchone()
    return msg[0] == user_id and msg[1] == chat_id


async def validate_message_content(message_id: int):
    """Checks message type.
    Args:
        message_id: Database message id.

    Returns:
        True if message type equals to 'text'
    """
    async_session = anext(get_async_session())
    session = await async_session
    query = select(message.c.type).where(message.c.id == message_id)
    result = await session.execute(query)
    msg = result.fetchone()
    return msg[0] == "text"


async def edit_message(message_id: int, value: str):
    """Updates message value in the database.
    Args:
        message_id: Database message id.
        value: New message value.
    """
    async_session = anext(get_async_session())
    session = await async_session
    query = select(message.c.timestamp).where(message.c.id == message_id)
    result = await session.execute(query)
    timestamp = result.fetchone()[0]
    stmt = update(message).where(message.c.id == message_id).values(value=value, timestamp=timestamp).returning(message.c.value)
    await session.execute(stmt)
    await session.commit()
