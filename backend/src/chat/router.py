from typing import List
from fastapi import APIRouter, Depends, WebSocket
from fastapi import WebSocketDisconnect, HTTPException

from sqlalchemy import select, and_, insert
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.chat.websocket_manager import manager
from backend.src.chat.models import chat, message, user_chat
from backend.src.auth.models import auth_user
from backend.src.auth.utils import get_current_user
from backend.src.auth.schemas import UserRead
from backend.src.database import get_async_session

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.get("/")
async def get_list_chat(
        session: AsyncSession = Depends(get_async_session),
        user: UserRead = Depends(get_current_user)
):
    subquery = select(user_chat).where(user_chat.c.user_id == user.id).subquery()
    query = select(chat).join(subquery).filter(subquery.c.chat_id == chat.c.id)
    result = await session.execute(query)
    return result.all()


@router.post("/")
async def create_chat(
        users: List[int],
        session: AsyncSession = Depends(get_async_session),
        user: UserRead = Depends(get_current_user)
):
    query = select(auth_user).where(auth_user.c.id.in_(users))
    result = await session.execute(query)
    result = result.all()
    stmt = insert(chat).values(name=f"{user.name} {' '.join([user['name'] for user in result])}").returning(chat.c.id)
    result = await session.execute(stmt)
    chat_id = result.fetchone()[0]

    stmt = insert(user_chat).values([{"user_id": user.id, "chat_id": chat_id}] + [
        {"user_id": user, "chat_id": chat_id} for user in users
    ])
    await session.execute(stmt)
    await session.commit()
    return {"status": 200, "details": "Chat has been created."}


# TODO make pagination: 20 messages, offset 0 -> 20 -> 40...
@router.get("/{chat_id}")
async def get_specific_chat(
        chat_id: int,
        session: AsyncSession = Depends(get_async_session),
        user: UserRead = Depends(get_current_user)
):
    subquery = select(user_chat.c.chat_id).where(
        and_(user_chat.c.user_id == user.id, user_chat.c.chat_id == chat_id)
    ).subquery()
    query = select(message).where(message.c.chat_id == subquery)
    result = await session.execute(query)
    return result.all()


@router.get("/{chat_id}/users")
async def get_users_in_chat(
        chat_id: int,
        session: AsyncSession = Depends(get_async_session),
        user: UserRead = Depends(get_current_user),
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
    if len([1 for db_user in result if db_user[0] == user.id]) == 0:
        raise HTTPException(status_code=401, detail="Invalid Credentials.")
    return result


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.accept_connection(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(user_id, data, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
