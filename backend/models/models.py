# from datetime import datetime
#
# import databases
# import ormar
# import sqlalchemy
#
# from backend.config import settings
#
#
# database = databases.Database(settings.db_url)
# metadata = sqlalchemy.MetaData()
#
#
# class BaseMeta(ormar.ModelMeta):
#     metadata = metadata
#     database = database
#
#
# class Role(ormar.Model):
#     class Meta(BaseMeta):
#         pass
#
#     id: int = ormar.Integer(primary_key=True)
#     name: str = ormar.String(max_length=128, nullable=False)
#     permissions = ormar.JSON()
#
#
# class User(ormar.Model):
#     class Meta(BaseMeta):
#         pass
#
#     id: int = ormar.Integer(primary_key=True)
#     email: str = ormar.String(max_length=128, unique=True, nullable=False)
#     username: str = ormar.String(max_length=128, nullable=False)
#     registered_at = ormar.DateTime(default=datetime.utcnow)
#     role_id: Role = ormar.ForeignKey(Role)
#     password: str = ormar.String(max_length=128, nullable=False)
#
#
# engine = sqlalchemy.create_engine(settings.db_url)
# metadata.create_all(engine)

"""
another style
"""
from datetime import datetime

import sqlalchemy
from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    JSON,
    TIMESTAMP,
    ForeignKey,
)

# from backend.config import settings


metadata = MetaData()

roles = Table(
    "roles",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("permissions", JSON),
)

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, nullable=False),
    Column("username", String, nullable=False),
    Column("registered_at", TIMESTAMP, default=datetime.utcnow),
    Column("role_id", Integer, ForeignKey("roles.id")),
    Column("password", String, nullable=False)
)

# engine = sqlalchemy.create_engine(settings.db_url)
# metadata.create_all(engine)
