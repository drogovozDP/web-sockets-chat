from fastapi.security import OAuth2PasswordBearer
from backend.src.config import SECRET_AUTH

ALGORITHM = "HS256"
oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/token")
