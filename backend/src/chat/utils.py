from typing import List, Dict
import json

from fastapi import WebSocket, Depends
from sqlalchemy import select, insert, delete

from backend.src.chat.models import user_chat, message
from backend.src.database import get_async_session


class ConnectionManager:
    def __init__(self):
        self.chat_to_socket: Dict[int, List[WebSocket]] = {}
        self.socket_to_chat: Dict[WebSocket, int] = {}

    def create_chat_if_not_exists(self, chat_id):
        if chat_id not in self.chat_to_socket:
            self.chat_to_socket[chat_id] = []

    def delete_chat_if_empty(self, chat_id):
        if len(self.chat_to_socket[chat_id]) == 0:
            del self.chat_to_socket[chat_id]

    async def accept_connection(self, websocket: WebSocket):
        await websocket.accept()
        self.create_chat_if_not_exists(0)
        self.chat_to_socket[0].append(websocket)
        self.socket_to_chat[websocket] = 0

    async def connect_to_chat(self, chat_id: int, websocket: WebSocket):
        old_chat_id = self.socket_to_chat[websocket]  # find where is the socket now.
        self.chat_to_socket[old_chat_id].remove(websocket)  # remove the socket from the current chat.
        self.delete_chat_if_empty(old_chat_id)
        self.create_chat_if_not_exists(chat_id)
        self.socket_to_chat[websocket] = chat_id  # set new chat id for the socket.
        self.chat_to_socket[chat_id].append(websocket)  # add to the new chat the socket.

    def disconnect(self, websocket: WebSocket):
        chat_id = self.socket_to_chat[websocket]
        del self.socket_to_chat[websocket]
        self.chat_to_socket[chat_id].remove(websocket)

    async def send_message(self, user_id, user_message: dict):
        # TODO save message
        async_session = anext(get_async_session())
        session = await async_session
        stmt = insert(message).values(
            value=user_message["value"],
            sender=user_id,
            chat_id=user_message["chat_id"]
        )
        await session.execute(stmt)
        await session.commit()

        for websocket in self.chat_to_socket[user_message["chat_id"]]:
            await websocket.send_text(json.dumps({"sender": user_id, **user_message}))

    async def broadcast(self, user_id: int, user_message: str, websocket: WebSocket):
        user_message = json.loads(user_message)
        message_type = user_message["type"]
        if message_type == "select_chat":
            await self.connect_to_chat(user_message["value"], websocket)

        elif message_type == "send_message":
            await self.send_message(user_id, user_message)

# TODO create services with sockets and db queries
manager = ConnectionManager()
