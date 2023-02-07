from datetime import datetime

import databases
import ormar
import sqlalchemy

from backend.config import settings


database = databases.Database(settings.db_url)
metadata = sqlalchemy.MetaData()


class BaseMeta(ormar.ModelMeta):
    metadata = metadata
    database = database


class Role(ormar.Model):
    class Meta(BaseMeta):
        pass

    id: int = ormar.Integer(primary_key=True)
    name: str = ormar.String(max_length=128, nullable=False)
    permissions = ormar.JSON()


class User(ormar.Model):
    class Meta(BaseMeta):
        pass

    id: int = ormar.Integer(primary_key=True)
    email: str = ormar.String(max_length=128, unique=True, nullable=False)
    username: str = ormar.String(max_length=128, nullable=False)
    password: str = ormar.String(max_length=128, nullable=False)
    registered_at = ormar.DateTime(default=datetime.utcnow)
    role_id: Role = ormar.ForeignKey(Role)


engine = sqlalchemy.create_engine(settings.db_url)
metadata.create_all(engine)
