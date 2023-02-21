from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, ForeignKey, Boolean, MetaData

from backend.src.auth.models import auth_user


metadata = MetaData()
# TODO make chat's id UUID
chat = Table(
    "chat",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
)

message = Table(
    "message",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("value", String, nullable=False),
    Column("sender", Integer, ForeignKey(auth_user.c.id)),
    Column("chat_id", Integer, ForeignKey(chat.c.id)),
    Column("checked", Boolean, default=False),
    Column("timestamp", TIMESTAMP, default=datetime.utcnow),
)

user_chat = Table(
    "user_chat",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey(auth_user.c.id)),
    Column("chat_id", Integer, ForeignKey(chat.c.id)),
)
