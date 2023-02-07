from datetime import datetime
from enum import Enum
from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

# from backend.models.models import User, database

app = FastAPI(
    title="Tutorial FastAPI"
)

fake_users = [
    {"id": 1, "role": "admin", "name": "Bob"},
    {"id": 2, "role": "investor", "name": "John"},
    {"id": 3, "role": "trader", "name": "Matt"},
]


class DegreeType(Enum):
    newbie = "newbie"
    middle = "middle"
    expert = "expert"


class Degree(BaseModel):
    id: int
    created_at: datetime
    type_degree: DegreeType


class UserScheme(BaseModel):
    id: int
    role: str
    name: str
    degree: Optional[List[Degree]] = []


@app.get("/users/{user_id}", response_model=List[UserScheme])
def get_user(user_id: int):
    return [user for user in fake_users if user["id"] == user_id]


fake_trades = [
    {"id": 1, "user_id": 1, "currency": "RUB", "side": "buy", "price": 100, "amount": 2.12},
    {"id": 2, "user_id": 1, "currency": "RUB", "side": "sell", "price": 125, "amount": 2.12},
]


class Trade(BaseModel):
    id: int
    user_id: int
    currency: str
    side: str
    price: float = Field(ge=0)
    amount: float


@app.post("/trades")
def add_trades(trades: List[Trade]):
    fake_trades.extend(trades)
    return {"status": 200, "data": fake_trades}


@app.get("/")
async def read_root():
    return {"status-200": 200}


@app.on_event("startup")
async def startup():
    return {"status": 200}


@app.on_event("shutdown")
async def shutdown():
    return "cocksucker"
