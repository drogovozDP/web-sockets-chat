import jwt
from fastapi import Depends, HTTPException
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from passlib import hash

from backend.src.config import SECRET_AUTH, ALGORITHM
from backend.src.database import get_async_session
from backend.src.auth.config import oauth2_schema
from backend.src.auth.models import auth_user
from backend.src.auth.schemas import UserCreate


async def get_user_by_email(email: str, session: AsyncSession):
    query = select(auth_user).where(auth_user.c.email == email)
    result = await session.execute(query)
    user = result.all()
    return user[0] if len(user) != 0 else None


async def create_user(user: UserCreate, session: AsyncSession):
    stmt = (
        insert(auth_user).values(
            email=user.email,
            name=user.name,
            surname=user.surname,
            hashed_password=hash.bcrypt.hash(user.password),
        )
    )
    await session.execute(stmt)
    await session.commit()
    return {"status": 200, "details": "User has been created."}


async def authenticate_user(email: str, password: str, session: AsyncSession):
    user = await get_user_by_email(email, session)

    if len(user) == 0 or not hash.bcrypt.verify(password, user.hashed_password):
        return False

    return user


async def create_token(user: auth_user):
    token = jwt.encode(
        {
            "email": user.email,
            "hashed_password": user.hashed_password,
        },
        SECRET_AUTH, algorithm=ALGORITHM  # TODO remove algorithm to .env file
    )
    return dict(access_token=token, token_type="bearer")


async def get_current_user(token: str = Depends(oauth2_schema), session: AsyncSession = Depends(get_async_session)):
    try:
        payload = jwt.decode(token, SECRET_AUTH, algorithms=[ALGORITHM])
        user = await get_user_by_email(payload["email"], session)
    except:
        raise HTTPException(status_code=401, detail="Invalid Email or Password.")
    return user


async def get_all_users(user_id: int, session: AsyncSession):
    query = select(auth_user).where(auth_user.c.id != user_id)
    result = await session.execute(query)
    return result.all()
