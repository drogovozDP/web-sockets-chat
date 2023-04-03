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
    """Gets a user from database by email.
    Args:
        email: user email.
        session: A database async session.

    Returns:
        User.
    """
    user = (await session.execute(select(auth_user).where(auth_user.c.email == email))).fetchone()
    return user if user else None


async def create_user(user: UserCreate, session: AsyncSession):
    """Creates a new user and saves in the database.
    Args:
        user: A user form for user registration.
        session: A database async session.

    Returns:
        User creation status.
    """
    create_new_user = (
        insert(auth_user).values(
            email=user.email,
            name=user.name,
            surname=user.surname,
            hashed_password=hash.bcrypt.hash(user.password),
        )
    )
    await session.execute(create_new_user)
    await session.commit()
    return {"status": 200, "details": "User has been created."}


async def authenticate_user(email: str, password: str, session: AsyncSession):
    """Authenticates user.
    Args:
        email: user email.
        password: user password.
        session: A database async session.

    Returns:
        Authenticated user or False.
    """
    user = await get_user_by_email(email, session)

    if user and hash.bcrypt.verify(password, user.hashed_password):
        return user

    return False


async def create_token(user: auth_user):
    """Creates JWT token for a user.
    Args:
        user: Model from database, auth_user.

    Returns:
        Dictionary of access token and token type.
    """
    token = jwt.encode(
        {"email": user.email},
        SECRET_AUTH, algorithm=ALGORITHM
    )
    return dict(access_token=token, token_type="bearer")


async def get_current_user(token: str = Depends(oauth2_schema), session: AsyncSession = Depends(get_async_session)):
    """Gets user from database based JWT token.
    Args:
        token: JWT token.
        session: A database async session.

    Returns:
        User.
    """
    try:
        payload = jwt.decode(token, SECRET_AUTH, algorithms=[ALGORITHM])
        user = await get_user_by_email(payload["email"], session)
    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid Email or Password.")
    return user


async def get_all_users(current_user_id: int, session: AsyncSession):
    """Gets all users from the database.
    Args:
        current_user_id: database id of a user.
        session: A database async session.
    Returns:
        List of all users.
    """
    return (await session.execute(select(auth_user).where(auth_user.c.id != current_user_id))).all()
