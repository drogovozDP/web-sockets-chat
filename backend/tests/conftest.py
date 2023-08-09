import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import create_engine

from backend.src.auth.models import metadata as auth_metadata
from backend.src.chat.models import metadata as chat_metadata
from backend.src.database import get_async_session
from backend.src.main import app


SQLALCHEMY_DATABASE_URL_SYNC = "sqlite:///./test.db"
SQLALCHEMY_DATABASE_URL_ASYNC = "sqlite+aiosqlite:///./test.db"

# SQLALCHEMY_DATABASE_URL_SYNC = "postgresql://test_user:test_pass@test_host:5434/test_db"
# SQLALCHEMY_DATABASE_URL_ASYNC = "postgresql+asyncpg://test_user:test_pass@test_host:5434/test_db"


engine = create_async_engine(SQLALCHEMY_DATABASE_URL_ASYNC)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
async def anext_session():
    return await anext(get_async_session())


@pytest.fixture(scope="session", autouse=True)
async def session():
    async_session = anext(get_async_session())
    return await async_session


def pytest_configure(config):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    engine = create_engine(SQLALCHEMY_DATABASE_URL_SYNC, connect_args={"check_same_thread": False})
    auth_metadata.create_all(bind=engine)
    chat_metadata.create_all(bind=engine)
    print("test run started!")


def pytest_sessionfinish(session, exitstatus):
    """
    Called after whole test run finished, right before
    returning the exit status to the system.
    """
    os.remove("./test.db")
    print(f"test run finished! exitstatus: {exitstatus}")
