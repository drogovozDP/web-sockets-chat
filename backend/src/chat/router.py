from fastapi import APIRouter, Depends, WebSocket

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.chat.models import chat, message, user_chat
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


socks = []

@router.websocket("/{chat_id}/ws")
async def websocket_endpoint(chat_id: int, websocket: WebSocket):
    print('a new websocket to create.')
    await websocket.accept()
    socks.append(websocket)

    while True:
        try:
            text = await websocket.receive_text()
            # resp = {'value': f"{text}, random.uniform(0, 1)"}
            for s in socks:
                await s.send_json(text)
            # await websocket.send_json(resp)
        except Exception as e:
            print('error:', e)
            socks.remove(websocket)
            break
    print('Bye..')
