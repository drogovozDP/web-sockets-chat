from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, Boolean, MetaData

from backend.src.auth.models import auth_user


metadata = MetaData()
chat = Table(
    "chat",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
)

user_chat = Table(
    "user_chat",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey(auth_user.c.id)),
    Column("chat_id", Integer, ForeignKey(chat.c.id)),
)

message = Table(
    "message",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("type", String, nullable=False),
    Column("value", String, nullable=False),
    Column("sender", Integer, ForeignKey(auth_user.c.id)),
    Column("chat_id", Integer, ForeignKey(chat.c.id)),
    Column("timestamp", TIMESTAMP, nullable=False),
)

unchecked_message = Table(
    "unchecked_message",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("message_id", Integer, ForeignKey(message.c.id)),
    Column("user_id", Integer, ForeignKey(auth_user.c.id)),
)
