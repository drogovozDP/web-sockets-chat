from datetime import datetime
from pathlib import Path

from pydantic import BaseModel


class UserIdNameSurname(BaseModel):
    """
    Schema for getting user's name, surname and id.
    """
    id: int
    name: str


class CreateChatResponse(BaseModel):
    """
    Schema for result of chat creation.
    """
    chat_id: int
    chat_name: str
    details: str


class MessagesFromSpecificChat(BaseModel):
    """
    Schema for getting messages from specific chat.
    """
    id: int
    type: str
    value: str
    sender: int
    chat_id: int
    timestamp: datetime
    name: str
    surname: str


class GetUsersInChat(BaseModel):
    """
    Schema for getting chat users.
    """
    id: int
    name: str
    surname: str


class UncheckedMessagesAmount(BaseModel):
    """
    Schema for getting amount of unchecked messages in the specific chat.
    """
    chat_id: int
    unchecked_messages: int


class SaveFileResponse(BaseModel):
    """
    Schema for a result of file saving.
    """
    status: int
    detail: Path
