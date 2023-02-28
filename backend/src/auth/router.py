from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.database import get_async_session
from backend.src.auth.schemas import UserCreate, UserRead
from backend.src.auth import utils


test_user = {
    "email": "dima@mail.com",
    "password": "dimapass",
}

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/register")
async def register(user: UserCreate, session: AsyncSession = Depends(get_async_session)):
    check_user = await utils.get_user_by_email(user.email, session)
    if len(check_user) != 0:
        raise HTTPException(status_code=400, detail="Email already in use.")
    response = await utils.create_user(user, session)
    return response


@router.post("/token")
async def generate_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_async_session)
):
    user = await utils.authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid Credentials.")

    return await utils.create_token(user)


# TODO remove hashed password from response
@router.get("/api/users/me")
async def get_user(user: UserRead = Depends(utils.get_current_user)):
    return user
