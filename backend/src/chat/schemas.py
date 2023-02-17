from datetime import datetime

from pydantic import BaseModel


class Chat(BaseModel):
    id: int
    name: str


class Message(BaseModel):
    id: int
    sender: int
    chat_id: int
    checked: bool
    timestamp: datetime


class UserChat(BaseModel):
    id: int
    user_id: int
    chat_id: int
