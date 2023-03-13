from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, Boolean, MetaData


metadata = MetaData()

auth_user = Table(
    "auth_user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, nullable=False),
    Column("name", String, nullable=False),
    Column("surname", String, nullable=False),
    Column("registered_at", TIMESTAMP, default=datetime.utcnow),
    Column("hashed_password", String, nullable=False),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_superuser", Boolean, default=False, nullable=False),
    Column("is_verified", Boolean, default=False, nullable=False),
)
