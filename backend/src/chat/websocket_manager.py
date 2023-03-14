from typing import List, Dict
import json

from fastapi import WebSocket, Depends

from backend.src.chat import utils


class ConnectionManager:
    def __init__(self):
        self.userid_to_socket: Dict[int, WebSocket] = {}

    async def accept_connection(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.userid_to_socket[user_id] = websocket

    def disconnect(self, user_id):
        del self.userid_to_socket[user_id]

    async def check_message(self, user_id: int, chat_id: int):
        await utils.check_messages_in_the_chat(user_id, chat_id)

    async def edit_message(self, user_message: dict):
        # TODO make validation for users and make join with user.name, user.surname for frontend
        await utils.edit_message(user_message["message_id"], user_message["value"])
        for userid in self.chat_to_online_userid[user_message["chat_id"]]:
            await self.userid_to_socket[userid].send_text(json.dumps(user_message))

    async def propagate_message(self, user_id, user_message):
        online_users_ids = await utils.get_online_users_in_chat(
            user_message["chat_id"],
            list(self.userid_to_socket.keys())
        )
        sender_name, sender_surname = await utils.get_sender_name_surname(user_id)
        for userid in online_users_ids:
            await self.userid_to_socket[userid].send_text(json.dumps({
                "name": sender_name,
                "surname": sender_surname,
                **user_message
            }))

    async def send_message(self, user_id, user_message: dict):
        message_id = await utils.save_message(user_id, user_message["chat_id"], user_message["value"])
        await self.propagate_message(user_id, {"id": message_id, **user_message})

    async def broadcast(self, user_id: int, user_message: str):
        user_message = json.loads(user_message)
        message_type = user_message["type"]
        if message_type == "send_message":
            await self.send_message(user_id, user_message)

        elif message_type == "check_message":
            await self.check_message(user_id, user_message["chat_id"])

        elif message_type == "edit_message":
            await self.edit_message(user_message)


# TODO create services with sockets and db queries
manager = ConnectionManager()
