from typing import List
from fastapi import APIRouter, Depends, WebSocket
from fastapi import WebSocketDisconnect, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.chat.websocket_manager import manager
from backend.src.auth.utils import get_current_user
from backend.src.auth.schemas import UserRead
from backend.src.database import get_async_session
from backend.src.chat import utils


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.get("/")
async def get_user_chat_list(
        user: UserRead = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
):
    return await utils.get_user_chat_list(user.id, session)


@router.post("/")
async def create_chat(
        user: int,
        users: List[int],
):
    chat_details = await utils.create_chat(users, user)
    return {"status": 200, "details": "Chat has been created.", "chat_details": chat_details}


# TODO make pagination: 20 messages, offset 0 -> 20 -> 40...
@router.get("/{chat_id}")
async def get_messages_from_specific_chat(
        chat_id: int,
        user: UserRead = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
):
    return await utils.get_messages_from_specific_chat(chat_id, user.id, session)


# TODO test_1: query chat that user doesn't have access; test_2: query chat that doesn't exist
@router.get("/{chat_id}/users")
async def get_users_in_chat(
        chat_id: int,
        session: AsyncSession = Depends(get_async_session),
        user: UserRead = Depends(get_current_user),
):
    result = await utils.get_users_in_chat(chat_id, session)
    if len([1 for db_user in result if db_user[0] == user.id]) == 0:
        raise HTTPException(status_code=401, detail="Invalid Credentials.")
    return result


@router.get("/{chat_id}/unchecked")
async def get_amount_of_unchecked_messages(
        chat_id: int,
        user: UserRead = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
):
    return await utils.get_amount_of_unchecked_messages(user.id, chat_id, session)


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.accept_connection(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(user_id, data)
    except WebSocketDisconnect:
        manager.disconnect(user_id)
