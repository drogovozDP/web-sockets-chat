from typing import List, Dict
import json

from fastapi import WebSocket, Depends
from sqlalchemy import select, insert, delete

from backend.src.chat import utils
from backend.src.chat.models import user_chat, message
from backend.src.database import get_async_session


class ConnectionManager:
    def __init__(self):
        self.userid_to_socket: Dict[int, WebSocket] = {}
        self.chat_to_userid: Dict[int, List[int]] = {}
        self.userid_to_chat: Dict[int, int] = {}

    def create_chat_if_not_exists(self, chat_id):
        if chat_id not in self.chat_to_userid:
            self.chat_to_userid[chat_id] = []

    def delete_chat_if_empty(self, chat_id):
        if len(self.chat_to_userid[chat_id]) == 0:
            del self.chat_to_userid[chat_id]

    async def accept_connection(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.userid_to_socket[user_id] = websocket
        self.create_chat_if_not_exists(0)
        self.chat_to_userid[0].append(user_id)
        self.userid_to_chat[user_id] = 0

    async def connect_to_chat(self, chat_id: int, user_id: int):
        old_chat_id = self.userid_to_chat[user_id]  # find where is the socket now.
        self.chat_to_userid[old_chat_id].remove(user_id)  # remove the socket from the current chat.
        self.delete_chat_if_empty(old_chat_id)
        self.create_chat_if_not_exists(chat_id)
        self.userid_to_chat[user_id] = chat_id  # set new chat id for the socket.
        self.chat_to_userid[chat_id].append(user_id)  # add to the new chat the socket.

    def disconnect(self, user_id):
        del self.userid_to_socket[user_id]
        chat_id = self.userid_to_chat[user_id]
        del self.userid_to_chat[user_id]
        self.chat_to_userid[chat_id].remove(user_id)

    def get_online_and_offline_users(self, user_ids, chat_id):
        online, offline = [], []
        for user_id in user_ids:
            if user_id in self.chat_to_userid[chat_id]:
                online.append(user_id)
            else:
                offline.append(user_id)
        return online, offline

    async def propagate_message(self, user_id, user_message, online_users):
        for userid in online_users:
            await self.userid_to_socket[userid].send_text(json.dumps({"sender": user_id, **user_message}))

    async def propagate_notification(self, chat_id, offline_users):
        for userid in offline_users:
            message_amount = await utils.get_amount_of_unchecked_messages_in_one_chat(userid, chat_id)
            print(message_amount, "asldfkj;aslkjdf;alskjdf;alksjdf;lakjsd;flkjasd;lfkja;sldkfj;alskdjf;ajksd;lj")

            if userid in self.userid_to_socket:
                await self.userid_to_socket[userid].send_text(json.dumps({
                    "type": "notification",
                    "chat_id": chat_id,
                    "message_amount": message_amount
                }))

    async def send_message(self, user_id, user_message: dict):
        chat_id = user_message["chat_id"]
        user_ids = await utils.get_users_in_chat_socket(chat_id)
        online, offline = self.get_online_and_offline_users(user_ids, chat_id)
        await utils.save_message(user_id, user_message, offline)
        await self.propagate_message(user_id, user_message, online)
        await self.propagate_notification(user_message["chat_id"], offline)

    async def broadcast(self, user_id: int, user_message: str):
        user_message = json.loads(user_message)
        message_type = user_message["type"]
        if message_type == "select_chat":
            await utils.check_messages_in_the_chat(user_id, user_message["value"])
            await self.connect_to_chat(user_message["value"], user_id)

        elif message_type == "send_message":
            await self.send_message(user_id, user_message)


# TODO create services with sockets and db queries
manager = ConnectionManager()
