from typing import List
from fastapi import APIRouter, Depends, WebSocket, UploadFile, File
from fastapi import WebSocketDisconnect, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.chat.websocket_manager import manager
from backend.src.auth.utils import get_current_user
from backend.src.auth.schemas import UserRead
from backend.src.database import get_async_session
from backend.src.chat import utils

from backend.src.chat.schemas import (
    UserIdNameSurname,
    CreateChatResponse,
    MessagesFromSpecificChat,
    GetUsersInChat,
    UncheckedMessagesAmount,
    SaveFileResponse,
)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.get("/")
async def get_user_chat_list(
        user: UserRead = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
):
    """Gets user's chat list.
    Args:
        user: Current logged-in user.
        session: A database async session.

    Returns:
        User's chat list.
    """
    return [UserIdNameSurname(**user) for user in (await utils.get_user_chat_list(user.id, session))]


@router.post("/")
async def create_chat(
        user: int,
        users: List[int],
):
    """Creates new chat based on input user ids.
    Args:
        user: Initiator database user id.
        users: Databases user ids.
    Returns:
        Status code and chat details.
    """
    chat_details = await utils.create_chat(user, users)
    return CreateChatResponse(**{"details": "Chat has been created.", **chat_details})


@router.get("/{chat_id}")
async def get_messages_from_specific_chat(
        chat_id: int,
        page: int,
        user: UserRead = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """Gets messages from database based on offset.
    Args:
        chat_id: Database chat id.
        page: Offset for messages.
        user: Current logged-in user.
        session: A database async session.

    Returns:
        Messages in the specific chat.
    """
    return [MessagesFromSpecificChat(**message) for message in (
        await utils.get_messages_from_specific_chat(chat_id, user.id, page, session)
    )]


@router.get("/{chat_id}/users")
async def get_users_in_chat(
        chat_id: int,
        session: AsyncSession = Depends(get_async_session),
        user: UserRead = Depends(get_current_user),
):
    """Gets all users in the specific chat.
    Args:
        chat_id: Database chat id.
        session: A database async session.
        user: Current logged-in user.

    Returns:
        All users in the specific chat.
    """
    users = await utils.get_users_in_chat(user.id, chat_id, session)
    if not users:
        raise HTTPException(status_code=401, detail="Invalid Credentials.")
    return [GetUsersInChat(**user) for user in users]


@router.get("/{chat_id}/unchecked")
async def get_amount_of_unchecked_messages(
        chat_id: int,
        user: UserRead = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """Gets from the database amount of unchecked messages for the specific user in the specific chat.
    Args:
        chat_id: Database chat id.
        user: Current logged-in user.
        session: A database async session.

    Returns:
        Amount of unchecked messages in the specific chat for the specific user.
    """
    unchecked_messages = await utils.get_amount_of_unchecked_messages(user.id, chat_id, session)
    return UncheckedMessagesAmount(
        **unchecked_messages if unchecked_messages is not None else {"chat_id": chat_id, "unchecked_messages": 0}
    )


@router.post("/{chat_id}/upload_file")
async def upload_file(
        chat_id: int,
        user: UserRead = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
        file: UploadFile = File(...),
):
    """Saves files.
    Args:
        chat_id: Database chat id.
        user: Current logged-in user.
        session: A database async session.
        file: File object.

    Returns:
        Status about file saving.
    """
    saved_file = await utils.save_file(file, chat_id, user.id, session)
    if saved_file["status"] == 400:
        HTTPException(**saved_file)
    return SaveFileResponse(**saved_file)


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """Handles client connections to the server. Receives and sends messages.
    Args:
        websocket: Client connection.
        user_id: Database user id.
    """
    await manager.accept_connection(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(user_id, data)
    except WebSocketDisconnect:
        manager.disconnect(user_id)
