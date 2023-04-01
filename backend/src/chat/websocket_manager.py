from typing import Dict
import json

from fastapi import WebSocket

from backend.src.chat import utils


class ConnectionManager:
    """This is a WebSocket manager. It keeps all WebSocket connection as a field,
    receives all messages and propagates them to all connections.
    """
    userid_to_socket: Dict[int, WebSocket] = {}

    def __new__(cls):
        """Checks if this class has filed 'instance' and if it does, return it. Otherwise, creates and returns it.
        Returns:
            An instance of this class.
        """
        if not hasattr(cls, "instance"):
            cls.instance = super(ConnectionManager, cls).__new__(cls)
        return cls.instance

    async def accept_connection(self, websocket: WebSocket, user_id: int):
        """Accepts and saves new connection.
        Args:
            websocket: Connection to the server.
            user_id: Database user id.
        """
        await websocket.accept()
        self.userid_to_socket[user_id] = websocket

    def disconnect(self, user_id: int):
        """Deletes connectionsl
        Args:
            user_id: Database user id.
        """
        del self.userid_to_socket[user_id]

    async def create_chat(self, user_id: int, message: dict):
        """Creates new chat and propagates this to all connected users.
        Args:
            user_id: Database user id.
            message: Message from WebSocket connection.
        """
        chat_details = await utils.create_chat(user_id, message["value"])
        await self.propagate_message(user_id, {**chat_details, **message})

    async def check_message(self, user_id: int, chat_id: int):
        """Deletes unchecked messages for the specific user in the specific chat.
        Args:
            user_id: Database user id.
            chat_id: Database chat id.
        """
        await utils.check_messages_in_the_chat(user_id, chat_id)

    async def edit_message(self, user_id: int, message: dict):
        """Updates message content.
        Args:
            user_id: Database user id.
            message: Message from WebSocket connection.
        """
        is_owner = await utils.validate_message_author(message["message_id"], user_id, message["chat_id"])
        is_text = await utils.validate_message_content(message["message_id"])
        if is_owner and is_text:
            await utils.edit_message(message["message_id"], message["value"])
            await self.propagate_message(user_id, message)

    async def propagate_message(self, user_id, message):
        """Propagates messages to all connected users.
        Args:
            user_id: Database user id.
            message: Message from WebSocket connection.
        """
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
        """Saves a received message to the database and propagates it to all connected users.
        Args:
            user_id: Database user id.
            message: Message from WebSocket connection.
        """
        message_id = await utils.save_message(user_id, message["chat_id"], message["value"], message["type"])
        await self.propagate_message(user_id, {"id": message_id, "sender": user_id, **message})

    async def broadcast(self, user_id: int, message: str):
        """Receives a message from all connected users, processes it and broadcasts the result to the connected users.
        Args:
            user_id: Database user id.
            message: Message from WebSocket connection.
        """
        message = json.loads(message)
        ws_type = message["ws_type"]
        if ws_type == "send_message":
            await self.send_message(user_id, message)

        elif ws_type == "check_message":
            await self.check_message(user_id, message["chat_id"])

        elif ws_type == "edit_message":
            await self.edit_message(user_id, message)

        elif ws_type == "create_chat":
            await self.create_chat(user_id, message)


manager = ConnectionManager()
