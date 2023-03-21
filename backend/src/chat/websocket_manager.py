from typing import Dict
import json

from fastapi import WebSocket

from backend.src.chat import utils


class ConnectionManager:
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(ConnectionManager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.userid_to_socket: Dict[int, WebSocket] = {}

    async def accept_connection(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.userid_to_socket[user_id] = websocket

    def disconnect(self, user_id: int):
        del self.userid_to_socket[user_id]

    async def create_chat(self, user_id: int, message: dict):
        chat_details = await utils.create_chat(user_id, message["value"])
        await self.propagate_message(user_id, {**chat_details, **message})

    async def check_message(self, user_id: int, chat_id: int):
        await utils.check_messages_in_the_chat(user_id, chat_id)

    async def edit_message(self, user_id: int, message: dict):
        is_owner = await utils.validate_message_author(message["message_id"], user_id, message["chat_id"])
        if is_owner:
            await utils.edit_message(message["message_id"], message["value"])
            await self.propagate_message(user_id, message)

    async def propagate_message(self, user_id, message):
        online_users_ids = await utils.get_online_users_in_chat(
            message["chat_id"],
            list(self.userid_to_socket.keys())
        )
        sender_name, sender_surname = await utils.get_sender_name_surname(user_id)
        for userid in online_users_ids:
            await self.userid_to_socket[userid].send_text(json.dumps({
                "name": sender_name,
                "surname": sender_surname,
                **message
            }))

    async def send_message(self, user_id, message: dict):
        message_id = await utils.save_message(user_id, message["chat_id"], message["value"])
        await self.propagate_message(user_id, {"id": message_id, "sender": user_id, **message})

    async def broadcast(self, user_id: int, message: str):
        message = json.loads(message)
        message_type = message["type"]
        if message_type == "send_message":
            await self.send_message(user_id, message)

        elif message_type == "check_message":
            await self.check_message(user_id, message["chat_id"])

        elif message_type == "edit_message":
            await self.edit_message(user_id, message)

        elif message_type == "create_chat":
            await self.create_chat(user_id, message)


manager = ConnectionManager()
