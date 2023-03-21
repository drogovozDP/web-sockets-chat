from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.src.chat.router import router as router_chat
# from backend.src.auth_depricated.router import router as router_auth
from backend.src.auth.router import router as router_auth


app = FastAPI(
    title="Chat FastAPI"
)

# TODO need to put in into .env
origins = [
    "http://127.0.0.1:3000",
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
