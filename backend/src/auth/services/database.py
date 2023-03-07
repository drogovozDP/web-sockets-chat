from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.auth.models import auth_user


async def get_user_by_email(email: str, session: AsyncSession):
    query = select(auth_user).where(auth_user.c.email == email)
    result = await session.execute(query)
    return result.all()[0]
