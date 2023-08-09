import pytest
from backend.src.database import get_async_session


def test_create_user(client):
    response = client.post(
        "/auth/register/",
        json={
            "email": "asdf@mail.com",
            "password": "kek",
            "name": "sus",
            "surname": "sursus",
        },
    )
    assert response.status_code == 200, response.text


@pytest.mark.asyncio
async def test_check_db():
    async_session = anext(get_async_session())
    session = await async_session
    a = await session.execute("SELECT 1")
    assert 0, a