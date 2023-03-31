from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.src.config import BASE_URL
from backend.src.chat.router import router as router_chat
from backend.src.auth.router import router as router_auth


app = FastAPI(
    title="Chat FastAPI"
)

origins = [
    BASE_URL,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_auth)
app.include_router(router_chat)
